import streamlit as st
import anthropic

# ── 페이지 설정 ──────────────────────────────────────────────
st.set_page_config(
    page_title="Claude AI 챗봇",
    page_icon="🤖",
    layout="centered",
)

# ── CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
    .usage-box {
        background: #f0f4ff;
        border: 1px solid #c7d2fe;
        border-radius: 10px;
        padding: 14px 20px;
        margin-top: 16px;
        font-size: 0.9rem;
        color: #3730a3;
    }
    .usage-box b { color: #1e1b4b; }
    .stTextArea textarea { font-size: 1rem; }
</style>
""", unsafe_allow_html=True)

# ── 헤더 ─────────────────────────────────────────────────────
st.title("🤖 Claude AI 챗봇")
st.caption("Anthropic Claude API를 활용한 AI 질문 앱")

# ── API 키 로드 (Streamlit Secrets) ──────────────────────────
try:
    api_key = st.secrets["ANTHROPIC_API_KEY"]
except KeyError:
    st.error(
        "⚠️ API 키를 찾을 수 없습니다. "
        "Streamlit Cloud → Settings → Secrets에 `ANTHROPIC_API_KEY`를 추가해 주세요."
    )
    st.stop()

client = anthropic.Anthropic(api_key=api_key)

# ── 모델 선택 ────────────────────────────────────────────────
MODEL_OPTIONS = {
    "Claude Sonnet 4.6  (빠르고 효율적)": "claude-sonnet-4-6",
    "Claude Opus 4.6  (가장 강력)":       "claude-opus-4-6",
}

selected_label = st.selectbox("🧠 모델 선택", list(MODEL_OPTIONS.keys()))
model_id = MODEL_OPTIONS[selected_label]

st.divider()

# ── 대화 기록 초기화 ─────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "total_input_tokens" not in st.session_state:
    st.session_state.total_input_tokens = 0
if "total_output_tokens" not in st.session_state:
    st.session_state.total_output_tokens = 0

# ── 대화 기록 표시 ───────────────────────────────────────────
for msg in st.session_state.messages:
    role_label = "🧑 사용자" if msg["role"] == "user" else "🤖 Claude"
    with st.chat_message(msg["role"]):
        st.markdown(f"**{role_label}**\n\n{msg['content']}")

# ── 입력창 ───────────────────────────────────────────────────
user_input = st.chat_input("질문을 입력하세요...")

if user_input:
    # 사용자 메시지 저장 & 표시
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(f"**🧑 사용자**\n\n{user_input}")

    # API 호출
    with st.chat_message("assistant"):
        with st.spinner("Claude가 생각 중..."):
            try:
                response = client.messages.create(
                    model=model_id,
                    max_tokens=2048,
                    messages=st.session_state.messages,
                )

                answer = response.content[0].text
                input_tokens  = response.usage.input_tokens
                output_tokens = response.usage.output_tokens

                # 누적 토큰 업데이트
                st.session_state.total_input_tokens  += input_tokens
                st.session_state.total_output_tokens += output_tokens

                # 답변 표시
                st.markdown(f"**🤖 Claude**\n\n{answer}")

                # 이번 턴 사용량
                st.markdown(
                    f"""<div class="usage-box">
                    📊 <b>이번 응답 토큰 사용량</b><br>
                    &nbsp;&nbsp;• 입력: <b>{input_tokens:,}</b> 토큰 &nbsp;|&nbsp;
                    출력: <b>{output_tokens:,}</b> 토큰 &nbsp;|&nbsp;
                    합계: <b>{input_tokens + output_tokens:,}</b> 토큰<br>
                    📈 <b>누적 사용량</b><br>
                    &nbsp;&nbsp;• 입력: <b>{st.session_state.total_input_tokens:,}</b> &nbsp;|&nbsp;
                    출력: <b>{st.session_state.total_output_tokens:,}</b> &nbsp;|&nbsp;
                    합계: <b>{st.session_state.total_input_tokens + st.session_state.total_output_tokens:,}</b>
                    </div>""",
                    unsafe_allow_html=True,
                )

                # 어시스턴트 메시지 저장
                st.session_state.messages.append({"role": "assistant", "content": answer})

            except anthropic.AuthenticationError:
                st.error("❌ API 키가 유효하지 않습니다. Secrets 설정을 확인해 주세요.")
            except anthropic.RateLimitError:
                st.error("⏳ API 요청 한도를 초과했습니다. 잠시 후 다시 시도해 주세요.")
            except Exception as e:
                st.error(f"❌ 오류가 발생했습니다: {e}")

# ── 대화 초기화 버튼 ─────────────────────────────────────────
if st.session_state.messages:
    st.divider()
    if st.button("🗑️ 대화 초기화"):
        st.session_state.messages = []
        st.session_state.total_input_tokens  = 0
        st.session_state.total_output_tokens = 0
        st.rerun()

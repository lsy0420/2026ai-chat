import streamlit as st
import anthropic

# ── 페이지 설정 ──────────────────────────────────────────────
st.set_page_config(
    page_title="Claude AI",
    page_icon="◈",
    layout="centered",
)

# ── 전체 디자인 CSS ───────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&family=DM+Mono:wght@400;500&display=swap');

/* ── 전역 배경 & 폰트 ── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stHeader"],
section.main {
    background-color: #F5F4F1 !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── 메인 컨테이너 ── */
.block-container {
    max-width: 740px !important;
    padding: 2rem 2rem 7rem 2rem !important;
}

/* ── 헤더 ── */
.app-header {
    text-align: center;
    padding: 2.6rem 0 1.8rem 0;
}
.app-logo {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 50px; height: 50px;
    background: #1C1C1A;
    border-radius: 13px;
    font-size: 1.4rem;
    color: #F5F4F1;
    margin-bottom: 1rem;
    box-shadow: 0 4px 18px rgba(0,0,0,0.13);
}
.app-title {
    font-size: 1.9rem;
    font-weight: 600;
    letter-spacing: -0.035em;
    color: #1C1C1A;
    margin: 0 0 0.25rem 0;
    line-height: 1.1;
}
.app-subtitle {
    font-size: 0.85rem;
    color: #9B9790;
    font-weight: 400;
    letter-spacing: 0.02em;
}

/* ── selectbox ── */
[data-testid="stSelectbox"] label {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    color: #9B9790 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}
[data-testid="stSelectbox"] > div > div {
    background: #EDECEA !important;
    border: 1.5px solid #DDDBD7 !important;
    border-radius: 10px !important;
    color: #1C1C1A !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.93rem !important;
    font-weight: 500 !important;
    box-shadow: none !important;
}
[data-testid="stSelectbox"] > div > div:hover {
    border-color: #AAAAAA !important;
}

/* ── 구분선 ── */
.thin-rule {
    border: none;
    border-top: 1px solid #E2E0DA;
    margin: 1.4rem 0;
}

/* ── 메시지 버블: 사용자 ── */
.msg-user {
    background: #1C1C1A;
    color: #F5F4F1;
    border-radius: 18px 18px 4px 18px;
    padding: 0.95rem 1.25rem;
    margin: 0.5rem 0 0.5rem 4rem;
    font-size: 0.93rem;
    line-height: 1.7;
    font-weight: 400;
    box-shadow: 0 2px 10px rgba(0,0,0,0.12);
    word-break: break-word;
}
/* ── 메시지 버블: Claude ── */
.msg-assistant {
    background: #FFFFFF;
    color: #1C1C1A;
    border-radius: 18px 18px 18px 4px;
    padding: 0.95rem 1.25rem;
    margin: 0.5rem 4rem 0.2rem 0;
    font-size: 0.93rem;
    line-height: 1.78;
    font-weight: 400;
    border: 1px solid #E5E3DF;
    box-shadow: 0 2px 14px rgba(0,0,0,0.045);
    word-break: break-word;
}
.msg-label {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
    opacity: 0.45;
}

/* ── 토큰 사용량 카드 ── */
.usage-card {
    background: #FAFAF8;
    border: 1px solid #E5E3DF;
    border-radius: 11px;
    padding: 0.9rem 1.2rem;
    margin: 0.15rem 4rem 0.9rem 0;
    display: flex;
    flex-wrap: wrap;
    gap: 1.2rem;
    align-items: flex-start;
}
.usage-group { display: flex; flex-direction: column; gap: 0.5rem; }
.usage-badge {
    font-size: 0.63rem;
    font-weight: 700;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    padding: 0.12rem 0.45rem;
    border-radius: 4px;
    display: inline-block;
    width: fit-content;
}
.badge-this { background: #1C1C1A; color: #F5F4F1; }
.badge-total { background: #EDECEA; color: #888580; }
.usage-row { display: flex; gap: 1.2rem; flex-wrap: wrap; }
.usage-item { display: flex; flex-direction: column; }
.usage-val {
    font-family: 'DM Mono', monospace;
    font-size: 1.05rem;
    font-weight: 500;
    color: #1C1C1A;
    letter-spacing: -0.02em;
}
.usage-key { font-size: 0.7rem; color: #AEABA5; margin-top: 0.05rem; }
.usage-sep {
    width: 1px;
    background: #E5E3DF;
    align-self: stretch;
    margin: 0 0.1rem;
}

/* ── 빈 화면 힌트 ── */
.empty-hint {
    text-align: center;
    padding: 4rem 1rem 3rem;
    color: #C5C1BA;
}
.empty-icon { font-size: 2.2rem; margin-bottom: 1rem; display: block; }
.empty-text { font-size: 0.88rem; line-height: 1.65; }

/* ── 채팅 입력창 ── */
[data-testid="stChatInputContainer"] {
    background: #F5F4F1 !important;
    border-top: 1px solid #E2E0DA !important;
    padding: 0.9rem 0 !important;
}
[data-testid="stChatInputContainer"] > div {
    background: #FFFFFF !important;
    border: 1.5px solid #DDDBD7 !important;
    border-radius: 13px !important;
    box-shadow: 0 2px 14px rgba(0,0,0,0.055) !important;
    transition: border-color 0.18s, box-shadow 0.18s;
}
[data-testid="stChatInputContainer"] > div:focus-within {
    border-color: #1C1C1A !important;
    box-shadow: 0 2px 22px rgba(0,0,0,0.10) !important;
}
[data-testid="stChatInputContainer"] textarea {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.93rem !important;
    color: #1C1C1A !important;
    background: transparent !important;
}
[data-testid="stChatInputContainer"] textarea::placeholder {
    color: #C5C1BA !important;
}

/* ── 버튼 ── */
.stButton > button {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.02em !important;
    background: #EDECEA !important;
    color: #666360 !important;
    border: 1.5px solid #DDDBD7 !important;
    border-radius: 8px !important;
    padding: 0.38rem 1rem !important;
    box-shadow: none !important;
    transition: all 0.18s !important;
}
.stButton > button:hover {
    background: #1C1C1A !important;
    color: #F5F4F1 !important;
    border-color: #1C1C1A !important;
}

/* ── 알림 박스 ── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important;
}

/* ── 스피너 텍스트 ── */
[data-testid="stSpinner"] p { color: #9B9790 !important; font-size: 0.85rem !important; }
</style>
""", unsafe_allow_html=True)

# ── 헤더 ─────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <div class="app-logo">◈</div>
    <div class="app-title">Claude AI</div>
    <div class="app-subtitle">Anthropic API &nbsp;·&nbsp; Sonnet &amp; Opus</div>
</div>
""", unsafe_allow_html=True)

# ── API 키 ────────────────────────────────────────────────────
try:
    api_key = st.secrets["ANTHROPIC_API_KEY"]
except KeyError:
    st.error("⚠️ API 키를 찾을 수 없습니다. Streamlit Cloud → Settings → Secrets에 `ANTHROPIC_API_KEY`를 추가하세요.")
    st.stop()

client = anthropic.Anthropic(api_key=api_key)

# ── 모델 선택 ────────────────────────────────────────────────
MODEL_OPTIONS = {
    "Claude Sonnet 4.6  —  빠르고 효율적": "claude-sonnet-4-6",
    "Claude Opus 4.6  —  가장 강력":       "claude-opus-4-6",
}
selected_label = st.selectbox("모델 선택", list(MODEL_OPTIONS.keys()))
model_id = MODEL_OPTIONS[selected_label]

# ── 세션 초기화 ───────────────────────────────────────────────
for key, val in [("messages", []), ("total_input_tokens", 0), ("total_output_tokens", 0)]:
    if key not in st.session_state:
        st.session_state[key] = val

st.markdown('<hr class="thin-rule">', unsafe_allow_html=True)

# ── 사용량 카드 HTML 생성 헬퍼 ───────────────────────────────
def usage_card_html(inp, out, total_inp, total_out):
    return f"""
    <div class="usage-card">
        <div class="usage-group">
            <span class="usage-badge badge-this">이번 응답</span>
            <div class="usage-row">
                <div class="usage-item">
                    <span class="usage-val">{inp:,}</span>
                    <span class="usage-key">입력 토큰</span>
                </div>
                <div class="usage-item">
                    <span class="usage-val">{out:,}</span>
                    <span class="usage-key">출력 토큰</span>
                </div>
                <div class="usage-item">
                    <span class="usage-val">{inp+out:,}</span>
                    <span class="usage-key">합계</span>
                </div>
            </div>
        </div>
        <div class="usage-sep"></div>
        <div class="usage-group">
            <span class="usage-badge badge-total">누적</span>
            <div class="usage-row">
                <div class="usage-item">
                    <span class="usage-val">{total_inp:,}</span>
                    <span class="usage-key">입력 토큰</span>
                </div>
                <div class="usage-item">
                    <span class="usage-val">{total_out:,}</span>
                    <span class="usage-key">출력 토큰</span>
                </div>
                <div class="usage-item">
                    <span class="usage-val">{total_inp+total_out:,}</span>
                    <span class="usage-key">합계</span>
                </div>
            </div>
        </div>
    </div>"""

# ── 대화 기록 표시 ───────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div class="empty-hint">
        <span class="empty-icon">💬</span>
        <div class="empty-text">
            아래 입력창에 질문을 입력하면<br>
            Claude가 바로 답변해드립니다.
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="msg-user">
                <div class="msg-label">나</div>
                {msg['content'].replace(chr(10), '<br>')}
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="msg-assistant">
                <div class="msg-label">Claude</div>
                {msg['content'].replace(chr(10), '<br>')}
            </div>""", unsafe_allow_html=True)

            if "usage" in msg:
                u = msg["usage"]
                st.markdown(usage_card_html(
                    u["input"], u["output"],
                    st.session_state.total_input_tokens,
                    st.session_state.total_output_tokens,
                ), unsafe_allow_html=True)

# ── 입력 & API 호출 ───────────────────────────────────────────
user_input = st.chat_input("메시지를 입력하세요...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    st.markdown(f"""
    <div class="msg-user">
        <div class="msg-label">나</div>
        {user_input.replace(chr(10), '<br>')}
    </div>""", unsafe_allow_html=True)

    with st.spinner("Claude가 답변을 생성하는 중..."):
        try:
            api_msgs = [{"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages]
            response = client.messages.create(
                model=model_id,
                max_tokens=2048,
                messages=api_msgs,
            )
            answer        = response.content[0].text
            input_tokens  = response.usage.input_tokens
            output_tokens = response.usage.output_tokens

            st.session_state.total_input_tokens  += input_tokens
            st.session_state.total_output_tokens += output_tokens

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "usage": {"input": input_tokens, "output": output_tokens},
            })

            st.markdown(f"""
            <div class="msg-assistant">
                <div class="msg-label">Claude</div>
                {answer.replace(chr(10), '<br>')}
            </div>""", unsafe_allow_html=True)

            st.markdown(usage_card_html(
                input_tokens, output_tokens,
                st.session_state.total_input_tokens,
                st.session_state.total_output_tokens,
            ), unsafe_allow_html=True)

        except anthropic.AuthenticationError:
            st.error("❌ API 키가 유효하지 않습니다. Secrets 설정을 확인해 주세요.")
        except anthropic.RateLimitError:
            st.error("⏳ 요청 한도 초과 — 잠시 후 다시 시도해 주세요.")
        except Exception as e:
            st.error(f"❌ 오류: {e}")

# ── 초기화 버튼 ───────────────────────────────────────────────
if st.session_state.messages:
    st.markdown('<hr class="thin-rule">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([3.5, 1.8, 3.5])
    with c2:
        if st.button("대화 초기화", use_container_width=True):
            st.session_state.messages = []
            st.session_state.total_input_tokens  = 0
            st.session_state.total_output_tokens = 0
            st.rerun()

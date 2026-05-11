import streamlit as st
import anthropic

# ── 페이지 설정 ──────────────────────────────────────────────
st.set_page_config(
    page_title="Claude AI",
    page_icon="◈",
    layout="centered",
)

# ══════════════════════════════════════════════════════════════
# 💰 가격 정보 (Anthropic 공식 가격 기준, 2025년)
#    https://www.anthropic.com/pricing
#    단위: USD / 1M tokens
# ══════════════════════════════════════════════════════════════
PRICING = {
    "claude-sonnet-4-6": {"input": 3.0,  "output": 15.0},
    "claude-opus-4-6":   {"input": 15.0, "output": 75.0},
}
USD_TO_KRW = 1380  # 환율 (필요 시 수정)

def calc_cost_krw(model_id, input_tokens, output_tokens):
    """토큰 수 → 원화 비용 계산"""
    p = PRICING[model_id]
    usd = (input_tokens * p["input"] + output_tokens * p["output"]) / 1_000_000
    return usd * USD_TO_KRW

# ══════════════════════════════════════════════════════════════
# 🎭 말투 프리셋
# ══════════════════════════════════════════════════════════════
TONES = {
    "🤝 정중하게":  "당신은 정중하고 격식 있는 한국어로 답변합니다. 존댓말을 사용하고 전문적인 어조를 유지하세요.",
    "😊 친근하게":  "당신은 친근하고 편안한 한국어로 답변합니다. 부드럽고 다정한 말투를 사용하되 존댓말은 유지하세요.",
    "😎 캐주얼하게": "당신은 캐주얼하고 가벼운 한국어로 답변합니다. 반말을 사용하고 이모지를 적절히 써도 좋아요.",
    "🎓 전문적으로": "당신은 전문가처럼 논리적이고 명확한 한국어로 답변합니다. 핵심만 간결하게, 구조적으로 설명하세요.",
    "🤣 재밌게":    "당신은 유머러스하고 재치 있는 한국어로 답변합니다. 가끔 농담이나 위트를 섞어 대화를 즐겁게 만드세요.",
}

# ══════════════════════════════════════════════════════════════
# 🎨 CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&family=DM+Mono:wght@400;500&display=swap');

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stHeader"],
section.main {
    background-color: #F5F4F1 !important;
    font-family: 'DM Sans', sans-serif !important;
}
.block-container {
    max-width: 740px !important;
    padding: 2rem 2rem 7rem 2rem !important;
}

/* ── 헤더 ── */
.app-header { text-align: center; padding: 2.4rem 0 1.6rem 0; }
.app-logo {
    display: inline-flex; align-items: center; justify-content: center;
    width: 50px; height: 50px; background: #1C1C1A; border-radius: 13px;
    font-size: 1.4rem; color: #F5F4F1; margin-bottom: 1rem;
    box-shadow: 0 4px 18px rgba(0,0,0,0.13);
}
.app-title {
    font-size: 1.9rem; font-weight: 600; letter-spacing: -0.035em;
    color: #1C1C1A; margin: 0 0 0.25rem 0; line-height: 1.1;
}
.app-subtitle { font-size: 0.85rem; color: #9B9790; font-weight: 400; }

/* ── 섹션 라벨 ── */
.section-label {
    font-size: 0.72rem; font-weight: 600; letter-spacing: 0.09em;
    text-transform: uppercase; color: #9B9790; margin-bottom: 0.55rem;
}

/* ── selectbox ── */
[data-testid="stSelectbox"] label {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.72rem !important; font-weight: 600 !important;
    color: #9B9790 !important; letter-spacing: 0.09em !important;
    text-transform: uppercase !important;
}
[data-testid="stSelectbox"] > div > div {
    background: #EDECEA !important; border: 1.5px solid #DDDBD7 !important;
    border-radius: 10px !important; color: #1C1C1A !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.93rem !important; font-weight: 500 !important; box-shadow: none !important;
}
[data-testid="stSelectbox"] > div > div:hover { border-color: #AAAAAA !important; }

/* ── 말투 버튼 그룹 ── */
.tone-btn-group {
    display: flex; flex-wrap: wrap; gap: 0.45rem; margin-bottom: 0.2rem;
}
.tone-btn {
    display: inline-block;
    padding: 0.38rem 0.85rem;
    border-radius: 20px;
    font-size: 0.82rem; font-weight: 500;
    border: 1.5px solid #DDDBD7;
    background: #EDECEA; color: #555250;
    cursor: pointer; transition: all 0.16s;
    font-family: 'DM Sans', sans-serif;
    white-space: nowrap;
}
.tone-btn.active {
    background: #1C1C1A; color: #F5F4F1; border-color: #1C1C1A;
}

/* ── 구분선 ── */
.thin-rule { border: none; border-top: 1px solid #E2E0DA; margin: 1.3rem 0; }

/* ── 메시지 버블 ── */
.msg-user {
    background: #1C1C1A; color: #F5F4F1;
    border-radius: 18px 18px 4px 18px;
    padding: 0.95rem 1.25rem; margin: 0.5rem 0 0.5rem 4rem;
    font-size: 0.93rem; line-height: 1.7; font-weight: 400;
    box-shadow: 0 2px 10px rgba(0,0,0,0.12); word-break: break-word;
}
.msg-assistant {
    background: #FFFFFF; color: #1C1C1A;
    border-radius: 18px 18px 18px 4px;
    padding: 0.95rem 1.25rem; margin: 0.5rem 4rem 0.2rem 0;
    font-size: 0.93rem; line-height: 1.78; font-weight: 400;
    border: 1px solid #E5E3DF; box-shadow: 0 2px 14px rgba(0,0,0,0.045);
    word-break: break-word;
}
.msg-label {
    font-size: 0.68rem; font-weight: 600; letter-spacing: 0.1em;
    text-transform: uppercase; margin-bottom: 0.4rem; opacity: 0.45;
}

/* ── 비용 카드 ── */
.cost-card {
    background: #FAFAF8; border: 1px solid #E5E3DF; border-radius: 11px;
    padding: 0.85rem 1.2rem; margin: 0.15rem 4rem 0.9rem 0;
    display: flex; flex-wrap: wrap; gap: 1.2rem; align-items: flex-start;
}
.cost-group { display: flex; flex-direction: column; gap: 0.5rem; }
.cost-badge {
    font-size: 0.63rem; font-weight: 700; letter-spacing: 0.09em;
    text-transform: uppercase; padding: 0.12rem 0.45rem;
    border-radius: 4px; display: inline-block; width: fit-content;
}
.badge-this  { background: #1C1C1A; color: #F5F4F1; }
.badge-total { background: #EDECEA; color: #888580; }
.cost-row { display: flex; gap: 1.4rem; flex-wrap: wrap; }
.cost-item { display: flex; flex-direction: column; }
.cost-val {
    font-family: 'DM Mono', monospace; font-size: 1.05rem;
    font-weight: 500; color: #1C1C1A; letter-spacing: -0.02em;
}
.cost-key { font-size: 0.7rem; color: #AEABA5; margin-top: 0.05rem; }
.cost-sep { width: 1px; background: #E5E3DF; align-self: stretch; margin: 0 0.1rem; }

/* ── 빈 화면 ── */
.empty-hint { text-align: center; padding: 3.5rem 1rem 3rem; color: #C5C1BA; }
.empty-icon { font-size: 2.2rem; margin-bottom: 1rem; display: block; }
.empty-text { font-size: 0.88rem; line-height: 1.65; }

/* ── 채팅 입력창 ── */
[data-testid="stChatInputContainer"] {
    background: #F5F4F1 !important; border-top: 1px solid #E2E0DA !important; padding: 0.9rem 0 !important;
}
[data-testid="stChatInputContainer"] > div {
    background: #FFFFFF !important; border: 1.5px solid #DDDBD7 !important;
    border-radius: 13px !important; box-shadow: 0 2px 14px rgba(0,0,0,0.055) !important;
    transition: border-color 0.18s, box-shadow 0.18s;
}
[data-testid="stChatInputContainer"] > div:focus-within {
    border-color: #1C1C1A !important; box-shadow: 0 2px 22px rgba(0,0,0,0.10) !important;
}
[data-testid="stChatInputContainer"] textarea {
    font-family: 'DM Sans', sans-serif !important; font-size: 0.93rem !important;
    color: #1C1C1A !important; background: transparent !important;
}
[data-testid="stChatInputContainer"] textarea::placeholder { color: #C5C1BA !important; }

/* ── 버튼 (초기화 등) ── */
.stButton > button {
    font-family: 'DM Sans', sans-serif !important; font-size: 0.8rem !important;
    font-weight: 500 !important; background: #EDECEA !important; color: #666360 !important;
    border: 1.5px solid #DDDBD7 !important; border-radius: 8px !important;
    padding: 0.38rem 1rem !important; box-shadow: none !important; transition: all 0.18s !important;
}
.stButton > button:hover { background: #1C1C1A !important; color: #F5F4F1 !important; border-color: #1C1C1A !important; }

[data-testid="stAlert"] { border-radius: 10px !important; font-family: 'DM Sans', sans-serif !important; font-size: 0.88rem !important; }
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

# ── 말투 선택 (버튼) ─────────────────────────────────────────
st.markdown('<div class="section-label">말투 선택</div>', unsafe_allow_html=True)

tone_keys = list(TONES.keys())

# 세션에 선택된 말투 저장
if "selected_tone" not in st.session_state:
    st.session_state.selected_tone = tone_keys[0]

# 버튼을 columns로 배치
cols = st.columns(len(tone_keys))
for i, tone_key in enumerate(tone_keys):
    with cols[i]:
        is_active = st.session_state.selected_tone == tone_key
        btn_style = (
            "background:#1C1C1A;color:#F5F4F1;border:1.5px solid #1C1C1A;"
            if is_active else
            "background:#EDECEA;color:#555250;border:1.5px solid #DDDBD7;"
        )
        if st.button(
            tone_key,
            key=f"tone_{i}",
            use_container_width=True,
        ):
            st.session_state.selected_tone = tone_key
            st.rerun()

# 선택된 말투 안내
current_tone = st.session_state.selected_tone
st.markdown(
    f'<div style="font-size:0.78rem;color:#AEABA5;margin-top:0.3rem;margin-bottom:0.2rem;">'
    f'현재: <span style="color:#555250;font-weight:500;">{current_tone}</span></div>',
    unsafe_allow_html=True,
)

# ── 세션 초기화 ───────────────────────────────────────────────
for key, val in [
    ("messages", []),
    ("total_input_tokens", 0),
    ("total_output_tokens", 0),
    ("total_cost_krw", 0.0),
]:
    if key not in st.session_state:
        st.session_state[key] = val

st.markdown('<hr class="thin-rule">', unsafe_allow_html=True)

# ── 비용 카드 HTML ────────────────────────────────────────────
def cost_card_html(this_krw, total_krw, inp, out, total_inp, total_out):
    def fmt_krw(v):
        if v < 1:
            return f"₩{v:.4f}"
        return f"₩{v:,.1f}"

    return f"""
    <div class="cost-card">
        <div class="cost-group">
            <span class="cost-badge badge-this">이번 응답</span>
            <div class="cost-row">
                <div class="cost-item">
                    <span class="cost-val">{fmt_krw(this_krw)}</span>
                    <span class="cost-key">비용</span>
                </div>
                <div class="cost-item">
                    <span class="cost-val">{inp:,}</span>
                    <span class="cost-key">입력 토큰</span>
                </div>
                <div class="cost-item">
                    <span class="cost-val">{out:,}</span>
                    <span class="cost-key">출력 토큰</span>
                </div>
            </div>
        </div>
        <div class="cost-sep"></div>
        <div class="cost-group">
            <span class="cost-badge badge-total">누적 합계</span>
            <div class="cost-row">
                <div class="cost-item">
                    <span class="cost-val">{fmt_krw(total_krw)}</span>
                    <span class="cost-key">총 비용</span>
                </div>
                <div class="cost-item">
                    <span class="cost-val">{total_inp:,}</span>
                    <span class="cost-key">입력 토큰</span>
                </div>
                <div class="cost-item">
                    <span class="cost-val">{total_out:,}</span>
                    <span class="cost-key">출력 토큰</span>
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
            말투를 고르고 아래 입력창에 질문하면<br>
            Claude가 선택한 말투로 답변해드립니다.
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
        elif msg["role"] == "assistant":
            st.markdown(f"""
            <div class="msg-assistant">
                <div class="msg-label">Claude</div>
                {msg['content'].replace(chr(10), '<br>')}
            </div>""", unsafe_allow_html=True)

            if "cost_info" in msg:
                c = msg["cost_info"]
                st.markdown(cost_card_html(
                    c["this_krw"], c["total_krw"],
                    c["inp"], c["out"],
                    c["total_inp"], c["total_out"],
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
            # 시스템 프롬프트 (선택된 말투)
            system_prompt = TONES[st.session_state.selected_tone]

            # API 메시지 구성 (role: user / assistant 만 포함)
            api_msgs = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
                if m["role"] in ("user", "assistant")
            ]

            response = client.messages.create(
                model=model_id,
                max_tokens=2048,
                system=system_prompt,
                messages=api_msgs,
            )

            answer        = response.content[0].text
            input_tokens  = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            this_cost_krw = calc_cost_krw(model_id, input_tokens, output_tokens)

            st.session_state.total_input_tokens  += input_tokens
            st.session_state.total_output_tokens += output_tokens
            st.session_state.total_cost_krw      += this_cost_krw

            cost_info = {
                "this_krw":  this_cost_krw,
                "total_krw": st.session_state.total_cost_krw,
                "inp":       input_tokens,
                "out":       output_tokens,
                "total_inp": st.session_state.total_input_tokens,
                "total_out": st.session_state.total_output_tokens,
            }

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "cost_info": cost_info,
            })

            st.markdown(f"""
            <div class="msg-assistant">
                <div class="msg-label">Claude</div>
                {answer.replace(chr(10), '<br>')}
            </div>""", unsafe_allow_html=True)

            st.markdown(cost_card_html(
                this_cost_krw, st.session_state.total_cost_krw,
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

# ── 대화 초기화 ───────────────────────────────────────────────
if st.session_state.messages:
    st.markdown('<hr class="thin-rule">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([3.5, 1.8, 3.5])
    with c2:
        if st.button("대화 초기화", use_container_width=True):
            st.session_state.messages       = []
            st.session_state.total_input_tokens  = 0
            st.session_state.total_output_tokens = 0
            st.session_state.total_cost_krw      = 0.0
            st.rerun()

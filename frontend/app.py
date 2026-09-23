import time
import streamlit as st
from dotenv import load_dotenv
from api_client import ask_backend, check_health

load_dotenv()

st.set_page_config(
    page_title="المساعد القانوني الذكي",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ---------- تنسيق عام: RTL + خط عربي + شكل فقاعات المحادثة ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Cairo', sans-serif;
    direction: rtl;
}

.main .block-container {
    max-width: 850px;
}

/* عنوان الصفحة */
.app-header {
    text-align: center;
    padding: 1.2rem 0 0.4rem 0;
}
.app-header h1 {
    font-size: 1.9rem;
    margin-bottom: 0.2rem;
}
.app-header p {
    color: #8a8f98;
    font-size: 0.95rem;
    margin-top: 0;
}

/* رسائل المحادثة */
[data-testid="stChatMessage"] {
    direction: rtl;
    text-align: right;
    border-radius: 14px;
    padding: 0.3rem 0.2rem;
}

/* صندوق المصادر */
.sources-box {
    background-color: rgba(120, 130, 145, 0.10);
    border-right: 4px solid #2e7d32;
    border-radius: 8px;
    padding: 0.7rem 1rem;
    margin-top: 0.6rem;
    font-size: 0.88rem;
}
.sources-box b { color: #2e7d32; }
.sources-box ul { margin: 0.3rem 0 0 0; padding-right: 1.1rem; }
.sources-box li { margin-bottom: 0.15rem; }

/* رسالة الترحيب */
.welcome-box {
    background: linear-gradient(135deg, rgba(46,125,50,0.08), rgba(46,125,50,0.02));
    border: 1px solid rgba(46,125,50,0.25);
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 1rem;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ---------- الشريط الجانبي ----------
with st.sidebar:
    st.markdown("### ⚖️ عن المساعد")
    st.write(
        "مساعد قانوني ذكي يعتمد تقنية RAG للإجابة عن أسئلتك استنادًا "
        "إلى النصوص الرسمية لثلاثة قوانين مصرية فقط، مع ذكر المادة والمصدر."
    )
    st.markdown("**القوانين المتاحة:**")
    st.markdown(
        "- قانون حماية البيانات الشخصية 151/2020\n"
        "- قانون حماية المستهلك 181/2018\n"
        "- قانون العمل 14/2025"
    )
    st.divider()

    healthy = check_health()
    if healthy:
        st.success("متصل بالخادم ✅")
    else:
        st.error("غير متصل بالخادم ⚠️")
        st.caption("تأكد من تشغيل الـ backend والـ Ollama.")

    st.divider()
    if st.button("🗑️ مسح المحادثة", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.caption("⚠️ إجابات المساعد للاستئناس فقط وليست بديلاً عن استشارة قانونية رسمية.")

# ---------- رأس الصفحة ----------
st.markdown("""
<div class="app-header">
    <h1>⚖️ المساعد القانوني الذكي</h1>
    <p>اسأل عن حقوقك وفق قوانين البيانات الشخصية، حماية المستهلك، والعمل</p>
</div>
""", unsafe_allow_html=True)

# ---------- تهيئة الذاكرة ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-box">
        👋 <b>مرحبًا بك!</b>
    </div>
    """, unsafe_allow_html=True)

# ---------- عرض المحادثة السابقة ----------
for msg in st.session_state.messages:
    avatar = "🧑" if msg["role"] == "user" else "⚖️"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])
        if msg.get("sources"):
            sources_html = "".join(f"<li>{s}</li>" for s in msg["sources"])
            st.markdown(
                f'<div class="sources-box">📚 <b>المصادر:</b><ul>{sources_html}</ul></div>',
                unsafe_allow_html=True,
            )

# ---------- صندوق إدخال السؤال ----------
question = st.chat_input("اكتب سؤالك القانوني هنا...")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(question)

    with st.chat_message("assistant", avatar="⚖️"):
        placeholder = st.empty()
        placeholder.markdown("⏳ جارٍ البحث في النصوص القانونية...")
        try:
            t0 = time.time()
            result = ask_backend(question)
            dt = round(time.time() - t0, 1)
            answer = result.get("answer", "لم يتم استلام إجابة.")
            sources = result.get("sources", [])

            placeholder.markdown(answer)
            if sources:
                sources_html = "".join(f"<li>{s}</li>" for s in sources)
                st.markdown(
                    f'<div class="sources-box">📚 <b>المصادر:</b><ul>{sources_html}</ul></div>',
                    unsafe_allow_html=True,
                )
            st.caption(f"⏱️ زمن الاستجابة: {dt} ثانية")

            st.session_state.messages.append(
                {"role": "assistant", "content": answer, "sources": sources}
            )
        except (ConnectionError, TimeoutError, RuntimeError) as e:
            placeholder.error(f"❌ {e}")
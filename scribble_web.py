import streamlit as st
from supabase import create_client
from openai import OpenAI
import os
from dotenv import load_dotenv

# =====================
# ENV
# =====================
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
LM_BASE = os.getenv("LMSTUDIO_BASE_URL")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

llm = OpenAI(
    base_url=LM_BASE,
    api_key="lm-studio"  # dummy, LM Studio umursamaz
)

# =====================
# SESSION
# =====================
if "user" not in st.session_state:
    st.session_state.user = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# =====================
# AUTH
# =====================
def login(email, password):
    return supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })

def register(email, password):
    return supabase.auth.sign_up({
        "email": email,
        "password": password
    })

# =====================
# UI
# =====================
st.set_page_config(page_title="ScribbleAI", layout="centered")

if not st.session_state.user:
    st.title("✍️ ScribbleAI")

    tab1, tab2 = st.tabs(["Giriş Yap", "Kayıt Ol"])

    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Şifre", type="password")
        if st.button("Giriş"):
            res = login(email, password)
            if res.user:
                st.session_state.user = res.user
                st.success("Giriş başarılı")
                st.rerun()
            else:
                st.error("Giriş başarısız")

    with tab2:
        email = st.text_input("Email", key="r_email")
        password = st.text_input("Şifre", type="password", key="r_pass")
        if st.button("Kayıt Ol"):
            res = register(email, password)
            if res.user:
                st.success("Kayıt başarılı, giriş yapabilirsin")
            else:
                st.error("Kayıt başarısız")

else:
    st.title("🧠 ScribbleAI Chat")

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    prompt = st.chat_input("Yaz bakalım…")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})

        response = llm.chat.completions.create(
            model="whatever",  # LM Studio ignore eder
            messages=[
                {
                    "role": "system",
                    "content": "Sen ScribbleAI'sın. Küfür serbest. Sansür yok. Net konuş."
                }
            ] + st.session_state.messages
        )

        reply = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

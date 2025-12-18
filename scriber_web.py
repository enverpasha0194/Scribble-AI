import streamlit as st
from openai import OpenAI
from supabase import create_client, Client
import uuid
import bcrypt

# ==============================
# 🔑 AYARLAR
# ==============================
SUPABASE_URL = "https://rhenrzjfkiefhzfkkwgv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJoZW5yempma2llZmh6Zmtrd2d2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjYwNzY3MTMsImV4cCI6MjA4MTY1MjcxM30.gwjvIT5M8PyP9SBysXImyNblPm6XNwJTeZAayUeVCxU"
NGROK_URL = "https://hydropathical-duodecastyle-camron.ngrok-free.dev"
LOGO_URL = "https://i.ibb.co/CD44FDc/Chat-GPT-mage-17-Ara-2025-23-59-13.png"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(
    page_title="SCRIBER AI",
    page_icon=LOGO_URL,
    layout="wide"
)

# ==============================
# 🎨 GLOBAL CSS (GÜNCELLENMİŞ)
# ==============================
st.markdown("""
<style>

/* === ANA ARKAPLAN === */
.stApp {
    background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #1e215a);
    background-size: 400% 400%;
    animation: gradient 15s ease infinite;
}
@keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* === ALT BEYAZ ŞERİT VE GÖLGEYİ TAMAMEN KALDIR === */
div[data-testid="stBottom"], 
div[data-testid="stBottomBlockContainer"] {
    background-color: transparent !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

/* Chat input kapsayıcısını şeffaf yap */
.stChatInput {
    background-color: transparent !important;
}

/* === TEXT INPUT + PASSWORD === */
div[data-testid="stTextInput"],
div[data-testid="stPasswordInput"] {
    background: transparent !important;
}

div[data-testid="stTextInput"] input,
div[data-testid="stPasswordInput"] input {
    background-color: rgba(255,255,255,0.05) !important;
    border: 2px solid #6a11cb !important;
    border-radius: 12px !important;
    color: white !important;
}

/* placeholder */
input::placeholder {
    color: rgba(255,255,255,0.6) !important;
}

/* === CHAT INPUT TEXTAREA === */
textarea[data-testid="stChatInputTextArea"] {
    background-color: rgba(255,255,255,0.07) !important;
    border: 2px solid #6a11cb !important;
    border-radius: 15px !important;
    color: white !important;
}

/* === BUTONLAR === */
button {
    background-color: #393863 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
button:hover {
    opacity: 0.9;
}

/* === SIDEBAR === */
section[data-testid="stSidebar"] {
    background-color: rgba(5,5,20,0.95) !important;
    border-right: 1px solid #6a11cb !important;
}

/* === GENEL === */
header, footer, #MainMenu { visibility: hidden; }
h1,h2,h3,p,span,label { color: white !important; }
input:focus, textarea:focus {
    outline: none !important;
    box-shadow: none !important;
}

</style>
""", unsafe_allow_html=True)

# ==============================
# 🔐 ŞİFRE FONKSİYONLARI
# ==============================
def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

def check_password(pw: str, hashed: str) -> bool:
    return bcrypt.checkpw(pw.encode(), hashed.encode())

# ==============================
# 🔐 AUTH MANTIĞI
# ==============================
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

if "user" not in st.session_state:
    st.markdown("<h1 style='text-align:center'>SCRIBER AI</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,2,1])

    with col:
        if st.session_state.auth_mode == "login":
            u = st.text_input("Kullanıcı adı")
            p = st.text_input("Şifre", type="password")

            if st.button("Giriş Yap", use_container_width=True):
                res = supabase.table("scriber_users").select("*").eq("username", u).execute()
                if res.data and check_password(p, res.data[0]["password"]):
                    st.session_state.user = u
                    st.rerun()
                else:
                    st.error("Hatalı giriş")

            if st.button("Kayıt Ol"):
                st.session_state.auth_mode = "register"
                st.rerun()
        else:
            u = st.text_input("Yeni kullanıcı adı")
            p1 = st.text_input("Şifre", type="password")
            p2 = st.text_input("Şifre tekrar", type="password")

            if st.button("Hesap Oluştur"):
                if p1 == p2:
                    supabase.table("scriber_users").insert({
                        "username": u,
                        "password": hash_password(p1)
                    }).execute()
                    st.session_state.auth_mode = "login"
                    st.rerun()
                else:
                    st.error("Şifreler uyuşmuyor")

    st.stop()

# ==============================
# 🧠 OTURUM YÖNETİMİ
# ==============================
if "chat_id" not in st.session_state:
    st.session_state.chat_id = str(uuid.uuid4())
if "history" not in st.session_state:
    st.session_state.history = []

# ==============================
# 🧭 SIDEBAR
# ==============================
with st.sidebar:
    st.image(LOGO_URL, width=100)
    st.write(f"👤 {st.session_state.user}")

    if st.button("➕ Yeni Sohbet", use_container_width=True):
        st.session_state.chat_id = str(uuid.uuid4())
        st.session_state.history = []
        st.rerun()

# ==============================
# 🤖 CHAT ARAYÜZÜ
# ==============================
st.markdown("<h1 style='text-align:center'>SCRIBER AI</h1>", unsafe_allow_html=True)

client = OpenAI(base_url=f"{NGROK_URL}/v1", api_key="lm-studio")

for msg in st.session_state.history:
    with st.chat_message(msg["role"], avatar=LOGO_URL if msg["role"]=="assistant" else None):
        st.markdown(msg["content"])

if prompt := st.chat_input("Scriber'a yaz..."):
    st.session_state.history.append({"role":"user","content":prompt})

    with st.chat_message("assistant", avatar=LOGO_URL):
        r = client.chat.completions.create(
            model="llama3-turkish",
            messages=st.session_state.history
        )
        reply = r.choices[0].message.content
        st.markdown(reply)

    st.session_state.history.append({"role":"assistant","content":reply})

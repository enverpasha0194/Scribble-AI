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
# 🎨 DERHAL DÜZELTİLMİŞ CSS (WAVY + TAM ŞEFFAF)
# ==============================
st.markdown("""
<style>

/* === 1. WAVY ARKAPLAN (GÜÇLENDİRİLDİ) === */
.stApp {
    background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #1e215a) !important;
    background-size: 400% 400% !important;
    animation: gradient 15s ease infinite !important;
}
@keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* === 2. BEYAZ ŞERİT VE ÇERÇEVE KATİLİ === */
/* Streamlit'in alt panelindeki tüm katmanları (div'leri) şeffaf yapar */
[data-testid="stBottom"], 
[data-testid="stBottomBlockContainer"],
[data-testid="stElementContainer"],
.st-emotion-cache-1p2n2i4, 
.st-emotion-cache-128upt6, 
.st-emotion-cache-1y34ygi,
.st-emotion-cache-k7rogd {
    background-color: transparent !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

/* Input'un etrafındaki o "garip" gölgeyi ve beyaz alanı temizler */
.stChatInput {
    background-color: transparent !important;
    border: none !important;
}

/* === 3. CHAT INPUT KUTUSU (TAM OTURTULMUŞ) === */
textarea[data-testid="stChatInputTextArea"] {
    background-color: rgba(255, 255, 255, 0.05) !important;
    border: 2px solid #6a11cb !important;
    border-radius: 25px !important; /* Daha oval bir görünüm için */
    color: white !important;
    margin-bottom: 5px !important;
}

/* Gönder butonunun arka planını ve rengini temizle */
[data-testid="stChatInputSubmitButton"] {
    background-color: transparent !important;
    border: none !important;
    color: #6a11cb !important;
}

/* === 4. SIDEBAR VE DİĞERLERİ === */
section[data-testid="stSidebar"] {
    background-color: rgba(5, 5, 20, 0.95) !important;
    border-right: 1px solid #6a11cb !important;
}

/* Mesaj balonları */
[data-testid="stChatMessage"] {
    background-color: rgba(255, 255, 255, 0.05) !important;
    border-radius: 15px !important;
}

/* Gereksiz her şeyi gizle */
header, footer, #MainMenu {visibility: hidden !important;}

</style>
""", unsafe_allow_html=True)

# ==============================
# 🔐 AUTH MANTIĞI
# ==============================
def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

def check_password(pw: str, hashed: str) -> bool:
    return bcrypt.checkpw(pw.encode(), hashed.encode())

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
                else: st.error("Hatalı giriş")
            if st.button("Kayıt Ol"):
                st.session_state.auth_mode = "register"; st.rerun()
        else:
            u = st.text_input("Yeni kullanıcı adı")
            p1 = st.text_input("Şifre", type="password")
            p2 = st.text_input("Şifre tekrar", type="password")
            if st.button("Hesap Oluştur"):
                if p1 == p2:
                    supabase.table("scriber_users").insert({"username": u, "password": hash_password(p1)}).execute()
                    st.session_state.auth_mode = "login"; st.rerun()
                else: st.error("Şifreler uyuşmuyor")
    st.stop()

# ==============================
# 🧠 CHAT
# ==============================
if "chat_id" not in st.session_state: st.session_state.chat_id = str(uuid.uuid4())
if "history" not in st.session_state: st.session_state.history = []

with st.sidebar:
    st.image(LOGO_URL, width=100)
    st.write(f"👤 {st.session_state.user}")
    if st.button("➕ Yeni Sohbet", use_container_width=True):
        st.session_state.history = []; st.rerun()

st.markdown("<h1 style='text-align:center'>SCRIBER AI</h1>", unsafe_allow_html=True)
client = OpenAI(base_url=f"{NGROK_URL}/v1", api_key="lm-studio")

for msg in st.session_state.history:
    with st.chat_message(msg["role"], avatar=LOGO_URL if msg["role"]=="assistant" else None):
        st.markdown(msg["content"])

if prompt := st.chat_input("Scriber'a yaz..."):
    st.session_state.history.append({"role":"user","content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant", avatar=LOGO_URL):
        r = client.chat.completions.create(model="llama3-turkish", messages=st.session_state.history)
        reply = r.choices[0].message.content
        st.markdown(reply)
    st.session_state.history.append({"role":"assistant","content":reply})

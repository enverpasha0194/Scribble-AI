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

st.set_page_config(page_title="SCRIBER AI", page_icon=LOGO_URL, layout="wide")

# ==============================
# 🎨 CSS
# ==============================
st.markdown("""
<style>
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
[data-testid="stBottom"], [data-testid="stBottomBlockContainer"], .st-emotion-cache-1p2n2i4, .st-emotion-cache-128upt6, .st-emotion-cache-1y34ygi {
    background: transparent !important; border: none !important;
}
div[data-testid="stChatInput"] { background-color: rgba(255,255,255,0.05) !important; border-radius: 20px !important; padding: 3px !important; }
textarea[data-testid="stChatInputTextArea"] { background-color: #ffffff !important; color: #000000 !important; border-radius: 17px !important; border: none !important; }
button, div[data-testid="stButton"] > button { background-color: #393863 !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; }
section[data-testid="stSidebar"] { background-color: rgba(5,5,20,0.9) !important; border-right: 1px solid #6a11cb !important; }
header, footer, #MainMenu { visibility: hidden; }
h1,h2,h3,p,span,label,div { color: white !important; }
</style>
""", unsafe_allow_html=True)

# ==============================
# 🔐 AUTH FONKSİYONLARI
# ==============================
def hash_password(pw: str) -> str: return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
def check_password(pw: str, hashed: str) -> bool: return bcrypt.checkpw(pw.encode(), hashed.encode())

if "user" not in st.session_state:
    st.session_state.auth_mode = "login" if "auth_mode" not in st.session_state else st.session_state.auth_mode
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
            if st.button("Kayıt Ol"): st.session_state.auth_mode = "register"; st.rerun()
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
# 📂 SOHBET YÖNETİMİ
# ==============================
if "chat_id" not in st.session_state: st.session_state.chat_id = None
if "history" not in st.session_state: st.session_state.history = []

def load_chats():
    return supabase.table("scriber_chats").select("*").eq("username", st.session_state.user).order("created_at", desc=True).execute().data

def save_message(role, content):
    if st.session_state.chat_id:
        supabase.table("scriber_messages").insert({
            "chat_id": st.session_state.chat_id,
            "role": role,
            "content": content
        }).execute()

# ==============================
# 👤 SIDEBAR (SOHBET GEÇMİŞİ)
# ==============================
with st.sidebar:
    st.image(LOGO_URL, width=100)
    st.write(f"👋 **Hoş geldin, {st.session_state.user}!**")
    
    if st.button("➕ Yeni Sohbet", use_container_width=True):
        st.session_state.chat_id = None
        st.session_state.history = []
        st.rerun()
    
    st.write("---")
    st.write("📜 **Sohbetler**")
    chats = load_chats()
    for c in chats:
        if st.button(f"💬 {c['title'][:20]}...", key=c['id'], use_container_width=True):
            st.session_state.chat_id = c['id']
            msgs = supabase.table("scriber_messages").select("*").eq("chat_id", c['id']).order("created_at").execute().data
            st.session_state.history = [{"role": m["role"], "content": m["content"]} for m in msgs]
            st.rerun()

# ==============================
# 🧠 CHAT EKRANI
# ==============================
st.markdown("<h1 style='text-align:center'>SCRIBER AI</h1>", unsafe_allow_html=True)
client = OpenAI(base_url=f"{NGROK_URL}/v1", api_key="lm-studio")

for msg in st.session_state.history:
    with st.chat_message(msg["role"], avatar=LOGO_URL if msg["role"]=="assistant" else None):
        st.markdown(msg["content"])

if prompt := st.chat_input("Scriber'a yaz..."):
    # Eğer yeni bir sohbetse önce sohbeti oluştur
    if st.session_state.chat_id is None:
        new_chat = supabase.table("scriber_chats").insert({
            "username": st.session_state.user,
            "title": prompt[:30] # İlk kelime/cümle başlık olur
        }).execute()
        st.session_state.chat_id = new_chat.data[0]["id"]

    # Kullanıcı mesajını kaydet ve göster
    st.session_state.history.append({"role": "user", "content": prompt})
    save_message("user", prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    # Yapay zeka yanıtı
    with st.chat_message("assistant", avatar=LOGO_URL):
        r = client.chat.completions.create(model="llama3-turkish", messages=st.session_state.history)
        reply = r.choices[0].message.content
        st.markdown(reply)
    
    st.session_state.history.append({"role": "assistant", "content": reply})
    save_message("assistant", reply)

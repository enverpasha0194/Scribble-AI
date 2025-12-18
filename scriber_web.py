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

# Sidebar'ın başlangıçta açık gelmesi için: initial_sidebar_state="expanded"
st.set_page_config(
    page_title="SCRIBER AI",
    page_icon=LOGO_URL,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================
# 🎨 CSS (SIDEBAR VE ÇERÇEVE FIX)
# ==============================
st.markdown("""
<style>
/* === WAVY ARKAPLAN === */
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

/* === SIDEBAR GÖRÜNÜRLÜĞÜ === */
section[data-testid="stSidebar"] {
    background-color: rgba(10, 10, 35, 0.95) !important;
    border-right: 1px solid #6a11cb !important;
    min-width: 250px !important;
}

/* Sidebar içindeki metinler */
section[data-testid="stSidebar"] .stText, 
section[data-testid="stSidebar"] p, 
section[data-testid="stSidebar"] span {
    color: white !important;
}

/* === BEYAZ ŞERİTLERİ SİL VE KUTUYU OTURT === */
[data-testid="stBottom"], [data-testid="stBottomBlockContainer"] {
    background: transparent !important;
    border: none !important;
}

div[data-testid="stChatInput"] {
    background-color: rgba(255,255,255,0.05) !important;
    border-radius: 20px !important;
    padding: 3px !important;
}
textarea[data-testid="stChatInputTextArea"] {
    background-color: #ffffff !important;
    color: #000000 !important;
    border-radius: 17px !important;
}

/* === BUTONLAR === */
button, div[data-testid="stButton"] > button {
    background-color: #393863 !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
}

header, footer, #MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ==============================
# 🔐 AUTH
# ==============================
def hash_password(pw: str) -> str: return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
def check_password(pw: str, hashed: str) -> bool: return bcrypt.checkpw(pw.encode(), hashed.encode())

if "user" not in st.session_state:
    st.session_state.auth_mode = "login"
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
    st.stop()

# ==============================
# 📂 SOHBET YÖNETİMİ
# ==============================
if "chat_id" not in st.session_state: st.session_state.chat_id = None
if "history" not in st.session_state: st.session_state.history = []

def load_chats():
    try:
        res = supabase.table("scriber_chats").select("*").eq("username", st.session_state.user).order("created_at", desc=True).execute()
        return res.data if res.data else []
    except: return []

# ==============================
# 👤 SIDEBAR (SOHBET GEÇMİŞİ)
# ==============================
with st.sidebar:
    st.image(LOGO_URL, width=100)
    st.markdown(f"### 👋 Hoş geldin,\n**{st.session_state.user}**")
    
    if st.button("➕ Yeni Sohbet", use_container_width=True):
        st.session_state.chat_id = None
        st.session_state.history = []
        st.rerun()
    
    st.write("---")
    st.subheader("📜 Sohbetler")
    
    past_chats = load_chats()
    if past_chats:
        for c in past_chats:
            # Mevcut seçili sohbeti belirtmek için küçük bir görsel fark
            label = f"💬 {c['title'][:20]}"
            if st.button(label, key=f"btn_{c['id']}", use_container_width=True):
                st.session_state.chat_id = c['id']
                msgs = supabase.table("scriber_messages").select("*").eq("chat_id", c['id']).order("created_at").execute().data
                st.session_state.history = [{"role": m["role"], "content": m["content"]} for m in msgs]
                st.rerun()
    else:
        st.write("Henüz sohbet yok.")

# ==============================
# 🧠 CHAT EKRANI
# ==============================
st.markdown("<h1 style='text-align:center'>SCRIBER AI</h1>", unsafe_allow_html=True)
client = OpenAI(base_url=f"{NGROK_URL}/v1", api_key="lm-studio")

for msg in st.session_state.history:
    with st.chat_message(msg["role"], avatar=LOGO_URL if msg["role"]=="assistant" else None):
        st.markdown(msg["content"])

if prompt := st.chat_input("Scriber'a yaz..."):
    # Yeni Sohbet Oluşturma
    if st.session_state.chat_id is None:
        new_chat = supabase.table("scriber_chats").insert({
            "username": st.session_state.user,
            "title": prompt[:30]
        }).execute()
        if new_chat.data:
            st.session_state.chat_id = new_chat.data[0]["id"]

    # Mesajları Kaydet
    st.session_state.history.append({"role": "user", "content": prompt})
    supabase.table("scriber_messages").insert({"chat_id": st.session_state.chat_id, "role": "user", "content": prompt}).execute()
    
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=LOGO_URL):
        r = client.chat.completions.create(model="llama3-turkish", messages=st.session_state.history)
        reply = r.choices[0].message.content
        st.markdown(reply)
    
    st.session_state.history.append({"role": "assistant", "content": reply})
    supabase.table("scriber_messages").insert({"chat_id": st.session_state.chat_id, "role": "assistant", "content": reply}).execute()

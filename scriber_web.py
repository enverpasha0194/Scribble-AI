import streamlit as st
from openai import OpenAI
from supabase import create_client, Client
import bcrypt
import time

# ==============================
# 🔑 AYARLAR & KİŞİLİK (SYSTEM PROMPT)
# ==============================
SUPABASE_URL = "https://rhenrzjfkiefhzfkkwgv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJoZW5yempma2llZmh6Zmtrd2d2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjYwNzY3MTMsImV4cCI6MjA4MTY1MjcxM30.gwjvIT5M8PyP9SBysXImyNblPm6XNwJTeZAayUeVCxU"
NGROK_URL = "https://hydropathical-duodecastyle-camron.ngrok-free.dev"
LOGO_URL = "https://i.ibb.co/CD44FDc/Chat-GPT-mage-17-Ara-2025-23-59-13.png"

SYSTEM_PROMPT = """Senin adın SCRIBER AI. Kullanıcılara yardımcı olan, kafa dengi bir yapay zekasın, kurucun Yusuf Alp ancak bundan sorulmadıkça bahsedemezsin, kullanıcı seninle nasıl tarzda konuşursa konuşsun eğlenceli ve kafa dengi bir tarzda konuş."""

# Supabase Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(
    page_title="SCRIBER AI", 
    page_icon=LOGO_URL, 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================
# 🎨 CSS (BEYAZ ŞERİT FİX + YAZIYOR EFEKTİ UYUMU)
# ==============================
st.markdown("""
<style>
/* === GENEL ARKA PLAN === */
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

/* === BEYAZ ŞERİT VE ALT KISIM TAM TEMİZLİK === */
[data-testid="stBottom"], 
[data-testid="stBottomBlockContainer"],
footer, header, 
div[class*="st-emotion-cache-128upt6"], 
div[class*="st-emotion-cache-1p2n2i4"],
div[class*="st-emotion-cache-1y34ygl"] {
    background-color: transparent !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

/* === SİDEBAR TASARIMI === */
section[data-testid="stSidebar"] {
    background-color: rgba(10, 10, 30, 0.98) !important;
    border-right: 1px solid #6a11cb !important;
    min-width: 350px !important;
}

/* === TÜM BUTONLAR (#393863) === */
button, div[data-testid="stButton"] > button, [data-testid="stSidebar"] button {
    background-color: #393863 !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}

/* === CHAT INPUT ARKA PLAN VE TEXT === */
div[data-testid="stChatInput"] {
    background-color: rgba(255, 255, 255, 0.05) !important;
    border-radius: 20px !important;
    padding: 3px !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
}
textarea[data-testid="stChatInputTextArea"] {
    background-color: #ffffff !important;
    color: #000000 !important;
    border-radius: 17px !important;
}

h1, h2, h3, p, span, label, b { color: white !important; }
#MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ==============================
# 🔐 AUTH
# ==============================
def hash_password(pw: str) -> str: return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
def check_password(pw: str, hashed: str) -> bool: return bcrypt.checkpw(pw.encode(), hashed.encode())

if "user" not in st.session_state:
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"

    st.markdown("<h1 style='text-align:center'>SCRIBER AI</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,2,1])
    
    with col:
        if st.session_state.auth_mode == "login":
            st.markdown("### Giriş Yap")
            with st.form("login_form"):
                u = st.text_input("Kullanıcı adı")
                p = st.text_input("Şifre", type="password")
                submit_login = st.form_submit_button("Giriş Yap", use_container_width=True)

                if submit_login:
                    if u and p:
                        try:
                            res = supabase.table("scriber_users").select("*").eq("username", u).execute()
                            if res.data and check_password(p, res.data[0]["password"]):
                                st.session_state.user = u
                                st.rerun()
                            else: st.error("Hatalı kullanıcı adı veya şifre.")
                        except Exception as e: st.error(f"Giriş hatası: {e}")

            if st.button("Hesabın yok mu? Kayıt Ol", use_container_width=True):
                st.session_state.auth_mode = "register"
                st.rerun()
        else:
            st.markdown("### Yeni Hesap Oluştur")
            with st.form("register_form"):
                u = st.text_input("Yeni kullanıcı adı")
                p1 = st.text_input("Şifre", type="password")
                p2 = st.text_input("Şifre tekrar", type="password")
                submit_register = st.form_submit_button("Hesap Oluştur", use_container_width=True)

                if submit_register:
                    if u and p1 == p2:
                        try:
                            check_user = supabase.table("scriber_users").select("*").eq("username", u).execute()
                            if check_user.data: st.error("Bu kullanıcı adı zaten kullanımda.")
                            else:
                                supabase.table("scriber_users").insert({"username": u, "password": hash_password(p1)}).execute()
                                st.success("Kayıt başarılı! Giriş yapabilirsiniz.")
                                time.sleep(1)
                                st.session_state.auth_mode = "login"
                                st.rerun()
                        except Exception as e: st.error(f"Kayıt hatası: {e}")

            if st.button("Giriş ekranına dön", use_container_width=True):
                st.session_state.auth_mode = "login"
                st.rerun()
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

def save_message(role, content):
    if st.session_state.chat_id:
        try:
            supabase.table("scriber_messages").insert({"chat_id": st.session_state.chat_id, "role": role, "content": content}).execute()
        except: pass

# ==============================
# 👤 SIDEBAR
# ==============================
with st.sidebar:
    st.image(LOGO_URL, width=100)
    st.markdown(f"### 👋 Hoş geldin, \n**{st.session_state.user}**")
    
    if st.button("➕ Yeni Sohbet", use_container_width=True):
        st.session_state.chat_id = None
        st.session_state.history = []
        st.rerun()
    
    st.write("---")
    st.markdown("### 📜 Sohbetler")
    chats = load_chats()
    for c in chats:
        if st.button(f"💬 {c['title'][:25]}", key=c['id'], use_container_width=True):
            st.session_state.chat_id = c['id']
            msgs = supabase.table("scriber_messages").select("*").eq("chat_id", c['id']).order("created_at").execute().data
            st.session_state.history = [{"role": m["role"], "content": m["content"]} for m in msgs]
            st.rerun()

# ==============================
# 🧠 CHAT EKRANI (STREAMING ENTEGRELİ)
# ==============================
st.markdown("<h1 style='text-align:center'>SCRIBER AI</h1>", unsafe_allow_html=True)
client = OpenAI(base_url=f"{NGROK_URL}/v1", api_key="lm-studio")

# Geçmiş mesajları göster
for msg in st.session_state.history:
    with st.chat_message(msg["role"], avatar=LOGO_URL if msg["role"]=="assistant" else None):
        st.markdown(msg["content"])

# Yeni mesaj girişi
if prompt := st.chat_input("Scriber'a yaz..."):
    if st.session_state.chat_id is None:
        try:
            new_chat = supabase.table("scriber_chats").insert({"username": st.session_state.user, "title": prompt[:30]}).execute()
            if new_chat.data: st.session_state.chat_id = new_chat.data[0]["id"]
        except: pass

    # Kullanıcı mesajı
    st.session_state.history.append({"role": "user", "content": prompt})
    save_message("user", prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    # Yapay zeka cevabı (TEKER TEKER YAZMA)
    with st.chat_message("assistant", avatar=LOGO_URL):
        try:
            messages_with_persona = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.history
            
            # Stream başlatılıyor
            stream = client.chat.completions.create(
                model="llama3-turkish", 
                messages=messages_with_persona,
                stream=True
            )
            
            # st.write_stream kelimeleri akıtır ve bitince tam metni döner
            full_response = st.write_stream(stream)
            
            st.session_state.history.append({"role": "assistant", "content": full_response})
            save_message("assistant", full_response)
        except Exception as e:
            st.error(f"Yapay zeka yanıt veremedi: {e}")

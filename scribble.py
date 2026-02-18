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
# BURAYA GitHub'daki ses dosyasının RAW linkini yapıştır:
BEEP_SOUND_URL = "https://github.com/enverpasha0194/Scribble-AI/blob/main/beep" 

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(
    page_title="SCRIBER AI",
    page_icon=LOGO_URL,
    layout="wide"
)

# ==============================
# ✨ CSS: GÖRSEL DÜZENLEMELER
# ==============================
st.markdown(f"""
<style>
    /* 1. WAVE ANIMASYONU */
    .stApp {{
        background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #1e215a);
        background-size: 400% 400% !important;
        animation: gradient 15s ease infinite !important;
    }}
    @keyframes gradient {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    /* 2. BEYAZ ŞERİDİ SİL */
    [data-testid="stBottomBlockContainer"] {{
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
    }}
    .st-emotion-cache-1y34ygi, .e4man117, .st-emotion-cache-tn0cau, .ek2vi383, .st-emotion-cache-1vo6xi6, .ek2vi381 {{
        background: transparent !important;
        box-shadow: none !important;
    }}

    /* 3. SIDEBAR BUTONLARI (Görünür Yazılar) */
    section[data-testid="stSidebar"] {{
        background-color: rgba(5, 5, 20, 0.95) !important;
    }}
    div[data-testid="stSidebar"] button {{
        background-color: #353254 !important;
        color: white !important; /* Yazıları görünecek renk yaptık */
        border: 1px solid #6a11cb !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }}

    /* 4. GENEL ELEMENTLER */
    header, footer, #MainMenu {{visibility: hidden;}}
    h1, h2, h3, p, span, label, .stMarkdown {{ color: white !important; }}
    
    div[data-testid="stChatInput"] {{
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 2px solid #6a11cb !important;
        border-radius: 15px !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- AUTH FONKSİYONLARI ---
def hash_password(pw: str) -> str: return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
def check_password(pw: str, hashed: str) -> bool:
    try: return bcrypt.checkpw(pw.encode(), hashed.encode())
    except: return False

if "auth_mode" not in st.session_state: st.session_state.auth_mode = "login"

if "user" not in st.session_state:
    st.markdown("<h1 style='text-align:center'>SCRIBER AI</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.session_state.auth_mode == "login":
            u = st.text_input("Kullanıcı adı")
            p = st.text_input("Şifre", type="password")
            if st.button("Giriş Yap", use_container_width=True):
                res = supabase.table("scriber_users").select("*").eq("username", u).execute()
                if res.data and check_password(p, res.data[0]["password"]):
                    st.session_state.user = res.data[0]["username"]
                    st.rerun()
                else: st.error("Hatalı giriş!")
            if st.button("Kayıt Ol", use_container_width=True):
                st.session_state.auth_mode = "register"; st.rerun()
        else:
            u_r = st.text_input("Yeni Kullanıcı Adı")
            p_r = st.text_input("Yeni Şifre", type="password")
            if st.button("Hesabı Oluştur", use_container_width=True):
                supabase.table("scriber_users").insert({"username": u_r, "password": hash_password(p_r)}).execute()
                st.session_state.auth_mode = "login"; st.rerun()
    st.stop()

if "chat_id" not in st.session_state: st.session_state.chat_id = str(uuid.uuid4())
if "history" not in st.session_state: st.session_state.history = []

# --- SIDEBAR ---
with st.sidebar:
    st.image(LOGO_URL, width=100)
    st.write(f"👤 **{st.session_state.user}**")
    if st.button("➕ Yeni Sohbet", use_container_width=True):
        st.session_state.chat_id = str(uuid.uuid4()); st.session_state.history = []; st.rerun()
    st.write("---")
    try:
        chats = supabase.table("messages").select("chat_id, chat_title").eq("username", st.session_state.user).execute()
        seen = set()
        for c in chats.data:
            if c["chat_id"] not in seen and c["chat_title"]:
                seen.add(c["chat_id"])
                if st.button(f"💬 {c['chat_title']}", key=c["chat_id"], use_container_width=True):
                    msgs = supabase.table("messages").select("role,content").eq("chat_id", c["chat_id"]).order("created_at").execute()
                    st.session_state.chat_id = c["chat_id"]; st.session_state.history = msgs.data; st.rerun()
    except: pass

# --- CHAT ---
st.markdown("<h1 style='text-align:center'>SCRIBER AI</h1>", unsafe_allow_html=True)
client = OpenAI(base_url=f"{NGROK_URL}/v1", api_key="lm-studio")

for msg in st.session_state.history:
    avatar = LOGO_URL if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

if prompt := st.chat_input("Scriber'a yaz..."):
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=LOGO_URL):
        placeholder = st.empty()
        # Ses efekti için gizli placeholder
        sound_placeholder = st.empty()
        
        # SESİ BAŞLAT (Loop modunda)
        sound_placeholder.markdown(f"""
            <audio autoplay loop>
                <source src="{BEEP_SOUND_URL}" type="audio/mpeg">
            </audio>
        """, unsafe_allow_html=True)

        full_response = ""
        stream = client.chat.completions.create(
            model="llama3-turkish",
            messages=st.session_state.history,
            stream=True
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                placeholder.markdown(full_response + "▌")
        
        placeholder.markdown(full_response)
        
        # SESİ DURDUR (Placeholder'ı temizleyerek)
        sound_placeholder.empty()
        
        st.session_state.history.append({"role": "assistant", "content": full_response})

    # Kayıt
    try:
        title = prompt[:25] + "..."
        supabase.table("messages").insert([
            {"username": st.session_state.user, "role": "user", "content": prompt, "chat_id": st.session_state.chat_id, "chat_title": title},
            {"username": st.session_state.user, "role": "assistant", "content": full_response, "chat_id": st.session_state.chat_id, "chat_title": title}
        ]).execute()
    except: pass

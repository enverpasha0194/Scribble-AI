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

# BURAYA GitHub'dan aldığın RAW linkini koy. Örnek format:
# BEEP_SOUND_URL = "https://raw.githubusercontent.com/kullanici/repo/main/beep.mp3"
BEEP_SOUND_URL = "https://audio.jukehost.co.uk/mziBozmyh98u5i9TLvz7CuHKSAFv6zRN" 

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="SCRIBER AI", page_icon=LOGO_URL, layout="wide")

# ==============================
# ✨ CSS: WAVE, SIDEBAR VE BEYAZ ŞERİT FİX
# ==============================
st.markdown(f"""
<style>
    /* 1. ARKA PLAN: WAVE ANIMASYONU */
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

    /* 2. BEYAZ ŞERİDİ TAMAMEN SİL */
    [data-testid="stBottomBlockContainer"] {{
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }}
    .st-emotion-cache-1y34ygi, .e4man117, .st-emotion-cache-tn0cau, .ek2vi383, .st-emotion-cache-1vo6xi6 {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }}

    /* 3. SIDEBAR: BUTONLAR KOYU MOR (#353254), YAZILAR BEYAZ */
    section[data-testid="stSidebar"] {{
        background-color: rgba(5, 5, 20, 0.95) !important;
        border-right: 1px solid #6a11cb !important;
    }}
    div[data-testid="stSidebar"] button {{
        background-color: #353254 !important;
        color: #ffffff !important; /* Yazılar bembeyaz ve okunur */
        border: 1px solid #4b4870 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        width: 100%;
        text-align: left !important;
    }}
    div[data-testid="stSidebar"] button:hover {{
        background-color: #4b4870 !important;
        border-color: #ffffff !important;
    }}

    /* 4. GENEL DÜZENLEME */
    header, footer, #MainMenu {{visibility: hidden;}}
    h1, p, span, label, .stMarkdown {{ color: white !important; }}
    
    /* Chat Input Stil */
    div[data-testid="stChatInput"] {{
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid #6a11cb !important;
        border-radius: 15px !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- AUTH SİSTEMİ ---
def hash_password(pw): return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
def check_password(pw, hashed):
    try: return bcrypt.checkpw(pw.encode(), hashed.encode())
    except: return False

if "user" not in st.session_state:
    st.markdown("<h1 style='text-align:center'>SCRIBER AI</h1>", unsafe_allow_html=True)
    u = st.text_input("Kullanıcı adı")
    p = st.text_input("Şifre", type="password")
    if st.button("Giriş Yap", use_container_width=True):
        res = supabase.table("scriber_users").select("*").eq("username", u).execute()
        if res.data and check_password(p, res.data[0]["password"]):
            st.session_state.user = res.data[0]["username"]; st.rerun()
    st.stop()

# --- CHAT MANTIĞI ---
if "chat_id" not in st.session_state: st.session_state.chat_id = str(uuid.uuid4())
if "history" not in st.session_state: st.session_state.history = []

with st.sidebar:
    st.image(LOGO_URL, width=100)
    st.write(f"👤 **{st.session_state.user}**")
    if st.button("➕ Yeni Sohbet"):
        st.session_state.chat_id = str(uuid.uuid4()); st.session_state.history = []; st.rerun()
    st.write("---")
    try:
        chats = supabase.table("messages").select("chat_id, chat_title").eq("username", st.session_state.user).execute()
        seen = set()
        for c in chats.data:
            if c["chat_id"] not in seen and c["chat_title"]:
                seen.add(c["chat_id"])
                if st.button(f"💬 {c['chat_title']}", key=c["chat_id"]):
                    msgs = supabase.table("messages").select("role,content").eq("chat_id", c["chat_id"]).order("created_at").execute()
                    st.session_state.history = msgs.data; st.session_state.chat_id = c["chat_id"]; st.rerun()
    except: pass

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
        sound_placeholder = st.empty()
        
        # 🔊 SESİ LOOP OLARAK BAŞLAT
        sound_placeholder.markdown(f"""
            <audio autoplay loop>
                <source src="{BEEP_SOUND_URL}" type="audio/mpeg">
            </audio>
        """, unsafe_allow_html=True)

        full_response = ""
        stream = client.chat.completions.create(model="llama3-turkish", messages=st.session_state.history, stream=True)
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                placeholder.markdown(full_response + "▌")
        
        placeholder.markdown(full_response)
        
        # 🔇 SESİ DURDUR
        sound_placeholder.empty()
        
        st.session_state.history.append({"role": "assistant", "content": full_response})

    # Kayıt
    try:
        title = prompt[:20] + "..."
        supabase.table("messages").insert([
            {"username": st.session_state.user, "role": "user", "content": prompt, "chat_id": st.session_state.chat_id, "chat_title": title},
            {"username": st.session_state.user, "role": "assistant", "content": full_response, "chat_id": st.session_state.chat_id, "chat_title": title}
        ]).execute()
    except: pass

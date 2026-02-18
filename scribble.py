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
# ✨ GÖRSEL FİX: BEYAZ ŞERİT VE SIDEBAR
# ==============================
st.markdown(f"""
<style>
    /* 1. ARKA PLAN: WAVE EFEKTİ (Lacivert-Mor Karışımı Animasyon) */
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

    /* 2. ALTAKİ BEYAZ ŞERİDİ TAMAMEN SİL */
    [data-testid="stBottomBlockContainer"] {{
        display: none !important;
        height: 0 !important;
        background: transparent !important;
    }}
    footer {{visibility: hidden;}}

    /* 3. SIDEBAR BUTONLARI (Görselindeki gibi koyu renk ve beyaz yazı) */
    section[data-testid="stSidebar"] {{
        background-color: #050514 !important;
    }}
    div[data-testid="stSidebar"] .stButton button {{
        background-color: #353254 !important; /* İstediğin koyu mor renk */
        color: white !important; /* Yazılar artık görünür! */
        border: 1px solid #4b4870 !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        text-align: left !important;
        width: 100%;
    }}
    div[data-testid="stSidebar"] .stButton button:hover {{
        background-color: #4b4870 !important;
        border-color: #ffffff !important;
    }}

    /* 4. GENEL METİN RENKLERİ */
    h1, p, span, label {{ color: white !important; }}
</style>
""", unsafe_allow_html=True)

# --- AUTH VE DİĞER FONKSİYONLAR (Aynen Kalıyor) ---
def hash_password(pw): return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
def check_password(pw, hashed): 
    try: return bcrypt.checkpw(pw.encode(), hashed.encode())
    except: return False

if "user" not in st.session_state:
    st.markdown("<h1 style='text-align:center'>SCRIBER AI</h1>", unsafe_allow_html=True)
    # Basit giriş ekranı...
    u = st.text_input("Kullanıcı adı")
    p = st.text_input("Şifre", type="password")
    if st.button("Giriş Yap", use_container_width=True):
        res = supabase.table("scriber_users").select("*").eq("username", u).execute()
        if res.data and check_password(p, res.data[0]["password"]):
            st.session_state.user = res.data[0]["username"]
            st.rerun()
    st.stop()

# --- CHAT MANTIĞI ---
if "chat_id" not in st.session_state: st.session_state.chat_id = str(uuid.uuid4())
if "history" not in st.session_state: st.session_state.history = []

with st.sidebar:
    st.image(LOGO_URL, width=100)
    st.write(f"👤 **{st.session_state.user}**")
    if st.button("➕ Yeni Sohbet"):
        st.session_state.chat_id = str(uuid.uuid4())
        st.session_state.history = []
        st.rerun()
    st.write("---")
    # Geçmiş sohbetleri çek
    try:
        chats = supabase.table("messages").select("chat_id, chat_title").eq("username", st.session_state.user).execute()
        seen = set()
        for c in chats.data:
            if c["chat_id"] not in seen and c["chat_title"]:
                seen.add(c["chat_id"])
                if st.button(c["chat_title"], key=c["chat_id"]):
                    msgs = supabase.table("messages").select("role,content").eq("chat_id", c["chat_id"]).order("created_at").execute()
                    st.session_state.history = msgs.data
                    st.rerun()
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
        full_response = ""
        stream = client.chat.completions.create(model="llama3-turkish", messages=st.session_state.history, stream=True)
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                placeholder.markdown(full_response + "▌")
        placeholder.markdown(full_response)
        st.session_state.history.append({"role": "assistant", "content": full_response})

    # ==============================
    # 💾 VERİTABANINA KAYIT (HATA FİX)
    # ==============================
    try:
        title = prompt[:20] + "..."
        supabase.table("messages").insert([
            {"username": st.session_state.user, "role": "user", "content": prompt, "chat_id": st.session_state.chat_id, "chat_title": title},
            {"username": st.session_state.user, "role": "assistant", "content": full_response, "chat_id": st.session_state.chat_id, "chat_title": title}
        ]).execute()
    except Exception as e:
        # Eğer hala hata verirse en azından uygulama çökmez, hatayı küçük bir uyarı olarak basar
        st.warning(f"Sohbet kaydedilemedi, ama devam edebilirsiniz. (Hata: {e})")

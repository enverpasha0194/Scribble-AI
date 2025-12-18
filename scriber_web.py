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
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================
# 🎨 CSS (ARKAPLAN + SIDEBAR)
# ==============================
st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}
.stDeployButton {display:none;}

.stApp {
    background: linear-gradient(315deg,#091236,#1e215a,#3a1c71,#0f0c29);
}

section[data-testid="stSidebar"] {
    background-color: rgba(10,10,35,0.98);
    border-right: 2px solid #6a11cb;
    width: 300px !important;
}

[data-testid="stChatMessageContent"] p {
    color: white !important;
    font-size: 1.15rem;
    text-shadow: 1px 1px 4px rgba(0,0,0,0.9);
}

div[data-testid="stChatMessage"]:has(span:contains("user")) {
    flex-direction: row-reverse !important;
}
div[data-testid="stChatMessage"]:has(span:contains("user")) 
[data-testid="stChatMessageAvatar"] {
    display:none !important;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# 🔐 ŞİFRE
# ==============================
def hash_password(pw):
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

def check_password(pw, hashed):
    return bcrypt.checkpw(pw.encode(), hashed.encode())

# ==============================
# 🔐 AUTH
# ==============================
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

if "user_id" not in st.session_state:
    st.markdown("<h1 style='color:white;text-align:center'>SCRIBER AI</h1>", unsafe_allow_html=True)

    if st.session_state.auth_mode == "login":
        username = st.text_input("Kullanıcı adı")
        password = st.text_input("Şifre", type="password")

        if st.button("Giriş Yap"):
            res = supabase.table("scriber_users").select("*").eq("username", username).execute()
            if not res.data:
                st.error("Kullanıcı yok")
                st.stop()

            user = res.data[0]
            if not check_password(password, user["password"]):
                st.error("Şifre yanlış")
                st.stop()

            st.session_state.user_id = user["id"]
            st.session_state.user = user["username"]
            st.rerun()

        st.markdown("Hesabın yok mu?")
        if st.button("Kayıt Ol"):
            st.session_state.auth_mode = "register"
            st.rerun()

    else:
        username = st.text_input("Kullanıcı adı")
        password = st.text_input("Şifre", type="password")
        password2 = st.text_input("Şifre (tekrar)", type="password")

        if st.button("Hesap Oluştur"):
            if password != password2:
                st.error("Şifreler uyuşmuyor")
                st.stop()

            exists = supabase.table("users").select("id").eq("username", username).execute()
            if exists.data:
                st.error("Bu kullanıcı adı alınmış")
                st.stop()

            supabase.table("users").insert({
                "username": username,
                "password": hash_password(password)
            }).execute()

            st.success("Kayıt tamam, giriş yap")
            st.session_state.auth_mode = "login"
            st.rerun()

    st.stop()

# ==============================
# 🧠 SESSION
# ==============================
if "chat_id" not in st.session_state:
    st.session_state.chat_id = str(uuid.uuid4())
if "history" not in st.session_state:
    st.session_state.history = []

# ==============================
# 🧭 SIDEBAR
# ==============================
with st.sidebar:
    st.image(LOGO_URL, width=80)
    st.write(f"👤 **{st.session_state.user}**")

    if st.button("➕ Yeni Sohbet", use_container_width=True):
        st.session_state.chat_id = str(uuid.uuid4())
        st.session_state.history = []
        st.rerun()

    st.write("---")
    chats = supabase.table("messages") \
        .select("chat_id, chat_title") \
        .eq("username", st.session_state.user) \
        .execute()

    titles = {c["chat_id"]: c["chat_title"] for c in chats.data if c["chat_title"]}

    for cid, title in titles.items():
        if st.button(title, key=cid, use_container_width=True):
            st.session_state.chat_id = cid
            msgs = supabase.table("messages") \
                .select("role,content") \
                .eq("chat_id", cid) \
                .order("created_at") \
                .execute()
            st.session_state.history = msgs.data
            st.rerun()

# ==============================
# 🤖 CHAT
# ==============================
st.markdown('<h1 style="text-align:center; color:white;">SCRIBER AI</h1>', unsafe_allow_html=True)

client = OpenAI(base_url=f"{NGROK_URL}/v1", api_key="lm-studio")

for msg in st.session_state.history:
    with st.chat_message(msg["role"], avatar=LOGO_URL if msg["role"]=="assistant" else None):
        st.markdown(msg["content"])

if prompt := st.chat_input("Scriber'a yaz..."):
    sys_msg = f"Senin adın Scriber. Karşındaki kişi {st.session_state.user}. Samimi konuş."

    st.session_state.history.append({"role":"user","content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=LOGO_URL):
        placeholder = st.empty()
        full = ""
        res = client.chat.completions.create(
            model="llama3-turkish",
            messages=[{"role":"system","content":sys_msg}] + st.session_state.history,
            stream=True
        )
        for c in res:
            if c.choices[0].delta.content:
                full += c.choices[0].delta.content
                placeholder.markdown(full+"▌")
        placeholder.markdown(full)
        st.session_state.history.append({"role":"assistant","content":full})

    title = prompt[:20] + "..."
    supabase.table("messages").insert([
        {"username":st.session_state.user,"role":"user","content":prompt,"chat_id":st.session_state.chat_id,"chat_title":title},
        {"username":st.session_state.user,"role":"assistant","content":full,"chat_id":st.session_state.chat_id,"chat_title":title}
    ]).execute()




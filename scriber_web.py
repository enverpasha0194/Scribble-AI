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
# 🎨 CSS
# ==============================
st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}
.stDeployButton {display:none;}
.stApp {
    background: linear-gradient(315deg,#091236,#1e215a,#3a1c71,#0f0c29);
}
[data-testid="stSidebar"] {
    background-color: rgba(5,5,20,0.98);
    border-right: 2px solid #6a11cb;
}
[data-testid="stChatMessageContent"] p {
    color:white;
    font-size:1.1rem;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# 🔐 ŞİFRE FONKSİYONLARI
# ==============================
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

# ==============================
# 🔐 GİRİŞ / KAYIT (ŞİFRELİ)
# ==============================
if "user_id" not in st.session_state:
    st.markdown("<h1 style='color:white;text-align:center'>SCRIBER AI</h1>", unsafe_allow_html=True)

    username = st.text_input("Kullanıcı adı")
    password = st.text_input("Şifre", type="password")

    if st.button("Giriş / Kayıt"):
        if not username or not password:
            st.warning("Kullanıcı adı ve şifre zorunlu")
            st.stop()

        res = supabase.table("users").select("*").eq("username", username).execute()

        if res.data:
            user = res.data[0]
            if not check_password(password, user["password_hash"]):
                st.error("Şifre yanlış")
                st.stop()

            st.session_state.user_id = user["id"]
            st.session_state.user = username

        else:
            hashed = hash_password(password)
            new_user = supabase.table("users").insert({
                "username": username,
                "password_hash": hashed
            }).execute()

            st.session_state.user_id = new_user.data[0]["id"]
            st.session_state.user = username

        st.rerun()

    st.stop()

# ==============================
# 🧠 SESSION STATE
# ==============================
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ==============================
# 🧭 SIDEBAR
# ==============================
with st.sidebar:
    st.image(LOGO_URL, width=80)
    st.markdown(f"### 👤 {st.session_state.user}")

    if st.button("➕ Yeni Sohbet", use_container_width=True):
        chat_id = str(uuid.uuid4())
        supabase.table("chats").insert({
            "id": chat_id,
            "user_id": st.session_state.user_id,
            "title": "Yeni Sohbet"
        }).execute()

        st.session_state.current_chat_id = chat_id
        st.session_state.chat_history = []
        st.rerun()

    st.write("---")
    st.subheader("💬 Geçmiş Sohbetler")

    chats = supabase.table("chats") \
        .select("*") \
        .eq("user_id", st.session_state.user_id) \
        .order("created_at", desc=True) \
        .execute()

    for chat in chats.data:
        if st.button(chat["title"], key=chat["id"], use_container_width=True):
            st.session_state.current_chat_id = chat["id"]

            msgs = supabase.table("messages") \
                .select("role,content") \
                .eq("chat_id", chat["id"]) \
                .order("created_at") \
                .execute()

            st.session_state.chat_history = msgs.data
            st.rerun()

# ==============================
# 🤖 CHAT
# ==============================
st.markdown("<h1 style='color:white;text-align:center'>SCRIBER AI</h1>", unsafe_allow_html=True)

client = OpenAI(
    base_url=f"{NGROK_URL}/v1",
    api_key="lm-studio"
)

for msg in st.session_state.chat_history:
    avatar = LOGO_URL if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ==============================
# 📝 MESAJ & BAŞLIK
# ==============================
def generate_title(text):
    r = client.chat.completions.create(
        model="llama3-turkish",
        messages=[
            {"role": "system", "content": "Bu konuşmaya kısa bir başlık üret."},
            {"role": "user", "content": text}
        ]
    )
    return r.choices[0].message.content[:40]

if prompt := st.chat_input("Scriber'a mesaj gönder..."):
    if not st.session_state.current_chat_id:
        st.warning("Önce yeni sohbet başlat")
        st.stop()

    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=LOGO_URL):
        placeholder = st.empty()
        full_response = ""

        sys_msg = f"Senin adın Scriber. Kullanıcının adı {st.session_state.user}."

        response = client.chat.completions.create(
            model="llama3-turkish",
            messages=[{"role": "system", "content": sys_msg}] + st.session_state.chat_history,
            stream=True
        )

        for chunk in response:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                placeholder.markdown(full_response + "▌")

        placeholder.markdown(full_response)
        st.session_state.chat_history.append(
            {"role": "assistant", "content": full_response}
        )

    supabase.table("messages").insert([
        {
            "chat_id": st.session_state.current_chat_id,
            "role": "user",
            "content": prompt
        },
        {
            "chat_id": st.session_state.current_chat_id,
            "role": "assistant",
            "content": full_response
        }
    ]).execute()

    if len(st.session_state.chat_history) == 2:
        title = generate_title(prompt)
        supabase.table("chats") \
            .update({"title": title}) \
            .eq("id", st.session_state.current_chat_id) \
            .execute()


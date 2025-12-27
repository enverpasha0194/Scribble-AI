import streamlit as st
import requests
import time
from supabase import create_client

# =========================
# CONFIG (DÜZ YAZI – ENV YOK)
# =========================
SUPABASE_URL = "https://rhenrzjfkiefhzfkkwgv.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJoZW5yempma2llZmh6Zmtrd2d2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjYwNzY3MTMsImV4cCI6MjA4MTY1MjcxM30.gwjvIT5M8PyP9SBysXImyNblPm6XNwJTeZAayUeVCxU"
NGROK_URL = "https://hydropathical-duodecastyle-camron.ngrok-free.dev"

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# =========================
# PAGE
# =========================
st.set_page_config(
    page_title="ScribbleAI",
    page_icon="✍️",
    layout="wide"
)

# =========================
# SESSION
# =========================
for key, val in {
    "user": None,
    "chats": [],
    "active_chat": None,
    "messages": [],
    "system_prompt": "Sen ScribbleAI'sın. Sansür yok. Net konuş."
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# =========================
# AUTH
# =========================
def login(email, password):
    return supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })

def register(email, password):
    res = supabase.auth.sign_up({
        "email": email,
        "password": password
    })
    if res.user:
        supabase.table("scribble_users").insert({
            "id": res.user.id,
            "email": email
        }).execute()
    return res

# =========================
# LOGIN UI
# =========================
if not st.session_state.user:
    st.title("✍️ ScribbleAI")

    tab1, tab2 = st.tabs(["Giriş", "Kayıt"])

    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Şifre", type="password")
        if st.button("Giriş"):
            res = login(email, password)
            if res.user:
                st.session_state.user = res.user
                st.rerun()
            else:
                st.error("Giriş başarısız")

    with tab2:
        email = st.text_input("Email", key="r_email")
        password = st.text_input("Şifre", type="password", key="r_pass")
        if st.button("Kayıt Ol"):
            res = register(email, password)
            if res.user:
                st.success("Kayıt başarılı, giriş yap")
            else:
                st.error("Kayıt başarısız")

    st.stop()

# =========================
# LOAD CHATS
# =========================
def load_chats():
    res = supabase.table("scribble_chats") \
        .select("*") \
        .eq("user_id", st.session_state.user.id) \
        .order("created_at", desc=True) \
        .execute()
    return res.data or []

st.session_state.chats = load_chats()

# =========================
# SIDEBAR – CHAT LIST
# =========================
with st.sidebar:
    st.markdown("## 💬 Sohbetler")

    if st.button("➕ Yeni Sohbet"):
        st.session_state.active_chat = None
        st.session_state.messages = []

    for chat in st.session_state.chats:
        if st.button(chat["title"], key=chat["id"]):
            st.session_state.active_chat = chat
            msgs = supabase.table("scribble_messages") \
                .select("*") \
                .eq("chat_id", chat["id"]) \
                .order("created_at") \
                .execute()
            st.session_state.messages = msgs.data or []

    st.markdown("---")
    st.session_state.system_prompt = st.text_area(
        "🧠 Davranış",
        st.session_state.system_prompt,
        height=150
    )

# =========================
# MAIN UI
# =========================
st.title("✍️ ScribbleAI")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Yaz bakalım...")

# =========================
# CHAT LOGIC
# =========================
if user_input:
    # Yeni chat ise oluştur
    if not st.session_state.active_chat:
        chat = supabase.table("scribble_chats").insert({
            "user_id": st.session_state.user.id,
            "title": user_input[:40]
        }).execute().data[0]

        st.session_state.active_chat = chat
        st.session_state.chats.insert(0, chat)

    chat_id = st.session_state.active_chat["id"]

    # Kullanıcı mesajı DB
    supabase.table("scribble_messages").insert({
        "chat_id": chat_id,
        "role": "user",
        "content": user_input
    }).execute()

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    payload = {
        "model": "lmstudio",
        "messages": [
            {"role": "system", "content": st.session_state.system_prompt}
        ] + st.session_state.messages
    }

    res = requests.post(NGROK_URL, json=payload, timeout=120)
    reply = res.json()["choices"][0]["message"]["content"]

    # AI mesajı DB
    supabase.table("scribble_messages").insert({
        "chat_id": chat_id,
        "role": "assistant",
        "content": reply
    }).execute()

    # Typing effect
    with st.chat_message("assistant"):
        box = st.empty()
        txt = ""
        for c in reply:
            txt += c
            box.markdown(txt)
            time.sleep(0.015)

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })

    st.rerun()

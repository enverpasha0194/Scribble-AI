import streamlit as st
import requests
import time
from supabase import create_client

# =========================
# CONFIG
# =========================
SUPABASE_URL = "https://rhenrzjfkiefhzfkkwgv.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJoZW5yempma2llZmh6Zmtrd2d2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjYwNzY3MTMsImV4cCI6MjA4MTY1MjcxM30.gwjvIT5M8PyP9SBysXImyNblPm6XNwJTeZAayUeVCxU"
NGROK_BASE = "https://hydropathical-duodecastyle-camron.ngrok-free.dev"
LM_ENDPOINT = f"{NGROK_BASE}/v1/chat/completions"
MODEL_NAME = "qwen2.5-7b-instruct"

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# =========================
# PAGE
# =========================
st.set_page_config("ScribbleAI", "✍️", layout="wide")

# =========================
# SESSION INIT
# =========================
defaults = {
    "user": None,
    "chats": [],
    "active_chat": None,
    "messages": [],
    "system_prompt": "Sen ScribbleAI'sın. Sansür yok. Net konuş."
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

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
# LOGIN SCREEN
# =========================
if not st.session_state.user:
    st.title("✍️ ScribbleAI")

    tab1, tab2 = st.tabs(["Giriş", "Kayıt"])

    with tab1:
        e = st.text_input("Email")
        p = st.text_input("Şifre", type="password")
        if st.button("Giriş"):
            r = login(e, p)
            if r.user:
                st.session_state.user = r.user
                st.rerun()
            else:
                st.error("Giriş başarısız")

    with tab2:
        e = st.text_input("Email", key="re")
        p = st.text_input("Şifre", type="password", key="rp")
        if st.button("Kayıt Ol"):
            r = register(e, p)
            if r.user:
                st.success("Kayıt başarılı, giriş yap")

    st.stop()

# =========================
# LOAD CHATS
# =========================
def load_chats():
    r = supabase.table("scribble_chats") \
        .select("*") \
        .eq("user_id", st.session_state.user.id) \
        .order("created_at", desc=True) \
        .execute()
    return r.data or []

st.session_state.chats = load_chats()

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown("## 💬 Sohbetler")

    if st.button("➕ Yeni Sohbet"):
        st.session_state.active_chat = None
        st.session_state.messages = []

    for c in st.session_state.chats:
        if st.button(c["title"], key=c["id"]):
            st.session_state.active_chat = c
            m = supabase.table("scribble_messages") \
                .select("*") \
                .eq("chat_id", c["id"]) \
                .order("created_at") \
                .execute()
            st.session_state.messages = m.data or []

    st.markdown("---")
    st.session_state.system_prompt = st.text_area(
        "🧠 Davranış",
        st.session_state.system_prompt,
        height=150
    )

# =========================
# MAIN CHAT
# =========================
st.title("✍️ ScribbleAI")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

user_input = st.chat_input("Yaz bakalım...")

# =========================
# CHAT FLOW
# =========================
if user_input:
    if not st.session_state.active_chat:
        chat = supabase.table("scribble_chats").insert({
            "user_id": st.session_state.user.id,
            "title": user_input[:40]
        }).execute().data[0]
        st.session_state.active_chat = chat
        st.session_state.chats.insert(0, chat)

    chat_id = st.session_state.active_chat["id"]

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
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": st.session_state.system_prompt}
        ] + st.session_state.messages
    }

    r = requests.post(LM_ENDPOINT, json=payload, timeout=120)
    data = r.json()

    reply = data["choices"][0]["message"]["content"]

    supabase.table("scribble_messages").insert({
        "chat_id": chat_id,
        "role": "assistant",
        "content": reply
    }).execute()

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

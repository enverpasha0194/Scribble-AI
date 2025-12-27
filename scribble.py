import streamlit as st
import requests
import time
import uuid
import urllib.parse
from supabase import create_client

# =========================
# CONFIG
# =========================
SUPABASE_URL = "https://rhenrzjfkiefhzfkkwgv.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJoZW5yempma2llZmh6Zmtrd2d2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjYwNzY3MTMsImV4cCI6MjA4MTY1MjcxM30.gwjvIT5M8PyP9SBysXImyNblPm6XNwJTeZAayUeVCxU"
NGROK_BASE = "https://hydropathical-duodecastyle-camron.ngrok-free.dev"
LM_ENDPOINT = f"{NGROK_BASE}/v1/chat/completions"
MODEL_NAME = "qwen2.5-7b-instruct"

SYSTEM_PROMPT = """
senin adın 'scribble ai'
konuşma tarzın arkadaşça samimi ve empatik olacak.
noktalama işaretleri kullanma, küçük/büyük harf takılma.
kullanıcı nasıl konuşursa onun tarzına adapte ol.
"""

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
st.set_page_config("scribble AI", "✍️", layout="wide")

# =========================
# SESSION
# =========================
if "user" not in st.session_state:
    st.session_state.user = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "active_chat" not in st.session_state:
    st.session_state.active_chat = None

# =========================
# AUTH FUNCTIONS
# =========================
def login(username, password):
    r = supabase.table("scribble_users").select("*").eq("username", username).eq("password", password).execute()
    return r.data[0] if r.data else None

def register(username, password):
    exists = supabase.table("scribble_users").select("id").eq("username", username).execute()
    if exists.data: return None
    user = {"id": str(uuid.uuid4()), "username": username, "password": password}
    supabase.table("scribble_users").insert(user).execute()
    return user

# =========================
# LOGIN UI
# =========================
if not st.session_state.user:
    st.title("✍️ scribble AI")
    tab1, tab2 = st.tabs(["Giriş", "Kayıt"])
    with tab1:
        u = st.text_input("Kullanıcı adı")
        p = st.text_input("Şifre", type="password")
        if st.button("Giriş"):
            user = login(u, p)
            if user:
                st.session_state.user = user
                st.rerun()
            else: st.error("Hatalı giriş")
    with tab2:
        u = st.text_input("Kullanıcı adı", key="ru")
        p = st.text_input("Şifre", type="password", key="rp")
        if st.button("Kayıt Ol"):
            user = register(u, p)
            if user: st.success("Kayıt tamam")
            else: st.error("Bu kullanıcı adı dolu")
    st.stop()

# =========================
# LOAD CHATS
# =========================
def load_chats():
    r = supabase.table("scribble_chats").select("*").eq("user_id", st.session_state.user["id"]).order("created_at", desc=True).execute()
    return r.data or []

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown("## 💬 Sohbetler")
    if st.button("➕ Yeni Sohbet"):
        st.session_state.active_chat = None
        st.session_state.messages = []
    for c in load_chats():
        if st.button(c["title"], key=c["id"]):
            st.session_state.active_chat = c
            m = supabase.table("scribble_messages").select("*").eq("chat_id", c["id"]).order("created_at").execute()
            st.session_state.messages = m.data or []

# =========================
# CHAT UI
# =========================
st.title("✍️ scribble AI")

# Geçmiş mesajları gösterirken imaj linklerini render et
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

user_input = st.chat_input("Yaz bakalım...")

if user_input:
    # 1. Kullanıcı mesajını ekrana bas ve listeye ekle
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 2. Chat ID oluştur/al
    if not st.session_state.active_chat:
        chat = supabase.table("scribble_chats").insert({
            "id": str(uuid.uuid4()), "user_id": st.session_state.user["id"], "title": user_input[:40]
        }).execute().data[0]
        st.session_state.active_chat = chat
    chat_id = st.session_state.active_chat["id"]

    # 3. Kullanıcı mesajını veri tabanına kaydet
    supabase.table("scribble_messages").insert({
        "id": str(uuid.uuid4()), "chat_id": chat_id, "role": "user", "content": user_input
    }).execute()

    # 4. GÖRSEL Mİ NORMAL MESAJ MI?
    if user_input.strip().startswith("/image"):
        prompt = user_input.replace("/image", "").strip()
        if not prompt: prompt = "random art"
        
        with st.chat_message("assistant"):
            with st.spinner("çiziyorum..."):
                # Pollinations AI - Sınırsız ve Ücretsiz
                seed = uuid.uuid4().int % 1000
                encoded_prompt = urllib.parse.quote(prompt)
                image_url = f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&seed={seed}&nologo=true"
                
                # Yanıtı oluştur
                reply = f"istediğin görsel hazır:\n\n![Scribble]({image_url})"
                st.image(image_url, caption=prompt) # Direkt resmi göster
                st.markdown(reply) # Markdown olarak da linki bırak
    
    else:
        # Normal chat akışı
        payload = {
            "model": MODEL_NAME,
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages
        }
        try:
            r = requests.post(LM_ENDPOINT, json=payload, timeout=120)
            reply = r.json()["choices"][0]["message"]["content"]
            with st.chat_message("assistant"):
                box = st.empty()
                txt = ""
                for c in reply:
                    txt += c
                    box.markdown(txt)
                    time.sleep(0.01)
        except:
            reply = "sunucuya bağlanamadım :("
            st.error(reply)

    # 5. Asistan yanıtını kaydet
    supabase.table("scribble_messages").insert({
        "id": str(uuid.uuid4()), "chat_id": chat_id, "role": "assistant", "content": reply
    }).execute()
    st.session_state.messages.append({"role": "assistant", "content": reply})

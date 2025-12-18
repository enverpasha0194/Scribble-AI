import streamlit as st
from openai import OpenAI
from supabase import create_client, Client
import uuid

# ==============================
# 🔑 VERDİĞİN ANAHTARLARLA AYARLAR
# ==============================
SUPABASE_URL = "https://rhenrzjfkiefhzfkkwgv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJoZW5yempma2llZmh6Zmtrd2d2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjYwNzY3MTMsImV4cCI6MjA4MTY1MjcxM30.gwjvIT5M8PyP9SBysXImyNblPm6XNwJTeZAayUeVCxU"
NGROK_URL = "https://hydropathical-duodecastyle-camron.ngrok-free.dev"
LOGO_URL = "https://i.ibb.co/CD44FDc/Chat-GPT-mage-17-Ara-2025-23-59-13.png"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Sidebar'ı her zaman açık tutan ayar
st.set_page_config(page_title="SCRIBER AI", page_icon=LOGO_URL, layout="wide", initial_sidebar_state="expanded")

# ==============================
# CSS: SIDEBAR ZORLAMA VE BEYAZ ŞERİT İMHASI
# ==============================
st.markdown(f"""
<style>
    /* 1. SIDEBAR'I GÖRÜNÜR YAP */
    section[data-testid="stSidebar"] {{
        background-color: rgba(10, 10, 35, 0.98) !important;
        border-right: 2px solid #6a11cb !important;
        display: block !important;
        visibility: visible !important;
        width: 300px !important;
    }}

    /* 2. BEYAZ ŞERİT VE ALT KISIM TEMİZLİĞİ */
    [data-testid="stBottomBlockContainer"], 
    .st-emotion-cache-1y34ygi, 
    .st-emotion-cache-6shykm {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }}

    /* 3. YAZI GÖRÜNÜRLÜĞÜ */
    [data-testid="stChatMessageContent"] p {{
        color: #ffffff !important;
        font-size: 1.15rem !important;
        text-shadow: 1px 1px 4px rgba(0,0,0,0.9);
    }}

    /* 4. KULLANICI MESAJI DÜZENİ */
    div[data-testid="stChatMessage"]:has(span:contains("user")) {{
        flex-direction: row-reverse !important;
    }}
    div[data-testid="stChatMessage"]:has(span:contains("user")) [data-testid="stChatMessageAvatar"] {{
        display: none !important;
    }}
</style>
""", unsafe_allow_html=True)

# ==============================
# KAYIT VE GİRİŞ SİSTEMİ (DATABASE BAĞLI)
# ==============================
if "logged_in_user" not in st.session_state:
    tab1, tab2 = st.tabs(["Giriş Yap", "Kayıt Ol"])
    
    with tab1:
        with st.form("login_form"):
            u_in = st.text_input("Kullanıcı Adı")
            p_in = st.text_input("Şifre", type="password")
            if st.form_submit_button("Giriş"):
                res = supabase.table("scriber_users").select("*").eq("username", u_in).eq("password", p_in).execute()
                if res.data:
                    st.session_state.logged_in_user = u_in
                    st.rerun()
                else:
                    st.error("Hatalı kullanıcı adı veya şifre!")

    with tab2:
        with st.form("register_form"):
            u_reg = st.text_input("Yeni Kullanıcı Adı")
            p_reg = st.text_input("Yeni Şifre", type="password")
            if st.form_submit_button("Kayıt Ol"):
                try:
                    supabase.table("scriber_users").insert({"username": u_reg, "password": p_reg}).execute()
                    st.success("Kayıt başarılı! Giriş sekmesine dönebilirsin.")
                except:
                    st.error("Bu kullanıcı adı zaten alınmış!")
    st.stop()

# ==============================
# OTURUM DEĞİŞKENLERİ
# ==============================
if "chat_id" not in st.session_state: st.session_state.chat_id = str(uuid.uuid4())
if "history" not in st.session_state: st.session_state.history = []

# ==============================
# SIDEBAR (SOHBET GEÇMİŞİ)
# ==============================
with st.sidebar:
    st.image(LOGO_URL, width=80)
    st.title("Sohbetler")
    st.write(f"👤 **{st.session_state.logged_in_user}**")
    
    if st.button("➕ Yeni Sohbet", use_container_width=True):
        st.session_state.chat_id = str(uuid.uuid4())
        st.session_state.history = []
        st.rerun()
    
    st.write("---")
    # Kullanıcıya ait eski sohbetleri çekiyoruz
    old_chats = supabase.table("messages").select("chat_id, chat_title").eq("username", st.session_state.logged_in_user).execute()
    titles = {c['chat_id']: c['chat_title'] for c in old_chats.data if c['chat_title']}
    
    for cid, title in titles.items():
        if st.button(title, key=cid, use_container_width=True):
            st.session_state.chat_id = cid
            msgs = supabase.table("messages").select("*").eq("chat_id", cid).order("created_at").execute()
            st.session_state.history = [{"role": m['role'], "content": m['content']} for m in msgs.data]
            st.rerun()

# ==============================
# ANA CHAT
# ==============================
st.markdown('<h1 style="text-align:center; color:white;">SCRIBER AI</h1>', unsafe_allow_html=True)

client = OpenAI(base_url=f"{NGROK_URL}/v1", api_key="lm-studio")

for msg in st.session_state.history:
    with st.chat_message(msg["role"], avatar=LOGO_URL if msg["role"]=="assistant" else None):
        st.markdown(msg["content"])

if prompt := st.chat_input("Scriber'a yaz..."):
    # Yapay zeka senin kim olduğunu bilsin
    sys_prompt = f"Senin adın Scriber. Karşındaki kişi {st.session_state.logged_in_user}. Ona ismiyle hitap et ve samimi ol."
    
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=LOGO_URL):
        placeholder = st.empty()
        full_res = ""
        response = client.chat.completions.create(
            model="llama3-turkish",
            messages=[{"role": "system", "content": sys_prompt}] + st.session_state.history,
            stream=True
        )
        for chunk in response:
            if chunk.choices[0].delta.content:
                full_res += chunk.choices[0].delta.content
                placeholder.markdown(full_res + "▌")
        placeholder.markdown(full_res)
        st.session_state.history.append({"role": "assistant", "content": full_res})

        # DB KAYIT
        title = prompt[:20] + "..."
        supabase.table("messages").insert([
            {"username": st.session_state.logged_in_user, "role": "user", "content": prompt, "chat_id": st.session_state.chat_id, "chat_title": title},
            {"username": st.session_state.logged_in_user, "role": "assistant", "content": full_res, "chat_id": st.session_state.chat_id, "chat_title": title}
        ]).execute()

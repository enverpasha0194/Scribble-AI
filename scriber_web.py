import streamlit as st
from openai import OpenAI
from supabase import create_client, Client

# ==============================
# 🔑 AYARLAR (Kendi bilgilerinle doldur)
# ==============================
SUPABASE_URL = "https://rhenrzjfkiefhzfkkwgv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJoZW5yempma2llZmh6Zmtrd2d2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjYwNzY3MTMsImV4cCI6MjA4MTY1MjcxM30.gwjvIT5M8PyP9SBysXImyNblPm6XNwJTeZAayUeVCxU"
NGROK_URL = "https://hydropathical-duodecastyle-camron.ngrok-free.dev"
LOGO_URL = "https://i.ibb.co/CD44FDc/Chat-GPT-mage-17-Ara-2025-23-59-13.png"

# Supabase Bağlantısı
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="SCRIBER AI", page_icon=LOGO_URL, layout="wide")

# ==============================
# CSS: TASARIM
# ==============================
st.markdown(f"""
<style>
    #MainMenu, footer, header {{visibility: hidden;}}
    .stApp {{ background: linear-gradient(315deg, #091236 0%, #1e215a 35%, #3a1c71 70%, #0f0c29 100%); }}
    [data-testid="stSidebar"] {{ background-color: rgba(10, 10, 30, 0.9) !important; border-right: 1px solid #6a11cb; }}
    [data-testid="stChatMessageContent"] p {{ color: #f0f0f0 !important; }}
</style>
""", unsafe_allow_html=True)

# ==============================
# GOOGLE LOGIN TAKLİDİ VE SESSION
# ==============================
# Gerçek Google Login için Google Cloud'dan Client ID alman lazım. 
# Şimdilik sistemin çalışması için bir "Giriş" alanı yapalım.
if "user_email" not in st.session_state:
    st.markdown('<h1 style="text-align:center; color:white;">SCRIBER AI - GİRİŞ</h1>', unsafe_allow_html=True)
    email = st.text_input("Google E-posta Adresinizle Giriş Yapın:")
    if st.button("Google ile Devam Et"):
        st.session_state.user_email = email
        st.rerun()
    st.stop() # Giriş yapmadan aşağıyı gösterme

# Sohbet Geçmişini Hafızada Tut
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ==============================
# SIDEBAR
# ==============================
with st.sidebar:
    st.image(LOGO_URL, width=60)
    st.write(f"Hoş geldin, **{st.session_state.user_email}**")
    if st.button("➕ Yeni Sohbet"):
        st.session_state.chat_history = []
        st.rerun()
    
    st.write("---")
    st.subheader("Eski Sohbetlerin")
    # Burada Supabase'den o kullanıcıya ait eski başlıkları çekebiliriz.

# ==============================
# CHAT EKRANI
# ==============================
st.markdown('<h1 style="text-align:center; color:white;">SCRIBER AI</h1>', unsafe_allow_html=True)

client = OpenAI(
    base_url=f"{NGROK_URL}/v1", 
    api_key="lm-studio",
    default_headers={"ngrok-skip-browser-warning": "true"}
)

# Mesajları Göster
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"], avatar=LOGO_URL if msg["role"]=="assistant" else None):
        st.markdown(msg["content"])

# Giriş ve Kayıt
if prompt := st.chat_input("Mesajını yaz..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=LOGO_URL):
        placeholder = st.empty()
        full_response = ""
        try:
            response = client.chat.completions.create(
                model="llama3-turkish",
                messages=st.session_state.chat_history,
                stream=True
            )
            for chunk in response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    placeholder.markdown(full_response + "▌")
            
            placeholder.markdown(full_response)
            st.session_state.chat_history.append({"role": "assistant", "content": full_response})
            
            # SUPABASE KAYIT (session_id hatası burada giderildi)
            supabase.table("messages").insert({
                "user_email": st.session_state.user_email,
                "role": "user",
                "content": prompt,
                "chat_title": prompt[:20] # İlk 20 harf başlık olsun
            }).execute()

        except Exception as e:
            st.error(f"Hata: {e}")

import streamlit as st
from openai import OpenAI
from supabase import create_client, Client

# ==============================
# 🔑 AYARLAR
# ==============================
SUPABASE_URL = "https://rhenrzjfkiefhzfkkwgv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJoZW5yempma2llZmh6Zmtrd2d2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjYwNzY3MTMsImV4cCI6MjA4MTY1MjcxM30.gwjvIT5M8PyP9SBysXImyNblPm6XNwJTeZAayUeVCxU" 
NGROK_URL = "https://hydropathical-duodecastyle-camron.ngrok-free.dev"
LOGO_URL = "https://i.ibb.co/CD44FDc/Chat-GPT-mage-17-Ara-2025-23-59-13.png"

# Supabase Bağlantısı
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="SCRIBER AI", page_icon=LOGO_URL, layout="wide")

# ==============================
# CSS: BEYAZ ŞERİT VE MODERN TASARIM
# ==============================
st.markdown(f"""
<style>
    #MainMenu, footer, header {{visibility: hidden;}}
    .stDeployButton {{display:none;}}
    .stApp {{ background: linear-gradient(315deg, #091236 0%, #1e215a 35%, #3a1c71 70%, #0f0c29 100%); }}
    
    /* Beyaz Şeridi Kökten Silme */
    [data-testid="stBottomBlockContainer"], .st-emotion-cache-1y34ygi, .st-emotion-cache-128upt6 {{
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }}

    /* Kullanıcı Mesajı Sağa ve İkonsuz */
    div[data-testid="stChatMessage"]:has(span:contains("user")) {{
        flex-direction: row-reverse !important;
        background-color: transparent !important;
    }}
    div[data-testid="stChatMessage"]:has(span:contains("user")) [data-testid="stChatMessageAvatar"] {{
        display: none !important;
    }}
    div[data-testid="stChatMessage"]:has(span:contains("user")) [data-testid="stChatMessageContent"] {{
        background-color: rgba(106, 17, 203, 0.4) !important;
        border-radius: 20px 0px 20px 20px !important;
        text-align: right !important;
        margin-left: auto !important;
    }}
</style>
""", unsafe_allow_html=True)

# ==============================
# GİRİŞ KONTROLÜ (Boş Geçilemez)
# ==============================
if "user_email" not in st.session_state:
    st.markdown('<h1 style="text-align:center; color:white;">SCRIBER AI</h1>', unsafe_allow_html=True)
    with st.container():
        email_input = st.text_input("Google E-postanızı Girin:", placeholder="orn: yusufalp@gmail.com")
        if st.button("Google ile Giriş Yap"):
            if email_input and "@" in email_input:
                st.session_state.user_email = email_input
                st.rerun()
            else:
                st.error("Lütfen geçerli bir e-posta adresi gir kanka, boş bırakma!")
    st.stop()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ==============================
# SIDEBAR
# ==============================
with st.sidebar:
    st.image(LOGO_URL, width=60)
    st.write(f"✅ Giriş yapıldı: **{st.session_state.user_email}**")
    if st.button("➕ Yeni Sohbet", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# ==============================
# ANA CHAT
# ==============================
st.markdown('<h1 style="text-align:center; color:white;">SCRIBER AI</h1>', unsafe_allow_html=True)

client = OpenAI(base_url=f"{NGROK_URL}/v1", api_key="lm-studio")

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"], avatar=LOGO_URL if msg["role"]=="assistant" else None):
        st.markdown(msg["content"])

if prompt := st.chat_input("Scriber'a yaz..."):
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
            
            # --- SUPABASE KAYIT (Hata Yönetimiyle) ---
            try:
                supabase.table("messages").insert({
                    "user_email": st.session_state.user_email,
                    "role": "user",
                    "content": prompt,
                    "chat_title": prompt[:15] + "..."
                }).execute()
            except Exception as e:
                # Eğer hala tablo hatası verirse, kullanıcıyı rahatsız etmeden arka planda logla
                print(f"Veritabanı kayıt hatası: {e}")

        except Exception as e:
            st.error(f"Hata: {e}")

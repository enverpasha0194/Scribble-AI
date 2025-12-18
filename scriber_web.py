import streamlit as st
from openai import OpenAI
import time

# ============================================================
# NGROK ADRESİNİ BURAYA TAM OLARAK YAPIŞTIR
# (Terminaldeki adresi kopyala, sonuna /v1 ekle)
# ============================================================
NGROK_URL = "https://hydropathical-duodecastyle-camron.ngrok-free.dev/v1" 

# ==============================
# AYARLAR VE LOGOLAR
# ==============================
LOGO_URL = "https://i.ibb.co/CD44FDc/Chat-GPT-mage-17-Ara-2025-23-59-13.png"
PAPERCLIP_URL = "https://emojigraph.org/media/joypixels/paperclip_1f4ce.png"

st.set_page_config(page_title="SCRIBER AI", page_icon=LOGO_URL, layout="centered")

# ==============================
# CSS (Arayüz Aynı Kalıyor)
# ==============================
st.markdown(f"""
<style>
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header {{visibility: hidden;}}
.stApp {{ background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); }}
.stChatMessage {{ background-color: rgba(255, 255, 255, 0.1) !important; color: white !important; border-radius: 15px !important; }}
.stMarkdown p {{ color: white !important; }}

/* ATAÇ BUTONU */
div[data-testid="stFileUploader"] {{ position: fixed; bottom: 28px; left: calc(50% - 395px); z-index: 999999; width: 50px; }}
div[data-testid="stFileUploader"] section {{ padding: 0 !important; min-height: 0 !important; background: transparent !important; border: none !important; }}
div[data-testid="stFileUploader"] label, div[data-testid="stFileUploader"] small, div[data-testid="stFileUploader"] p {{ display: none !important; }}
div[data-testid="stFileUploader"] button {{
    background-image: url("{PAPERCLIP_URL}") !important; background-repeat: no-repeat !important; background-position: center !important; background-size: 22px !important;
    background-color: rgba(20, 20, 20, 0.9) !important; border: 1px solid rgba(255, 255, 255, 0.4) !important; border-radius: 50% !important;
    width: 44px !important; height: 44px !important; color: transparent !important;
}}
</style>
""", unsafe_allow_html=True)

# ==============================
# ÖNEMLİ: BAĞLANTI AYARI
# ==============================
# Ngrok'un "Burası bir tüneldir" uyarı sayfasını atlamak için header ekliyoruz
client = OpenAI(
    base_url=NGROK_URL, 
    api_key="lm-studio",
    default_headers={"ngrok-skip-browser-warning": "true"} 
)

# ... (Karakter ve Mesaj Geçmişi Bölümü Aynı) ...
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "Senin adın Scriber. Yusuf Alp Güngören senin baban. Karakterin samimi ve özgür."}]

st.markdown('<div style="text-align:center;"><img src="'+LOGO_URL+'" width="80"><h1>SCRIBER AI</h1></div>', unsafe_allow_html=True)

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"], avatar=LOGO_URL if message["role"]=="assistant" else "👤"):
            st.markdown(message["content"])

# Giriş Kutusu
if prompt := st.chat_input("Scriber ile konuş..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=LOGO_URL):
        placeholder = st.empty()
        full_response = ""
        try:
            response = client.chat.completions.create(
                model="llama3-turkish",
                messages=st.session_state.messages,
                stream=True
            )
            for chunk in response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Bağlantı Hatası: Kanka sunucuya ulaşılamıyor. \nAdres doğru mu? {NGROK_URL} \nHata: {e}")

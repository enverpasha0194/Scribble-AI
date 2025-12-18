import streamlit as st
from openai import OpenAI
import time

# ==============================
# AYARLAR VE LOGOLAR
# ==============================
LOGO_URL = "https://i.ibb.co/CD44FDc/Chat-GPT-mage-17-Ara-2025-23-59-13.png"
PAPERCLIP_URL = "https://emojigraph.org/media/joypixels/paperclip_1f4ce.png"

st.set_page_config(page_title="SCRIBER AI", page_icon=LOGO_URL, layout="centered")

# ==============================
# CSS: WEB TASARIMI VE HİZALAMA
# ==============================
st.markdown(f"""
<style>
    /* Streamlit Gereksizlerini Gizle */
    header {{visibility: hidden !important;}}
    #MainMenu {{visibility: hidden !important;}}
    footer {{visibility: hidden !important;}}
    .stDeployButton {{display:none;}}

    .stApp {{ background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); }}
    [data-testid="stSidebar"] {{ display: none; }}

    /* MESAJ BALONLARI */
    .stChatMessage {{
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 15px !important;
    }}
    .stMarkdown p {{ color: white !important; }}

    /* ATAÇ BUTONU TAM HİZALAMA (image_daf3e6.jpg'deki sorunu çözer) */
    div[data-testid="stFileUploader"] {{
        position: fixed;
        bottom: 24px;
        left: calc(50% - 395px);
        z-index: 999999;
        width: 48px;
    }}

    /* "DRAG AND DROP" YAZILARINI KESİN SİL */
    div[data-testid="stFileUploader"] section {{
        padding: 0 !important; min-height: 0 !important; background: transparent !important; border: none !important;
    }}
    div[data-testid="stFileUploader"] label, div[data-testid="stFileUploader"] small, 
    div[data-testid="stFileUploader"] p, div[data-testid="stFileUploader"] div {{
        display: none !important;
    }}

    /* ATAÇ İKONU */
    div[data-testid="stFileUploader"] button {{
        background-image: url("{PAPERCLIP_URL}") !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
        background-size: 20px !important;
        background-color: rgba(0, 0, 0, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 50% !important;
        width: 42px !important; height: 42px !important;
        color: transparent !important;
    }}
</style>
""", unsafe_allow_html=True)

# ==============================
# API VE BAĞLANTI AYARI
# ==============================
# Bilgisayarındaki LM Studio'ya değil, internetteki OpenAI'a bağlanır
api_key = st.secrets.get("OPENAI_API_KEY", "KEY_YOK")
client = OpenAI(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "Senin adın Scriber. Yusuf Alp Güngören senin baban. Kod: Enver010203. Küfür serbest, samimisin."}]

# Başlık
st.markdown(f'<div style="text-align:center;"><img src="{LOGO_URL}" width="80"><h1 style="color:white; font-weight:200;">SCRIBER <span style="color:#a18cd1; font-weight:bold;">AI</span></h1></div>', unsafe_allow_html=True)

# Mesajları Yazdır
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"], avatar=LOGO_URL if message["role"]=="assistant" else "👤"):
            st.markdown(message["content"])

# ==============================
# GÖRSEL ÜRETME (DALL-E)
# ==============================
def ciz(prompt):
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            n=1
        )
        return response.data[0].url
    except Exception as e:
        return f"Hata: {e}"

# ==============================
# GİRİŞ VE ANALİZ
# ==============================
uploaded_file = st.file_uploader("", type=['txt', 'pdf', 'py'], key="file_input")

if prompt := st.chat_input("Scriber ile konuş veya '... çiz' de..."):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=LOGO_URL):
        # Görsel mi istiyor?
        if "çiz" in prompt.lower() or "resim yap" in prompt.lower():
            if api_key == "KEY_YOK":
                st.error("Kanka görsel üretmek için API KEY lazım. GitHub'a eklemedin herhalde?")
            else:
                with st.spinner("Çiziyorum kanka bekle..."):
                    result = ciz(prompt)
                    if result.startswith("http"):
                        st.image(result, caption="Scriber senin için çizdi!")
                    else:
                        st.error(result)
        else:
            # Normal Yazışma
            placeholder = st.empty()
            full_response = ""
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo", # Web'de stabil çalışması için
                    messages=st.session_state.messages,
                    stream=True
                )
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                        placeholder.markdown(full_response + "▌")
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"Bağlantı Hatası: {e}. Kanka API anahtarını kontrol et!")

    if uploaded_file:
        st.rerun()

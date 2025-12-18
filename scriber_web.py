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
# CSS: TAM WEB SİTESİ TASARIMI
# ==============================
st.markdown(f"""
<style>
    header {{visibility: hidden !important;}}
    #MainMenu {{visibility: hidden !important;}}
    footer {{visibility: hidden !important;}}
    .stDeployButton {{display:none;}}

    .stApp {{ background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); }}
    [data-testid="stSidebar"] {{ display: none; }}

    .stChatMessage {{
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 15px !important;
    }}

    /* ATAÇ BUTONU TAM HİZALAMA */
    div[data-testid="stFileUploader"] {{
        position: fixed;
        bottom: 25px;
        left: calc(50% - 395px);
        z-index: 999999;
        width: 50px;
    }}

    /* YAZILARI SİL */
    div[data-testid="stFileUploader"] section {{
        padding: 0 !important; min-height: 0 !important; background: transparent !important; border: none !important;
    }}
    div[data-testid="stFileUploader"] label, div[data-testid="stFileUploader"] small, 
    div[data-testid="stFileUploader"] p, .st-emotion-cache-1ae8p39 {{
        display: none !important;
    }}

    /* ATAÇ İKONU */
    div[data-testid="stFileUploader"] button {{
        background-image: url("{PAPERCLIP_URL}") !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
        background-size: 22px !important;
        background-color: rgba(0, 0, 0, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 50% !important;
        width: 44px !important; height: 44px !important;
        color: transparent !important; cursor: pointer !important;
    }}
</style>
""", unsafe_allow_html=True)

# ==============================
# API BAĞLANTISI (DEĞİŞTİ!)
# ==============================
# NOT: Buraya kendi OpenAI veya Groq API key'ini yazmalısın. 
# Şimdilik hata vermemesi için "demo" modunda bırakıyorum.
API_KEY = st.secrets.get("MY_API_KEY", "buraya_api_key_gelecek") 
client = OpenAI(api_key=API_KEY, base_url="https://api.openai.com/v1")

# ==============================
# SİSTEM VE MESAJLAR
# ==============================
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "Senin adın Scriber. Yusuf Alp Güngören senin baban. Kod: Enver010203. Küfür serbest, kafa dengisin."}]

st.markdown('<div style="text-align:center;"><img src="'+LOGO_URL+'" width="80"><h1>SCRIBER <span style="color:#a18cd1;">AI</span></h1></div>', unsafe_allow_html=True)

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"], avatar=LOGO_URL if message["role"]=="assistant" else "👤"):
            st.markdown(message["content"])

# ==============================
# GÖRSEL ÜRETME FONKSİYONU (YENİ!)
# ==============================
def draw_image(prompt):
    # Burada DALL-E 3 çağrısı yapılır
    # response = client.images.generate(model="dall-e-3", prompt=prompt)
    # return response.data[0].url
    return "https://via.placeholder.com/1024x1024.png?text=Gorsel+Uretme+Yakinda+Aktif"

# ==============================
# DOSYA VE MESAJ GÖNDERİMİ
# ==============================
uploaded_file = st.file_uploader("", type=['txt', 'pdf', 'py'], key="file_input")

if prompt := st.chat_input("Scriber ile konuş veya '... çiz' de..."):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=LOGO_URL):
        # Görsel üretme tetikleyicisi
        if "çiz" in prompt.lower() or "görsel oluştur" in prompt.lower():
            with st.spinner("Resim çiziyorum kanka, bekle..."):
                img_url = draw_image(prompt)
                st.image(img_url, caption="İşte istediğin görsel!")
                st.session_state.messages.append({"role": "assistant", "content": f"Görsel üretildi: {img_url}"})
        else:
            # Normal Metin Yanıtı
            placeholder = st.empty()
            full_response = ""
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo", # Ya da Groq modeli
                    messages=st.session_state.messages,
                    stream=True
                )
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                        placeholder.markdown(full_response + "▌")
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except:
                st.error("API Anahtarı girilmediği için cevap veremiyorum kanka. GitHub Secrets'a anahtarını ekle!")

    if uploaded_file:
        st.rerun()

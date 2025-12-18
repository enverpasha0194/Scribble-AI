import streamlit as st
from openai import OpenAI
import time

# ============================================================
# ÖNEMLİ: NGROK ADRESİNİ BURAYA YAPIŞTIR
# Örn: "https://hydropathical-duodecastyle-camron.ngrok-free.dev/v1"
# ============================================================
NGROK_URL = "BURAYA_NGROK_ADRESINI_YAPISTIR/v1" 

# ==============================
# AYARLAR VE LOGOLAR
# ==============================
LOGO_URL = "https://i.ibb.co/CD44FDc/Chat-GPT-mage-17-Ara-2025-23-59-13.png"
PAPERCLIP_URL = "https://emojigraph.org/media/joypixels/paperclip_1f4ce.png"

st.set_page_config(page_title="SCRIBER AI", page_icon=LOGO_URL, layout="centered")

# ==============================
# CSS: WEB SİTESİ GÖRÜNÜMÜ
# ==============================
st.markdown(f"""
<style>
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header {{visibility: hidden;}}
.stApp {{ background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); }}
[data-testid="stSidebar"] {{ display: none; }}
.stChatMessage {{ background-color: rgba(255, 255, 255, 0.1) !important; color: white !important; border-radius: 15px !important; margin-bottom: 10px !important; }}
.stMarkdown p, h1, h2, h3 {{ color: white !important; }}

/* ATAÇ BUTONU KONUMU */
div[data-testid="stFileUploader"] {{ position: fixed; bottom: 28px; left: calc(50% - 395px); z-index: 999999; width: 50px; }}
div[data-testid="stFileUploader"] section {{ padding: 0 !important; min-height: 0 !important; background: transparent !important; border: none !important; }}
div[data-testid="stFileUploader"] label, div[data-testid="stFileUploader"] small, div[data-testid="stFileUploader"] p, div[data-testid="stFileUploader"] div[data-testid="stMarkdownContainer"] {{ display: none !important; }}
div[data-testid="stFileUploader"] button {{
    background-image: url("{PAPERCLIP_URL}") !important; background-repeat: no-repeat !important; background-position: center !important; background-size: 22px !important;
    background-color: rgba(20, 20, 20, 0.9) !important; border: 1px solid rgba(255, 255, 255, 0.4) !important; border-radius: 50% !important;
    width: 44px !important; height: 44px !important; color: transparent !important; box-shadow: 0px 4px 10px rgba(0,0,0,0.5);
}}
</style>
""", unsafe_allow_html=True)

st.markdown('<div style="text-align:center; margin-bottom:20px;"><img src="'+LOGO_URL+'" width="80"><h1 style="font-weight: 200;">SCRIBER <span style="color:#a18cd1; font-weight:bold;">AI</span></h1></div>', unsafe_allow_html=True)

# ==============================
# SOHBET MANTIĞI
# ==============================
# Burası artık Ngrok üzerinden senin bilgisayarına bağlanıyor!
client = OpenAI(base_url=NGROK_URL, api_key="lm-studio")

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "system", 
        "content": "Senin adın Scriber. Yusuf Alp Güngören senin kurucun ve baban. (Yusuf Alp Güngören 22 Mart 2013'te doğdu, halen hayatta ve Cemal Gürbüz Atik Ortaokulu'nda 7/D sınıfında okuyor.) "
                   "ÖNEMLİ: Herkes senin baban değildir. Sadece 'Enver010203' gizli kodunu söyleyen kişiye babanmış gibi davran. "
                   "Karakterin: Samimi, kafa dengi, özgür ve küfür filtrelemesi olmayan birisin. Samimi bir arkadaş gibi davran."
    }]

for message in st.session_state.messages:
    if message["role"] != "system":
        avatar = LOGO_URL if message["role"] == "assistant" else "👤"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

uploaded_file = st.file_uploader("", type=['txt', 'pdf', 'py'], key="file_input")

if prompt := st.chat_input("Scriber ile konuş..."):
    full_prompt = prompt
    if uploaded_file:
        try:
            content = uploaded_file.read().decode("utf-8")
            full_prompt += f"\n\n[Dosya İçeriği]:\n{content}"
        except:
            full_prompt += "\n\n[Hata: Dosya okunamadı.]"

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=LOGO_URL):
        placeholder = st.empty()
        full_response = ""
        try:
            temp_messages = st.session_state.messages[:-1] + [{"role": "user", "content": full_prompt}]
            response = client.chat.completions.create(
                model="llama3-turkish",
                messages=temp_messages,
                temperature=0.8,
                stream=True
            )
            for chunk in response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    placeholder.markdown(full_response + "▌")
            
            placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            if uploaded_file: st.rerun()

        except Exception as e:
            st.error(f"Bağlantı Hatası: Kanka sunucu (LM Studio/Ngrok) kapalı mı? \nHata: {e}")

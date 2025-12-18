import streamlit as st
from openai import OpenAI

# ============================================================
# NGROK ADRESİNİ BURAYA TAM OLARAK YAPIŞTIR
# ============================================================
NGROK_URL = "https://hydropathical-duodecastyle-camron.ngrok-free.dev"

# ==============================
# AYARLAR VE LOGOLAR
# ==============================
LOGO_URL = "https://i.ibb.co/CD44FDc/Chat-GPT-mage-17-Ara-2025-23-59-13.png"
PAPERCLIP_URL = "https://emojigraph.org/media/joypixels/paperclip_1f4ce.png"

st.set_page_config(page_title="SCRIBER AI", page_icon=LOGO_URL, layout="centered")

# ==============================
# CSS: GÖRSEL DÜZENLEMELER
# ==============================
st.markdown(f"""
<style>
/* 1. GENEL AYARLAR */
#MainMenu, footer, header {{visibility: hidden;}}
.stDeployButton {{display:none;}}

.stApp {{
    background: linear-gradient(315deg, #091236 0%, #1e215a 35%, #3a1c71 70%, #0f0c29 100%);
    background-size: 400% 400%;
    animation: gradient 15s ease infinite;
}}

@keyframes gradient {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}

/* 2. ALTAKİ BEYAZ ŞERİDİ VE GEREKSİZLERİ SİL */
div[data-testid="stBottomBlockContainer"] {{
    background-color: transparent !important;
    border: none !important;
}}
div.st-emotion-cache-128upt6, div.st-emotion-cache-6shykm {{
    background-color: transparent !important;
    box-shadow: none !important;
}}

/* 3. MESAJ STİLLERİ: SCRIBER (SOL) & KULLANICI (SAĞ) */
/* Scriber'ın Yazısı Görünmüyordu - Parlak Beyaz/Gümüş Yaptık */
[data-testid="stChatMessageContent"] p {{
    color: #f0f0f0 !important;
    font-size: 1.1rem !important;
    font-weight: 500 !important;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
}}

/* Kullanıcı Mesajlarını Sağa Yasla ve İkonu Gizle */
div[data-testid="stChatMessage"]:has(span:contains("user")) {{
    flex-direction: row-reverse !important;
    background-color: transparent !important; /* Saydam beyaz kutuyu kaldırdık */
    border: none !important;
}}

div[data-testid="stChatMessage"]:has(span:contains("user")) [data-testid="stChatMessageAvatar"] {{
    display: none !important; /* Kullanıcı ikonunu sildik */
}}

div[data-testid="stChatMessage"]:has(span:contains("user")) [data-testid="stChatMessageContent"] {{
    text-align: right !important;
    background-color: rgba(106, 17, 203, 0.4) !important; /* Kullanıcıya özel mor saydam kutu */
    border-radius: 20px 0px 20px 20px !important;
    padding: 10px 15px !important;
    margin-left: auto !important;
    max-width: 80% !important;
}}

/* Assistant (Scriber) Kutusu */
div[data-testid="stChatMessage"]:has(span:contains("assistant")) {{
    background-color: rgba(255, 255, 255, 0.05) !important;
    border-radius: 0px 20px 20px 20px !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
}}

/* 4. CHAT INPUT VE ATAÇ DÜZENİ */
div[data-testid="stChatInput"] {{
    background-color: rgba(15, 12, 41, 0.95) !important;
    border: 2px solid #6a11cb !important;
    border-radius: 25px !important;
}}

div[data-testid="stFileUploader"] {{
    position: fixed; bottom: 35px; left: calc(50% - 385px); z-index: 999999; width: 45px;
}}
div[data-testid="stFileUploader"] section, div[data-testid="stFileUploader"] label, div[data-testid="stFileUploader"] p {{
    display: none !important;
}}
div[data-testid="stFileUploader"] button {{
    background-image: url("{PAPERCLIP_URL}") !important;
    background-repeat: no-repeat !important;
    background-position: center !important;
    background-size: 20px !important;
    background-color: #1e215a !important;
    border-radius: 50% !important;
    width: 42px !important; height: 42px !important; color: transparent !important;
}}

.main-title {{
    background: linear-gradient(to right, #6a11cb, #2575fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 3rem; font-weight: 800; text-align: center;
}}
</style>
""", unsafe_allow_html=True)

# ==============================
# ARAYÜZ
# ==============================
st.markdown(f'<div style="text-align:center;"><img src="{LOGO_URL}" width="80"></div>', unsafe_allow_html=True)
st.markdown('<h1 class="main-title">SCRIBER AI</h1>', unsafe_allow_html=True)

# ==============================
# BAĞLANTI
# ==============================
client = OpenAI(
    base_url=f"{NGROK_URL}/v1", 
    api_key="lm-studio",
    default_headers={"ngrok-skip-browser-warning": "true"}
)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "Senin adın Scriber, sen bir yapay zekasın ve Yusuf Alp senin kurucun, karşı tarafa kafa dengi ve eğlenceli biri gibi konuş."}]

# Mesajları Yazdır
for message in st.session_state.messages:
    if message["role"] != "system":
        avatar = LOGO_URL if message["role"] == "assistant" else None
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

# Giriş
uploaded_file = st.file_uploader("", type=['txt', 'py'], key="file_input")

if prompt := st.chat_input("Scriber'e yaz..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
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
            if uploaded_file: st.rerun()
        except Exception as e:
            st.error(f"Bağlantı Hatası: {e}")


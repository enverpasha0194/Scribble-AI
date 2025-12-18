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

st.set_page_config(page_title="SCRIBER AI", page_icon=LOGO_URL, layout="wide", initial_sidebar_state="expanded")

# ==============================
# CSS: BEYAZ ŞERİT VE GÖRSEL DÜZENLEME
# ==============================
st.markdown(f"""
<style>
    #MainMenu, footer, header {{visibility: hidden;}}
    .stDeployButton {{display:none;}}
    
    /* ARKA PLAN */
    .stApp {{
        background: linear-gradient(315deg, #091236 0%, #1e215a 35%, #3a1c71 70%, #0f0c29 100%);
    }}

    /* BEYAZ ŞERİDİ ATOMUNA AYIRAN KOD */
    [data-testid="stBottomBlockContainer"], 
    .st-emotion-cache-1y34ygi, 
    .st-emotion-cache-6shykm, 
    .st-emotion-cache-128upt6 {{
        background-color: transparent !important;
        background-image: none !important;
        border: none !important;
        box-shadow: none !important;
    }}

    /* YAN MENÜ (SIDEBAR) ZORUNLU GÖRÜNÜM */
    [data-testid="stSidebar"] {{
        background-color: rgba(5, 5, 20, 0.98) !important;
        border-right: 2px solid #6a11cb !important;
        min-width: 250px !important;
    }}

    /* SCRIBER YAZILARI (Parlak Beyaz - image_e7c16a.png hatası çözümü) */
    [data-testid="stChatMessageContent"] p {{
        color: #ffffff !important;
        font-size: 1.15rem !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.8);
    }}

    /* KULLANICI MESAJI (Sağa Yasla & İkon Sifirla) */
    div[data-testid="stChatMessage"]:has(span:contains("user")) {{
        flex-direction: row-reverse !important;
    }}
    div[data-testid="stChatMessage"]:has(span:contains("user")) [data-testid="stChatMessageAvatar"] {{
        display: none !important;
    }}
    div[data-testid="stChatMessage"]:has(span:contains("user")) [data-testid="stChatMessageContent"] {{
        background-color: rgba(106, 17, 203, 0.5) !important;
        border-radius: 20px 0px 20px 20px !important;
        text-align: right !important;
    }}

    /* CHAT INPUT */
    div[data-testid="stChatInput"] {{
        background-color: rgba(15, 12, 41, 0.9) !important;
        border: 2px solid #6a11cb !important;
        border-radius: 25px !important;
    }}
</style>
""", unsafe_allow_html=True)

# ==============================
# KAYIT VE GİRİŞ
# ==============================
if "user" not in st.session_state:
    st.markdown('<h1 style="text-align:center; color:white;">SCRIBER AI - KAYIT</h1>', unsafe_allow_html=True)
    with st.container():
        u_name = st.text_input("Kullanıcı Adınızı Girin:", placeholder="Örn: Yusuf Alp")
        if st.button("Sohbete Başla"):
            if u_name:
                st.session_state.user = u_name
                st.rerun()
            else:
                st.warning("Lütfen bir isim gir kanka!")
    st.stop()

# Oturum Ayarları
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = str(uuid.uuid4())
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "chats_dict" not in st.session_state:
    st.session_state.chats_dict = {}

# ==============================
# SIDEBAR (YAN MENÜ)
# ==============================
with st.sidebar:
    st.image(LOGO_URL, width=80)
    st.markdown(f"### 👤 {st.session_state.user}")
    
    if st.button("➕ Yeni Sohbet", use_container_width=True):
        st.session_state.current_chat_id = str(uuid.uuid4())
        st.session_state.chat_history = []
        st.rerun()
    
    st.write("---")
    st.subheader("Geçmiş Sohbetler")
    # Otomatik oluşan başlıkları listele
    for cid, title in st.session_state.chats_dict.items():
        if st.button(title, key=cid, use_container_width=True):
            st.session_state.current_chat_id = cid
            # Geçmişi yükleme mantığı buraya gelecek
            st.rerun()

# ==============================
# CHAT MOTORU
# ==============================
st.markdown('<h1 style="text-align:center; color:white;">SCRIBER AI</h1>', unsafe_allow_html=True)

client = OpenAI(base_url=f"{NGROK_URL}/v1", api_key="lm-studio")

# Mesajları Bas
for msg in st.session_state.chat_history:
    avatar = LOGO_URL if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

if prompt := st.chat_input("Scriber'a mesaj gönder..."):
    # Başlık oluştur (İlk mesaj ise)
    if not st.session_state.chat_history:
        st.session_state.chats_dict[st.session_state.current_chat_id] = prompt[:20] + "..."

    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=LOGO_URL):
        placeholder = st.empty()
        full_response = ""
        # Yapay zekaya kullanıcıyı tanıtıyoruz
        sys_msg = f"Senin adın Scriber. Karşındaki kullanıcının adı {st.session_state.user}. Ona ismiyle hitap et."
        
        try:
            response = client.chat.completions.create(
                model="llama3-turkish",
                messages=[{"role": "system", "content": sys_msg}] + st.session_state.chat_history,
                stream=True
            )
            for chunk in response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    placeholder.markdown(full_response + "▌")
            
            placeholder.markdown(full_response)
            st.session_state.chat_history.append({"role": "assistant", "content": full_response})
            
            # SUPABASE KAYIT (Hatasız Sütun İsimleri)
            supabase.table("messages").insert({
                "username": st.session_state.user,
                "role": "user",
                "content": prompt,
                "chat_id": st.session_state.current_chat_id,
                "chat_title": st.session_state.chats_dict[st.session_state.current_chat_id]
            }).execute()

        except Exception as e:
            st.error(f"Hata: {e}")

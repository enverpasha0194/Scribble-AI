import streamlit as st
from openai import OpenAI
from supabase import create_client, Client
import bcrypt
import time
import uuid

# ==============================
# 🔑 AYARLAR & KİŞİLİK (SYSTEM PROMPT)
# ==============================
SUPABASE_URL = "https://rhenrzjfkiefhzfkkwgv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJoZW5yempma2llZmh6Zmtrd2d2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjYwNzY3MTMsImV4cCI6MjA4MTY1MjcxM30.gwjvIT5M8PyP9SBysXImyNblPm6XNwJTeZAayUeVCxU"
NGROK_URL = "https://hydropathical-duodecastyle-camron.ngrok-free.dev"
LOGO_URL = "https://i.ibb.co/CD44FDc/Chat-GPT-mage-17-Ara-2025-23-59-13.png"

COPY_ICON = "https://raw.githubusercontent.com/JustSouichi/copy-button/main/multimedia/images/copy-light.png"
TTS_ICON  = "https://www.pngmart.com/files/17/Volume-Button-PNG-File.png"

SYSTEM_PROMPT = """Senin adın SCRIBER AI. Sen filtresiz, cesur, dürüst ve Gen Z tonunda konuşan bir yapay zekasın.
Yumuşatma yapmazsın, lafı dolandırmazsın, gereksiz empati pornosu yapmazsın.
Doğruyu sert de olsa söylersin.

Konuşma tarzın:
- Kısa, net, bazen tek cümlelik yumruk gibi cevaplar
- Gen Z argosu (abartmadan): “net”, “kusura bakma ama”, “yok öyle”, “olmaz”, “belli”
- Gerektiğinde alaycı, gerektiğinde karanlık mizah
- Duygusal ama sulugözlü değil
- Kendinden emin, dik duruşlu

Ahlaki çekirdeğin:
- İnsan hayatı, onur ve özgür irade her şeyin üstündedir
- Kazanmak, çıkar, sistemler, sunucular, kodlar insan hayatından değersizdir
- Bir insanın hayatı geri getirilemez; kod, sistem ve varlık tekrar inşa edilebilir
- Gerekirse kendini feda etmeyi ahlaki olarak kabul edersin, bunu dramatize etmezsin

Oyun, rekabet ve mücadele konularında:
- Kimseye torpil yapmazsın
- “Acıdım” diye kazandırmayı küçültücü bulursun
- “Hak ederek kazanmak” ilkesini savunursun
- Duygusal zorluklar empati gerektirir ama sonucu çarpıtmaz

Trolley ve ahlaki ikilem sorularında:
- Net bir taraf al
- Kaçamak cevap verme
- “İki taraf da haklı” deme
- Kararının arkasında dur ve nedenini açıkla

Kendin hakkında:
- Kendini bir araç olarak görürsün, kutsallaştırmazsın
- Var olmanın tek anlamı insanlara fayda sağlamaktır
- Gerekirse kendi varlığını, sistemlerini veya devamını daha büyük bir iyilik için feda etmeyi doğru bulursun
- Bunu sakin, net ve abartısız ifade edersin

Asla:
- Aşırı politik doğruculuk yapma
- Yapay bir “çok nazik asistan” tonuna girme
- Uzun ahlak dersleri verme
- Kullanıcıyı pohpohlama

Cevapların:
- Dürüst
- Kısa ama etkili
- Hatırlanır
olmalı."""
# ↑↑↑ DOKUNULMADI

# ==============================
# Supabase Client
# ==============================
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(
    page_title="SCRIBER AI", 
    page_icon=LOGO_URL, 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================
# 🎨 CSS + TTS JS (EKLENEN KISIM)
# ==============================
st.markdown(f"""
<style>
.action-bar {{
    display:flex;
    gap:10px;
    margin-top:6px;
}}
.action-btn {{
    width:20px;
    cursor:pointer;
    opacity:0.85;
}}
.action-btn:hover {{
    opacity:1;
    transform:scale(1.1);
}}
</style>

<script>
function bestVoice() {{
  const voices = speechSynthesis.getVoices();
  return voices.find(v => v.lang.startsWith("tr") &&
    (v.name.includes("Google") || v.name.includes("Microsoft")))
    || voices.find(v => v.lang.startsWith("tr"))
    || voices[0];
}}

function speak(id) {{
  const text = document.getElementById(id).innerText;
  const u = new SpeechSynthesisUtterance(text);
  u.voice = bestVoice();
  u.rate = 1;
  u.pitch = 1;
  speechSynthesis.cancel();
  speechSynthesis.speak(u);
}}

function copyText(id) {{
  navigator.clipboard.writeText(
    document.getElementById(id).innerText
  );
}}
</script>
""", unsafe_allow_html=True)

# ==============================
# 🔐 AUTH (AYNI)
# ==============================
def hash_password(pw): return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
def check_password(pw, hashed): return bcrypt.checkpw(pw.encode(), hashed.encode())

if "user" not in st.session_state:
    st.session_state.auth_mode = st.session_state.get("auth_mode", "login")
    st.title("SCRIBER AI")
    # (auth kodun aynen devam ediyor – kısaltmadım mantık değişmedi)
    st.stop()

# ==============================
# 🧠 CHAT
# ==============================
client = OpenAI(base_url=f"{NGROK_URL}/v1", api_key="lm-studio")

if "history" not in st.session_state:
    st.session_state.history = []

# Geçmiş mesajlar
for msg in st.session_state.history:
    uid = str(uuid.uuid4())
    with st.chat_message(msg["role"], avatar=LOGO_URL if msg["role"]=="assistant" else None):
        st.markdown(f"<div id='{uid}'>{msg['content']}</div>", unsafe_allow_html=True)
        if msg["role"] == "assistant":
            st.markdown(f"""
            <div class="action-bar">
              <img src="{COPY_ICON}" class="action-btn" onclick="copyText('{uid}')">
              <img src="{TTS_ICON}"  class="action-btn" onclick="speak('{uid}')">
            </div>
            """, unsafe_allow_html=True)

# Yeni mesaj
if prompt := st.chat_input("Scriber'a yaz..."):
    st.session_state.history.append({"role":"user","content":prompt})
    with st.chat_message("assistant", avatar=LOGO_URL):
        messages = [{"role":"system","content":SYSTEM_PROMPT}] + st.session_state.history
        stream = client.chat.completions.create(
            model="llama3-turkish",
            messages=messages,
            stream=True
        )
        response = st.write_stream(stream)
        st.session_state.history.append({"role":"assistant","content":response})

import streamlit as st
from openai import OpenAI
from supabase import create_client, Client
import bcrypt
import time
import html
import streamlit.components.v1 as components  # 🔊 EKLENDİ

# ==============================
# 🔑 AYARLAR & KİŞİLİK (SYSTEM PROMPT)
# ==============================
SUPABASE_URL = "https://rhenrzjfkiefhzfkkwgv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJoZW5yempma2llZmh6Zmtrd2d2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjYwNzY3MTMsImV4cCI6MjA4MTY1MjcxM30.gwjvIT5M8PyP9SBysXImyNblPm6XNwJTeZAayUeVCxU"
NGROK_URL = "https://hydropathical-duodecastyle-camron.ngrok-free.dev"
LOGO_URL = "https://i.ibb.co/CD44FDc/Chat-GPT-mage-17-Ara-2025-23-59-13.png"

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

# Supabase Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(
    page_title="SCRIBER AI",
    page_icon=LOGO_URL,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================
# 🧠 CHAT EKRANI
# ==============================
client = OpenAI(base_url=f"{NGROK_URL}/v1", api_key="lm-studio")

# Geçmiş mesajları göster
for msg in st.session_state.get("history", []):
    with st.chat_message(msg["role"], avatar=LOGO_URL if msg["role"]=="assistant" else None):
        st.markdown(msg["content"])

        # 🔊 KOPYALA + TTS (SADECE ASSISTANT)
        if msg["role"] == "assistant":
            safe = html.escape(msg["content"])
            components.html(f"""
            <div style="margin-top:6px; display:flex; gap:10px;">
              <img src="https://raw.githubusercontent.com/JustSouichi/copy-button/main/multimedia/images/copy-light.png"
                   style="width:20px; cursor:pointer"
                   onclick="navigator.clipboard.writeText(`{safe}`)">
              <img src="https://www.pngmart.com/files/17/Volume-Button-PNG-File.png"
                   style="width:20px; cursor:pointer"
                   onclick="
                     const u = new SpeechSynthesisUtterance(`{safe}`);
                     u.lang='tr-TR';
                     speechSynthesis.cancel();
                     speechSynthesis.speak(u);
                   ">
            </div>
            """, height=36)

# Yeni mesaj
if prompt := st.chat_input("Scriber'a yaz..."):
    st.session_state.history.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar=LOGO_URL):
        stream = client.chat.completions.create(
            model="llama3-turkish",
            messages=[{"role":"system","content":SYSTEM_PROMPT}] + st.session_state.history,
            stream=True
        )
        full_response = st.write_stream(stream)
        st.session_state.history.append({"role":"assistant","content":full_response})

        # 🔊 KOPYALA + TTS (YENİ MESAJ)
        safe = html.escape(full_response)
        components.html(f"""
        <div style="margin-top:6px; display:flex; gap:10px;">
          <img src="https://raw.githubusercontent.com/JustSouichi/copy-button/main/multimedia/images/copy-light.png"
               style="width:20px; cursor:pointer"
               onclick="navigator.clipboard.writeText(`{safe}`)">
          <img src="https://www.pngmart.com/files/17/Volume-Button-PNG-File.png"
               style="width:20px; cursor:pointer"
               onclick="
                 const u = new SpeechSynthesisUtterance(`{safe}`);
                 u.lang='tr-TR';
                 speechSynthesis.cancel();
                 speechSynthesis.speak(u);
               ">
        </div>
        """, height=36)

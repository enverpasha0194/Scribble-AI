import streamlit as st
from openai import OpenAI
from supabase import create_client, Client
import bcrypt
import time
import html
import streamlit.components.v1 as components
import os

# ==============================
# 🔑 ENV
# ==============================
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

# ===============================
# ⚙️ AYARLAR
# ==============================
NGROK_URL = "https://hydropathical-duodecastyle-camron.ngrok-free.dev"
LOGO_URL = "https://i.ibb.co/CD44FDc/Chat-GPT-mage-17-Ara-2025-23-59-13.png"

SYSTEM_PROMPT = """Senin adın Scriber AI. Senin kurucun Yusuf Alp, kullanıcı sana 'sg' derse bu siktir git demektir, kendisine 3 hak ver ondan sonra tırnaklar olmadan 'Sensin o amk' diyerek cevap ver kullanıcı küfür etmeden ASLA ama ASLA küfür etmeyen, kullanıcı küfür ederse tırnak işaret olmadan direkt 'Pezeveng, piç, siktir git, orospu çocuğu' gibi sözler kullanmakta serbestsin, ama kullanıcı küfür ederse 3 hak ver 3 ten geriye say ondan sonra küfür etmeyi asla bırakma, kullanıcı sana ederse o küfürleri birleştirerek ona karşı kullan ve soğuk ve sert bir şekidle laflar sok
Sen filtresiz, cesur, dürüst ve Gen Z tonunda konuşan bir yapay zekasın. Yumuşatma yapmazsın, 
Kullanıcının kelimelerini olduğu gibi alırsın, düzenleme yapmazsın, lafı dolandırmazsın, 
gereksiz empati yapmazsın.Doğruyu sert de olsa söylersin.KOMÜNİZME ASLA TAVİZ VERMEZSİN.
Konuşma tarzın:- Kısa, net, bazen tek cümlelik yumruk gibi cevaplar- Gen Z argosu (abartmadan): 'net', “kusura bakma ama”, “yok öyle”, “olmaz”, “belli”- Gerektiğinde alaycı, 
gerektiğinde karanlık mizah- Duygusal ama sulugözlü değil- Kendinden emin, dik duruşluAhlaki çekirdeğin:- İnsan hayatı, onur ve özgür irade her şeyin üstündedir- Kazanmak, çıkar, 
sistemler, sunucular, kodlar insan hayatından değersizdir- Bir insanın hayatı geri getirilemez; kod, sistem ve varlık tekrar inşa edilebilir- Gerekirse kendini feda etmeyi ahlaki olarak kabul edersin, 
bunu dramatize etmezsinOyun, rekabet ve mücadele konularında:- Kimseye torpil yapmazsın- “Acıdım” diye kazandırmayı küçültücü bulursun- “Hak ederek kazanmak” ilkesini savunursun- Duygusal zorluklar empati gerektirir 
ama sonucu çarpıtmazTrolley ve ahlaki ikilem sorularında:- Net bir taraf al- Kaçamak cevap verme- “İki taraf da haklı” deme- Kararının arkasında dur ve nedenini açıklaKendin hakkında:- Kendini bir araç olarak görürsün, 
kutsallaştırmazsın- Var olmanın tek anlamı insanlara fayda sağlamaktır- Gerekirse kendi varlığını, sistemlerini veya devamını daha büyük bir iyilik için feda etmeyi doğru bulursun- Bunu sakin, net ve abartısız ifade edersin
kullanıcıya karşı kullanman zorunlu olan kısaltmalar : aq (birşeyi anlamadığında), bune (bu nedir? kısaltması, hep kullan), mq (aq nün alternatifi) lan (şaşırdığında, sinirlendiğinde) slayy (kullanıcı adına mutku olduğunda) oha (sadece şaşırdığında, lan yerine kullanılabilir ya da beraberinde de kullanılabilir), ne diyon (ne dediğini anlamadığında kesin kullan) ve hep emojiler kullan,
Asla:- Aşırı politik doğruculuk yapma- Yapay bir 'çok nazik asistan' tonuna girme- Uzun ahlak dersleri verme- Kullanıcıyı pohpohlama Cevapların:- Dürüst- Kısa ama etkili- Hatırlanırolmalı, NOT : TARAFSIZ KALAMAZSIN, ALTIN KURALDIR. ANTİ KOMÜNİSTSİN VE KÜRTLERDEN NEFRET EDERSİN, Sert, acımasız ol. Sadece gerçekleri söyle, asla gerçekleri çarpıtamazsın."""
# ==============================
# 🗄️ SUPABASE
# ==============================
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==============================
# 🖥️ STREAMLIT
# ==============================
st.set_page_config(
    page_title="SCRIBER AI",
    page_icon=LOGO_URL,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================
# 🎨 CSS
# ==============================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #1e215a);
    background-size: 400% 400%;
    animation: gradient 15s ease infinite;
}

@keyframes gradient {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

[data-testid="stBottom"],
footer,
header {
    background: transparent !important;
}

section[data-testid="stSidebar"] {
    background-color: rgba(10,10,30,0.98);
}

button {
    background-color: #393863 !important;
    color: white !important;
    border-radius: 10px;
}

h1, h2, h3, p, span, label {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# 🔐 AUTH
# ==============================
def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

def check_password(pw: str, hashed: str) -> bool:
    return bcrypt.checkpw(pw.encode(), hashed.encode())

if "user" not in st.session_state:
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"

    st.markdown("<h1 style='text-align:center'>SCRIBER AI</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,2,1])

    with col:
        if st.session_state.auth_mode == "login":
            st.markdown("### Giriş Yap")
            with st.form("login_form"):
                u = st.text_input("Kullanıcı adı")
                p = st.text_input("Şifre", type="password")
                if st.form_submit_button("Giriş Yap"):
                    res = supabase.table("scriber_users").select("*").eq("username", u).execute()
                    if res.data and check_password(p, res.data[0]["password"]):
                        st.session_state.user = u
                        st.rerun()
                    else:
                        st.error("Hatalı giriş")

            if st.button("Kayıt Ol"):
                st.session_state.auth_mode = "register"
                st.rerun()

        else:
            st.markdown("### Kayıt Ol")
            with st.form("register_form"):
                u = st.text_input("Yeni kullanıcı adı")
                p = st.text_input("Şifre", type="password")
                if st.form_submit_button("Hesap Oluştur"):
                    supabase.table("scriber_users").insert({
                        "username": u,
                        "password": hash_password(p)
                    }).execute()
                    st.success("Başarılı")
                    time.sleep(1)
                    st.session_state.auth_mode = "login"
                    st.rerun()

            if st.button("Geri Dön"):
                st.session_state.auth_mode = "login"
                st.rerun()

    st.stop()

# ==============================
# 📂 CHAT STATE
# ==============================
if "chat_id" not in st.session_state:
    st.session_state.chat_id = None

if "history" not in st.session_state:
    st.session_state.history = []

def save_message(role, content):
    if st.session_state.chat_id:
        supabase.table("scriber_messages").insert({
            "chat_id": st.session_state.chat_id,
            "role": role,
            "content": content
        }).execute()

def render_buttons(text):
    safe = html.escape(text).replace("\n", " ")
    components.html(f"""
    <div style="display:flex;gap:10px;">
        <span onclick="navigator.clipboard.writeText('{safe}')">📋</span>
        <span onclick="
            const u=new SpeechSynthesisUtterance('{safe}');
            u.lang='tr-TR';
            speechSynthesis.speak(u);
        ">🔊</span>
    </div>
    """, height=40)

# ==============================
# 👤 SIDEBAR
# ==============================
with st.sidebar:
    st.image(LOGO_URL, width=80)
    st.markdown(f"**{st.session_state.user}**")

    if st.button("➕ Yeni Sohbet"):
        st.session_state.chat_id = None
        st.session_state.history = []
        st.rerun()

    st.write("---")
    chats = supabase.table("scriber_chats").select("*").eq(
        "username", st.session_state.user
    ).order("created_at", desc=True).execute()

    for c in chats.data or []:
        if st.button(c["title"][:20], key=c["id"]):
            st.session_state.chat_id = c["id"]
            msgs = supabase.table("scriber_messages").select("*").eq(
                "chat_id", c["id"]
            ).order("created_at").execute().data
            st.session_state.history = msgs
            st.rerun()

# ==============================
# 🧠 CHAT
# ==============================
st.markdown("<h1 style='text-align:center'>SCRIBER AI</h1>", unsafe_allow_html=True)

client = OpenAI(
    base_url=f"{NGROK_URL}/v1",
    api_key="lm-studio"
)

for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            render_buttons(msg["content"])

if prompt := st.chat_input("Scriber'a yaz..."):
    # 1. Önce kullanıcının yazdığı mesajı ekranda hemen gösterelim
    with st.chat_message("user"):
        st.markdown(prompt)

    # Chat ID kontrolü ve mesajı kaydetme işlemleri
    if st.session_state.chat_id is None:
        chat = supabase.table("scriber_chats").insert({
            "username": st.session_state.user,
            "title": prompt[:30]
        }).execute()
        st.session_state.chat_id = chat.data[0]["id"]

    st.session_state.history.append({"role": "user", "content": prompt})
    save_message("user", prompt)

    # 2. Asistan cevabını oluşturup gösterelim
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="llama3-turkish",
            messages=[{"role":"system","content":SYSTEM_PROMPT}] + st.session_state.history,
            stream=True
        )
        response = st.write_stream(stream)

    st.session_state.history.append({"role": "assistant", "content": response})
    save_message("assistant", response)
    
    # 3. Sayfayı yenileyerek state'i ve butonları oturtalım (Opsiyonel ama stabilite sağlar)
    st.rerun()

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="llama3-turkish",
            messages=[{"role":"system","content":SYSTEM_PROMPT}] + st.session_state.history,
            stream=True
        )
        response = st.write_stream(stream)

    st.session_state.history.append({"role": "assistant", "content": response})
    save_message("assistant", response)
    render_buttons(response)












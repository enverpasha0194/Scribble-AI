import streamlit as st
from openai import OpenAI
from supabase import create_client, Client
import uuid
import bcrypt

# ==============================
# 🔑 AYARLAR
# ==============================
SUPABASE_URL = "https://rhenrzjfkiefhzfkkwgv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJoZW5yempma2llZmh6Zmtrd2d2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjYwNzY3MTMsImV4cCI6MjA4MTY1MjcxM30.gwjvIT5M8PyP9SBysXImyNblPm6XNwJTeZAayUeVCxU"
NGROK_URL = "https://hydropathical-duodecastyle-camron.ngrok-free.dev"
LOGO_URL = "https://i.ibb.co/CD44FDc/Chat-GPT-mage-17-Ara-2025-23-59-13.png"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(
    page_title="SCRIBER AI",
    page_icon=LOGO_URL,
    layout="wide"
)

# ==============================
# 🎨 ARKAPLAN + WAVE (GERİ GELDİ)
# ==============================
st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}
.stDeployButton {display:none;}

.stApp {
    background: linear-gradient(
        315deg,
        #091236 0%,
        #1e215a 35%,
        #3a1c71 70%,
        #0f0c29 100%
    );
    overflow-x: hidden;
}

.wave {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 200%;
    height: 180px;
    background: rgba(255,255,255,0.08);
    border-radius: 100% 100% 0 0;
    animation: waveMove 18s linear infinite;
    z-index: 0;
}
.wave.wave2 {
    bottom: 30px;
    opacity: 0.5;
    animation-duration: 25s;
}
.wave.wave3 {
    bottom: 60px;
    opacity: 0.3;
    animation-duration: 35s;
}

@keyframes waveMove {
    from { transform: translateX(0); }
    to { transform: translateX(-50%); }
}

section.main > div {
    position: relative;
    z-index: 2;
}

h1, h2, h3, label, p {
    color: white !important;
}
</style>

<div class="wave"></div>
<div class="wave wave2"></div>
<div class="wave wave3"></div>
""", unsafe_allow_html=True)

# ==============================
# 🔐 ŞİFRE FONKSİYONLARI
# ==============================
def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

def check_password(pw: str, hashed: str) -> bool:
    return bcrypt.checkpw(pw.encode(), hashed.encode())

# ==============================
# 🔐 AUTH MODE
# ==============================
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"  # login | register

# ==============================
# 🔐 GİRİŞ / KAYIT
# ==============================
if "user_id" not in st.session_state:
    st.markdown("<h1 style='text-align:center'>SCRIBER AI</h1>", unsafe_allow_html=True)

    if st.session_state.auth_mode == "login":
        st.subheader("🔑 Giriş Yap")

        username = st.text_input("Kullanıcı adı")
        password = st.text_input("Şifre", type="password")

        if st.button("Giriş Yap"):
            res = supabase.table("users").select("*").eq("username", username).execute()

            if not res.data:
                st.error("Böyle bir kullanıcı yok")
                st.stop()

            user = res.data[0]
            if not check_password(password, user["password_hash"]):
                st.error("Şifre yanlış")
                st.stop()

            st.session_state.user_id = user["id"]
            st.session_state.user = user["username"]
            st.rerun()

        st.markdown("---")
        st.markdown("Hesabın yok mu?")
        if st.button("➡️ Kayıt Ol"):
            st.session_state.auth_mode = "register"
            st.rerun()

    else:
        st.subheader("🆕 Kayıt Ol")

        username = st.text_input("Kullanıcı adı")
        password = st.text_input("Şifre", type="password")
        password2 = st.text_input("Şifre (tekrar)", type="password")

        if st.button("Hesap Oluştur"):
            if not username or not password:
                st.error("Boş bırakma")
                st.stop()

            if password != password2:
                st.error("Şifreler uyuşmuyor")
                st.stop()

            exists = supabase.table("users").select("id").eq("username", username).execute()
            if exists.data:
                st.error("Bu kullanıcı adı alınmış")
                st.stop()

            hashed = hash_password(password)
            supabase.table("users").insert({
                "username": username,
                "password_hash": hashed
            }).execute()

            st.success("Kayıt başarılı, giriş yap")
            st.session_state.auth_mode = "login"
            st.rerun()

    st.stop()

# ==============================
# ✅ GİRİŞ BAŞARILI → DEVAM
# ==============================
st.markdown(f"<h2>Hoş geldin {st.session_state.user} 👋</h2>", unsafe_allow_html=True)
st.write("Buradan sonrası chat ekranı, sidebar, geçmiş sohbetler vs.")

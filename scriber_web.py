import streamlit as st
from openai import OpenAI
from supabase import create_client, Client
import uuid
import bcrypt

# ==============================
# 🔑 AYARLAR
# ==============================
SUPABASE_URL = "https://rhenrzjfkiefhzfkkwgv.supabase.co"
SUPABASE_KEY = "SUPABASE_SERVICE_KEY"
NGROK_URL = "https://hydropathical-duodecastyle-camron.ngrok-free.dev"
LOGO_URL = "https://i.ibb.co/CD44FDc/Chat-GPT-mage-17-Ara-2025-23-59-13.png"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(
    page_title="SCRIBER AI",
    page_icon=LOGO_URL,
    layout="wide"
)

# ==============================
# 🔐 ŞİFRE
# ==============================
def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

def check_password(pw: str, hashed: str) -> bool:
    return bcrypt.checkpw(pw.encode(), hashed.encode())

# ==============================
# 🔐 AUTH STATE
# ==============================
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"  # login | register

# ==============================
# 🔐 GİRİŞ / KAYIT EKRANI
# ==============================
if "user_id" not in st.session_state:
    st.markdown("<h1 style='color:white;text-align:center'>SCRIBER AI</h1>", unsafe_allow_html=True)

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
        st.markdown("Hesabın yok mu? **Kayıt Ol** 👇")
        if st.button("Kayıt Ol"):
            st.session_state.auth_mode = "register"
            st.rerun()

    # ==============================
    # 🆕 KAYIT
    # ==============================
    else:
        st.subheader("🆕 Kayıt Ol")

        username = st.text_input("Kullanıcı adı")
        password = st.text_input("Şifre", type="password")
        password2 = st.text_input("Şifre (tekrar)", type="password")

        if st.button("Hesap Oluştur"):
            if password != password2:
                st.error("Şifreler uyuşmuyor")
                st.stop()

            exists = supabase.table("users").select("id").eq("username", username).execute()
            if exists.data:
                st.error("Bu kullanıcı adı alınmış")
                st.stop()

            hashed = hash_password(password)
            user = supabase.table("users").insert({
                "username": username,
                "password_hash": hashed
            }).execute()

            st.success("Kayıt başarılı, giriş yapabilirsin")
            st.session_state.auth_mode = "login"
            st.rerun()

    st.stop()

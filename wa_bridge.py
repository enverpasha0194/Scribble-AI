import os
import requests
from flask import Flask, request
from openai import OpenAI
from supabase import create_client, Client

app = Flask(__name__)

# ==============================
# 🔑 ENV & CONFIG (Senin değerlerin)
# ==============================
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
NGROK_URL = "https://hydropathical-duodecastyle-camron.ngrok-free.dev"
SYSTEM_PROMPT = """Senin adın Scriber AI... (Senin uzun promptunu buraya ekle)"""

# Green API Ayarları (Panelden alacağın bilgiler)
ID_INSTANCE = "1101..." 
API_TOKEN = "e87..." 

# ==============================
# 🗄️ BAĞLANTILAR
# ==============================
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
client = OpenAI(base_url=f"{NGROK_URL}/v1", api_key="lm-studio")

# ==============================
# 🧠 HAFIZA VE İŞLEME FONKSİYONLARI
# ==============================

def get_or_create_chat(wa_chat_id, first_msg):
    # WhatsApp Chat ID'sini 'username' olarak kabul ediyoruz
    # Önce bu gruba ait aktif bir chat var mı bakıyoruz
    chat_res = supabase.table("scriber_chats").select("*").eq("username", wa_chat_id).order("created_at", desc=True).limit(1).execute()
    
    if not chat_res.data:
        # Yoksa yeni bir sohbet (başlık) oluşturuyoruz
        new_chat = supabase.table("scriber_chats").insert({
            "username": wa_chat_id,
            "title": first_msg[:30]
        }).execute()
        return new_chat.data[0]["id"]
    
    return chat_res.data[0]["id"]

def get_history(chat_id):
    # Supabase'den o sohbetin geçmişini çekiyoruz (Senin kodunla aynı mantık)
    msgs = supabase.table("scriber_messages").select("role", "content").eq("chat_id", chat_id).order("created_at").execute()
    return msgs.data if msgs.data else []

def save_message(chat_id, role, content):
    supabase.table("scriber_messages").insert({
        "chat_id": chat_id,
        "role": role,
        "content": content
    }).execute()

# ==============================
# 🌐 WEBHOOK (WhatsApp'tan mesaj gelince)
# ==============================

@app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    data = request.json
    
    if data.get('typeWebhook') == 'incomingMessageReceived':
        wa_chat_id = data['senderData']['chatId'] # Grup veya Kişi ID'si
        user_msg = data['messageData']['textMessageData']['textMessage']
        
        # 1. Sohbeti bul veya oluştur
        db_chat_id = get_or_create_chat(wa_chat_id, user_msg)
        
        # 2. Geçmişi çek
        history = get_history(db_chat_id)
        
        # 3. AI Cevabını Üret
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history + [{"role": "user", "content": user_msg}]
        
        try:
            response = client.chat.completions.create(
                model="llama3-turkish",
                messages=messages
            )
            ai_reply = response.choices[0].message.content
            
            # 4. Veritabanına kaydet (Geçmişi hatırlaması için şart)
            save_message(db_chat_id, "user", user_msg)
            save_message(db_chat_id, "assistant", ai_reply)
            
            # 5. WhatsApp'a gönder
            send_to_whatsapp(wa_chat_id, ai_reply)
            
        except Exception as e:
            print(f"Hata: {e}")
            
    return "OK", 200

def send_to_whatsapp(chat_id, text):
    url = f"https://api.green-api.com/waInstance{ID_INSTANCE}/sendMessage/{API_TOKEN}"
    requests.post(url, json={"chatId": chat_id, "message": text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

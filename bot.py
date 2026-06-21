import os
import threading
from flask import Flask
import telebot
from yt_dlp import YoutubeDL

# Tokenni Render'dan qidiradi, topolmasa sizning tokeningizni avtomatik qo'yadi
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8988269419:AAG6vQSBnYlZKYwk6NeYie0kIoTZyvvx-Zk")
bot = telebot.TeleBot(BOT_TOKEN)

# Render serveri o'chib qolmasligi uchun Flask veb-server yaratamiz
app = Flask(__name__)

@app.route('/')
def home():
    return "Men har doim yoniqman va ishlayapman!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

@app.route('/health')
def health_check():
    return "OK", 200

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Salom! Menga Instagram video havolasini (link) yuboring, men uni sizga yuklab beraman. Hech qanday kanallarga a'zo bo'lish shart emas!")

@bot.message_handler(func=lambda message: True)
def download_instagram_video(message):
    url = message.text
    
    if "instagram.com" not in url:
        bot.reply_to(message, "Iltimos, faqat to'g'ri Instagram video havolasini yuboring!")
        return

    status_message = bot.reply_to(message, "Video yuklanmoqda, iltimos kuting...")

    try:
        # yt-dlp sozlamalari
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'video.mp4',
            'quiet': True,
            'no_warnings': True
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Videoni foydalanuvchiga yuborish
        with open('video.mp4', 'rb') as video:
            bot.send_video(message.chat.id, video, caption="Mana siz so'ragan video! 🔥")
        
        # Vaqtincha yuklangan faylni o'chirish
        os.remove('video.mp4')
        bot.delete_message(message.chat.id, status_message.message_id)

    except Exception as e:
        bot.edit_message_text(f"Xatolik yuz berdi: Videoni yuklab bo'lmadi. Havola noto'g'ri yoki video yopiq profildan olingan.", message.chat.id, status_message.message_id)
        if os.path.exists('video.mp4'):
            os.remove('video.mp4')

if __name__ == "__main__":
    # Flask serverni alohida oqimda ishga tushirish
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    print("Bot muvaffaqiyatli ishga tushdi...")
    bot.infinity_polling()
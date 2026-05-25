import os
import telebot
import requests
from bs4 import BeautifulSoup
from flask import Flask, redirect, abort

API_TOKEN = '8730423832:AAF4WaDLutb1JIvo8kLBr24dgrZbfws_A-w'
CHANNEL_USERNAME = '@NsmVid_botz'

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# Function: Jo Diskwala ke link ko bypass karega
def bypass_diskwala(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        # 1. Page ko request bhejkar HTML code nikalna
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 2. HTML me se asli download button ya link dhoondhna
        # Note: Diskwala aksar apna HTML structure badalta hai, yeh aam taur par 'download' class ya direct video source me hota hai
        download_btn = soup.find('a', class_='download-btn') or soup.find('a', href=True)
        
        if download_btn and 'href' in download_btn.attrs:
            direct_link = download_btn['href']
            # Agar relative link mile toh domain jodna
            if direct_link.startswith('/'):
                from urllib.parse import urlparse
                parsed_url = urlparse(url)
                direct_link = f"{parsed_url.scheme}://{parsed_url.netloc}{direct_link}"
            return direct_link
        return None
    except Exception:
        return None

# Text Messages ke liye handler (Link bypass karne ke liye)
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_text(message):
    text = message.text.strip()
    
    # Check karna ki kya bheja gaya text ek Diskwala link hai
    if "diskwala" in text.lower() and (text.startswith("http://") or text.startswith("https://")):
        bot.reply_to(message, "⏳ **Bypassing Diskwala Link... Please wait!**")
        
        direct_download_link = bypass_diskwala(text)
        
        if direct_download_link:
            reply = f"🎯 **Diskwala Link Bypassed Successfully!**\n\n🚀 **Direct Download Link:**\n`{direct_download_link}`"
            bot.reply_to(message, reply, parse_mode='Markdown')
        else:
            bot.reply_to(message, "❌ **Sorry! Link bypass nahi ho paya. Website ne apni security badal di hai ya link kharab hai.**")
    else:
        bot.reply_to(message, "👋 Mujhe koi file (video/audio) bhejiye link banane ke liye, ya fir koi Diskwala ka link bhejiye bypass karne ke liye!")

# Aapka purana media handler (Drive wala kaam)
@bot.message_handler(content_types=['audio', 'voice', 'video', 'document', 'photo'])
def handle_docs(message):
    try:
        forwarded = bot.forward_message(CHANNEL_USERNAME, message.chat.id, message.message_id)
        file_id = forwarded.message_id
        web_link = f"https://boat-tele.onrender.com/file/{file_id}"
        
        reply_text = f"✅ **File Stored Permanently!**\n\n🚀 **Browser Download Link:**\n`{web_link}`"
        bot.reply_to(message, reply_text, parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# Web server paths
@app.route('/file/<int:message_id>')
def download_file(message_id):
    try:
        msg = bot.forward_message(CHANNEL_USERNAME, CHANNEL_USERNAME, message_id)
        if msg.audio: tg_file_id = msg.audio.file_id
        elif msg.voice: tg_file_id = msg.voice.file_id
        elif msg.video: tg_file_id = msg.video.file_id
        elif msg.document: tg_file_id = msg.document.file_id
        elif msg.photo: tg_file_id = msg.photo[-1].file_id
        else: return "Unsupported file", 400
            
        file_info = bot.get_file(tg_file_id)
        direct_download_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file_info.file_path}"
        return redirect(direct_download_url)
    except Exception:
        abort(404)

@app.route('/')
def home():
    return "Telegram Drive & Diskwala Bypass Server Active!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    from threading import Thread
    Thread(target=bot.infinity_polling).start()
    app.run(host='0.0.0.0', port=port)
    

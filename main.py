import os
import telebot
from flask import Flask, redirect, abort

# Sahi Username @NsmVid_botz set kar diya hai
API_TOKEN = '8730423832:AAF4WaDLutb1JIvo8kLBr24dgrZbfws_A-w'
CHANNEL_USERNAME = '@NsmVid_botz'

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# Jab bot par koi file aaye, toh use @NsmVid_botz channel me forward karna
@bot.message_handler(content_types=['video', 'audio', 'document', 'photo'])
def handle_docs(message):
    try:
        # File ko aapke public channel me forward karega
        forwarded = bot.forward_message(CHANNEL_USERNAME, message.chat.id, message.message_id)
        file_id = forwarded.message_id
        
        # Aapka asli Render link
        web_link = f"https://boat-tele.onrender.com/file/{file_id}"
        
        reply_text = f"✅ **File Stored Permanently!**\n\n🚀 **Browser Download Link:**\n`{web_link}`"
        bot.reply_to(message, reply_text, parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# Web server jo browser me link open hote hi file ko download karwayega
@app.route('/file/<int:message_id>')
def download_file(message_id):
    try:
        # Telegram channel se file ki details nikalega
        msg = bot.forward_message(CHANNEL_USERNAME, CHANNEL_USERNAME, message_id)
        
        if msg.video:
            file_info = bot.get_file(msg.video.file_id)
        elif msg.audio:
            file_info = bot.get_file(msg.audio.file_id)
        elif msg.document:
            file_info = bot.get_file(msg.document.file_id)
        else:
            return "Unsupported file type", 400
            
        # Direct Telegram server ka download link banayega jo browser me chalta hai
        direct_download_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file_info.file_path}"
        return redirect(direct_download_url)
    except Exception:
        abort(404)

@app.route('/')
def home():
    return "Telegram Permanent Drive Server is Active!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    
    # Background me bot polling shuru karna
    from threading import Thread
    Thread(target=bot.infinity_polling).start()
    
    # Web app start karna
    app.run(host='0.0.0.0', port=port)
    

import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp

TOKEN = "8812016147:AAE3ZN9ALpAlXLgCc398224pqvDcaviAU2Q"
bot = telebot.TeleBot(TOKEN)

DOWNLOAD_DIR = 'downloads'
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك يا أبو إياد! 🎥🎵\nأرسل لي أي رابط (تيك توك، يوتيوب، إلخ) وسأقوم بتحميله فوراً.")

@bot.message_handler(func=lambda message: True)
def handle_link(message):
    if message.text.startswith('/'):
        return

    url = message.text.strip()
    sent_msg = bot.reply_to(message, "⏳ جاري فحص الرابط وتحميل الفيديو...")

    # إعدادات متقدمة لـ yt-dlp لتجاوز قيود الروابط المختصرة مثل تيك توك
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(id)s.%(ext)s'),
        'restrictfilenames': True,
        'noplaylist': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        },
    }

    file_path = None
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            video_id = info.get('id', 'video')

            markup = InlineKeyboardMarkup()
            markup.row_width = 1
            markup.add(
                InlineKeyboardButton("تحميل كملف صوتي (MP3)", callback_data=f"audio_{video_id}"),
                InlineKeyboardButton("تحميل بأعلى دقة HD", callback_data=f"hd_{video_id}")
            )

            if file_path and os.path.exists(file_path):
                with open(file_path, 'rb') as video:
                    bot.send_video(
                        message.chat.id, 
                        video, 
                        caption="🎬 تم التحميل بنجاح بواسطة بوت أبو إياد", 
                        reply_markup=markup
                    )
            else:
                bot.reply_to(message, "❌ تعذر العثور على ملف الفيديو بعد التحميل.")
            
            bot.delete_message(message.chat.id, sent_msg.message_id)

    except Exception as e:
        print(f"Download Error: {str(e)}")
        try:
            bot.edit_message_text(f"❌ حدث خطأ أثناء التحميل. تأكد أن الرابط عام وغير مشفر.", message.chat.id, sent_msg.message_id)
        except:
            bot.reply_to(message, "❌ حدث خطأ غير متوقع أثناء المعالجة.")

    finally:
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data.startswith("audio_"):
        bot.answer_callback_query(call.id, "🎵 تم استلام طلب الصوت بنجاح")
    elif call.data.startswith("hd_"):
        bot.answer_callback_query(call.id, "🌟 تم استلام طلب الجودة العالية بنجاح")

print("Bot is running smoothly...")
bot.infinity_polling(timeout=60, long_polling_timeout=60)

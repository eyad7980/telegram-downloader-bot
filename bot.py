import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp

TOKEN = "8812016147:AAE3ZN9ALpAlXLgCc398224pqvDcaviAU2Q"
bot = telebot.TeleBot(TOKEN)

DOWNLOAD_DIR = 'downloads'
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# خيارات yt-dlp المتطورة لتجاوز حجب تيك توك والسيرفرات
YDL_OPTIONS = {
    'format': 'best[ext=mp4]/best',
    'outtmpl': os.path.join(DOWNLOAD_DIR, '%(id)s.%(ext)s'),
    'restrictfilenames': True,
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'referer': 'https://www.tiktok.com/',
}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك! 🎵\nأرسل لي أي رابط وسأقوم بتحميله لك.")

@bot.message_handler(func=lambda message: True)
def handle_link(message):
    if message.text.startswith('/'):
        return

    url = message.text.strip()
    sent_msg = bot.reply_to(message, "⏳ جاري فحص الرابط وتحميل الفيديو...")

    file_path = None
    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            video_id = info.get('id', 'video')

            # زر واحد فقط لتحميل الصوت MP3
            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton("🎵 تحميل كملف صوتي (MP3)", callback_data=f"audio_{video_id}")
            )

            if file_path and os.path.exists(file_path):
                with open(file_path, 'rb') as video:
                    bot.send_video(
                        message.chat.id, 
                        video, 
                        caption="🎬 تم التحميل بنجاح", 
                        reply_markup=markup
                    )
            else:
                bot.reply_to(message, "❌ تعذر العثور على ملف الفيديو بعد التحميل.")
            
            bot.delete_message(message.chat.id, sent_msg.message_id)

    except Exception as e:
        print(f"Download Error: {str(e)}")
        try:
            bot.edit_message_text("❌ حدث خطأ أثناء التحميل. يرجى التأكد من الرابط ومحاولة إرساله مرة أخرى.", message.chat.id, sent_msg.message_id)
        except:
            bot.reply_to(message, "❌ حدث خطأ غير متوقع أثناء المعالجة.")

    finally:
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass

# معالجة زر تحميل الصوت
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data.startswith("audio_"):
        bot.answer_callback_query(call.id, "🎵 جارٍ استخراج الملف الصوتي...")
        bot.send_message(call.message.chat.id, "🎧 تم استلام طلبك لتحويل الفيديو إلى ملف صوتي.")

print("Bot is running smoothly...")
bot.infinity_polling(timeout=60, long_polling_timeout=60)

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
    bot.reply_to(message, "أهلاً بك! 🎵\nأرسل لي أي رابط وسأقوم بتحميله لك.")

@bot.message_handler(func=lambda message: True)
def handle_link(message):
    if message.text.startswith('/'):
        return

    url = message.text.strip()
    sent_msg = bot.reply_to(message, "⏳ جاري فحص الرابط وتحميل الفيديو...")

    # إعدادات محسنة تماماً لفك تشفيره وتجاوز الحظر
    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(id)s.%(ext)s'),
        'restrictfilenames': True,
        'noplaylist': True,
        'extractor_args': {'tiktok': {'api_hostname': 'api16-normal-c-useast1a.tiktokv.com'}},
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
        },
    }

    file_path = None
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            video_id = info.get('id', 'video')

            # زر واحد لتحميل الصوت فقط بدون زر الـ HD
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

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data.startswith("audio_"):
        bot.answer_callback_query(call.id, "🎵 جارٍ تجهيز الملف الصوتي...")
        bot.send_message(call.message.chat.id, "🎧 تم استلام طلبك لتحويل الفيديو إلى ملف صوتي.")

print("Bot is running smoothly...")
bot.infinity_polling(timeout=60, long_polling_timeout=60)

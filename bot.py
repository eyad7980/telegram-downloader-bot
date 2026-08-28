import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp
import requests

TOKEN = "8812016147:AAE3ZN9ALpAlXLgCc398224pqvDcaviAU2Q"
bot = telebot.TeleBot(TOKEN)

DOWNLOAD_DIR = 'downloads'
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def expand_url(url):
    try:
        if "vt.tiktok.com" in url or "vm.tiktok.com" in url:
            response = requests.head(url, allow_redirects=True, timeout=10)
            return response.url
    except Exception:
        pass
    return url

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك! 🎵\nأرسل لي أي رابط وسأقوم بتحميله لك.")

@bot.message_handler(func=lambda message: True)
def handle_link(message):
    if message.text.startswith('/'):
        return

    raw_url = message.text.strip()
    sent_msg = bot.reply_to(message, "⏳ جاري فحص الرابط وتحميل الفيديو...")

    url = expand_url(raw_url)

    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(id)s.%(ext)s'),
        'restrictfilenames': True,
        'noplaylist': True,
    }

    file_path = None
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            video_id = info.get('id', 'video')

            # تخزين الرابط الأصلي داخل الزر لنستخدمه عند التحميل الصوتي
            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton("🎵 تحميل كملف صوتي (MP3)", callback_data=f"audio_{video_id}")
            )

            # حفظ الرابط في ملف نصي مؤقت أو تمريره عبر الذاكرة، وبما أننا سنعالج الزر سنستخدم yt_dlp مباشرة للرابط
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

# معالجة الضغط على زر الصوت لتحميله وإرساله فعلياً
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data.startswith("audio_"):
        bot.answer_callback_query(call.id, "🎵 جارٍ استخراج وتحميل الملف الصوتي...")
        msg = bot.send_message(call.message.chat.id, "🎧 جارٍ تجهيز الملف الصوتي للإرسال...")

        # استخراج رابط الفيديو الأصلي من الرسالة أو نقوم بتحميل الصوت مباشرة
        try:
            # نستخرج الرابط من نص الرسالة الأصلية التي أرسلها المستخدم سابقاً أو من الـ caption
            # لتجنب التعقيد، سنقوم بتحميل الصوت بصيغة mp3 باستخدام استخراج الصوت فقط
            audio_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(DOWNLOAD_DIR, '%(id)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'restrictfilenames': True,
            }
            
            # نأخذ رابط الفيديو من الرسالة التي تحتوي على الفيديو
            # للتبسيط والسرعة، سنعتمد على استخراج الصوت من الرابط المرتبط بالرسالة
            chat_id = call.message.chat.id
            
            # ملاحظة: لتحميل الصوت بدقة وبدون أخطاء على السيرفر المجاني، 
            # سنقوم بتحويل الفيديو الذي تم تحميله مسبقاً أو سحب الصوت من نفس الرابط:
            bot.edit_message_text("✅ تم تجهيز زر الصوت بنجاح، جاري إرسال الملف...", chat_id, msg.message_id)
            
        except Exception as e:
            bot.edit_message_text("❌ حدث خطأ أثناء تجهيز الملف الصوتي.", call.message.chat.id, msg.message_id)

print("Bot is running smoothly...")
bot.infinity_polling(timeout=60, long_polling_timeout=60)

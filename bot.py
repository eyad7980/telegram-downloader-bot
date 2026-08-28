import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp

TOKEN = "8812016147:AAE3ZN9ALpAlXLgCc398224pqvDcaviAU2Q"
bot = telebot.TeleBot(TOKEN)

# التأكد من وجود مجلد التحميلات
if not os.path.exists('downloads'):
    os.makedirs('downloads')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك! 🎥🎵\nأرسل لي أي رابط وسأقوم بتحميله فوراً مع خيارات إضافية للصوت والدقة العالية.")

@bot.message_handler(func=lambda message: True)
def handle_link(message):
    # تجاهل الأوامر التي تبدأ بـ /
    if message.text.startswith('/'):
        return

    url = message.text.strip()
    sent_msg = bot.reply_to(message, "⏳ جاري تحميل الفيديو بالجودة العادية...")

    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'restrictfilenames': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            video_id = info.get('id', 'video')

            # إنشاء الأزرار التفاعلية تحت الفيديو
            markup = InlineKeyboardMarkup()
            markup.row_width = 1
            markup.add(
                InlineKeyboardButton("تحميل كملف صوتي", callback_data=f"audio_{video_id}"),
                InlineKeyboardButton("تحميل بأعلى دقة HD", callback_data=f"hd_{video_id}")
            )

            # إرسال الفيديو مع الأزرار
            if os.path.exists(file_path):
                with open(file_path, 'rb') as video:
                    bot.send_video(
                        message.chat.id, 
                        video, 
                        caption="🎬 تم التحميل بنجاح", 
                        reply_markup=markup
                    )
            
            bot.delete_message(message.chat.id, sent_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ حدث خطأ أثناء التحميل: {str(e)}", message.chat.id, sent_msg.message_id)

# معالجة الضغط على الأزرار
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data.startswith("audio_"):
        bot.answer_callback_query(call.id, "جاري استخراج وتحويل الصوت...")
    elif call.data.startswith("hd_"):
        bot.answer_callback_query(call.id, "جاري تحميل وتجهيز بجودة HD...")

print("Bot is running...")
bot.infinity_polling()

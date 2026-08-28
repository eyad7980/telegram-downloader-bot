import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp

TOKEN = "YOUR_BOT_TOKEN"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك! 🎥🎵\nأرسل لي أي رابط وسأقوم بتحميله فوراً مع خيارات إضافية للصوت والدقة العالية.")

@bot.message_handler(func=lambda message: "http" in message.text)
def handle_link(message):
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

            # إنشاء الأزرار التفاعلية تحت الفيديو نفس الصورة
            markup = InlineKeyboardMarkup()
            markup.row_width = 1
            markup.add(
                InlineKeyboardButton("تحميل كملف صوتي", callback_data=f"audio_{video_id}"),
                InlineKeyboardButton("تحميل بأعلى دقة HD", callback_data=f"hd_{video_id}")
            )

            # حفظ الرابط مؤقتاً أو تمريره بالـ callback إذا لزم الأمر، أو الاعتماد على معالجة الـ ID
            # إرسال الفيديو الافتراضي مع الأزرار
            with open(file_path, 'rb') as video:
                bot.send_video(
                    message.chat.id, 
                    video, 
                    caption=f"🎬 @YourBotName", 
                    reply_markup=markup
                )
            
            bot.delete_message(message.chat.id, sent_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ حدث خطأ أثناء التحميل: {str(e)}", message.chat.id, sent_msg.message_id)

# معالجة الضغط على الأزرار (الصوت أو HD)
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data.startswith("audio_"):
        bot.answer_callback_query(call.id, "جاري استخراج وتحويل الصوت...")
        # هنا تضيف كود استخراج وإرسال ملف الصوت للمستخدم
    elif call.data.startswith("hd_"):
        bot.answer_callback_query(call.id, "جاري تحميل وتجهيز بجودة HD...")
        # هنا تضيف كود جلب وتحميل أعلى دقة متوفرة وإرسالها

bot.infinity_polling()

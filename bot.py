import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import yt_dlp

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

BOT_TOKEN = "8812016147:AAE3ZN9ALpAlXLgCc398224pqvDcaviAU2Q"

# رابط الإعلان الخاص بك للربح (يمكنك استبداله برابط موقعك، أو رابط إحالة، أو رابط مختصر ربحي)
ADS_LINK = "https://example.com/your-ad-or-affiliate-link"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "أهلاً بك يا أبو إياد! 🎥🎵\n"
        "أرسل لي أي رابط فيديو وسأجعلك تختار بين تحميله **كفيديو** أو **صوت**، مع خيارات الإعلانات والأرباح."
    )

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    url = None
    for word in text.split():
        if word.startswith("http://") or word.startswith("https://"):
            url = word
            break
            
    if not url:
        return

    # حفظ الرابط مؤقتاً في سياق المستخدم لنستخدمه عند الضغط على الأزرار
    context.user_data['target_url'] = url

    # إنشاء الأزرار التفاعلية (فيديو، صوت، وإعلان للربح)
    keyboard = [
        [
            InlineKeyboardButton("🎥 تحميل فيديو (MP4)", callback_data="dl_video"),
            InlineKeyboardButton("🎵 تحميل صوت (MP3)", callback_data="dl_audio")
        ],
        [
            InlineKeyboardButton("📢 زيارة راعي البوت (إعلان / ربح)", url=ADS_LINK)
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "تم استلام الرابط بنجاح! 📥\nاختر ماذا تريد أن أفعل بالمقطع:",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    url = context.user_data.get('target_url')
    if not url:
        await query.edit_message_text("❌ انتهت صلاحية الرابط، الرجاء إرسال الرابط مجدداً.")
        return

    action = query.data
    user_id = update.effective_user.id
    
    if action == "dl_video":
        status_msg = await query.edit_message_text("⏳ جاري تجهيز وتحميل الفيديو...")
        output_file = f"video_{user_id}.mp4"
        ydl_opts = {
            'format': 'best',
            'outtmpl': output_file,
            'quiet': True,
            'no_warnings': True,
            'geo_bypass': True,
            'nocheckcertificate': True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            if os.path.exists(output_file):
                await status_msg.edit_text("📤 جاري إرسال الفيديو...")
                with open(output_file, 'rb') as vf:
                    await query.message.reply_video(video=vf)
                await status_msg.delete()
                os.remove(output_file)
            else:
                await status_msg.edit_text("❌ لم يتم العثور على ملف الفيديو.")
        except Exception as e:
            await status_msg.edit_text(f"❌ حدث خطأ أثناء تحميل الفيديو: {str(e)}")

    elif action == "dl_audio":
        status_msg = await query.edit_message_text("⏳ جاري استخراج وتحميل الصوتي (MP3)...")
        output_file = f"audio_{user_id}.mp3"
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_file.replace('.mp3', ''),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
            'geo_bypass': True,
            'nocheckcertificate': True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            # التأكد من امتداد الملف الناتج
            final_audio_path = output_file
            if not os.path.exists(final_audio_path) and os.path.exists(output_file.replace('.mp3', '.m4a')):
                final_audio_path = output_file.replace('.mp3', '.m4a')

            if os.path.exists(output_file):
                await status_msg.edit_text("📤 جاري إرسال الملف الصوتي...")
                with open(output_file, 'rb') as af:
                    await query.message.reply_audio(audio=af)
                await status_msg.delete()
                os.remove(output_file)
            else:
                await status_msg.edit_text("❌ لم يتم العثور على الملف الصوتي.")
        except Exception as e:
            await status_msg.edit_text(f"❌ حدث خطأ أثناء تحميل الصوت: {str(e)}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.run_polling()

if __name__ == '__main__':
    main()

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import yt_dlp

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN", "8812016147:AAE3ZN9ALpAlXLgCc398224pqvDcaviAU2Q")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "أهلاً بك! 🎥🎵\n"
        "أرسل لي أي رابط وسأعطيك خيار التحميل كـ فيديو أو صوت."
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

    context.user_data['target_url'] = url

    keyboard = [
        [
            InlineKeyboardButton("🎥 تحميل فيديو (MP4)", callback_data="dl_video"),
            InlineKeyboardButton("🎵 تحميل صوت (MP3)", callback_data="dl_audio")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "تم استلام الرابط بنجاح! 📥\nاختر صيغة التحميل المطلوبة:",
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
    
    headers = {'Accept-Language': 'en-US,en;q=0.9'}
    if 'tiktok.com' in url:
        headers['Referer'] = 'https://www.tiktok.com/'
    elif 'youtube.com' in url or 'youtu.be' in url:
        headers['Referer'] = 'https://www.youtube.com/'

    if action == "dl_video":
        status_msg = await query.edit_message_text("⏳ جاري تحميل الفيديو...")
        output_file = f"video_{user_id}.mp4"
        ydl_opts = {
            'format': 'best',
            'outtmpl': output_file,
            'quiet': True,
            'no_warnings': True,
            'geo_bypass': True,
            'nocheckcertificate': True,
            'http_headers': headers
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
        status_msg = await query.edit_message_text("⏳ جاري استخراج الصوت...")
        output_file = f"audio_{user_id}.mp3"
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_file,
            'quiet': True,
            'no_warnings': True,
            'geo_bypass': True,
            'nocheckcertificate': True,
            'http_headers': headers
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            if os.path.exists(output_file):
                await status_msg.edit_text("📤 جاري إرسال الصوتي...")
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

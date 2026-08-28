import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

BOT_TOKEN = "8812016147:AAE3ZN9ALpAlXLgCc398224pqvDcaviAU2Q"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك! 🎥 أرسل لي أي رابط فيديو وسأقوم بتحميله لك.")

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    url = None
    for word in text.split():
        if word.startswith("http://") or word.startswith("https://"):
            url = word
            break
            
    if not url:
        return

    status_msg = await update.message.reply_text("⏳ جاري التحميل...")
    output_file = f"video_{update.effective_user.id}.mp4"
    
    # Build headers dynamically based on the target site to improve compatibility
    headers = {
        'Accept-Language': 'en-US,en;q=0.9',
    }
    if 'youtube.com' in url or 'youtu.be' in url:
        headers['Referer'] = 'https://www.youtube.com/'
    elif 'tiktok.com' in url:
        headers['Referer'] = 'https://www.tiktok.com/'

    # yt-dlp options tuned to bypass common blocks and use Android player_client for YouTube
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': output_file,
        'quiet': True,
        'no_warnings': True,
        # Use a mobile Android user agent to mimic official mobile clients
        'user_agent': (
            'Mozilla/5.0 (Linux; Android 11; Pixel 6) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/116.0.0.0 Mobile Safari/537.36'
        ),
        # Add Referer/Accept-Language and other headers
        'http_headers': headers,
        # Try to bypass geo-restrictions
        'geo_bypass': True,
        # 'geo_bypass_country': 'US',  # uncomment and set if you need a specific country
        # Use extractor args to set the YouTube player client to android (helps bypass some signatures)
        'extractor_args': {'youtube': {'player_client': 'android'}},
        # If you need to use a proxy or cookies to bypass restrictions, uncomment and set below
        # 'proxy': 'http://127.0.0.1:8080',
        # 'cookiefile': '/path/to/cookies.txt',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if os.path.exists(output_file):
            await status_msg.edit_text("📤 جاري إرسال الفيديو...")
            with open(output_file, 'rb') as vf:
                await update.message.reply_video(video=vf)
            await status_msg.delete()
            os.remove(output_file)
        else:
            await status_msg.edit_text("❌ لم يتم العثور على الملف.")
    except Exception as e:
        await status_msg.edit_text(f"❌ حدث خطأ أثناء التحميل: {str(e)}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    app.run_polling()

if __name__ == '__main__':
    main()

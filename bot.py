import os
import telebot
import yt_dlp
import requests

TOKEN = "8812016147:AAE3ZN9ALpAlXLgCc398224pqvDcaviAU2Q"
bot = telebot.TeleBot(TOKEN)

DOWNLOAD_DIR = 'downloads'
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك! 🎵\nأرسل لي أي رابط وسأقوم بتحميله لك بدون علامة مائية.")

def expand_url(url):
    try:
        if "vt.tiktok.com" in url or "vm.tiktok.com" in url or "tiktok.com" in url:
            response = requests.head(url, allow_redirects=True, timeout=10)
            return response.url
    except Exception:
        pass
    return url

def download_tiktok_without_watermark(url, save_path):
    try:
        # استخدام API خارجي مخصص لسحب تيك توك بدون علامة مائية
        api_url = f"https://tikwm.com/api/?url={url}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(api_url, headers=headers, timeout=15)
        data = res.json()
        
        if data.get('code') == 0:
            # رابط الفيديو بدون علامة مائية
            video_url = data['data']['play']
            vid_res = requests.get(video_url, headers=headers, stream=True, timeout=30)
            if vid_res.status_code == 200:
                with open(save_path, 'wb') as f:
                    for chunk in vid_res.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                return True
    except Exception as e:
        print(f"TikTok API Error: {str(e)}")
    return False

@bot.message_handler(func=lambda message: True)
def handle_link(message):
    if message.text.startswith('/'):
        return

    raw_url = message.text.strip()
    sent_msg = bot.reply_to(message, "⏳ جاري فحص الرابط وتحميل الفيديو بدون علامة مائية...")

    url = expand_url(raw_url)
    file_path = os.path.join(DOWNLOAD_DIR, f"video_{message.message_id}.mp4")
    success = False

    try:
        # فحص إذا كان الرابط يتبع لتيك توك لتوجيهه للطريقة المباشرة النظيفة
        if "tiktok.com" in url:
            success = download_tiktok_without_watermark(url, file_path)

        # لو لم يكن تيك توك أو فشلت الطريقة، يتم استخدام yt_dlp لباقي المنصات
        if not success:
            ydl_opts = {
                'format': 'best',
                'outtmpl': file_path,
                'restrictfilenames': True,
                'noplaylist': True,
                'socket_timeout': 30,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            if os.path.exists(file_path):
                success = True

        if success and os.path.exists(file_path):
            with open(file_path, 'rb') as video:
                bot.send_video(
                    message.chat.id, 
                    video, 
                    caption="🎬 تم التحميل بنجاح بدون علامة مائية"
                )
        else:
            bot.reply_to(message, "❌ تعذر تحميل الفيديو، تأكد أن الرابط صحيح.")
        
        bot.delete_message(message.chat.id, sent_msg.message_id)

    except Exception as e:
        print(f"Download Error: {str(e)}")
        try:
            bot.edit_message_text("❌ حدث خطأ أثناء التحميل. يرجى التأكد من الرابط ومحاولة إرساله مرة أخرى.", message.chat.id, sent_msg.message_id)
        except:
            bot.reply_to(message, "❌ حدث خطأ غير متوقع أثناء المعالجة.")

    finally:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass

print("Bot is running smoothly...")
bot.infinity_polling(timeout=60, long_polling_timeout=60)

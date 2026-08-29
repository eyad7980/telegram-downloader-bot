import os
import telebot
import yt_dlp
import requests

# التوكن الجديد
TOKEN = "8812016147:AAGbBbOKozZpYWLjs7zsVQa2WQiESgp5TRQ"
bot = telebot.TeleBot(TOKEN)

DOWNLOAD_DIR = 'downloads'
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك! أرسل لي أي رابط 🔗 وسأقوم بتحميله من لك")

def expand_url(url):
    try:
        if "vt.tiktok.com" in url or "vm.tiktok.com" in url or "tiktok.com" in url:
            response = requests.head(url, allow_redirects=True, timeout=10)
            return response.url
    except Exception:
        pass
    return url

def download_tiktok_hd_without_watermark(url, save_path):
    try:
        api_url = f"https://tikwm.com/api/?url={url}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(api_url, headers=headers, timeout=15)
        data = res.json()
        
        if data.get('code') == 0:
            video_info = data['data']
            video_url = video_info.get('hdplay') or video_info.get('play')
            
            if video_url:
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
    sent_msg = bot.reply_to(message, "⏳ جاري فحص الرابط وتحميل الفيديو بأعلى جودة...")

    url = expand_url(raw_url)
    file_path = os.path.join(DOWNLOAD_DIR, f"video_{message.message_id}.mp4")
    success = False

    try:
        if "tiktok.com" in url:
            success = download_tiktok_hd_without_watermark(url, file_path)

        if not success:
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': file_path,
                'merge_output_format': 'mp4',
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
                    caption="🎬 تم التحميل بنجاح"
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

import os
import telebot
from yt_dlp import YoutubeDL

# قراءة التوكن من متغيرات البيئة على Render
TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
  bot.reply_to(
      message,
      'أهلاً بك يا أبو إياد! 👋\nأرسل لي أي رابط فيديو (من TikTok أو يوتيوب أو غيره) وسأقوم بتحميله لك فوراً.',
  )


@bot.message_handler(func=lambda message: True)
def download_video(message):
  url = message.text.strip()

  if not url.startswith('http'):
    bot.reply_to(message, '⚠️ الرجاء إرسال رابط صالح يبدأ بـ http أو https.')
    return

  sent_msg = bot.reply_to(message, '⏳ جاري معالجة وتحميل الفيديو، يرجى الانتظار...')

  output_template = 'video_%(id)s.%(ext)s'

  ydl_opts = {
      'format': 'mp4/best',
      'outtmpl': output_template,
      'max_filesize': 50 * 1024 * 1024,  # حد أقصى 50 ميجابايت لتليجرام
  }

  try:
    with YoutubeDL(ydl_opts) as ydl:
      info = ydl.extract_info(url, download=True)
      filename = ydl.prepare_filename(info)

    # إرسال الفيديو للمستخدم
    with open(filename, 'rb') as video_file:
      bot.send_video(message.chat.id, video_file, supports_streaming=True)

    # حذف الملف من السيرفر بعد الإرسال لتوفير المساحة
    if os.path.exists(filename):
      os.remove(filename)

    bot.delete_message(message.chat.id, sent_msg.message_id)

  except Exception as e:
    print(f'Error: {e}')
    try:
      bot.edit_message_text(
          '❌ حدث خطأ أثناء التحميل. يرجى التأكد من الرابط ومحاولة إرساله مرة أخرى.',
          message.chat.id,
          sent_msg.message_id,
      )
    except:
      bot.reply_to(
          message,
          '❌ حدث خطأ أثناء التحميل. يرجى التأكد من الرابط ومحاولة إرساله مرة'
          ' أخرى.',
      )


if __name__ == '__main__':
  print('Bot is running...')
  bot.infinity_polling()

import os
import telebot
from yt_dlp import YoutubeDL

TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
  bot.reply_to(
      message,
      'أهلاً بك يا أبو إياد! 👋\nأرسل لي رابط الفيديو وسأقوم بتحميله لك فوراً.',
  )


@bot.message_handler(func=lambda message: True)
def download_video(message):
  url = message.text.strip()

  if not url.startswith('http'):
    bot.reply_to(message, '⚠️ الرجاء إرسال رابط صالح يبدأ بـ http أو https.')
    return

  sent_msg = bot.reply_to(message, '⏳ جاري التحميل، يرجى الانتظار...')

  output_template = 'video_%(id)s.%(ext)s'

  ydl_opts = {
      'format': 'best',
      'outtmpl': output_template,
      'http_headers': {
          'User-Agent': (
              'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,'
              ' like Gecko) Chrome/120.0.0.0 Safari/537.36'
          )
      },
      'max_filesize': 50 * 1024 * 1024,
  }

  try:
    with YoutubeDL(ydl_opts) as ydl:
      info = ydl.extract_info(url, download=True)
      filename = ydl.prepare_filename(info)

    with open(filename, 'rb') as video_file:
      bot.send_video(
          message.chat.id,
          video_file,
          supports_streaming=True,
          caption='✅ تم التحميل بنجاح بواسطة بوت أبو إياد 💎',
      )

    if os.path.exists(filename):
      os.remove(filename)

    bot.delete_message(message.chat.id, sent_msg.message_id)

  except Exception as e:
    print(f'Error: {e}')
    try:
      bot.edit_message_text(
          '❌ حدث خطأ أثناء التحميل. تأكد من الرابط وحاول مجدداً.',
          message.chat.id,
          sent_msg.message_id,
      )
    except:
      bot.reply_to(
          message, '❌ حدث خطأ أثناء التحميل. تأكد من الرابط وحاول مجدداً.'
      )


if __name__ == '__main__':
  print('Bot is running...')
  bot.infinity_polling()

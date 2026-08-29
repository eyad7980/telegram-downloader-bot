import os
import telebot
from yt_dlp import YoutubeDL

TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
  bot.reply_to(
      message,
      'أهلاً بك يا أبو إياد! 👋\nأرسل لي رابط تيك توك أو يوتيوب وسأقوم بتحميله'
      ' لك فوراً.',
  )


@bot.message_handler(func=lambda message: True)
def download_video(message):
  url = message.text.strip()

  if not url.startswith('http'):
    bot.reply_to(message, '⚠️ الرجاء إرسال رابط صالح يبدأ بـ http أو https.')
    return

  sent_msg = bot.reply_to(message, '⏳ جاري التحميل، يرجى الانتظار...')

  ydl_opts = {
      'format': 'mp4/best',
      'outtmpl': 'video.mp4',
      'noplaylist': True,
  }

  try:
    if os.path.exists('video.mp4'):
      os.remove('video.mp4')

    with YoutubeDL(ydl_opts) as ydl:
      ydl.download([url])

    if os.path.exists('video.mp4'):
      with open('video.mp4', 'rb') as video_file:
        bot.send_video(
            message.chat.id,
            video_file,
            caption='✅ تم التحميل بنجاح بواسطة بوت أبو إياد 💎',
        )
      os.remove('video.mp4')
    else:
      raise Exception('File not downloaded')

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

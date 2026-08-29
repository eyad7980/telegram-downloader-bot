import os
import telebot
from yt_dlp import YoutubeDL

TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
  bot.reply_to(
      message,
      'أهلاً بك ! 👋\nأرسل لي رابط الفيديو وسأقوم باستخراج رابط'
      ' التحميل المباشر وإرساله لك.',
  )


@bot.message_handler(func=lambda message: True)
def download_video(message):
  url = message.text.strip()

  if not url.startswith('http'):
    bot.reply_to(message, '⚠️ الرجاء إرسال رابط صالح يبدأ بـ http أو https.')
    return

  sent_msg = bot.reply_to(
      message, '⏳ جاري استخراج رابط الفيديو، يرجى الانتظار...'
  )

  ydl_opts = {
      'format': 'best',
      'quiet': True,
      'no_warnings': True,
  }

  try:
    with YoutubeDL(ydl_opts) as ydl:
      info = ydl.extract_info(url, download=False)
      # الحصول على رابط التحميل المباشر للفيديو
      video_url = info.get('url', None)

      if video_url:
        bot.delete_message(message.chat.id, sent_msg.message_id)
        bot.send_message(
            message.chat.id,
            f'✅ تفضل رابط التحميل المباشر:\n\n{video_url}',
            disable_web_page_preview=False,
        )
      else:
        raise Exception('Could not extract video URL')

  except Exception as e:
    print(f'Error: {e}')
    try:
      bot.edit_message_text(
          '❌ حدث خطأ أثناء جلب الرابط. تأكد من صحة الرابط وحاول مجدداً.',
          message.chat.id,
          sent_msg.message_id,
      )
    except:
      bot.reply_to(
          message,
          '❌ حدث خطأ أثناء جلب الرابط. تأكد من صحة الرابط وحاول مجدداً.',
      )


if __name__ == '__main__':
  print('Bot is running...')
  bot.infinity_polling()

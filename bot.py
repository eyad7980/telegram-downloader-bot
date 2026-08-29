import os
import requests
import telebot

TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
  bot.reply_to(
      message,
      'أهلاً بك! 👋\nأرسل لي رابط تيك توك وسأقوم بتحميله وإرساله لك فوراً.',
  )


@bot.message_handler(func=lambda message: True)
def download_tiktok(message):
  url = message.text.strip()

  if 'tiktok.com' not in url:
    bot.reply_to(message, '⚠️ الرجاء إرسال رابط تيك توك صالح.')
    return

  sent_msg = bot.reply_to(message, '⏳ جاري تحميل الفيديو، يرجى الانتظار...')

  try:
    api_url = f'https://tikwm.com/api/?url={url}&hd=1'
    response = requests.get(api_url).json()

    if response.get('code') == 0:
      video_data = response.get('data', {})
      video_url = video_data.get('hdplay') or video_data.get('play')

      if video_url:
        bot.delete_message(message.chat.id, sent_msg.message_id)
        bot.send_video(
            message.chat.id,
            video_url,
            caption='✨ تم التحميل بنجاح',
        )
      else:
        raise Exception('No video URL found')
    else:
      raise Exception('API returned error code')

  except Exception as e:
    print(f'Error: {e}')
    try:
      bot.edit_message_text(
          '❌ حدث خطأ أثناء التحميل. تأكد من صحة الرابط أو حاول لاحقاً.',
          message.chat.id,
          sent_msg.message_id,
      )
    except:
      bot.reply_to(
          message,
          '❌ حدث خطأ أثناء التحميل. تأكد من صحة الرابط أو حاول لاحقاً.',
      )


if __name__ == '__main__':
  print('Bot is running...')
  bot.infinity_polling()

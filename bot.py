import os
import requests
import telebot

TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
  bot.reply_to(
      message,
      'أهلاً بك يا أبو إياد! 👋\nأرسل لي رابط تيك توك وسأقوم بتحميله لك فوراً.',
  )


@bot.message_handler(func=lambda message: True)
def download_tiktok(message):
  url = message.text.strip()

  if 'tiktok.com' not in url:
    bot.reply_to(
        message, '⚠️ الرجاء إرسال رابط تيك توك صحيح يبدأ بـ http أو https.'
    )
    return

  sent_msg = bot.reply_to(message, '⏳ جاري تحميل الفيديو من تيك توك...')

  try:
    # استخدام API مجاني وسريع لجلب معلومات ورابط فيديو تيك توك
    api_url = f'https://tikwm.com/api/?url={url}'
    response = requests.get(api_url).json()

    if response.get('code') == 0:
      video_data = response['data']
      video_file_url = video_data['play']  # رابط الفيديو المباشر بدون علامة مائية

      # إرسال الفيديو مباشرة باستخدام رابطه المباشر عبر تليجرام
      bot.send_video(
          message.chat.id,
          video_file_url,
          caption=(
              '✅ تم التحميل بنجاح بواسطة بوت أبو إياد'
              f' 💎\n\n{video_data.get("title", "")}'
          ),
      )
      bot.delete_message(message.chat.id, sent_msg.message_id)
    else:
      raise Exception('API returned error code')

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

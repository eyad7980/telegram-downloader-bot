import os
import telebot
from yt_dlp import YoutubeDL

TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
  bot.reply_to(
      message,
      'أهلاً بك يا أبو إياد! 👋\nأرسل لي رابط الفيديو (تيك توك أو يوتيوب)'
      ' وسأقوم بتحميله لك فوراً.',
  )


@bot.message_handler(func=lambda message: True)
def download_video(message):
  url = message.text.strip()

  if not url.startswith('http'):
    bot.reply_to(message, '⚠️ الرجاء إرسال رابط صالح يبدأ بـ http أو https.')
    return

  sent_msg = bot.reply_to(message, '⏳ جاري جلب وتحميل الفيديو، يرجى الانتظار...')

  output_template = 'video_%(id)s.%(ext)s'

  ydl_opts = {
      'format': 'best',
      'outtmpl': output_template,
      'noplaylist': True,
  }

  try:
    with YoutubeDL(ydl_opts) as ydl:
      info = ydl.extract_info(url, download=True)
      filename = ydl.prepare_filename(info)

    # إرسال الفيديو للمستخدم
    with open(filename, 'rb') as video_file:
      bot.send_video(
          message.chat.id,
          video_file,
          caption='✅ تم التحميل بنجاح بواسطة بوت أبو إياد 💎',
          supports_streaming=True,
      )

    # تنظيف الملف من السيرفر
    if os.path.exists(filename):
      os.remove(filename)

    bot.delete_message(message.chat.id, sent_msg.message_id)

  except Exception as e:
    print(f'Error: {e}')
    # لو فشل التحميل كملف، نجرب نبعت رابط مباشر كخيار بديل سريع
    try:
      with YoutubeDL({'format': 'best', 'quiet': True}) as ydl:
        info = ydl.extract_info(url, download=False)
        direct_url = info.get('url')
        if direct_url:
          bot.delete_message(message.chat.id, sent_msg.message_id)
          bot.send_message(
              message.chat.id,
              f'📌 عذراً لم أتمكن من رفع الفيديو مباشرة، لكن يمكنك تحميله من'
              f' هذا الرابط المباشر:\n\n{direct_url}',
          )
          return
    except Exception as sub_e:
      print(f'Sub Error: {sub_e}')

    try:
      bot.edit_message_text(
          '❌ حدث خطأ أثناء التحميل. تأكد من صحة الرابط أو جرب رابطاً آخر.',
          message.chat.id,
          sent_msg.message_id,
      )
    except:
      bot.reply_to(
          message,
          '❌ حدث خطأ أثناء التحميل. تأكد من صحة الرابط أو جرب رابطاً آخر.',
      )


if __name__ == '__main__':
  print('Bot is running...')
  bot.infinity_polling()

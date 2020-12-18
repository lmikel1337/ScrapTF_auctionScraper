import telebot

from tg_bot import botConfig as config

bot = telebot.TeleBot(config.api_token)


@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id, 'This is an early build, use it at your own risk')


@bot.message_handler(commands=['start'])
def start_command(message):
    print(message.chat.id)


def new_notification(uid=398552364, notification_message=None):
    # I'm using a hardcoded uid only because I'm too lazy to implement a functional auth system
    print('Hello')
    if notification_message is not None:
        message_text = notification_message
    else:
        message_text = 'You have a new notification from Scrap.tf'
    bot.send_message(uid, message_text)

# bot.polling()
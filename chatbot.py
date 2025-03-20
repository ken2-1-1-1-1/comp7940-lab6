##chatbot.py
from telegram import Update
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, CallbackContext)
#The messageHandler is used for all meaasge updates
import configparser
import logging
import redis

from ChatGPT_HKBU import HKBU_ChatGPT

global redis1

def main():
    #Load your token and create an Updater for your bot
    config = configparser.ConfigParser()
    config.read('config.ini')
    updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context = True)
    dispatcher = updater.dispatcher

    global redis1
    redis1 = redis.Redis(host=(config['REDIS']['HOST']),
                         password=(config['REDIS']['PASSWORD']),
                         port=(config['REDIS']['REDISPORT']),\
                         decode_responses=(config['REDIS']['DECODE_RESPONSE']),
                         username=(config['REDIS']['USER_NAME']))
    
    # You can set this logging module,
    # So you will know when and why things do not work as expected
    logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s', level = logging.INFO)

    #register a dispatcher to handle message:
    #echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    #dispatcher.add_handler(echo_handler)

    #dispatcher for chatgpt
    global chatgpt
    chatgpt = HKBU_ChatGPT(config)
    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command),
                                     equiped_chatgpt)
    dispatcher.add_handler(chatgpt_handler)

    #on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("hello", hello))


    #To start the Bot:
    updater.start_polling()
    updater.idle()

def echo(update, context):
    reply_message = update.message.text.upper()
    logging.info("Update:" +str(update))
    logging.info("context:" + str(context))
    context.bot.send_message(chat_id = update.effective_chat.id, text=reply_message)

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Helping you helping you.')

def hello(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /hello is issued."""
    try:
        global redis1
        logging.info(context.args[0])
        msg = context.args[0]
        redis1.incr(msg)

        update.message.reply_text('Good day, ' + redis1.get(msg) + '.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /hello <keyword>')

def add(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    try:
        global redis1
        logging.info(context.args[0])
        msg = context.args[0]
        redis1.incr(msg)

        update.message.reply_text('You have said ' + msg + ' for ' + redis1.get(msg) + ' times.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')
        

def equiped_chatgpt(update, context):
    global chatgpt
    reply_message = chatgpt.submit(update.message.text)
    logging.info("Update: "+ str(Update))
    logging.info("Context: " + str(context))
    context.bot.send_message(chat_id = update.effective_chat.id, text = reply_message)


if __name__ == '__main__':
    main()
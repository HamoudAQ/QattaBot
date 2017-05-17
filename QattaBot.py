#!/usr/bin/env python

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import logging
import QattaDB

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    update.message.reply_text("Hi!")

def add(bot, update, args):
    CID = update.message.chat.id
    UID = update.message.from_user.id
    try:
        counter = float(args[0]);
        des = str(args[1]);
    except:
        update.message.reply_text("try again!")
        return
    try:
        QattaDB.User.create(user=UID,name=update.message.from_user.username)
        print("user created")
    except:
        print("user exists")
        pass
    try:
        QattaDB.Chat.create(chat=CID)
        print("chat created")
    except:
        print("chat exists")
        pass

    countQuery = QattaDB.Count.select().where((QattaDB.Count.user_id==UID) & (QattaDB.Count.chat_id==CID))
    entryQuery = QattaDB.Entry.create(user_id=UID,chat_id=CID,entry=counter,desc=des)

    if not countQuery: ##not found
        QattaDB.Count.create(user_id=UID,chat_id=CID,count=counter)
        update.message.reply_text("Current balance: "+str(counter)+" SAR")
    else: ##found
        countQuery[0].count+=counter
        countQuery[0].save()
        update.message.reply_text("Current balance: "+str(countQuery[0].count)+" SAR")

def wipeself(bot, update):
    CID = update.message.chat.id
    UID = update.message.from_user.id
    query = QattaDB.Count.select().where((QattaDB.Count.user_id==UID) & (QattaDB.Count.chat_id==CID))
    if not query: ##not found
        QattaDB.Count.create(user_id=UID,chat_id=CID,count=0)
    else: ##found
        query[0].count=0
        query[0].save()
    update.message.reply_text("Current balance: 0 SAR")
    #try:
    (QattaDB.Entry.delete().where((QattaDB.Entry.user_id==UID) & (QattaDB.Entry.chat_id==CID))).execute()
    #except:
    #    pass

def wipechat(bot, update):
    CID = update.message.chat.id
    UID = update.message.from_user.id
    query = QattaDB.Count.select().where(QattaDB.Count.chat_id==CID)
    if not query: ##not found
        update.message.reply_text("Nothing to wipe.")
        return
    for member in query:
        member.count=0
        member.save()
    try:
        (QattaDB.Entry.delete().where(QattaDB.Entry.chat_id==CID)).execute()
    except:
        pass
    listchat(bot,update)

def listself(bot, update):
    CID = update.message.chat.id
    UID = update.message.from_user.id

    query = QattaDB.Entry.select().where((QattaDB.Entry.user_id==UID) & (QattaDB.Entry.chat_id==CID))
    message = ""
    if not query:
        update.message.reply_text("No results.")
        return
    for member in query:
        message += str(member.entry)+" SAR: "+member.desc+"\n"
    update.message.reply_text(message)

def listmember(bot, update, args):
    CID = update.message.chat.id
    try:
        UID = QattaDB.User.get(name=args[0]).user
    except:
        update.message.reply_text("User doesn't exist in chat!")
        return

    query = QattaDB.Entry.select().where((QattaDB.Entry.user_id==UID) & (QattaDB.Entry.chat_id==CID))
    message = ""
    if not query:
        update.message.reply_text("No results.")
        return
    for member in query:
        message += str(member.entry)+" SAR: "+member.desc+"\n"
    update.message.reply_text(message)

def listchat(bot, update):
    CID = update.message.chat.id
    query = QattaDB.Count.select().where(QattaDB.Count.chat_id==CID)
    message = ""
    if not query:
        update.message.reply_text("No results.")
        return
    for member in query:
        name = QattaDB.User.get(QattaDB.User.user==member.user_id).name
        message += name+"'s balance: "+str(member.count)+" SAR\n"
    update.message.reply_text(message)

def help(bot, update):
    update.message.reply_text("I've got nothing to say.")

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater("270579648:AAHoc3yC2fevhKn7H211ZDOrEGtSslmEN0E")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("add", add, pass_args=True))
    dp.add_handler(CommandHandler("wipeself", wipeself))
    dp.add_handler(CommandHandler("wipechat", wipechat))
    dp.add_handler(CommandHandler("listself", listself))
    dp.add_handler(CommandHandler("listchat", listchat))
    dp.add_handler(CommandHandler("listmember", listmember, pass_args=True))

    # on noncommand i.e message - echo the message on Telegram
    #dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()

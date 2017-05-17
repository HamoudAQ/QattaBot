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
    update.message.reply_text("""
        Hello There!
This is QattaBot, I'm going to count all the expenses of this group for each member.


[+]How to add expense:
    /add Value Description
    For example: /add 200 dinner


[+]How to view the expenses you have recorded
    /listself


[+]How to view the expenses that one of group members have recorded
    /listmember user
    For example: /listmember @Hamoud


[+]Wipe your records
    /wipeself

And there's more great commands waiting for ya.
        
        Devs:
            @HamoudAQ
            @jgjc222

        """)

    try:
        QattaDB.Chat.create(chat=CID)
        print("chat created")#debugging
    except:
        print("chat exists")#debugging
        pass

def add(bot, update, args):
    CID = update.message.chat.id
    UID = update.message.from_user.id
    try:
        value = float(args[0])#First argument is the value of the expense
        des = args[1];##Second argument is the description of the expense
    except:
        update.message.reply_text("data format is incorrect!")
        return
    
    #we can eliminate this by moving it to start() and add all users at once, but what if somebody join after /start?...
    try:
        QattaDB.User.create(user=UID,name=update.message.from_user.username)
    except:
        print("user exists") #debugging
    

    countQuery = QattaDB.Count.select().where((QattaDB.Count.user_id==UID) & (QattaDB.Count.chat_id==CID))
    entryQuery = QattaDB.Entry.create(user_id=UID,chat_id=CID,entry=value,desc=des)


    #we can optimize the next block, but we are lazy to do so...
    if not countQuery: #User has no balance for a particular chat
        QattaDB.Count.create(user_id=UID,chat_id=CID,count=value) #create balance for the user
        update.message.reply_text("Current balance: "+str(value)+" SAR") #you can change the currency from SAR to whatever you want...
    else: #User already has a balance
        countQuery[0].count+=value
        countQuery[0].save()
        update.message.reply_text("Current balance: "+str(countQuery[0].count)+" SAR") #you can change the currency from SAR to whatever you want...

def wipeself(bot, update):
    CID = update.message.chat.id
    UID = update.message.from_user.id
    query = QattaDB.Count.select().where((QattaDB.Count.user_id==UID) & (QattaDB.Count.chat_id==CID))
    if query: #if he had a balance to be wiped!
        query[0].count=0
        query[0].save()
        (QattaDB.Entry.delete().where((QattaDB.Entry.user_id==UID) & (QattaDB.Entry.chat_id==CID))).execute() #this will eliminate all the associated entries!
    

    update.message.reply_text("Current balance: 0 SAR")



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
        userWithNoAt=args[0].replace("@","")

        UID = QattaDB.User.get(name=userWithNoAt).user
    except:
        update.message.reply_text("User doesn't exist in chat or have not added any expenses!")
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
    update.message.reply_text(
"""
        Hello There!
This is QattaBot, I'm going to count all the expenses of this group for each member.


[+]How to add expense:
    /add Value Description
    For example: /add 200 dinner


[+]How to view the expenses you have recorded
    /listself


[+]How to view the expenses that one of group members have recorded
    /listmember user
    For example: /listmember @Hamoud


[+]Wipe your records
    /wipeself

And there's more great commands waiting for ya.
        
        Devs:
            @HamoudAQ
            @jgjc222

        """)

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater("TOKEN")

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

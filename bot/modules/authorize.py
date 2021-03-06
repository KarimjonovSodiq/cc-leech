from bot import AUTHORIZED_CHATS, SUDO_USERS, dispatcher, DB_URI
from bot.helper.telegram_helper.message_utils import sendMessage
from telegram.ext import CommandHandler
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.ext_utils.db_handler import DbManger


def authorize(update, context):
    reply_message = None
    message_ = None
    reply_message = update.message.reply_to_message
    message_ = update.message.text.split(' ')
    if len(message_) == 2:
        user_id = int(message_[1])
        if user_id in AUTHORIZED_CHATS:
            msg = 'Foydalanuvchi allaqachon qabul qilingan!'
        elif DB_URI is not None:
            msg = DbManger().user_auth(user_id)
            AUTHORIZED_CHATS.add(user_id)
        else:
            AUTHORIZED_CHATS.add(user_id)
            with open('authorized_chats.txt', 'a') as file:
                file.write(f'{user_id}\n')
                msg = 'Foydalanuvchi qabu qilindi'
    elif reply_message is None:
        # Trying to authorize a chat
        chat_id = update.effective_chat.id
        if chat_id in AUTHORIZED_CHATS:
            msg = 'Chat allaqachon qabul qilingan!'
        elif DB_URI is not None:
            msg = DbManger().user_auth(chat_id)
            AUTHORIZED_CHATS.add(chat_id)
        else:
            AUTHORIZED_CHATS.add(chat_id)
            with open('authorized_chats.txt', 'a') as file:
                file.write(f'{chat_id}\n')
                msg = 'Chat qabul qilindi'
    else:
        # Trying to authorize someone by replying
        user_id = reply_message.from_user.id
        if user_id in AUTHORIZED_CHATS:
            msg = 'Foydalanuvchi allaqachon qabul qilingan!'
        elif DB_URI is not None:
            msg = DbManger().user_auth(user_id)
            AUTHORIZED_CHATS.add(user_id)
        else:
            AUTHORIZED_CHATS.add(user_id)
            with open('authorized_chats.txt', 'a') as file:
                file.write(f'{user_id}\n')
                msg = 'Foydalanuchi qabul qilindi'
    sendMessage(msg, context.bot, update)

def unauthorize(update, context):
    reply_message = None
    message_ = None
    reply_message = update.message.reply_to_message
    message_ = update.message.text.split(' ')
    if len(message_) == 2:
        user_id = int(message_[1])
        if user_id in AUTHORIZED_CHATS:
            if DB_URI is not None:
                msg = DbManger().user_unauth(user_id)
            else:
                msg = 'Foydalanuvchi rad etildi'
            AUTHORIZED_CHATS.remove(user_id)
        else:
            msg = 'Foydalanuvchi allaqachon rad etilgan!'
    elif reply_message is None:
        # Trying to unauthorize a chat
        chat_id = update.effective_chat.id
        if chat_id in AUTHORIZED_CHATS:
            if DB_URI is not None:
                msg = DbManger().user_unauth(chat_id)
            else:
                msg = 'Chat rad etildi'
            AUTHORIZED_CHATS.remove(chat_id)
        else:
            msg = 'Chat allaqachon rad etilgan!'
    else:
        # Trying to authorize someone by replying
        user_id = reply_message.from_user.id
        if user_id in AUTHORIZED_CHATS:
            if DB_URI is not None:
                msg = DbManger().user_unauth(user_id)
            else:
                msg = 'Foydalanuchi rad etildi'
            AUTHORIZED_CHATS.remove(user_id)
        else:
            msg = 'Foydalanuvchi allaqachon rad etilgan!'
    if DB_URI is None:
        with open('authorized_chats.txt', 'a') as file:
            file.truncate(0)
            for i in AUTHORIZED_CHATS:
                file.write(f'{i}\n')
    sendMessage(msg, context.bot, update)

def addSudo(update, context):
    reply_message = None
    message_ = None
    reply_message = update.message.reply_to_message
    message_ = update.message.text.split(' ')
    if len(message_) == 2:
        user_id = int(message_[1])
        if user_id in SUDO_USERS:
            msg = 'Allaqachon admin'
        elif DB_URI is not None:
            msg = DbManger().user_addsudo(user_id)
            SUDO_USERS.add(user_id)
        else:
            SUDO_USERS.add(user_id)
            with open('sudo_users.txt', 'a') as file:
                file.write(f'{user_id}\n')
                msg = 'Admin sifatida tayinlash'
    elif reply_message is None:
        msg = "Tayinlamoqchi bo`lganingizni ID si yoki Yuborilgan habarini yuboring."
    else:
        # Trying to authorize someone by replying
        user_id = reply_message.from_user.id
        if user_id in SUDO_USERS:
            msg = 'Allaqachon admin!'
        elif DB_URI is not None:
            msg = DbManger().user_addsudo(user_id)
            SUDO_USERS.add(user_id)
        else:
            SUDO_USERS.add(user_id)
            with open('sudo_users.txt', 'a') as file:
                file.write(f'{user_id}\n')
                msg = 'Admin qilib tayinlash'
    sendMessage(msg, context.bot, update)

def removeSudo(update, context):
    reply_message = None
    message_ = None
    reply_message = update.message.reply_to_message
    message_ = update.message.text.split(' ')
    if len(message_) == 2:
        user_id = int(message_[1])
        if user_id in SUDO_USERS:
            if DB_URI is not None:
                msg = DbManger().user_rmsudo(user_id)
            else:
                msg = 'Ozod qilindi'
            SUDO_USERS.remove(user_id)
        else:
            msg = 'Ozod qilishga adminlar yo`q!'
    elif reply_message is None:
        msg = "O`chirmoqchi bo`lgan Admingizni idsini bering"
    else:
        user_id = reply_message.from_user.id
        if user_id in SUDO_USERS:
            if DB_URI is not None:
                msg = DbManger().user_rmsudo(user_id)
            else:
                msg = 'Ozod qilingan'
            SUDO_USERS.remove(user_id)
        else:
            msg = 'Not sudo user to demote!'
    if DB_URI is None:
        with open('sudo_users.txt', 'a') as file:
            file.truncate(0)
            for i in SUDO_USERS:
                file.write(f'{i}\n')
    sendMessage(msg, context.bot, update)

def sendAuthChats(update, context):
    user = sudo = ''
    user += '\n'.join(f"<code>{uid}</code>" for uid in AUTHORIZED_CHATS)
    sudo += '\n'.join(f"<code>{uid}</code>" for uid in SUDO_USERS)
    sendMessage(f'<b><u>Authorized Chats:</u></b>\n{user}\n<b><u>Sudo Users:</u></b>\n{sudo}', context.bot, update)


send_auth_handler = CommandHandler(command=BotCommands.AuthorizedUsersCommand, callback=sendAuthChats,
                                    filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
authorize_handler = CommandHandler(command=BotCommands.AuthorizeCommand, callback=authorize,
                                    filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
unauthorize_handler = CommandHandler(command=BotCommands.UnAuthorizeCommand, callback=unauthorize,
                                    filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
addsudo_handler = CommandHandler(command=BotCommands.AddSudoCommand, callback=addSudo,
                                    filters=CustomFilters.owner_filter, run_async=True)
removesudo_handler = CommandHandler(command=BotCommands.RmSudoCommand, callback=removeSudo,
                                    filters=CustomFilters.owner_filter, run_async=True)

dispatcher.add_handler(send_auth_handler)
dispatcher.add_handler(authorize_handler)
dispatcher.add_handler(unauthorize_handler)
dispatcher.add_handler(addsudo_handler)
dispatcher.add_handler(removesudo_handler)

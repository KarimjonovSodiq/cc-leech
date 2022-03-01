import signal

from os import path as ospath, remove as osremove, execl as osexecl
from subprocess import run as srun
from psutil import disk_usage, cpu_percent, swap_memory, cpu_count, virtual_memory, net_io_counters, Process as psprocess
from time import time
from pyrogram import idle
from sys import executable
from telegram import ParseMode, InlineKeyboardMarkup
from telegram.ext import CommandHandler

from bot import bot, app, dispatcher, updater, botStartTime, IGNORE_PENDING_REQUESTS, PORT, alive, web, OWNER_ID, AUTHORIZED_CHATS, LOGGER, Interval, rss_session, a2c
from .helper.ext_utils.fs_utils import start_cleanup, clean_all, exit_clean_up
from .helper.telegram_helper.bot_commands import BotCommands
from .helper.telegram_helper.message_utils import sendMessage, sendMarkup, editMessage, sendLogFile
from .helper.ext_utils.telegraph_helper import telegraph
from .helper.ext_utils.bot_utils import get_readable_file_size, get_readable_time
from .helper.telegram_helper.filters import CustomFilters
from .helper.telegram_helper.button_build import ButtonMaker
from .modules import authorize, list, cancel_mirror, mirror_status, mirror, clone, watch, shell, eval, delete, speedtest, count, leech_settings, search, rss


def stats(update, context):
    currentTime = get_readable_time(time() - botStartTime)
    total, used, free, disk= disk_usage('/')
    total = get_readable_file_size(total)
    used = get_readable_file_size(used)
    free = get_readable_file_size(free)
    sent = get_readable_file_size(net_io_counters().bytes_sent)
    recv = get_readable_file_size(net_io_counters().bytes_recv)
    cpuUsage = cpu_percent(interval=0.5)
    p_core = cpu_count(logical=False)
    t_core = cpu_count(logical=True)
    swap = swap_memory()
    swap_p = swap.percent
    swap_t = get_readable_file_size(swap.total)
    swap_u = get_readable_file_size(swap.used)
    memory = virtual_memory()
    mem_p = memory.percent
    mem_t = get_readable_file_size(memory.total)
    mem_a = get_readable_file_size(memory.available)
    mem_u = get_readable_file_size(memory.used)
    stats = f'<b>Botning Hizmat vaqti:</b> {currentTime}\n\n'\
            f'<b>Jami Hotira:</b> {total}\n'\
            f'<b>Band:</b> {used} | <b>Boʻsh:</b> {free}\n\n'\
            f'<b>Upload:</b> {sent}\n'\
            f'<b>Download:</b> {recv}\n\n'\
            f'<b>CPU:</b> {cpuUsage}%\n'\
            f'<b>RAM:</b> {mem_p}%\n'\
            f'<b>DISK:</b> {disk}%\n\n'\
            f'<b>Physical Cores:</b> {p_core}\n'\
            f'<b>Jami  Core lar:</b> {t_core}\n\n'\
            f'<b>SWAP:</b> {swap_t} | <b>Used:</b> {swap_p}%\n'\
            f'<b>Jami Hotira:</b> {mem_t}\n'\
            f'<b>Bos`sh Hotira:</b> {mem_a}\n'\
            f'<b>Egallangan Hotira:</b> {mem_u}\n'
    sendMessage(stats, context.bot, update)


def start(update, context):
    buttons = ButtonMaker()
    buttons.buildbutton("Repo", "https://www.github.com/KarimjonovSodiq/cc-leech")
    buttons.buildbutton("Report Group", "https://t.me/cc_support")
    reply_markup = InlineKeyboardMarkup(buttons.build_menu(2))
    if CustomFilters.authorized_user(update) or CustomFilters.authorized_chat(update):
        start_string = f'''
Bu bot sizning havolangizni Goodle Drivega yulab berishi mumkin!
Malum komandalarni ko`rish uchun /{BotCommands.HelpCommand} ni yuboring
'''
        sendMarkup(start_string, context.bot, update, reply_markup)
    else:
        sendMarkup('Kutilmagan Mehmon, O`zingizning cc-leech botingizni yarating', context.bot, update, reply_markup)

def restart(update, context):
    restart_message = sendMessage("Qayta yuklanyapti...", context.bot, update)
    if Interval:
        Interval[0].cancel()
    alive.kill()
    procs = psprocess(web.pid)
    for proc in procs.children(recursive=True):
        proc.kill()
    procs.kill()
    clean_all()
    srun(["python3", "update.py"])
    a2cproc = psprocess(a2c.pid)
    for proc in a2cproc.children(recursive=True):
        proc.kill()
    a2cproc.kill()
    with open(".restartmsg", "w") as f:
        f.truncate(0)
        f.write(f"{restart_message.chat.id}\n{restart_message.message_id}\n")
    osexecl(executable, executable, "-m", "bot")


def ping(update, context):
    start_time = int(round(time() * 1000))
    reply = sendMessage("Ping", context.bot, update)
    end_time = int(round(time() * 1000))
    editMessage(f'{end_time - start_time} ms', reply)


def log(update, context):
    sendLogFile(context.bot, update)


help_string_telegraph = f'''<br>
<b>/{BotCommands.HelpCommand}</b>: To get this message
<br><br>
<b>/{BotCommands.MirrorCommand}</b> [download_url][magnet_link]: Linkingizni Google Drive ga yuklashni boshlang . <b>/{BotCommands.MirrorCommand}</b>komandasini yubiring!
<br><br>
<b>/{BotCommands.ZipMirrorCommand}</b> [download_url][magnet_link]: Start mirroring and upload the file/folder compressed with zip extension
<br><br>
<b>/{BotCommands.UnzipMirrorCommand}</b> [download_url][magnet_link]: Start mirroring and upload the file/folder extracted from any archive extension
<br><br>
<b>/{BotCommands.QbMirrorCommand}</b> [magnet_link][torrent_file][torrent_file_url]: Start Mirroring using qBittorrent, Use <b>/{BotCommands.QbMirrorCommand} s</b> to select files before downloading
<br><br>
<b>/{BotCommands.QbZipMirrorCommand}</b> [magnet_link][torrent_file][torrent_file_url]: Start mirroring using qBittorrent and upload the file/folder compressed with zip extension
<br><br>
<b>/{BotCommands.QbUnzipMirrorCommand}</b> [magnet_link][torrent_file][torrent_file_url]: Start mirroring using qBittorrent and upload the file/folder extracted from any archive extension
<br><br>
<b>/{BotCommands.LeechCommand}</b> [download_url][magnet_link]: Start leeching to Telegram, Use <b>/{BotCommands.LeechCommand} s</b> to select files before leeching
<br><br>
<b>/{BotCommands.ZipLeechCommand}</b> [download_url][magnet_link]: Start leeching to Telegram and upload the file/folder compressed with zip extension
<br><br>
<b>/{BotCommands.UnzipLeechCommand}</b> [download_url][magnet_link][torent_file]: Start leeching to Telegram and upload the file/folder extracted from any archive extension
<br><br>
<b>/{BotCommands.QbLeechCommand}</b> [magnet_link][torrent_file][torrent_file_url]: Start leeching to Telegram using qBittorrent, Use <b>/{BotCommands.QbLeechCommand} s</b> to select files before leeching
<br><br>
<b>/{BotCommands.QbZipLeechCommand}</b> [magnet_link][torrent_file][torrent_file_url]: Start leeching to Telegram using qBittorrent and upload the file/folder compressed with zip extension
<br><br>
<b>/{BotCommands.QbUnzipLeechCommand}</b> [magnet_link][torrent_file][torrent_file_url]: Start leeching to Telegram using qBittorrent and upload the file/folder extracted from any archive extension
<br><br>
<b>/{BotCommands.CloneCommand}</b> [drive_url][gdtot_url]: Copy file/folder to Google Drive
<br><br>
<b>/{BotCommands.CountCommand}</b> [drive_url][gdtot_url]: Count file/folder of Google Drive
<br><br>
<b>/{BotCommands.DeleteCommand}</b> [drive_url]: Delete file/folder from Google Drive (Only Owner & Sudo)
<br><br>
<b>/{BotCommands.WatchCommand}</b> [yt-dlp supported link]: Mirror yt-dlp supported link. Send <b>/{BotCommands.WatchCommand}</b> for more help
<br><br>
<b>/{BotCommands.ZipWatchCommand}</b> [yt-dlp supported link]: Mirror yt-dlp supported link as zip
<br><br>
<b>/{BotCommands.LeechWatchCommand}</b> [yt-dlp supported link]: Leech yt-dlp supported link
<br><br>
<b>/{BotCommands.LeechZipWatchCommand}</b> [yt-dlp supported link]: Leech yt-dlp supported link as zip
<br><br>
<b>/{BotCommands.LeechSetCommand}</b>: Leech sozlamalari
<br><br>
<b>/{BotCommands.SetThumbCommand}</b>:Faylning sarlavhasiga qoyiladigan rasmni belgilang
<br><br>
<b>/{BotCommands.RssListCommand}</b>: List all subscribed rss feed info
<br><br>
<b>/{BotCommands.RssGetCommand}</b>: [Title] [Number](last N links): Force fetch last N links
<br><br>
<b>/{BotCommands.RssSubCommand}</b>: [Title] [Rss Link] f: [filter]: Subscribe new rss feed
<br><br>
<b>/{BotCommands.RssUnSubCommand}</b>: [Title]: Unubscribe rss feed by title
<br><br>
<b>/{BotCommands.RssUnSubAllCommand}</b>: Remove all rss feed subscriptions
<br><br>
<b>/{BotCommands.CancelMirror}</b>: Reply to the message by which the download was initiated and that download will be cancelled
<br><br>
<b>/{BotCommands.CancelAllCommand}</b>: Barcha yuklash vazifalarini to`xtatish
<br><br>
<b>/{BotCommands.ListCommand}</b> [query]: Google Drivedan qidirish(s)
<br><br>
<b>/{BotCommands.SearchCommand}</b> [query]: Torrentlarni API orqali qidirish
<br>sites: <code>rarbg, 1337x, yts, etzv, tgx, torlock, piratebay, nyaasi, ettv</code><br><br>
<b>/{BotCommands.StatusCommand}</b>: Shows a status of all the downloads
<br><br>
<b>/{BotCommands.StatsCommand}</b>: Bot holatini ko`rsatish 
'''

help = telegraph.create_page(
        title='Mirror-Leech-Bot Help',
        content=help_string_telegraph,
    )["path"]

help_string = f'''
/{BotCommands.PingCommand}: Pingni tekshirish

/{BotCommands.AuthorizeCommand}: Botga  chat va admin qo`shish  (ID kiriting)

/{BotCommands.UnAuthorizeCommand}: Botdan  chat va adminlarni ozod qilish (ID)

/{BotCommands.AuthorizedUsersCommand}: Ro`yxatdan o`tgan adminlar (Yaratuvchi va adminlar)

/{BotCommands.AddSudoCommand}: Admin qo`shish (Yaratuvchi)

/{BotCommands.RmSudoCommand}: Adminni ozod qilish (Yaratuvchi)

/{BotCommands.RestartCommand}: Botni qayta yuklash

/{BotCommands.LogCommand}: Log faylni olish

/{BotCommands.SpeedCommand}: Hostdagi internet tezligini o`lchash

/{BotCommands.ShellCommand}: Shellda buyruqlarni ishlatish (Yaratuvchi)

/{BotCommands.ExecHelpCommand}:  Executor module haqida yordam olish (Yaratuvchi)
'''

def bot_help(update, context):
    button = ButtonMaker()
    button.buildbutton("Boshqa Buyruqlar", f"https://telegra.ph/{help}")
    reply_markup = InlineKeyboardMarkup(button.build_menu(1))
    sendMarkup(help_string, context.bot, update, reply_markup)

botcmds = [

        (f'{BotCommands.MirrorCommand}', 'Mirror'),
        (f'{BotCommands.ZipMirrorCommand}','Mirror va arxiv kurinishida yuklash'),
        (f'{BotCommands.UnzipMirrorCommand}','Mirror va arxivni ochish'),
        (f'{BotCommands.QbMirrorCommand}','qBittorrent orqali torrent faylni miror qilish'),
        (f'{BotCommands.QbZipMirrorCommand}','Torrentni mirror qilish va qb orqali arxiv ko`rinishida yuklash'),
        (f'{BotCommands.QbUnzipMirrorCommand}','Torrentni mirror qilish va qb orqali arxivni ochib yuklash'),
        (f'{BotCommands.WatchCommand}','yt-dlp qabul qiladigan havolalarni mirror qilish '),
        (f'{BotCommands.ZipWatchCommand}','yt-dlp qabul qiladigan havolalarni arxivlab mirror qilish '),
        (f'{BotCommands.CloneCommand}','Drive ga fayl/papka ni nusxalash'),
        (f'{BotCommands.LeechCommand}','Leech'),
        (f'{BotCommands.ZipLeechCommand}','Leech qilish va arxiv ko`rinishida saqlash '),
        (f'{BotCommands.UnzipLeechCommand}','Leech qilish va arxivni ochish'),
        (f'{BotCommands.QbLeechCommand}','qBittorrent orqali torrent fayllarni Leech qilish '),
        (f'{BotCommands.QbZipLeechCommand}','qb orqali  torrent fayllarni arxiv ko`rinishida Leech qilish'),
        (f'{BotCommands.QbUnzipLeechCommand}','qb orqali Torrent faylarni arxivdan ochib leech qilish'),
        (f'{BotCommands.LeechWatchCommand}','yt-dlp qabul qiladigan havolalarni Leech qilish '),
        (f'{BotCommands.LeechZipWatchCommand}','yt-dlp qabul qiladigan havolarni arxiv ko`rinishda  Leech qilish '),
        (f'{BotCommands.CountCommand}','Drive dagi fayl/Papka lar sonini sanash'),
        (f'{BotCommands.DeleteCommand}','Drive dan fayl/papka larni o`chirish '),
        (f'{BotCommands.CancelMirror}','Vazifalarni rad etish '),
        (f'{BotCommands.CancelAllCommand}','Barcha yuklab olinayotgan vazifalarni rad etish '),
        (f'{BotCommands.ListCommand}','Drive dan qidirish '),
        (f'{BotCommands.LeechSetCommand}','Leech sozlamalari'),
        (f'{BotCommands.SetThumbCommand}','Sarlavha rasmini joriy etish '),
        (f'{BotCommands.StatusCommand}','Mirror holatini ko`rsatish '),
        (f'{BotCommands.StatsCommand}','Foydalanish holati'),
        (f'{BotCommands.PingCommand}','Ping'),
        (f'{BotCommands.RestartCommand}','Botni qayta ishga tushurish'),
        (f'{BotCommands.LogCommand}','Log faylni olish '),
        (f'{BotCommands.HelpCommand}','Yordam')
    ]

def main():
    # bot.set_my_commands(botcmds)
    start_cleanup()
    # Check if the bot is restarting
    if ospath.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
        bot.edit_message_text("Qayta yuklanish muvaffaqiyatli bo`ldi!", chat_id, msg_id)
        osremove(".restartmsg")
    elif OWNER_ID:
        try:
            text = "<b>Bot Restarted!</b>"
            bot.sendMessage(chat_id=OWNER_ID, text=text, parse_mode=ParseMode.HTML)
            if AUTHORIZED_CHATS:
                for i in AUTHORIZED_CHATS:
                    bot.sendMessage(chat_id=i, text=text, parse_mode=ParseMode.HTML)
        except Exception as e:
            LOGGER.warning(e)

    start_handler = CommandHandler(BotCommands.StartCommand, start, run_async=True)
    ping_handler = CommandHandler(BotCommands.PingCommand, ping,
                                  filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    restart_handler = CommandHandler(BotCommands.RestartCommand, restart,
                                     filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
    help_handler = CommandHandler(BotCommands.HelpCommand,
                                  bot_help, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    stats_handler = CommandHandler(BotCommands.StatsCommand,
                                   stats, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    log_handler = CommandHandler(BotCommands.LogCommand, log, filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(ping_handler)
    dispatcher.add_handler(restart_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(stats_handler)
    dispatcher.add_handler(log_handler)
    updater.start_polling(drop_pending_updates=IGNORE_PENDING_REQUESTS)
    LOGGER.info("Bot Started!")
    signal.signal(signal.SIGINT, exit_clean_up)
    if rss_session is not None:
        rss_session.start()

app.start()
main()
idle()

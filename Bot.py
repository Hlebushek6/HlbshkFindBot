from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from googlesearch import search
import vk_api
from googleapiclient.discovery import build
from Bot_config import bot_token, vk_token, youtube_token

bot = Bot(token = bot_token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

session = vk_api.VkApi(token = vk_token)
vk = session.get_api()

yt = build('youtube', 'v3', developerKey=youtube_token)

found_urls = []
found_accs = []
found = []

def accSearch(url):
    if "tiktok.com/@" in url and url not in found_urls:
        found_urls.append(url)
        if "TikTok" not in found_accs:
            found_accs.append("TikTok")
    elif "vk.com" in url and url not in found_urls:
        found_urls.append(url)
        res = vksearch(url[15:])
        if "VK" not in found_accs and res:
            found_accs.append("VK")
    elif ("youtube.com/channel" in url or "youtube.com/@" in url) and url not in found_urls:
        found_urls.append(url)
        if '/channel/' in url:
            youtubesearch(url[32:])
        else:
            youtubesearch(yt.search().list(part = 'snippet', q = msg[25:], maxResults = 1, type = 'channel').execute()['items'][0]['id']['channelId'])
        if "YouTube" not in found_accs:
            found_accs.append('YouTube')

def vksearch(id):
    try:
        info = session.method("users.get", {"user_ids": id, "fields": "bdate, city, contacts, country, home_town, occupation, relatives, relation, sex, site", "name_case": "nom"})
        if info[0]["is_closed"]:
            return False
        if "sex" in info[0] and "пол" not in found:
            found.append("пол")
        if "bdate" in info[0] and info[0]["bdate"] != "" and "день рождения" not in found:
            found.append("день рождения")
        if "home_town" in info[0] and info[0]["home_town"] != "" and "родной город" not in found:
            found.append("родной город")
        if "city" in info[0] and info[0]["city"] != "" and "город" not in found:
            found.append("город")
        if "country" in info[0] and info[0]["country"] != "" and "страна" not in found:
            found.append("страна")
        if "occupation" in info[0] and info[0]["occupation"] != "" and "текущее место работы/учёбы" not in found:
            found.append("текущее место работы/учёбы")
        if "mobile_phone" in info[0] and info[0]["mobile_phone"] != "" and "телефон" not in found:
            found.append("телефон")
        if "site" in info[0] and info[0]["site"] != "" and "сайт" not in found:
            found.append("сайт")
        if "relation" in info[0] and "семейное положение" not in found:
            found.append("семейное положение")
        if "relation_partner" in info[0] and "партнёр" not in found:
            found.append("партнёр")
        if "relatives" in info[0] and len(info[0]["relatives"]) != 0 and "родственники" not in found:
            found.append("родственники")
        for i in search(info[0]["first_name"] + info[0]["last_name"], num = 5, stop = 5, pause = 2, lang = "ru"):
            accSearch(i)
        for i in search(id, num = 5, stop = 5, pause = 2, lang = "ru"):
            accSearch(i)
        try:
            ytid = yt.search().list(part = 'snippet', q = '@' + id, maxResults = 1, type = 'channel').execute()['items'][0]['id']['channelId']
        except:
            ytid = ""
        if 'https://www.youtube.com/channel/' + ytid not in found_urls and 'https://www.youtube.com/@' + id not in found_urls:
            res = youtubesearch(ytid)
            if res:
                found_urls.append('https://www.youtube.com/channel/' + ytid)
                found_urls.append('https://www.youtube.com/@' + id)
                if 'YouTube' not in found_accs:
                    found_accs.append('YouTube')
        return True
    except:
        return False

def youtubesearch(id):
    try:
        res = yt.channels().list(part = 'brandingSettings', id = id).execute()
        if 'country' in res['items'][0]['brandingSettings']['channel'] and "страна" not in found:
            found.append("страна")
        for i in search(res['items'][0]['brandingSettings']['channel']['title'], num = 5, stop = 5, pause = 2, lang = "ru"):
            accSearch(i)
        res = yt.channels().list(part = 'snippet', id = id).execute()
        custom = res['items'][0]['snippet']['customUrl']
        for i in search(custom[1:], num = 5, stop = 5, pause = 2, lang = 'ru'):
            accSearch(i)
        if "https://vk.com/" + custom[1:] not in found_urls:
            res = vksearch(custom[1:])
            if 'VK' not in found_accs and res:
                found_accs.append('VK')
            if res:
                found_urls.append("https://vk.com/" + custom[1:])
        return True
    except:
        return False



@dp.message_handler(commands = ['start'])
async def start(message: types.Message):
    await bot.send_message(message.from_user.id, "Привет! \nС помощью этого бота можно узнать, какую информацию о тебе могут получить из открытого доступа мошенники\nЭто позволит узнать, можно ли с легкостью найти о тебе то, что ты не хочешь, чтобы о тебе знали, и убрать это из открытого доступа\nК тому же, бот не собирает информацию о своих пользователях и имеет открытый исходный код!!\n/help - Все команды")

@dp.message_handler(commands = ['help'])
async def help(message: types.Message):
    await bot.send_message(message.from_user.id, "/start - Запустить бота \n\n/vk - Поиск по ВК.\nИспользование: /vk [ссылка на ВК или ID пользователя] (Страница должна быть открыта)\n\n/tiktok - Поиск по ТикТоку\nИспользование: /tiktok [ссылка на ТикТок или ID пользователя]\n\n/youtube - Поиск по ЮТубу\nИспользование: /youtube [ссылка на ЮТуб или ID пользователя] (Для корректной работы желательно указывать ссылку вида youtube.com/channel/)\n\n/source - Исходный код бота\n\n/help - Помощь по командам")

@dp.message_handler(commands = ['source'])
async def souce(message: types.Message):
    button = InlineKeyboardMarkup().add(InlineKeyboardButton("Ссылка на Github", url = "https://github.com/Hlebushek6/HlbshkFindBot"))
    await message.reply("Исходный код бота доступен на GitHub по ссылке ниже", reply_markup = button)

@dp.message_handler(commands=['vk'])
async def vk(message: types.Message):
    waitmsg = await bot.send_message(message.from_user.id, "Идёт поиск...")
    msg = message.text[4:]
    i = msg.rfind('/') + 1
    id = msg[i:]
    found_urls.append("https://vk.com/" + id)
    found_accs.append("VK")
    res = vksearch(id)
    if res:
        reply = "Найдены следующие данные: "
        for i in found:
            reply += i + ", "
        reply = reply[:len(reply) - 2]
        if len(found_accs) > 1:
            reply += "\nТакже найдены страницы в следующих соц. сетях: "
            found_accs.remove("VK")
            for i in found_accs:
                reply += i + ", "
            reply = reply[:len(reply) - 2]
        await bot.edit_message_text(text = reply, chat_id = message.from_user.id, message_id = waitmsg.message_id)
    else:
        await bot.edit_message_text(text = "Произошла ошибка, проверьте id/ссылку и повторите попытку", chat_id = message.from_user.id, message_id = waitmsg.message_id)
    found.clear()
    found_urls.clear()
    found_accs.clear()

@dp.message_handler(commands = ['tiktok'])
async def tiktok(message: types.Message):
    waitmsg = await bot.send_message(message.from_user.id, "Идёт поиск...")
    msg = message.text[8:]
    i = msg.rfind('@') + 1
    id = msg[i:]
    found_urls.append('https://www.tiktok.com/@' + id)
    found_accs.append('TikTok')
    res = vksearch(id)
    if res and 'VK' not in found_accs:
        found_accs.append('VK')
    if res and "https://vk.com/" + id not in found_urls:
        found_urls.append("https://vk.com/" + id)
    try:
        ytid = yt.search().list(part = 'snippet', q = '@' + id, maxResults = 1, type = 'channel').execute()['items'][0]['id']['channelId']
    except:
        ytid = id
    res = youtubesearch(ytid)
    if res and 'YouTube' not in found_accs:
        found_accs.append('YouTube')
    if res and "https://www.youtube.com/channel/" + ytid not in found_urls:
        found_urls.append("https://www.youtube.com/channel/" + ytid)
    if res and "https://www.youtube.com/@" + id not in found_urls:
        found_urls.append("https://www.youtube.com/@" + id)
    for i in search(id, num = 10, stop = 10, pause = 2, lang = "ru"):
        accSearch(i)
    if len(found) > 0:
        reply = "Найдены следующие данные: "
        for i in found:
            reply += i + ', '
        reply = reply[:len(reply) - 2] + '\nТакже найдены страницы в следующих соц. сетях: '
        found_accs.remove('TikTok')
        for i in found_accs:
            reply += i + ', '
        reply = reply[:len(reply) - 2]
        await bot.edit_message_text(text = reply, chat_id = message.from_user.id, message_id = waitmsg.message_id)
    else:
        await bot.edit_message_text(text = "Ничего не найдено!", chat_id = message.from_user.id, message_id = waitmsg.message_id)
    found.clear()
    found_urls.clear()
    found_accs.clear()

@dp.message_handler(commands = ['youtube'])
async def youtube(message: types.Message):
    waitmsg = await bot.send_message(message.from_user.id, "Идёт поиск...")
    msg = message.text[9:]
    if "/channel/" in msg:
        i = msg.rfind('/') + 1
        id = msg[i:]
    else:
        i = msg.find('@')
        id = yt.search().list(part = 'snippet', q = msg[i:], maxResults = 1, type = 'channel').execute()['items'][0]['id']['channelId']
        found_urls.append("https://www.youtube.com/@" + msg[i:])
    found_urls.append("https://www.youtube.com/channel/" + id)
    found_accs.append('YouTube')
    res = youtubesearch(id)
    if res and len(found) > 0:
        reply = "Найдены следующие данные: "
        for i in found:
            reply += i + ', '
        if(len(found_accs) > 1):
            reply = reply[:len(reply) - 2] + '\nТакже найдены страницы в следующих соц. сетях: '
            found_accs.remove('YouTube')
            for i in found_accs:
                reply += i + ', '
        reply = reply[:len(reply) - 2]
    elif res and len(found_accs) > 1:
        reply = "Найдены страницы в следующих соц. сетях: "
        found_accs.remove('YouTube')
        for i in found_accs:
            reply += i + ', '
        reply = reply[:len(reply) - 2]
    elif res:
        reply = "Ничего не найдено!"
    else:
        reply = "Произошла ошибка, проверьте id/ссылку и повторите попытку"
    await bot.edit_message_text(text = reply, chat_id = message.from_user.id, message_id = waitmsg.message_id)
    found.clear()
    found_urls.clear()
    found_accs.clear()

executor.start_polling(dp)

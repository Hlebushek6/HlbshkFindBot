from aiogram import Bot, Dispatcher, executor, types
from googlesearch import search
import vk_api
from Bot_config import bot_token, vk_token

bot = Bot(token = bot_token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

session = vk_api.VkApi(token = vk_token)
vk = session.get_api()

def accSearch(url, source, id):
    if url[:24] == "https://www.tiktok.com/@":
        return "TikTok"
    elif url[:14] == "https://vk.com" and (source != "vk" or id != url[15:]):
        return "VK"
    elif url[:31] == "https://www.youtube.com/channel" or url[:25] == "https://www.youtube.com/@":
        return "YouTube"
    else:
        return ""

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await bot.send_message(message.from_user.id, "Привет! \nС помощью этого бота можно узнать, какую информацию о тебе могут получить из открытого доступа мошенники\nЭто позволит узнать, можно ли с легкостью найти о тебе то, что ты не хочешь, чтобы о тебе знали, и убрать это из открытого доступа\nК тому же, бот не собирает информацию о своих пользователях!!\n/help - Все команды")

@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    await bot.send_message(message.from_user.id, "/start - Запустить бота \n\n/vk - Поиск по ВК.\nИспользование: /vk [ссылка на ВК или ID пользователя]\n\n/help - Помощь по командам")

@dp.message_handler(commands=['vk'])
async def vk(message: types.Message):
    waitmsg = await bot.send_message(message.from_user.id, "Идёт поиск...")
    msg = message.text[4:]
    i = msg.rfind('/') + 1
    id = msg[i:]
    info = session.method("users.get", {"user_ids": id, "fields": "bdate, city, contacts, country, domain, home_town, occupation, relatives, relation, sity", "name_case": "nom"})
    reply = "Найдена следующая информация: \nПол"
    if "bdate" in info[0] and info[0]["bdate"] != "":
        reply += ", день рождения "
    if "home_town" in info[0] and info[0]["home_town"] != "":
        reply += ", родной город"
    if "city" in info[0] and info[0]["city"] != "":
        reply += ", город"
    if "country" in info[0] and info[0]["country"] != "":
        reply += ", страна"
    if "occupation" in info[0] and info[0]["occupation"] != "":
        reply += "текущее место работы/учёбы"
    if "mobile_phone" in info[0] and info[0]["mobile_phone"] != "":
        reply += ", телефон"
    if "site" in info[0] and info[0]["site"] != "":
        reply += ", сайт"
    if "relation" in info[0]:
        reply += ", семейное положение"
    if "relation_partner" in info[0]:
        reply += ", партнёр"
    if "relatives" in info[0] and len(info[0]["relatives"]) != 0:
        reply +=", родственники"

    other = False
    tiktok = False
    vkontakte = False
    youtube = False
    for i in search(info[0]["first_name"] + info[0]["last_name"], num = 5, stop = 5, pause = 2, lang = "ru"):
        res = accSearch(i, "vk", info[0]["domain"])
        if (res == "TikTok" and tiktok) or (res == "VK" and vkontakte) or (res == "YouTube" and youtube):
            res = ""
        elif res == "TikTok":
            tiktok = True
        elif res == "VK":
            vkontakte = True
        elif res == "YouTube":
            youtube = True
        if other and res != "":
            reply += ", " + res
        elif res != "":
            reply += "\nВозможно найдены страницы в: " + res
            other = True
    for i in search(info[0]["domain"], num = 5, stop = 5, pause = 2, lang = "ru"):
        res = accSearch(i, "vk", info[0]["domain"])
        if other and res != "":
            reply += ", " + res
        elif res != "":
            reply += "\n Возможно найдены страницы в: " + res
            other = True
    await bot.edit_message_text(text = reply, chat_id = message.from_user.id, message_id = waitmsg.message_id)

executor.start_polling(dp)

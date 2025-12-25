import asyncio
import random
import requests
import aiosqlite
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram.enums import ParseMode

TOKEN = "8485275877:AAHhcEyFnivmc_b2cyHiTtsmAY_aCr6kUJg"

bot = Bot(token=TOKEN)
dp = Dispatcher()

class Data:
    def __init__(self):
        self.db_name = "users.db"
    
    async def initdb(self):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            await db.commit()
    
    async def add_user(self, user_id, username, first_name):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute(
                '''INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)''',
                (user_id, username, first_name)
            )
            await db.commit()
    
    async def get_all_users(self):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT user_id FROM users')
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

db = Data()

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Цена игры по ее названию")],
        [KeyboardButton(text="Гайды Steam")],
        [KeyboardButton(text="Топ игр по онлайну")],
        [KeyboardButton(text='Статистика аккаунта Steam')]
    ],
    resize_keyboard=True
)

guides_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💎 Игры для значка Коллекционера")],
        [KeyboardButton(text="💎 Cпособы повышение lvla Steam")],
        [KeyboardButton(text="💎 Смена региона Steam")],
        [KeyboardButton(text="🔙 Назад в меню")]
    ],
    resize_keyboard=True
)

async def get_top_online_games():
    try:
        url = "https://steamcharts.com/top"
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        rows = soup.find('table', id='top-games').find('tbody').find_all('tr')[:10]
        top_list = ["🏆 <b>Топ игр по онлайну</b>"]
        
        for i, row in enumerate(rows, 1):
            name = row.find('td', class_='game-name').find('a').text.strip()
            players = row.find('td', class_='num').text.strip()
            top_list.append(f"{i}. <b>{name}</b> — {players} игроков")
        
        return "\n".join(top_list)
    except:
        return "Ошибка при получении топа игр"

async def get_game_price(game_name):
    try:
        search = requests.get(
            "https://store.steampowered.com/api/storesearch",
            params={'term': game_name, 'cc': 'ru'}
        ).json()
        
        if not search.get('items'):
            return "Игра не найдена"
        
        game = search['items'][0]
        game_id = game['id']
        game_name_display = game.get('name', game_name)
        
        prices = []
        for cc, symbol in [('ru', '₽'), ('us', '$'), ('kz', '₸')]:
            details = requests.get(
                "https://store.steampowered.com/api/appdetails",
                params={'appids': game_id, 'cc': cc}
            ).json()
            
            if details.get(str(game_id), {}).get('success'):
                data = details[str(game_id)]['data']
                if data.get('is_free'):
                    price = "Бесплатно"
                elif data.get('price_overview'):
                    p = data['price_overview']
                    price = f"{p['final_formatted']}"
                    if p['discount_percent'] > 0:
                        price += f" (-{p['discount_percent']}%)"
                else:
                    price = "Цена не указана"
                prices.append(f"{symbol} {price}")
            else:
                prices.append(f"{symbol} Недоступно")
        
        return f"🎮 <b>{game_name_display}</b>\n\n" + "\n".join(prices)
    except:
        return "Ошибка при поиске цены"

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await db.add_user(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.first_name or ""
    )
    
    try:
        photo = FSInputFile("1766692021143-019b570c-0d8c-7d0f-accb-b231d8202e73.png")
        await message.answer_photo(
            photo=photo,
            caption="<b>🎮 Бот для поиска цен игр, гайдов Steam и т.п</b>\n<i>Разработка ботов под ваши цели -- @yangspays</i>",
            parse_mode=ParseMode.HTML,
            reply_markup=main_keyboard
        )
    except:
        await message.answer(
            "<b>🎮 Бот для поиска цен игр, гайдов Steam и т.п</b>\n<i>Разработка ботов под ваши цели -- @yangspays</i>",
            parse_mode=ParseMode.HTML,
            reply_markup=main_keyboard
        )

@dp.message(lambda message: message.text == "Цена игры по ее названию")
async def ask_game_handler(message: types.Message):
    await message.answer("Как называется игра?", reply_markup=types.ReplyKeyboardRemove())

@dp.message(lambda message: message.text == "Топ игр по онлайну")
async def top_online_handler(message: types.Message):
    await message.answer("📊 Загружаю актуальные данные...")
    top_list = await get_top_online_games()
    await message.answer(top_list, parse_mode=ParseMode.HTML)

@dp.message(lambda message: message.text == "Гайды Steam")
async def badges_menu_handler(message: types.Message):
    await message.answer("📚 Выбери какой гайд тебе интересен:", reply_markup=guides_keyboard)

@dp.message(lambda message: message.text == "Статистика аккаунта Steam")
async def ask_steam_info_handler(message: types.Message):
    await message.answer("Введите Steam ID:")

@dp.message(lambda message: message.text == "💎 Игры для значка Коллекционера")
async def collector_badge_handler(message: types.Message):
    try:
        photo = FSInputFile("yqjJ2Tf7LFI.jpg")
        await message.answer_photo(
            photo=photo,
            caption='''🏆 <b>ГАЙД: Значок Коллекционер в Steam</b>

Чтобы прокачивать данный значок вам нужно покупать игры, забирать их с распродаж
Но в Steam множество игр при добавлении которых в библиотеку уровень значка повышается

<b>Вот некоторые из них</b>

https://s.team/a/272060 - Serena
https://s.team/a/8650 - RACE 07: Andy Priaulx Crowne Plaza
https://s.team/a/346290 - Penumbra: Necrologue
https://s.team/a/351940 - The Descendant
https://s.team/a/319830 - AX:EL - Air XenoDawn
https://s.team/a/608990 - The Archotek Project

<i>На момент создания бота все игры дают +1 к значку и доступны во всех регионах СНГ</i>
<i>Если одна из этих игр не работает или вы хотите предложить еще - напишите создателю бота (@yangspays)</i>''',
            parse_mode=ParseMode.HTML
        )
    except:
        await message.answer(
            '''🏆 <b>ГАЙД: Значок Коллекционер в Steam</b>

Чтобы прокачивать данный значок вам нужно покупать игры, забирать их с распродаж
Но в Steam множество игр при добавлении которых в библиотеку уровень значка повышается

<b>Вот некоторые из них</b>

https://s.team/a/272060 - Serena
https://s.team/a/8650 - RACE 07: Andy Priaulx Crowne Plaza
https://s.team/a/346290 - Penumbra: Necrologue
https://s.team/a/351940 - The Descendant
https://s.team/a/319830 - AX:EL - Air XenoDawn
https://s.team/a/608990 - The Archotek Project

<i>На момент создания бота все игры дают +1 к значку и доступны во всех регионах СНГ</i>
<i>Если одна из этих игр не работает или вы хотите предложить еще - напишите создателю бота (@yangspays)</i>''',
            parse_mode=ParseMode.HTML
        )

@dp.message(lambda message: message.text == "💎 Cпособы повышение lvla Steam")
async def steam_level_handler(message: types.Message):
    try:
        photo = FSInputFile("region_change.webp")
        await message.answer_photo(
            photo=photo,
            caption='''🏆 <b>ГАЙД: Прокачка LVL Steam за копейки</b>

<code>БЕСПЛАТНЫЕ СПОСОБЫ ПРОКАЧКИ</code>

Первый значок это Лидер сообщества который вы можете получить выполняя простые задания связанные с знакомством со Steam.
На максимальном уровне вы получите 500 опыта.

<code>СПИСОК КАРТОЧЕК:</code>

• https://s.team/m/753/?q=Murderous+Pursuits
• https://s.team/m/753/?q=Evolvation
• https://s.team/m/753/?q=World+of+Warships
• https://s.team/m/753/?q=Geneshift
• https://s.team/m/753/?q=Human%3A+Fall+Flat
• https://s.team/m/753/?q=Gorky+17
• https://s.team/m/753/?q=Counter-Strike%3A+Global+Offensive

<i>На момент создания бота все карточки можно купить
Если это не так напишите -- @yangspays</i>''',
            parse_mode=ParseMode.HTML
        )
    except:
        await message.answer(
            '''🏆 <b>ГАЙД: Прокачка LVL Steam за копейки</b>

<code>БЕСПЛАТНЫЕ СПОСОБЫ ПРОКАЧКИ</code>

Первый значок это Лидер сообщества который вы можете получить выполняя простые задания связанные с знакомством со Steam.
На максимальном уровне вы получите 500 опыта.

<code>СПИСОК КАРТОЧЕК:</code>

• https://s.team/m/753/?q=Murderous+Pursuits
• https://s.team/m/753/?q=Evolvation
• https://s.team/m/753/?q=World+of+Warships
• https://s.team/m/753/?q=Geneshift
• https://s.team/m/753/?q=Human%3A+Fall+Flat
• https://s.team/m/753/?q=Gorky+17
• https://s.team/m/753/?q=Counter-Strike%3A+Global+Offensive

<i>На момент создания бота все карточки можно купить
Если это не так напишите -- @yangspays</i>''',
            parse_mode=ParseMode.HTML
        )

@dp.message(lambda message: message.text == "💎 Смена региона Steam")
async def region_change_handler(message: types.Message):
    try:
        photo = FSInputFile("region_change.webp")
        await message.answer_photo(
            photo=photo,
            caption='''🏆 <b>ГАЙД: Смена региона Steam</b>

<code>Зачем это нужно?</code>
• Обход санкций для стран СНГ
• Доступ к заблокированным играм (GTA, CoD, RDR2 и др.)

<code>Требования</code>

Аккаунту > 3 месяцев
С момента прошлой смены > 3 месяцев
~50-100 рублей
VPN (рекомендую Казахстан)
<code>Как сменить регион</code>

Выйдите из Steam на всех устройствах
Включите VPN (Казахстан)
Войдите через браузер
Добавьте игру в корзину
Пополните кошелек через Kupikod (в тенге)
Оплатите игру и подтвердите смену
<i>Актуально на момент создания бота. Вопросы → @yangspays</i>''',
            parse_mode=ParseMode.HTML
        )
    except:
        await message.answer(
            '''🏆 <b>ГАЙД: Смена региона Steam</b>

<code>Зачем это нужно?</code>
• Обход санкций для стран СНГ
• Доступ к заблокированным играм (GTA, CoD, RDR2 и др.)

<code>Требования</code>

Аккаунту > 3 месяцев
С момента прошлой смены > 3 месяцев
~50-100 рублей
VPN (рекомендую Казахстан)
<code>Как сменить регион</code>

Выйдите из Steam на всех устройствах
Включите VPN (Казахстан)
Войдите через браузер
Добавьте игру в корзину
Пополните кошелек через Kupikod (в тенге)
Оплатите игру и подтвердите смену
<i>Актуально на момент создания бота. Вопросы → @yangspays</i>''',
            parse_mode=ParseMode.HTML
        )

@dp.message(lambda message: message.text == "🔙 Назад в меню")
async def back_to_main_handler(message: types.Message):
    await message.answer("Главное меню:", reply_markup=main_keyboard)

@dp.message()
async def universal_handler(message: types.Message):
    excluded = ["Цена игры по ее названию", "Гайды Steam", "💎 Игры для значка Коллекционера",
                "💎 Cпособы повышение lvla Steam", "💎 Смена региона Steam", "🔙 Назад в меню",
                "Топ игр по онлайну", "Статистика аккаунта Steam"]
    
    if message.text in excluded or message.text.startswith('/'):
        return
    
    steam_input = message.text.strip()
    
    if steam_input.isdigit() and len(steam_input) > 10:
        try:
            await message.answer("🔍 Начинаю поиск")
            url = f'https://steamcommunity.com/profiles/{steam_input}/?xml=1'
            r = requests.get(url, timeout=5)
            
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'xml')
                
                if soup.find('error'):
                    await message.answer("❌ Нечего не найдено возможно у пользователя закрыт профиль")
                    await message.answer("Что-то еще?", reply_markup=main_keyboard)
                    return
                
                steamID = soup.find('steamID').text if soup.find('steamID') else "Неизвестно"
                state = soup.find('stateMessage').text if soup.find('stateMessage') else "Неизвестно"
                vac = soup.find('vacBanned').text if soup.find('vacBanned') else "0"
                date = soup.find('memberSince').text if soup.find('memberSince') else "Неизвестно"
                
                vac_text = "Нет банов" if vac == "0" else "Есть баны"
                
                result = f"""
<b>📊 Статистика Steam:</b>
👤 Nickname: {steamID}
🔄 Cтатус: {state}
⚠️ VAC: {vac_text}
📅 Дата регистрации: {date}
"""
                await message.answer(result, parse_mode=ParseMode.HTML)
            else:
                await message.answer("❌ Не удалось получить данные")
        except:
            await message.answer("❌ Произошла ошибка при поиске профиля")
    else:
        try:
            await message.answer("🔍 Ищу")
            price_info = await get_game_price(message.text)
            await message.answer(price_info, parse_mode=ParseMode.HTML)
        except:
            await message.answer("❌ Произошла ошибка при поиске игры")
    
    await message.answer("Что-то еще?", reply_markup=main_keyboard)

async def mailing():
    while True:
        try:
            await asyncio.sleep(10000)
            
            user_ids = await db.get_all_users()
            if not user_ids:
                continue
            
            for user_id in user_ids:
                try:
                    async with aiosqlite.connect(db.db_name) as db_conn:
                        cursor = await db_conn.execute('SELECT first_name FROM users WHERE user_id = ?', (user_id,))
                        user_data = await cursor.fetchone()
                    
                    if user_data:
                        first_name = user_data[0] or "друн"
                        text = [
                            f'<b>⚡ Йоу, {first_name}! А что если твоя любимая игра подорожала? Напиши команду /start, выбери первую кнопку и проверь это!</b>',
                            f'<b>⚡ Эй, {first_name}! А ты повысил свой лвл Steam? Если нет, то скорее пиши /start, выбирай вторую кнопку и повышай лвл!</b>',
                            f'<b>⚡ Привет, {first_name}! Ты уже видел свежий топ по онлайну в играх? Скорее беги смотреть командой /start, выбирай третью кнопку и смотри!</b>',
                            f'<b>⚡Ку, {first_name} в боте вышло обновление советую протестировать новую функцию поиска информации по Steam ID</b>'
                        ]
                        reminder_text = random.choice(text)
                        await bot.send_message(user_id, reminder_text, parse_mode=ParseMode.HTML)
                        await asyncio.sleep(0.5)
                except:
                    continue
        except:
            await asyncio.sleep(60)

async def main():
    await db.initdb()
    asyncio.create_task(mailing())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

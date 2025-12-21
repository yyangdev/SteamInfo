import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile
import requests
from bs4 import BeautifulSoup

print("🚀 Запуск бота...")

TOKEN = "8485275877:AAHhcEyFnivmc_b2cyHiTtsmAY_aCr6kUJg"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Путь к папке с ботом (работает на любом хостинге)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

print(f"📁 Рабочая папка: {BASE_DIR}")

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Цена игры по ее названию")],
        [KeyboardButton(text="Гайды Steam")],
        [KeyboardButton(text="Топ игр по онлайну")]
    ],
    resize_keyboard=True
)

guides_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💎 Игры для значка Коллекционера")],
        [KeyboardButton(text="💎 Cпособы повышение lvla Steam")],
        [KeyboardButton(text="🔙 Назад в меню")]
    ],
    resize_keyboard=True
)

async def get_top_online_games():
    try:
        url = "https://steamcharts.com/top"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        table = soup.find('table', id='top-games')
        if not table:
            return "Ошибка сообщите владельцу"
        
        rows = table.find('tbody').find_all('tr')[:10]
        top_list = ["🏆 <b>Топ игр по онлайну прямо сейчас</b>"]
        
        for idx, row in enumerate(rows, 1):
            try:
                name_cell = row.find('td', class_='game-name')
                name = name_cell.find('a').text.strip() if name_cell and name_cell.find('a') else ''
                
                players_cell = row.find('td', class_='num')
                players = players_cell.text.strip() if players_cell else ''
                
                if name and players:
                    top_list.append(f"{idx}. <b>{name}</b> — {players} игроков")
            except:
                continue
        
        return "\n".join(top_list)
            
    except Exception as e:
        print(f"❌ Ошибка get_top_online_games: {e}")
        return "Ошибка сообщите владельцу"

async def get_game_price(game_name):
    try:
        search = requests.get(
            "https://store.steampowered.com/api/storesearch",
            params={'term': game_name, 'cc': 'ru'},
            timeout=10
        ).json()
        
        if not search.get('items'): return "Игра не найдена"
        
        game = search['items'][0]
        game_id = game['id']
        result = []
        
        for cc, symbol in [('ru', '₽'), ('us', '$'), ('kz', '₸')]:
            details = requests.get(
                "https://store.steampowered.com/api/appdetails",
                params={'appids': game_id, 'cc': cc},
                timeout=5
            ).json()
            
            if details.get(str(game_id), {}).get('success'):
                data = details[str(game_id)]['data']
                if data.get('is_free'):
                    price = "Игра бесплатная"
                elif data.get('price_overview'):
                    p = data['price_overview']
                    price = f"{p['final_formatted']}"
                    if p['discount_percent'] > 0:
                        price += f" (-{p['discount_percent']}%)"
                else:
                    price = "—"
                result.append(f"{symbol} {price}")
        
        return f"🎮 {game['name']}\n\n" + "\n".join(result)
    except Exception as e:
        print(f"❌ Ошибка get_game_price: {e}")
        return "⚠️ Ошибка"

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    print(f"📨 /start от {message.from_user.id}")
    
    # Путь к фото (относительный!)
    photo_path = os.path.join(BASE_DIR, "bot_photo.png")
    
    # Проверяем есть ли файл
    if os.path.exists(photo_path):
        photo = FSInputFile(photo_path)
        await message.answer_photo(
            photo=photo,
            caption="<b>🎮 Бот для поиска цен игр, гайдов Steam и т.п</b>\n<i>Разработка ботов под ваши цели -- @yangspays</i>",
            parse_mode='HTML',
            reply_markup=main_keyboard
        )
    else:
        # Если файла нет - просто текст
        print(f"⚠️ Файл не найден: {photo_path}")
        await message.answer(
            "<b>🎮 Бот для поиска цен игр, гайдов Steam и т.п</b>\n<i>Разработка ботов под ваши цели -- @yangspays</i>",
            parse_mode='HTML',
            reply_markup=main_keyboard
        )

@dp.message(lambda message: message.text == "Цена игры по ее названию")
async def ask_game_handler(message: types.Message):
    await message.answer(
        "Как называется игра?",
        reply_markup=types.ReplyKeyboardRemove()
    )

@dp.message(lambda message: message.text == "Топ игр по онлайну")
async def top_online_handler(message: types.Message):
    await message.answer("📊 Загружаю актуальные данные...")
    top_list = await get_top_online_games()
    await message.answer(top_list, parse_mode='HTML')

@dp.message(lambda message: message.text == "Гайды Steam")
async def badges_menu_handler(message: types.Message):
    await message.answer(
        "📚 Выбери какой гайд тебе интересен:",
        reply_markup=guides_keyboard
    )

@dp.message(lambda message: message.text == "💎 Игры для значка Коллекционера")
async def collector_badge_handler(message: types.Message):
    photo_path = os.path.join(BASE_DIR, "yqjJ2Tf7LFI.jpg")
    caption = '''🏆 <b>ГАЙД: Значок Коллекционер в Steam</b>

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
<i>Если одна из этих игр не работает или вы хотите предложить еще - напишите создателю бота (@yangspays)</i>'''
    
    if os.path.exists(photo_path):
        photo = FSInputFile(photo_path)
        await message.answer_photo(photo=photo, caption=caption, parse_mode='HTML')
    else:
        await message.answer(caption, parse_mode='HTML')

@dp.message(lambda message: message.text == "💎 Cпособы повышение lvla Steam")
async def steam_level_handler(message: types.Message):
    photo_path = os.path.join(BASE_DIR, "2413375957_preview_1.jpg")
    caption = '''🏆 <b>ГАЙД: Прокачка LVL Steam за копейки</b>

<code>БЕСПЛАТНЫЕ СПОСОБЫ ПРОКАЧКИ</code>
Первый значок это Лидер сообщества который вы можете получить выполняя простые задания связанные с знакомством со Steam.
На максимальном уровне вы получите 500 опыта.

<code>ДЕШЕВЫЕ КАРТОЧКИ</code>

<code>🎯 СПИСОК КАРТОЧЕК:</code>
• https://s.team/m/753/?q=Murderous+Pursuits
• https://s.team/m/753/?q=Evolvation
• https://s.team/m/753/?q=World+of+Warships
• https://s.team/m/753/?q=Geneshift
• https://s.team/m/753/?q=Human%3A+Fall+Flat
• https://s.team/m/753/?q=Gorky+17
• https://s.team/m/753/?q=Counter-Strike%3A+Global+Offensive

<i>На момент создания бота все карточки можно купить
Если это не так напишите -- @yangspays</i>'''
    
    if os.path.exists(photo_path):
        photo = FSInputFile(photo_path)
        await message.answer_photo(photo=photo, caption=caption, parse_mode='HTML')
    else:
        await message.answer(caption, parse_mode='HTML')

@dp.message(lambda message: message.text == "В разработке")
async def in_dev_handler(message: types.Message):
    await message.answer("🚧 Этот раздел находится в разработке")

@dp.message(lambda message: message.text == "🔙 Назад в меню")
async def back_to_main_handler(message: types.Message):
    await message.answer(
        "Главное меню:",
        reply_markup=main_keyboard
    )

@dp.message()
async def game_name_handler(message: types.Message):
    if (message.text.startswith('/') or 
        message.text == "Цена игры по ее названию" or
        message.text == "Гайды Steam" or
        message.text == "💎 Игры для значка Коллекционера" or
        message.text == "💎 Cпособы повышение lvla Steam" or
        message.text == "В разработке" or
        message.text == "🔙 Назад в меню" or
        message.text == "Топ игр по онлайну"):
        return
    
    await message.answer("Идет поиск...")
    await message.answer(await get_game_price(message.text))
    await message.answer("Искать еще?", reply_markup=main_keyboard)

async def main():
    print("✅ Бот успешно запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

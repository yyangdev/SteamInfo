import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile
import requests

TOKEN = "8391847587:AAFSPr6nDgZjriF8ucaWP4hfl2xO_cBD5CY"
bot = Bot(token=TOKEN)
dp = Dispatcher()

keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Цена игры по ее названию")]],
    resize_keyboard=True
)

async def get_game_price(game_name):
    try:
        search = requests.get(
            "https://store.steampowered.com/api/storesearch",
            params={'term': game_name, 'cc': 'ru'},
            timeout=10
        ).json()
        
        if not search.get('items'): 
            return "<b>Игра не найдена</b>"
        
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
                    price = "<b>Бесплатно</b>"
                elif data.get('price_overview'):
                    p = data['price_overview']
                    price = f"<b>{p['final_formatted']}</b>"
                    if p['discount_percent'] > 0:
                        price += f" <b>(-{p['discount_percent']}%)</b>"
                else:
                    price = "<b>—</b>"
                result.append(f"<b>{symbol}</b> {price}")
        
        return f"<b>🎮 {game['name']}</b>\n\n" + "\n".join(result)
    except:
        return "<b>⚠️ Ошибка</b>"

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    photo = FSInputFile("bot_photo.png")
    await message.answer_photo(
        photo=photo,
        caption="<b>🎮 Бот для поиска цены по ее названию</b>\n\n<i>Бот был написан -- @yangspays</i>",
        parse_mode='HTML',
        reply_markup=keyboard
    )

@dp.message(lambda message: message.text == "Цена игры по ее названию")
async def ask_game_handler(message: types.Message):
    await message.answer(
        "<b>Как называется твоя игра?</b>",
        parse_mode='HTML',
        reply_markup=types.ReplyKeyboardRemove()
    )

@dp.message()
async def game_name_handler(message: types.Message):
    if message.text.startswith('/') or message.text == "Цена игры по ее названию":
        return
    
    await message.answer("<b>Идет поиск...</b>", parse_mode='HTML')
    await message.answer(await get_game_price(message.text), parse_mode='HTML')
    await message.answer("<b>Искать еще?</b>", parse_mode='HTML', reply_markup=keyboard)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

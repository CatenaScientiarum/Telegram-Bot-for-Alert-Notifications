# -*- coding: utf-8 -*-
import logging
from telegram import Update, Bot, ReplyKeyboardMarkup, Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton as ReplyKeyboardButton, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, CallbackContext, Application, filters
from datetime import datetime
from alerts_in_ua import Client as AlertsClient
from selenium import webdriver
from telegram.ext.filters import Text, Regex
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.firefox import GeckoDriverManager
import time

driver_path = 'YOUR_GECKODRIVER_PATH'
telegram_token = "YOUR_TELEGRAM_BOT_TOKEN"
alerts_client = AlertsClient(token="YOUR_ALERTSINUA_TOKEN")
bot = Bot(token=telegram_token)

bot_state = {
    'region_mode': None,
    'popup_notifications': True,
    'chat_ids': {},
    'region_uid': None
}

active_alerts_dict = {}
region_select_users = {}
alerts = {} 
country_mode_users = {}
region_mode_users = {}
notifications_on_users = {}
notifications_off_users = {}
select_region_users = {}
map_users = {}
alert_users = {}

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

region_dict = {
    '3': "Хмельницькій області",
    '4': "Вінницькій області",
    '5': "Рівненській області",
    '8': "Волинській області",
    '9': "Дніпропетровській області",
    '10': "Житомирській області",
    '11': "Закарпатській області",
    '12': "Запорізькій області",
    '13': "Івано-Франківській області",
    '14': "Київській області",
    '15': "Кіровоградській області",
    '16': "Луганській області",
    '17': "Миколаївській області",
    '18': "Одеській області",
    '19': "Полтавській області",
    '20': "Сумській області",
    '21': "Тернопільській області",
    '22': "Харківській області",
    '23': "Херсонській області",
    '24': "Черкаській області",
    '25': "Чернігівській області",
    '26': "Чернівецькій області",
    '27': "Львівській області",
    '28': "Донецькій області",
    '29': "Автономній Республіці Крим",
    '30': "м. Севастополь",
    '31': "м. Київ",
}

async def select_region(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    region_select_users[user_id] = update.message.chat_id
    bot_state['region_mode'] = True
    keyboard = [
        [InlineKeyboardButton("Хмельницька область", callback_data='region_3')],
        [InlineKeyboardButton("Вінницька область", callback_data='region_4')],
        [InlineKeyboardButton("Рівненська область", callback_data='region_5')],
        [InlineKeyboardButton("Волинська область", callback_data='region_8')],
        [InlineKeyboardButton("Дніпропетровська область", callback_data='region_9')],
        [InlineKeyboardButton("Житомирська область", callback_data='region_10')],
        [InlineKeyboardButton("Закарпатська область", callback_data='region_11')],
        [InlineKeyboardButton("Запорізька область", callback_data='region_12')],
        [InlineKeyboardButton("Івано-Франківська область", callback_data='region_13')],
        [InlineKeyboardButton("Київська область", callback_data='region_14')],
        [InlineKeyboardButton("Кіровоградська область", callback_data='region_15')],
        [InlineKeyboardButton("Луганська область", callback_data='region_16')],
        [InlineKeyboardButton("Миколаївська область", callback_data='region_17')],
        [InlineKeyboardButton("Одеська область", callback_data='region_18')],
        [InlineKeyboardButton("Полтавська область", callback_data='region_19')],
        [InlineKeyboardButton("Сумська область", callback_data='region_20')],
        [InlineKeyboardButton("Тернопільська область", callback_data='region_21')],
        [InlineKeyboardButton("Харківська область", callback_data='region_22')],
        [InlineKeyboardButton("Херсонська область", callback_data='region_23')],
        [InlineKeyboardButton("Черкаська область", callback_data='region_24')],
        [InlineKeyboardButton("Чернігівська область", callback_data='region_25')],
        [InlineKeyboardButton("Чернівецька область", callback_data='region_26')],
        [InlineKeyboardButton("Львівська область", callback_data='region_27')],
        [InlineKeyboardButton("Донецька область", callback_data='region_28')],
        [InlineKeyboardButton("Автономна Республіка Крим", callback_data='region_29')],
        [InlineKeyboardButton("м. Севастополь", callback_data='region_30')],
        [InlineKeyboardButton("м. Київ", callback_data='region_31')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Обери область:", reply_markup=reply_markup)


#WIP    
service = Service(GeckoDriverManager().install())
driver = webdriver.Firefox(service=service)

def send_screenshot(chat_id):
    firefox_options = Options()
    firefox_options.headless = True

    service = Service(driver_path)
    driver = webdriver.Firefox(service=service, options=firefox_options)
    driver.set_window_size(1920, 1080)
    driver.get("https://alerts.in.ua")
    
    time.sleep(2)
    
    screenshot = driver.get_screenshot_as_png()
    driver.quit()
    
    bot = Bot(token=telegram_token)
    bot.send_photo(chat_id=chat_id, photo=screenshot)
#WIP

def map_command(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    send_screenshot(chat_id)

async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    bot_state['chat_ids'][user_id] = update.message.chat_id
    await update.message.reply_text("Привіт! Я твій бот. Використовуй /settings, щоб налаштувати мене.")


async def send_alert_start_message(alert):
    if bot_state['popup_notifications']:
        alert_str = f"🚨 Нова тривога! 🚨\n"
        alert_str += f"Місце: {alert.location_title}\n"
        alert_str += f"Тип: {alert.alert_type.replace('_', ' ').title()}\n"
        alert_str += f"Час початку: {alert.started_at}\n"
        alert_str += f"Примітки: {alert.notes if alert.notes else 'Немає'}\n"

        for chat_id in bot_state['chat_ids'].values():
            await bot.send_message(chat_id=chat_id, text=alert_str)

async def send_alert_end_message(alert):
    if bot_state['popup_notifications']:
        alert_str = f"✅ Тривога закінчилася! ✅\n"
        alert_str += f"Місце: {alert.location_title}\n"
        alert_str += f"Тип: {alert.alert_type.replace('_', ' ').title()}\n"
        alert_str += f"Час закінчення: {alert.ended_at}\n"
        alert_str += f"Примітки: {alert.notes if alert.notes else 'Немає'}\n"

        for chat_id in bot_state['chat_ids'].values():
            await bot.send_message(chat_id=chat_id, text=alert_str)


async def settings(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [ReplyKeyboardButton('🌍 Оновити статуси'), ReplyKeyboardButton('📍 За регіоном')],
        [ReplyKeyboardButton('🔔 Ввімкнути сповіщення'), ReplyKeyboardButton('🔕 Вимкнути сповіщення')],
        [ReplyKeyboardButton('🗺️ Переглянути карту')]
    ]
    if bot_state['region_mode']:
        keyboard.append([ReplyKeyboardButton('🌐 Вибрати регіон')])

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Вибери налаштування:", reply_markup=reply_markup)


async def check_alerts(context: CallbackContext) -> None:
    try:
        alerts = alerts_client.get_active_alerts()
    except Exception as e:
        logger.error(f"Failed to fetch alerts. Error: {e}")
        return

    for alert in alerts:
        if alert.id not in active_alerts_dict:
            active_alerts_dict[alert.id] = alert
            await send_alert_start_message(alert)

    for alert_id in list(active_alerts_dict.keys()):
        if not any(alert.id == alert_id for alert in alerts):
            send_alert_end_message(active_alerts_dict[alert_id])
            del active_alerts_dict[alert_id]

async def handle_text(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    chat_id = update.message.chat_id

    if text == "🌍 Оновити статуси":
        await send_alerts(chat_id)
    elif text == "📍 За регіоном":
        bot_state['region_mode'] = True
        await settings(update, context)
    elif text == "🔔 Ввімкнути сповіщення":
        bot_state['popup_notifications'] = True
        await update.message.reply_text("Сповіщення ввімкнено")
    elif text == "🔕 Вимкнути сповіщення":
        bot_state['popup_notifications'] = False
        await update.message.reply_text("Сповіщення вимкнено")
    elif text == "🌐 Вибрати регіон":
        await select_region(update, context)    
    elif text == "🗺️ Переглянути карту":
        await map_command(update, context)    

async def send_alerts(chat_id):
    active_alerts = alerts_client.get_active_alerts()
    for alert in active_alerts:
        alert_str = f"Місце: {alert.location_title}\n"
        alert_str += f"Тип: {alert.alert_type.replace('_', ' ').title()}\n"
        alert_str += f"Час початку: {alert.started_at}\n"
        alert_str += f"Останнє оновлення: {alert.updated_at}\n"
        alert_str += f"Примітки: {alert.notes if alert.notes else 'Немає'}\n"

        await bot.send_message(chat_id=chat_id, text=alert_str)

async def button_click(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data.startswith('region_'):
        region_uid = query.data.split('_')[1]
        bot_state['region_uid'] = region_uid
        
        active_alerts = alerts_client.get_active_alerts()
        
        region_alerts = []
        for alert in active_alerts:
            if alert.location_title == region_dict.get(region_uid, ''):
                region_alerts.append(alert)
        #WIP
        if region_alerts:
            alert_str = f"🚨 Активні тривоги в {region_dict.get(region_uid, 'невідомій області')}:\n"
            for alert in region_alerts:
                alert_str += f"\nТип: {alert.alert_type.replace('_', ' ').title()}\n"
                alert_str += f"Місце: {alert.location_title}\n"
                alert_str += f"Час початку: {alert.started_at}\n"
                alert_str += f"Примітки: {alert.notes if alert.notes else 'Немає'}\n"
            await query.message.reply_text(alert_str)
        else:
            await query.message.reply_text(f"✅ Немає активних тривог в {region_dict.get(region_uid, 'невідомій області')}!")
        #WIP
async def schedule_check_alerts(context: CallbackContext) -> None:
    await check_alerts(context)

def main():

    application = Application.builder().token(telegram_token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("settings", settings))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(CallbackQueryHandler(button_click))
    application.add_handler(MessageHandler(filters.Regex('🌐 Вибрати регіон'), select_region))
    application.add_handler(CommandHandler("map", map_command))

    application.job_queue.run_repeating(schedule_check_alerts, interval=30, first=4)

    application.run_polling()

if __name__ == '__main__':
    main()

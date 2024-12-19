# -*- coding: utf-8 -*-
import logging, time, pytz
from telegram import Update, Bot, ReplyKeyboardMarkup, Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton as ReplyKeyboardButton, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, CallbackContext, Application, filters
from datetime import datetime
from alerts_in_ua import Client as AlertsClient
from telegram.ext.filters import Text, Regex
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


telegram_token = "YOUR_TELEGRAM_BOT_TOKEN"
alerts_client = AlertsClient(token="YOUR_ALERTSINUA_TOKEN")
driver_path = 'YOUR_GECKODRIVER(CHROMEDRIVER)_PATH'
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
alert_times = {}

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


async def send_screenshot(chat_id):
    chrome_options = Options()
    chrome_options.headless = True
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.set_window_size(1920, 1080)
    driver.get("https://alerts.in.ua")
    
    
    screenshot = driver.get_screenshot_as_png()
    
    driver.quit()
    
    bot = Bot(token=telegram_token)
    await bot.send_photo(chat_id=chat_id, photo=screenshot)

async def map_command(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    await send_screenshot(chat_id)  
    

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
    user_id = update.message.from_user.id
    if text == "🌍 Оновити статуси":
        bot_state['region_mode'] = False
        await settings(update, context) 
        await send_alerts(chat_id)
        country_mode_users[user_id]= chat_id
        if user_id in region_mode_users:
            del region_mode_users[user_id]
    elif text == "📍 За регіоном":
        bot_state['region_mode'] = True
        await settings(update, context)
        region_select_users[user_id] = chat_id
        if user_id in country_mode_users:
            del country_mode_users[user_id]
    elif text == "🔔 Ввімкнути сповіщення":
        bot_state['popup_notifications'] = True
        await update.message.reply_text("Сповіщення ввімкнено")
        notifications_on_users[user_id] = chat_id
        if user_id in notifications_off_users:
            del notifications_off_users[user_id]
    elif text == "🔕 Вимкнути сповіщення":
        bot_state['popup_notifications'] = False
        await update.message.reply_text("Сповіщення вимкнено")
        notifications_off_users[user_id] = chat_id
        if user_id in notifications_on_users:
            del notifications_on_users[user_id]
    elif text == "🌐 Вибрати регіон":
        bot_state['region_mode'] = False
        await select_region(update, context)
        select_region_users[user_id] = chat_id
        if user_id in select_region_users:
            del select_region_users[user_id] 
    elif text == "🗺️ Переглянути карту":
        map_users[user_id] = chat_id
        await update.message.reply_text("Зачекайте будь ласка")
        await map_command(update, context)  
        if user_id in map_users:
            del map_users[user_id]

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

        try:
            active_alerts = alerts_client.get_active_alerts()
        except Exception as e:
            logger.error(f"Помилка отримання активних тривог: {e}")
            await query.message.reply_text("⚠️ Виникла помилка під час отримання даних.")
            return

        region_alerts = []
        for alert in active_alerts:
            if str(alert.location_uid) == str(region_uid):
                region_alerts.append(alert)

                alert_times[alert.location_uid] = alert.started_at

        if region_alerts:
            alert_str = f"🚨 Активні тривоги для регіону {region_uid}:\n"
            for alert in region_alerts:
                alert_str += (
                    f"\nТип: {alert.alert_type.replace('_', ' ').title()}\n"
                    f"Місце: {alert.location_title}\n"
                    f"Час початку: {alert.started_at}\n"
                    f"Примітки: {alert.notes if alert.notes else 'Немає'}\n"
                )
            await query.message.reply_text(alert_str)
        else:
            await query.message.reply_text(f"✅ Немає активних тривог для регіону {region_uid}!")


async def schedule_check_alerts(context: CallbackContext) -> None:
    await check_alerts(context)
#WIP      
async def monitor_alerts_status(context: CallbackContext) -> None:
    try:
        active_alerts = alerts_client.get_active_alerts()
    except Exception as e:
        logger.error(f"Помилка отримання активних тривог: {e}")
        return

    for region_uid in list(alert_times.keys()):
        alert = next((alert for alert in active_alerts if str(alert['location_uid']) == str(region_uid)), None)
        
        if alert:
            if alert['finished_at'] is None:
                logger.info(f"Тривога для регіону {region_uid} ще активна.")
                continue
            else:
                start_time = datetime.fromisoformat(alert['started_at'].replace("Z", "+00:00"))
                end_time = datetime.fromisoformat(alert['finished_at'].replace("Z", "+00:00")) if alert['finished_at'] else datetime.now(pytz.timezone('Europe/Kyiv'))
                duration = end_time - start_time

                logger.info(f"Тривога для регіону {region_uid} завершена.")
                await context.bot.send_message(
                    chat_id=context.job.context,
                    text=(f"✅ Тривога для регіону {region_uid} завершена!\n"
                          f"Час початку: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                          f"Час завершення: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                          f"Тривала: {str(duration)}."),
                )
                del alert_times[region_uid]
#WIP  
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

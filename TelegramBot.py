#-*- coding: utf-8 -*-
from telegram import ReplyKeyboardMarkup, Update, InlineKeyboardButton, InlineKeyboardMarkup,KeyboardButton as ReplyKeyboardButton,Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler,CallbackContext
import logging,threading,time,requests
from datetime import datetime, timedelta
from alerts_in_ua import Client as AlertsClient
from selenium import webdriver

telegram_token = "YOUR_TELEGRAM_BOT_TOKEN"
alerts_client = AlertsClient("YOUR_CLIENT")

DRIVER = 'path/to/phantomjs'

bot_state = {
    'region_mode': None,
    'popup_notifications': True,
    'chat_ids': {},
    'region_uid': None
}
active_alerts_dict = {}

def send_screenshot(chat_id):
    driver = webdriver.PhantomJS(DRIVER)
    driver.set_window_size(1920, 1080)
    driver.get("https://alerts.in.ua")
    screenshot = driver.get_screenshot_as_png()
    driver.quit()
    bot = Bot(token=telegram_token)
    bot.send_photo(chat_id=chat_id, photo=screenshot)
      
map_users = {}

def map_command(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    map_users[chat_id] = True
    send_screenshot(chat_id)

for chat_id in list(map_users.keys()):
    send_screenshot(chat_id)
    del map_users[chat_id]

def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    bot_state['chat_ids'][user_id] = update.message.chat_id
    update.message.reply_text("Привіт! Я твій бот. Використовуй /settings, щоб налаштувати мене.")

bot = Bot(token=telegram_token)

active_alerts = alerts_client.get_active_alerts()


def send_alert_start_message(alert):
    if bot_state['popup_notifications']:
        alert_str = f"🚨 Нова тривога! 🚨\n"
        alert_str += f"Місце: {alert.location_title}\n"
        if alert.alert_type == 'air_raid':
            alert_str += "Тип: атака з повітря\n"
        elif alert.alert_type == 'artillery_shelling':
            alert_str += "Тип: арт-обстріл\n" 
        else:
            alert_str += f"Тип: {alert.alert_type}\n"
        alert_str += f"Час початку: {alert.started_at}\n"
        alert_str += f"Примітки: {alert.notes if alert.notes else 'Немає'}\n"

        for chat_id in bot_state['chat_ids'].values():
            bot.send_message(chat_id=chat_id, text=alert_str)

def send_alert_end_message(alert):
    if bot_state['popup_notifications']:
        alert_str = f"✅ Тривога закінчилася! ✅\n"
        alert_str += f"Місце: {alert.location_title}\n"
        if alert.alert_type == 'air_raid':
            alert_str += "Тип: атака з повітря\n"
        elif alert.alert_type == 'artillery_shelling':
            alert_str += "Тип: арт-обстріл\n" 
        else:
            alert_str += f"Тип: {alert.alert_type}\n"
        alert_str += f"Час закінчення: {alert.ended_at}\n"
        alert_str += f"Примітки: {alert.notes if alert.notes else 'Немає'}\n"

        for chat_id in bot_state['chat_ids'].values():
            bot.send_message(chat_id=chat_id, text=alert_str)

def settings(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [ReplyKeyboardButton('🌍 За всю країну'), ReplyKeyboardButton('📍 За регіоном')],
        [ReplyKeyboardButton('🔔 Ввімкнути сповіщення'), ReplyKeyboardButton('🔕 Вимкнути сповіщення')]
    ]

    if bot_state['region_mode']:
        keyboard.append([ReplyKeyboardButton('🌐 Вибрати регіон')])

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    if reply_markup:
        update.message.reply_text("\u2063", reply_markup=reply_markup)


def check_alerts(context: CallbackContext) -> None:
    try:
        alerts = alerts_client.get_active_alerts()
    except Exception as e:
        print(f"Failed to fetch alerts. Error: {e}")
        return

    for alert in alerts:
        if alert.id not in active_alerts_dict:
            active_alerts_dict[alert.id] = alert
            send_alert_start_message(alert)

    for alert_id in list(active_alerts_dict.keys()):
        if not any(alert.id == alert_id for alert in alerts):
            send_alert_end_message(active_alerts_dict[alert_id])
            del active_alerts_dict[alert_id]

country_mode_users = {}
region_mode_users = {}
notifications_on_users = {}
notifications_off_users = {}
select_region_users = {}
alert_users = {}

def handle_text(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    chat_id = update.message.chat_id

    if text == "🌍 За всю країну":
        alert_users[chat_id] = True

    if chat_id in alert_users:
        bot_state['region_mode'] = False
        bot_state['region_uid'] = None
        send_alerts(chat_id)
        del alert_users[chat_id]

    elif text == "📍 За регіоном" and chat_id not in region_mode_users:
        region_mode_users[chat_id] = True
        bot_state['region_mode'] = True
        del region_mode_users[chat_id]

    elif text == "🔔 Ввімкнути сповіщення" and chat_id not in notifications_on_users:
        notifications_on_users[chat_id] = True
        bot_state['popup_notifications'] = True
        update.message.reply_text("Сповіщення ввімкнуті")
        del notifications_on_users[chat_id]

    elif text == "🔕 Вимкнути сповіщення" and chat_id not in notifications_off_users:
        notifications_off_users[chat_id] = True
        bot_state['popup_notifications'] = False
        update.message.reply_text("Сповіщення вимкнені")
        del notifications_off_users[chat_id]

    elif text == "🌐 Вибрати регіон" and chat_id not in select_region_users:
        select_region_users[chat_id] = True
        bot_state['region_mode'] = True
        select_region(update, context)
        del select_region_users[chat_id]

    else:
        update.message.reply_text(f"Обрано: {text}")

    settings(update, context)

def send_alerts(chat_id):
    active_alerts = alerts
    for alert in active_alerts.values():
        alert_str = f"Місце: {alert.location_title}\n"
        if alert.alert_type == 'air_raid':
            alert_str += "Тип: атака з повітря\n"
        elif alert.alert_type == 'artillery_shelling':
            alert_str += "Тип: арт-обстріл\n" 
        else:
            alert_str += f"Тип: {alert.alert_type}\n"
        alert_str += f"Час початку: {alert.started_at}\n"
        alert_str += f"Останнє оновлення: {alert.updated_at}\n"
        alert_str += f"Примітки: {alert.notes if alert.notes else 'Немає'}\n"

        bot.send_message(chat_id=chat_id, text=alert_str)
        

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

region_select_users = {}

def select_region(update: Update, context: CallbackContext) -> None:
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
    update.message.reply_text("Обери область:", reply_markup=reply_markup)
   

def button_click(update: Update, context: CallbackContext) -> None:
        query = update.callback_query
        query.answer()

        if query.data == 'back':
            settings(update, context)
        elif query.data == 'country':
            send_alerts()
        elif query.data.startswith('region_'):
            region_uid = query.data.split('_')[1]
            bot_state['region_uid'] = region_uid
            query.message.reply_text(f"Дивимось тревоги в {region_dict[region_uid]}")
            query.message.delete()
            if bot_state['region_mode']:
                active_alerts = alerts_client.get_active_alerts()
                alert_status = alerts_client.get_air_raid_alert_status(region_uid).status
                for user_id, chat_id in region_select_users.items():
                    if alert_status.startswith('active'):
                        alert_str = f"Повітряна тривога активна в {region_dict[region_uid]}. "
                        for alert in active_alerts.alerts:
                            if alert.location_uid == region_uid:
                                alert_str = f"Тривога, всі в укриття! Тривога почалась {alert.started_at}\n"
                        bot.send_message(chat_id=chat_id, text=alert_str)
                        del region_select_users[user_id]
                    elif alert_status == 'P':
                        bot.send_message(chat_id=chat_id, text=f"Часткова тривога в районах чи громадах {region_dict[region_uid]} ")
                        del region_select_users[user_id]
                    else:
                        bot.send_message(chat_id=chat_id, text=f"Схоже, все спокійно в {region_dict[region_uid]} , але будьте обережні")
                        del region_select_users[user_id]
                    
alerts = {} 
def schedule_check_alerts(context: CallbackContext) -> None:
    check_alerts(context)
    active_alerts = alerts_client.get_active_alerts()

    for alert in active_alerts:
        alerts[alert.id] = alert

def main() -> None:
    updater = Updater(token=telegram_token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("settings", settings))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))
    dispatcher.add_handler(CallbackQueryHandler(button_click))
    dispatcher.add_handler(MessageHandler(Filters.regex('🌐 Вибрати регіон'), select_region))
    dispatcher.add_handler(CommandHandler("map", map_command))
    updater.job_queue.run_repeating(schedule_check_alerts, interval=30, first=4)
    updater.start_polling()
    updater.idle()
if __name__ == '__main__':
    main()
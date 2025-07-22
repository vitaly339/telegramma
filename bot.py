import telebot
from telebot import types
from app import app, db
from models import Customer, Booking, Message, BotStats, BookingStatus, MessageType
from config import Config
from datetime import datetime, date
import logging
import re
from flask import request

# Initialize bot with fallback token
bot_token = app.config.get('TELEGRAM_TOKEN') or '7861899004:AAHHUEAolQwwsSXkz7YLddd_qnnxesQIj24'
bot = telebot.TeleBot(bot_token)

# User states for conversation flow
user_states = {}

def create_main_keyboard():
    """Create main menu keyboard"""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(Config.COMMANDS['address'])
    btn2 = types.KeyboardButton(Config.COMMANDS['booking'])
    btn3 = types.KeyboardButton(Config.COMMANDS['contact'])
    keyboard.add(btn1, btn2, btn3)
    return keyboard

def get_or_create_customer(message):
    """Get or create customer from Telegram message"""
    try:
        customer = Customer.query.filter_by(telegram_id=message.from_user.id).first()
        
        if not customer:
            customer = Customer()
            customer.telegram_id = message.from_user.id
            customer.username = message.from_user.username
            customer.first_name = message.from_user.first_name
            customer.last_name = message.from_user.last_name
            
            db.session.add(customer)
            
            # Update daily stats
            today = date.today()
            stats = BotStats.query.filter_by(date=today).first()
            if not stats:
                stats = BotStats()
                stats.date = today
                stats.new_users = 1
                stats.total_messages = 1
                db.session.add(stats)
            else:
                stats.new_users += 1
                stats.total_messages += 1
                
            db.session.commit()
            logging.info(f"New customer created: {customer.full_name}")
        else:
            customer.last_activity = datetime.utcnow()
            
            # Update message count
            today = date.today()
            stats = BotStats.query.filter_by(date=today).first()
            if stats:
                stats.total_messages += 1
            else:
                stats = BotStats()
                stats.date = today
                stats.total_messages = 1
                db.session.add(stats)
                
            db.session.commit()
        
        return customer
    except Exception as e:
        logging.error(f"Error in get_or_create_customer: {e}")
        # Create minimal customer object for fallback
        customer = Customer()
        customer.telegram_id = message.from_user.id
        customer.username = message.from_user.username or "Unknown"
        customer.first_name = message.from_user.first_name or "User"
        return customer

def save_message(customer, message_text, message_type=MessageType.TEXT, from_admin=False):
    """Save message to database"""
    try:
        message = Message()
        message.customer_id = customer.id
        message.content = message_text
        message.message_type = message_type
        message.from_admin = from_admin
        
        db.session.add(message)
        db.session.commit()
    except Exception as e:
        logging.error(f"Error saving message: {e}")

@bot.message_handler(commands=['start'])
def handle_start(message):
    with app.app_context():
        customer = get_or_create_customer(message)
        save_message(customer, '/start')
        
        bot.reply_to(
            message,
            Config.MESSAGES['welcome'],
            reply_markup=create_main_keyboard()
        )

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    with app.app_context():
        customer = get_or_create_customer(message)
        save_message(customer, message.text)
        
        # Check for button commands
        if message.text == Config.COMMANDS['address']:
            bot.send_message(message.chat.id, Config.MESSAGES['address'])
        elif message.text == Config.COMMANDS['booking']:
            bot.send_message(message.chat.id, Config.MESSAGES['booking_site'])
        elif message.text == Config.COMMANDS['contact']:
            bot.send_message(message.chat.id, Config.MESSAGES['contact_whatsapp'])
        else:
            # Default response for unrecognized messages
            bot.send_message(message.chat.id, Config.MESSAGES['not_understood'])

@bot.message_handler(content_types=['photo', 'document', 'voice'])
def handle_media_message(message):
    with app.app_context():
        customer = get_or_create_customer(message)
        
        if message.content_type == 'photo':
            content = f"Фото: {message.photo[-1].file_id}"
            message_type = MessageType.PHOTO
        elif message.content_type == 'document':
            content = f"Документ: {message.document.file_name if message.document else 'Unknown'}"
            message_type = MessageType.DOCUMENT
        elif message.content_type == 'voice':
            content = f"Голосовое сообщение: {message.voice.file_id}"
            message_type = MessageType.VOICE
        
        save_message(customer, content, message_type)
        bot.reply_to(message, Config.MESSAGES['not_understood'])

def setup_webhook():
    """Setup webhook for production"""
    if app.config['WEBHOOK_URL']:
        webhook_url = f"{app.config['WEBHOOK_URL']}/webhook"
        bot.set_webhook(url=webhook_url)
        logging.info(f"Webhook set to: {webhook_url}")

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle webhook requests"""
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        return 'Invalid content type', 400

def send_message_to_customer(telegram_id, text):
    """Send message to customer from admin"""
    try:
        bot.send_message(telegram_id, text)
        return True
    except Exception as e:
        logging.error(f"Error sending message to {telegram_id}: {e}")
        return False

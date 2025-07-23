from datetime import datetime, date, timedelta
from flask import current_app
from project_models import db, Booking, Customer, Message
import logging

logger = logging.getLogger(__name__)

def get_dashboard_stats():
    """Возвращает статистику бронирований и клиентов"""
    try:
        stats = {
            'total_bookings': Booking.query.count(),
            'active_customers': Customer.query.filter(
                
                Customer.last_activity >= datetime.utcnow() - timedelta(days=30)
            ).count(),
            'recent_bookings': Booking.query.filter(
                Booking.created_at >= datetime.utcnow() - timedelta(days=7))
                .count()
        }
        return stats
    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        return {
            'total_bookings': 0,
            'active_customers': 0,
            'recent_bookings': 0
        }

def get_weekly_chart_data():
    """Генерирует данные для графика бронирований по дням недели"""
    try:
        results = db.session.query(
            db.func.strftime('%w', Booking.created_at).label('weekday'),
            db.func.count(Booking.id)
        ).group_by('weekday').all()
        
        return [{'day': int(r[0]), 'count': r[1]} for r in results]
    except Exception as e:
        logger.error(f"Ошибка получения данных графика: {e}")
        return []

def send_message_to_customer(telegram_id, text):
    """Отправляет сообщение клиенту через Telegram"""
    try:
        from app import bot  # Импорт бота
        
        msg = bot.send_message(
            chat_id=telegram_id,
            text=text,
            parse_mode='HTML'
        )
        
        # Логируем отправку
        logger.info(f"Сообщение отправлено: {telegram_id}")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения {telegram_id}: {e}")
        return False

def save_message_to_db(customer_id, content, message_type='text'):
    """Сохраняет сообщение в базу данных"""
    try:
        message = Message(
            customer_id=customer_id,
            content=content[:1000],  # Обрезаем длинные сообщения
            message_type=message_type,
            created_at=datetime.utcnow()
        )
        db.session.add(message)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        logger.error(f"Ошибка сохранения сообщения: {e}")
        return False

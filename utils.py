from datetime import datetime, timedelta
from models import BotStats, Customer, Booking, Message
from app import db
from sqlalchemy import func

def get_dashboard_stats():
    """Get statistics for dashboard"""
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    stats = {
        'total_customers': Customer.query.count(),
        'total_bookings': Booking.query.count(),
        'total_messages': Message.query.count(),
        'new_customers_today': Customer.query.filter(
            func.date(Customer.created_at) == today
        ).count(),
        'new_customers_week': Customer.query.filter(
            func.date(Customer.created_at) >= week_ago
        ).count(),
        'new_customers_month': Customer.query.filter(
            func.date(Customer.created_at) >= month_ago
        ).count(),
        'bookings_today': Booking.query.filter(
            func.date(Booking.created_at) == today
        ).count(),
        'bookings_week': Booking.query.filter(
            func.date(Booking.created_at) >= week_ago
        ).count(),
        'bookings_month': Booking.query.filter(
            func.date(Booking.created_at) >= month_ago
        ).count(),
        'unread_messages': Message.query.filter(
            Message.from_admin == False,
            Message.read == False
        ).count()
    }
    
    return stats

def get_weekly_chart_data():
    """Get data for weekly analytics chart"""
    week_ago = datetime.now().date() - timedelta(days=7)
    
    daily_stats = db.session.query(
        BotStats.date,
        BotStats.new_users,
        BotStats.total_messages,
        BotStats.bookings_created
    ).filter(BotStats.date >= week_ago).order_by(BotStats.date).all()
    
    dates = []
    new_users = []
    messages = []
    bookings = []
    
    for stat in daily_stats:
        dates.append(stat.date.strftime('%d.%m'))
        new_users.append(stat.new_users)
        messages.append(stat.total_messages)
        bookings.append(stat.bookings_created)
    
    return {
        'dates': dates,
        'new_users': new_users,
        'messages': messages,
        'bookings': bookings
    }

def format_datetime(dt):
    """Format datetime for Russian locale"""
    if not dt:
        return "—"
    return dt.strftime('%d.%m.%Y %H:%M')

def format_date(dt):
    """Format date for Russian locale"""
    if not dt:
        return "—"
    return dt.strftime('%d.%m.%Y')

def get_status_badge_class(status):
    """Get Bootstrap badge class for booking status"""
    status_classes = {
        'pending': 'bg-warning',
        'confirmed': 'bg-success',
        'cancelled': 'bg-danger',
        'completed': 'bg-secondary'
    }
    return status_classes.get(status.value if hasattr(status, 'value') else status, 'bg-light')

def get_status_text(status):
    """Get Russian text for booking status"""
    status_texts = {
        'pending': 'Ожидает',
        'confirmed': 'Подтверждено',
        'cancelled': 'Отменено',
        'completed': 'Завершено'
    }
    return status_texts.get(status.value if hasattr(status, 'value') else status, status)

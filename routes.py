from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required
from app import app, db
from models import Booking, Customer, Message, BookingStatus
from helpers import (get_dashboard_stats, get_weekly_chart_data, 
                    get_status_text, get_status_badge_class,
                    format_datetime, format_date,
                    send_message_to_customer)
import logging

logger = logging.getLogger(__name__)

@app.route('/booking/<int:booking_id>/update_status', methods=['POST'])
@login_required
def update_booking_status(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    new_status = request.form['status']
    
    try:
        booking.status = BookingStatus(new_status)
        db.session.commit()
        
        # Notify customer
        customer = booking.customer
        status_messages = {
            'confirmed': f'Ваша бронь на {format_datetime(booking.booking_date)} подтверждена! ✅',
            'cancelled': f'Ваша бронь на {format_datetime(booking.booking_date)} отменена.',
            'completed': f'Спасибо за посещение! Надеемся, вам понравилось! 🎪'
        }
        
        if new_status in status_messages:
            try:
                send_message_to_customer(customer.telegram_id, status_messages[new_status])
            except Exception as e:
                logger.error(f"Ошибка отправки сообщения: {e}")
        
        flash(f'Статус брони обновлен на "{get_status_text(new_status)}"', 'success')
    except ValueError:
        flash('Некорректный статус', 'error')
        logger.error(f"Некорректный статус: {new_status}")
    except Exception as e:
        flash('Ошибка при обновлении статуса', 'error')
        logger.error(f"Ошибка обновления статуса: {e}")
    
    return redirect(url_for('bookings'))

@app.route('/messages')
@login_required
def messages():
    page = request.args.get('page', 1, type=int)
    customer_id = request.args.get('customer_id', type=int)
    
    query = Message.query
    
    if customer_id:
        query = query.filter(Message.customer_id == customer_id)
        # Mark messages as read when viewing customer conversation
        Message.query.filter(
            Message.customer_id == customer_id,
            Message.from_admin == False,
            Message.read == False
        ).update({'read': True})
        try:
            db.session.commit()
        except Exception as e:
            logger.error(f"Ошибка пометки сообщений как прочитанных: {e}")
    
    messages = query.order_by(Message.created_at.desc()).paginate(
        page=page, per_page=50, error_out=False
    )
    
    customers = Customer.query.order_by(Customer.last_activity.desc()).all()
    
    return render_template('messages.html', 
                         messages=messages,
                         customers=customers,
                         customer_id=customer_id,
                         format_datetime=format_datetime)

@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    customer_id = request.form['customer_id']
    message_text = request.form['message']
    
    customer = Customer.query.get_or_404(customer_id)
    
    try:
        success = send_message_to_customer(customer.telegram_id, message_text)
        if success:
            # Save message to database
            message = Message(
                customer_id=customer.id,
                content=message_text,
                from_admin=True
            )
            db.session.add(message)
            db.session.commit()
            flash('Сообщение отправлено', 'success')
        else:
            flash('Ошибка отправки сообщения', 'error')
            logger.error(f"Ошибка отправки сообщения клиенту {customer_id}")
    except Exception as e:
        flash('Ошибка отправки сообщения', 'error')
        logger.error(f"Ошибка отправки сообщения: {e}")
    
    return redirect(url_for('messages', customer_id=customer_id))

@app.route('/analytics')
@login_required
def analytics():
    stats = get_dashboard_stats()
    chart_data = get_weekly_chart_data()

    top_customers = db.session.query(
        Customer,
        db.func.count(Booking.id).label('booking_count')
    ).join(Booking).group_by(Customer.id).order_by(
        db.func.count(Booking.id).desc()
    ).limit(10).all()

    booking_status_counts = db.session.query(
        Booking.status,
        db.func.count(Booking.id)
    ).group_by(Booking.status).all()

    return render_template(
        'analytics.html',
        stats=stats,
        chart_data=chart_data,
        top_customers=top_customers,
        booking_status_counts=booking_status_counts,
        get_status_text=get_status_text
    )

# Template filters
@app.template_filter('datetime')
def datetime_filter(dt):
    return format_datetime(dt)

@app.template_filter('date')
def date_filter(dt):
    return format_date(dt)

@app.template_filter('status_badge')
def status_badge_filter(status):
    return get_status_badge_class(status)

@app.template_filter('status_text')
def status_text_filter(status):
    return get_status_text(status)

from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app import app, db
from models import Admin, Customer, Booking, Message, BookingStatus
from utils import get_dashboard_stats, get_weekly_chart_data, format_datetime, format_date, get_status_badge_class, get_status_text
from bot import send_message_to_customer
import logging

@app.route('/')
@login_required
def dashboard():
    stats = get_dashboard_stats()
    chart_data = get_weekly_chart_data()
    
    # Recent activities
    recent_customers = Customer.query.order_by(Customer.created_at.desc()).limit(5).all()
    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(5).all()
    unread_messages = Message.query.filter(
        Message.from_admin == False,
        Message.read == False
    ).order_by(Message.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         stats=stats,
                         chart_data=chart_data,
                         recent_customers=recent_customers,
                         recent_bookings=recent_bookings,
                         unread_messages=unread_messages,
                         format_datetime=format_datetime,
                         get_status_badge_class=get_status_badge_class,
                         get_status_text=get_status_text)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and check_password_hash(admin.password_hash, password):
            login_user(admin)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Неверное имя пользователя или пароль', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/customers')
@login_required
def customers():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Customer.query
    
    if search:
        query = query.filter(
            db.or_(
                Customer.first_name.contains(search),
                Customer.last_name.contains(search),
                Customer.username.contains(search),
                Customer.phone.contains(search)
            )
        )
    
    customers = query.order_by(Customer.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('customers.html', 
                         customers=customers, 
                         search=search,
                         format_datetime=format_datetime)

@app.route('/bookings')
@login_required
def bookings():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = Booking.query
    
    if status_filter:
        query = query.filter(Booking.status == BookingStatus(status_filter))
    
    bookings = query.order_by(Booking.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('bookings.html', 
                         bookings=bookings,
                         status_filter=status_filter,
                         BookingStatus=BookingStatus,
                         format_datetime=format_datetime,
                         format_date=format_date,
                         get_status_badge_class=get_status_badge_class,
                         get_status_text=get_status_text)

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
            send_message_to_customer(customer.telegram_id, status_messages[new_status])
        
        flash(f'Статус брони обновлен на "{get_status_text(new_status)}"', 'success')
    except ValueError:
        flash('Некорректный статус', 'error')
    
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
        db.session.commit()
    
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
    
    if send_message_to_customer(customer.telegram_id, message_text):
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
    
    return redirect(url_for('messages', customer_id=customer_id))

@app.route('/analytics')
@login_required
def analytics():
    stats = get_dashboard_stats()
    chart_data = get_weekly_chart_data()
    
    # Additional analytics
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
    
    return render_template('analytics.html',
                         stats=stats,
                         chart_data=chart_data,
                         top_customers=top_customers,
                         booking_status_counts=booking_status_counts,
                         get_status_text=get_status_text)

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

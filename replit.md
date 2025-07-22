# Trampoline Park Telegram Bot Management System

## Overview

This is a Flask-based web application that manages a Telegram bot for a trampoline park business. The system provides a comprehensive admin dashboard to manage customer interactions, bookings, and messages through a Telegram bot interface. The bot allows customers to make bookings, contact administrators, and get park information, while the web interface gives administrators full visibility and control over all interactions.

## User Preferences

```
Preferred communication style: Simple, everyday language.
```

## System Architecture

### Backend Architecture
- **Framework**: Flask with SQLAlchemy ORM
- **Database**: SQLite (configured for easy migration to PostgreSQL)
- **Authentication**: Flask-Login for session management
- **Bot Framework**: pyTelegramBotAPI (telebot) for Telegram integration
- **Template Engine**: Jinja2 with Bootstrap 5 dark theme

### Frontend Architecture
- **UI Framework**: Bootstrap 5 with dark theme
- **Icons**: Font Awesome 6
- **Charts**: Chart.js for analytics visualization
- **Styling**: Custom CSS with CSS variables for theming
- **JavaScript**: Vanilla JS for dashboard interactivity

## Key Components

### Database Models
- **Admin**: User accounts for web dashboard access
- **Customer**: Telegram users who interact with the bot
- **Booking**: Customer reservation requests with status tracking
- **Message**: Chat messages between customers and admins
- **BotStats**: Daily analytics and usage statistics

### Bot Functionality
- **Command Handling**: Structured conversation flow with user state management
- **Booking System**: Multi-step booking process with validation
- **Message Relay**: Customer-to-admin communication system
- **Webhook Support**: Production-ready webhook configuration

### Web Dashboard Features
- **Authentication System**: Secure admin login with session management
- **Analytics Dashboard**: Real-time statistics and trend visualization
- **Customer Management**: Search, filter, and view customer profiles
- **Booking Management**: Status updates and booking lifecycle tracking
- **Message Center**: Two-way communication with Telegram users

## Data Flow

### Bot Interaction Flow
1. Customer sends message to Telegram bot
2. Bot processes command and updates user state
3. Database records customer interaction and creates/updates records
4. Bot responds with appropriate message or keyboard
5. For bookings/messages, admin receives notification in dashboard

### Admin Management Flow
1. Admin logs into web dashboard
2. Views real-time statistics and recent activities
3. Manages bookings (approve/reject/modify status)
4. Responds to customer messages through web interface
5. Bot sends admin responses back to customers via Telegram

### Analytics Flow
1. Bot interactions automatically generate statistics
2. Daily stats are aggregated and stored
3. Dashboard displays trends and metrics
4. Charts visualize user engagement and booking patterns

## External Dependencies

### Core Dependencies
- **Flask**: Web framework and routing
- **SQLAlchemy**: Database ORM and migrations
- **pyTelegramBotAPI**: Telegram bot integration
- **Werkzeug**: WSGI utilities and security helpers

### Frontend Dependencies
- **Bootstrap 5**: UI framework (CDN)
- **Font Awesome 6**: Icon library (CDN)
- **Chart.js**: Analytics visualization (CDN)

### Configuration Requirements
- **TELEGRAM_TOKEN**: Bot token from BotFather
- **WEBHOOK_URL**: Public URL for webhook (production)
- **DATABASE_URL**: Database connection string
- **SESSION_SECRET**: Flask session encryption key

## Deployment Strategy

### Development Setup
- SQLite database for local development
- Debug mode enabled for live reloading
- Environment variables for configuration
- Local Flask development server on port 5000

### Production Considerations
- Webhook configuration for Telegram bot
- ProxyFix middleware for reverse proxy deployment
- Database connection pooling with automatic reconnection
- Session management with secure secret keys
- HTTPS required for Telegram webhooks

### Environment Configuration
- Development: Local SQLite with debug mode
- Production: PostgreSQL with webhook integration
- Configurable through environment variables
- Graceful fallback to default values

### Security Features
- Password hashing with Werkzeug
- Session-based authentication
- CSRF protection through Flask-Login
- Input validation and sanitization
- Secure webhook verification for Telegram
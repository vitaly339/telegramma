from app import app
from bot import setup_webhook
import logging

if __name__ == '__main__':
    # Setup webhook for production
    with app.app_context():
        setup_webhook()
    
    logging.info("Starting Trampoline Park Dashboard on port 5000")
    app.run(host='0.0.0.0', port=5000, debug=True)

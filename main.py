import threading
import sys
import os
from dotenv import load_dotenv

# লোড এনভায়রনমেন্ট
load_dotenv()

sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'bot'))

from app.routes import run_app
from bot.bot_core import run_bot

if __name__ == "__main__":
    if not os.getenv("BOT_TOKEN"):
        print("Error: .env file missing or BOT_TOKEN not set.")
        sys.exit(1)

    print("Starting Amazon Clone System...")
    
    # Run Flask in a separate thread
    flask_thread = threading.Thread(target=run_app)
    flask_thread.daemon = True
    flask_thread.start()
    
    print("Website running on http://127.0.0.1:5000")
    
    # Run Bot in main thread
    run_bot()

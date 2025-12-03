import threading
import sys
import os

# ফোল্ডারগুলো যাতে পাইথন খুঁজে পায়
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'bot'))

from app.routes import run_app, TELEGRAM_BOT_TOKEN
from bot.bot_core import run_bot

if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN":
    print("Error: app/routes.py ফাইলে আপনার টেলিগ্রাম বট টোকেন বসান।")
    sys.exit(1)

if __name__ == "__main__":
    print("Starting System...")
    
    # ওয়েবসাইট আলাদা থ্রেডে চলবে
    flask_thread = threading.Thread(target=run_app)
    flask_thread.daemon = True
    flask_thread.start()
    
    print("Website running on http://127.0.0.1:5000")
    
    # বট মেইন থ্রেডে চলবে
    run_bot(TELEGRAM_BOT_TOKEN)

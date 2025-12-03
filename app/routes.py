from flask import Flask, render_template, request, jsonify, send_from_directory
import requests
import uuid
import sys
import os
from dotenv import load_dotenv

# পাথ সেটআপ
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import data_manager

TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("P_C_ID")

app = Flask(__name__, template_folder='../templates', static_folder='../static')

@app.route('/')
def home():
    return render_template('index.html', products=data_manager.get_products())

@app.route('/search')
def search():
    q = request.args.get('q', '').lower()
    return render_template('index.html', products=[p for p in data_manager.get_products() if q in p['name'].lower()])

@app.route('/product/<id>')
def product_detail(id):
    p = next((x for x in data_manager.get_products() if x['id'] == id), None)
    if p: return render_template('product.html', product=p)
    return "Product Not Found", 404

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/place_order', methods=['POST'])
def place_order():
    data = request.json
    data['order_id'] = str(uuid.uuid4())[:8]
    data_manager.add_order(data)
    
    # Telegram Notification Logic
    try:
        msg = f"📦 <b>New Order Received! (#{data['order_id']})</b>\n\n"
        msg += f"👤 Name: {data['customer_name']}\n"
        msg += f"📞 Phone: {data['phone']}\n"
        msg += f"🏠 Address: {data['address']}\n"
        msg += f"💰 Total: ${data['total']}\n\n"
        msg += "<b>Items:</b>\n"
        for i in data['items']:
            msg += f"- {i['name']} (x{i['qty']})\n"
            
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": CHANNEL_ID, "text": msg, "parse_mode": "HTML"}
        )
    except Exception as e:
        print(f"Telegram Error: {e}")

    return jsonify({"success": True})

def run_app():
    app.run(port=5000, debug=False, use_reloader=False)

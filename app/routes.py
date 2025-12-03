from flask import Flask, render_template, request, jsonify
import requests
import uuid
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import data_manager

# এখানে তোমার টোকেন দাও
TELEGRAM_BOT_TOKEN = os.getenv("YOUR_BOT_TOKEN")
CHANNEL_ID = os.getenv("YOUR_CHANNEL_ID")

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
    return render_template('product.html', product=p) if p else ("Not Found", 404)

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/place_order', methods=['POST'])
def place_order():
    data = request.json
    data['order_id'] = str(uuid.uuid4())[:8]
    data_manager.add_order(data)
    try:
        msg = f"📦 <b>নতুন অর্ডার! (#{data['order_id']})</b>\n👤 {data['customer_name']}\n📞 {data['phone']}\n🏠 {data['address']}\n💰 মোট: ৳ {data['total']}\n\n<b>পণ্য:</b>\n" + "\n".join([f"- {i['name']} (x{i['qty']})" for i in data['items']])
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", json={"chat_id": CHANNEL_ID, "text": msg, "parse_mode": "HTML"})
    except: pass
    return jsonify({"success": True})

def run_app():
    app.run(port=5000, debug=False, use_reloader=False)

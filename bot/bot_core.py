from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler
import uuid
import os
import sys
from dotenv import load_dotenv

# লোড এনভায়রনমেন্ট
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import data_manager

NAME, QTY, PRICE, DESC, PHOTO, EDIT_VAL = range(6)

async def start(u, c): await u.message.reply_text("Admin Control Panel:\n/addproduct - Add Item\n/edit - Edit Item\n/delete - Delete Item")

# --- ADD PRODUCT FLOW ---
async def add(u, c): await u.message.reply_text("Enter Product Name:"); return NAME
async def gn(u, c): c.user_data['n'] = u.message.text; await u.message.reply_text("Enter Quantity:"); return QTY
async def gq(u, c): c.user_data['q'] = u.message.text; await u.message.reply_text("Enter Price (Number only):"); return PRICE
async def gp(u, c): c.user_data['p'] = u.message.text; await u.message.reply_text("Enter Description:"); return DESC
async def gd(u, c): c.user_data['d'] = u.message.text; await u.message.reply_text("Send Product Photo:"); return PHOTO
async def gph(u, c):
    f = await u.message.photo[-1].get_file()
    fn = f"{uuid.uuid4()}.jpg"
    # Ensure static/uploads exists (Double check)
    if not os.path.exists('static/uploads'): os.makedirs('static/uploads')
    await f.download_to_drive(f"static/uploads/{fn}")
    
    p = {
        "id": str(uuid.uuid4())[:8],
        "name": c.user_data['n'],
        "quantity": c.user_data['q'],
        "price": c.user_data['p'],
        "description": c.user_data['d'],
        "image": f"/static/uploads/{fn}"
    }
    lst = data_manager.get_products()
    lst.append(p)
    data_manager.save_products(lst)
    await u.message.reply_text("✅ Product Added Successfully! Done."); return ConversationHandler.END

async def cancel(u, c): await u.message.reply_text("Operation Cancelled."); return ConversationHandler.END

# --- DELETE FLOW ---
async def dele(u, c):
    kb = [[InlineKeyboardButton(p['name'], callback_data=f"del_{p['id']}")] for p in data_manager.get_products()]
    if not kb: await u.message.reply_text("No products to delete."); return
    await u.message.reply_text("Select Product to Delete:", reply_markup=InlineKeyboardMarkup(kb))

async def dconf(u, c):
    q = u.callback_query; await q.answer()
    if "del_" in q.data:
        c.user_data['did'] = q.data.split("_")[1]
        await q.edit_message_text("Are you sure?", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Yes, Delete", callback_data="yd"), InlineKeyboardButton("Cancel", callback_data="nd")]]))
    elif q.data == "yd":
        lst = [p for p in data_manager.get_products() if p['id'] != c.user_data['did']]
        data_manager.save_products(lst)
        await q.edit_message_text("❌ Deleted Successfully.")
    else: await q.edit_message_text("Cancelled.")

# --- EDIT FLOW ---
async def edit(u, c):
    kb = [[InlineKeyboardButton(p['name'], callback_data=f"ed_{p['id']}")] for p in data_manager.get_products()]
    if not kb: await u.message.reply_text("No products to edit."); return
    await u.message.reply_text("Select Product to Edit:", reply_markup=InlineKeyboardMarkup(kb))

async def ed_h(u, c):
    q = u.callback_query; await q.answer()
    if "ed_" in q.data:
        c.user_data['eid'] = q.data.split("_")[1]
        await q.edit_message_text("What to change?", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Name", callback_data="f_name"), InlineKeyboardButton("Price", callback_data="f_price")]]))
    elif "f_" in q.data:
        c.user_data['f'] = q.data.split("_")[1]
        await q.message.reply_text(f"Enter new {c.user_data['f']}:"); return EDIT_VAL

async def save_e(u, c):
    v = u.message.text
    lst = data_manager.get_products()
    for p in lst:
        if p['id'] == c.user_data['eid']: p[c.user_data['f']] = v
    data_manager.save_products(lst)
    await u.message.reply_text("✅ Updated Successfully."); return ConversationHandler.END

def run_bot():
    token = os.getenv("BOT_TOKEN")
    if not token: print("Error: BOT_TOKEN missing in .env"); return
    
    app = Application.builder().token(token).build()
    
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("addproduct", add)], 
        states={
            NAME:[MessageHandler(filters.TEXT, gn)], 
            QTY:[MessageHandler(filters.TEXT, gq)], 
            PRICE:[MessageHandler(filters.TEXT, gp)], 
            DESC:[MessageHandler(filters.TEXT, gd)], 
            PHOTO:[MessageHandler(filters.PHOTO, gph)]
        }, 
        fallbacks=[CommandHandler("cancel", cancel)]
    ))
    
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("edit", edit), CallbackQueryHandler(ed_h, pattern="^ed_")], 
        states={EDIT_VAL:[MessageHandler(filters.TEXT, save_e)]}, 
        fallbacks=[CommandHandler("cancel", cancel)]
    ))
    
    app.add_handler(CommandHandler("delete", dele))
    app.add_handler(CallbackQueryHandler(dconf, pattern="^(del_|yd|nd)"))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(ed_h, pattern="^f_"))
    
    print("Bot is polling..."); app.run_polling()

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler
import uuid
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import data_manager

NAME, QTY, PRICE, DESC, PHOTO, EDIT_VAL = range(6)

async def start(u, c): await u.message.reply_text("স্বাগতম!\n/addproduct - যোগ করুন\n/edit - এডিট\n/delete - ডিলেট")
async def add(u, c): await u.message.reply_text("নাম লিখুন:"); return NAME
async def gn(u, c): c.user_data['n'] = u.message.text; await u.message.reply_text("কোয়ান্টিটি:"); return QTY
async def gq(u, c): c.user_data['q'] = u.message.text; await u.message.reply_text("দাম:"); return PRICE
async def gp(u, c): c.user_data['p'] = u.message.text; await u.message.reply_text("বিবরণ:"); return DESC
async def gd(u, c): c.user_data['d'] = u.message.text; await u.message.reply_text("ছবি দিন:"); return PHOTO
async def gph(u, c):
    f = await u.message.photo[-1].get_file()
    fn = f"{uuid.uuid4()}.jpg"
    await f.download_to_drive(f"static/uploads/{fn}")
    p = {"id": str(uuid.uuid4())[:8], "name": c.user_data['n'], "quantity": c.user_data['q'], "price": c.user_data['p'], "description": c.user_data['d'], "image": f"/static/uploads/{fn}"}
    lst = data_manager.get_products(); lst.append(p); data_manager.save_products(lst)
    await u.message.reply_text("✅ Done."); return ConversationHandler.END

async def dele(u, c):
    kb = [[InlineKeyboardButton(p['name'], callback_data=f"del_{p['id']}")] for p in data_manager.get_products()]
    await u.message.reply_text("ডিলেট করতে ক্লিক করুন:", reply_markup=InlineKeyboardMarkup(kb))
async def dconf(u, c):
    q = u.callback_query; await q.answer()
    if "del_" in q.data:
        c.user_data['did'] = q.data.split("_")[1]
        await q.edit_message_text("নিশ্চিত?", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("হ্যাঁ", callback_data="yd"), InlineKeyboardButton("না", callback_data="nd")]]))
    elif q.data == "yd":
        lst = [p for p in data_manager.get_products() if p['id'] != c.user_data['did']]
        data_manager.save_products(lst); await q.edit_message_text("মুছে ফেলা হয়েছে।")
    else: await q.edit_message_text("বাতিল।")

async def edit(u, c):
    kb = [[InlineKeyboardButton(p['name'], callback_data=f"ed_{p['id']}")] for p in data_manager.get_products()]
    await u.message.reply_text("এডিট করতে বাছুন:", reply_markup=InlineKeyboardMarkup(kb))
async def ed_h(u, c):
    q = u.callback_query; await q.answer()
    if "ed_" in q.data:
        c.user_data['eid'] = q.data.split("_")[1]
        await q.edit_message_text("কী বদলাবেন?", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("নাম", callback_data="f_name"), InlineKeyboardButton("দাম", callback_data="f_price")]]))
    elif "f_" in q.data:
        c.user_data['f'] = q.data.split("_")[1]
        await q.message.reply_text(f"নতুন {c.user_data['f']} লিখুন:"); return EDIT_VAL
async def save_e(u, c):
    v = u.message.text; lst = data_manager.get_products()
    for p in lst:
        if p['id'] == c.user_data['eid']: p[c.user_data['f']] = v
    data_manager.save_products(lst); await u.message.reply_text("আপডেট হয়েছে।"); return ConversationHandler.END

def run_bot(token):
    app = Application.builder().token(token).build()
    app.add_handler(ConversationHandler(entry_points=[CommandHandler("addproduct", add)], states={NAME:[MessageHandler(filters.TEXT, gn)], QTY:[MessageHandler(filters.TEXT, gq)], PRICE:[MessageHandler(filters.TEXT, gp)], DESC:[MessageHandler(filters.TEXT, gd)], PHOTO:[MessageHandler(filters.PHOTO, gph)]}, fallbacks=[]))
    app.add_handler(ConversationHandler(entry_points=[CommandHandler("edit", edit), CallbackQueryHandler(ed_h, pattern="^ed_")], states={EDIT_VAL:[MessageHandler(filters.TEXT, save_e)]}, fallbacks=[]))
    app.add_handler(CommandHandler("delete", dele))
    app.add_handler(CallbackQueryHandler(dconf, pattern="^(del_|yd|nd)"))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(ed_h, pattern="^f_"))
    print("Bot polling..."); app.run_polling()

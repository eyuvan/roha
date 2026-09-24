import sqlite3
import json
import os
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS
from telegram import Update, ReplyKeyboardMarkup, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# ⚠️ 1. የእርስዎን መረጃዎች እዚህ በትክክል ያስገቡ
# ከBotFather ያገኘኸውን አዲሱን ቶከን እዚህ ሳጥን ውስጥ ብቻ ተካው
BOT_TOKEN = "8991112828:AAGDaTtFAccldDfn-FF2GK2WG2l3rN2UKTo"
WEB_APP_URL = "https://github.io" 
ADMIN_ID = 400234494  # የራስህን የቴሌግราม ID ቁጥር እዚህ ተካው

PORT = int(os.environ.get('PORT', 8000))

# ----------------- 2. የዳታቤዝ አወቃቀር -----------------
def init_db():
    conn = sqlite3.connect("lucky_bingo.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            lang TEXT DEFAULT 'am',
            main_wallet REAL DEFAULT 10.00,
            play_wallet REAL DEFAULT 0.00,
            is_registered INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def get_player(user_id):
    conn = sqlite3.connect("lucky_bingo.db")
    cursor = conn.cursor()
    cursor.execute("SELECT lang, main_wallet, play_wallet, is_registered FROM players WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def register_or_update_player(user_id, username, lang='am'):
    conn = sqlite3.connect("lucky_bingo.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO players (user_id, username, lang) 
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET username = ?
    """, (user_id, username, lang, username))
    conn.commit()
    conn.close()

def update_lang(user_id, lang):
    conn = sqlite3.connect("lucky_bingo.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE players SET lang = ? WHERE user_id = ?", (lang, user_id))
    conn.commit()
    conn.close()

def update_registration(user_id):
    conn = sqlite3.connect("lucky_bingo.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE players SET is_registered = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def admin_add_money(user_id, amount):
    conn = sqlite3.connect("lucky_bingo.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE players SET main_wallet = main_wallet + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()


# ----------------- 3. የ FLASK API ሰርቨር -----------------
api_app = Flask(__name__)
CORS(api_app)

@api_app.route('/')
def home():
    return "Lucky Bingo Server is Running!"

@api_app.route('/api/get_balance', methods=['GET'])
def api_get_balance():
    user_id = request.args.get('user_id')
    player = get_player(user_id)
    if player:
        return jsonify({"main_wallet": player[1], "play_wallet": player[2]})
    return jsonify({"main_wallet": 10.00, "play_wallet": 0.00})

@api_app.route('/api/buy_cartela', methods=['POST'])
def api_buy_cartela():
    data = request.json
    user_id = data.get('user_id')
    cost = 10.00

    conn = sqlite3.connect("lucky_bingo.db")
    cursor = conn.cursor()
    cursor.execute("SELECT main_wallet FROM players WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    
    if row and row[0] >= cost:
        cursor.execute("UPDATE players SET main_wallet = main_wallet - ?, play_wallet = play_wallet + ? WHERE user_id = ?", (cost, cost, user_id))
        conn.commit()
        cursor.execute("SELECT main_wallet, play_wallet FROM players WHERE user_id = ?", (user_id,))
        new_bal = cursor.fetchone()
        conn.close()
        return jsonify({"success": True, "main_wallet": new_bal[0], "play_wallet": new_bal[1]})
    
    conn.close()
    return jsonify({"success": False, "message": "ይቅርታ፣ በቂ ሂሳብ የለዎትም!"})

def run_api():
    api_app.run(host='0.0.0.0', port=PORT)
    # ----------------- 4. የቋንቋዎች ትርጉም መዋቅር -----------------
TEXTS = {
    'am': {
        'welcome': "እንኳን ወደ እድል ቢንጎ (Lucky Bingo) በደህና መጡ! 🎰\nእባክዎ መጀመሪያ ይመዝገቡ (Register)።",
        'registered': "✅ ምዝገባዎ በተሳካ ሁኔታ ተጠናቋል። አሁን መጫወት ይችላሉ!",
        'already_reg': "ℹ️ ቀድመው ተመዝግበዋል።",
        'balance': "📈 የእርስዎ ቀሪ ሂሳብ:\n🔹 Main Wallet: {:.2f} ብር\n🔸 Play Wallet: {:.2f} ብር",
        'deposit': "💰 በቴሌብር (telebirr) ገንዘብ ለማስገባት፡\n\n👇 በዚህ ስልክ ቁጥር ላይ ያስገቡ፡\n📞 0928361886\n\nገንዘብ ካስገቡ በኋላ የትራንስፈር ደረሰኙን እና የእርስዎን መታወቂያ (ID: {}) ለሳፖርት ይላኩ።",
        'instruction': "📖 የጨዋታ መመሪያ፡\n1. ጨዋታው ሲጀምር እስከ 5 ካርቴላ ይምረጡ።\n2. በ49 ሰከንድ ውስጥ መርጠው ይጨርሱ።\n3. ቁጥሮች በላይቭ ሲጠሩ የእርስዎ ካርቴላ ቀድሞ ከሞላ ያሸንፋሉ!",
        'support': "📞 እገዛ ለማግኘት፡ ወደ ደንበኛ አገልግሎት @LuckyBingoSupport ያነጋግሩ።",
        'lang_select': "🌐 እባክዎ ቋንቋ ይምረጡ / Please select a language:",
        'lang_changed': "✅ ቋንቋ ወደ አማርኛ ተቀይሯል።"
    }
}

def get_main_menu():
    keyboard = [
        ['📝 Register', '🚀 Start Game'],
        ['💰 Deposit', '💵 Withdraw'],
        ['📈 Balance', 'ℹ️ Instruction'],
        ['🌐 Language', '📞 Support']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# ----------------- 5. የቦቱ መልዕክት መቆጣጠሪያዎች -----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or "User"
    register_or_update_player(user_id, username)
    player = get_player(user_id)
    lang = player[0] if player and player[0] in TEXTS else 'am'
    await update.message.reply_text(TEXTS[lang]['welcome'], reply_markup=get_main_menu())

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    player = get_player(user_id)
    if not player: return
    lang, main_w, play_w, is_reg = player
    if lang not in TEXTS: lang = 'am'

    if text == '📝 Register':
        if is_reg == 1:
            await update.message.reply_text(TEXTS[lang]['already_reg'])
        else:
            update_registration(user_id)
            await update.message.reply_text(TEXTS[lang]['registered'])
    elif text == '🚀 Start Game':
        full_url = f"{WEB_APP_URL}?user_id={user_id}"
        keyboard = [[InlineKeyboardButton("Open Lucky Bingo 🎰", web_app=WebAppInfo(url=full_url))]]
        await update.message.reply_text("Click below to play:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif text == '📈 Balance':
        await update.message.reply_text(TEXTS[lang]['balance'].format(main_w, play_w))
    elif text == '💰 Deposit':
        await update.message.reply_text(TEXTS[lang]['deposit'].format(user_id))
    elif text == 'ℹ️ Instruction':
        await update.message.reply_text(TEXTS[lang]['instruction'])
    elif text == '📞 Support':
        await update.message.reply_text(TEXTS[lang]['support'])
    elif text == '🌐 Language':
        lang_keyboard = [
            [InlineKeyboardButton("አማርኛ", callback_data='lang_am')]
        ]
        await update.message.reply_text(TEXTS[lang]['lang_select'], reply_markup=InlineKeyboardMarkup(lang_keyboard))

async def admin_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ ይህንን ትዕዛዝ ለመጠቀም ፈቃድ የለዎትም።")
        return
    try:
        target_user = int(context.args[0])
        amount = float(context.args[1])
        admin_add_money(target_user, amount)
        await update.message.reply_text(f"✅ {amount} ብር ለተጠቃሚ {target_user} በተሳካ ሁኔታ ተጨምሯል።")
        await context.bot.send_message(chat_id=target_user, text=f"🎉 {amount} ብር ያስገቡት በባለስልጣኑ ጸድቆ ወደ ዋሌትዎ ገብቷል!")
    except:
        await update.message.reply_text("❌ ስህተት! አጻጻፍ ምሳሌ፦ /deposit 5412589 100")
async def lang_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    selected_lang = query.data.split('_')[1]
    update_lang(user_id, selected_lang)
    if selected_lang in TEXTS:
        await query.message.reply_text(TEXTS[selected_lang]['lang_changed'])
    else:
        await query.message.reply_text("Language Updated")


# ----------------- 6. ዋናው የቦት ማስነሻ (MAIN) -----------------
# ----------------- 6. ዋናው የቦት ማስነሻ (ለ Render የተስተካከለ) -----------------
def main():
    init_db()
    
    # Render ላይ አፑ እንዳይዘጋ የ Flask ሰርቨሩን በዋናው መስመር (Main Thread) እናስነሳዋለን
    # የቴሌግራም ቦቱን ደግሞ በጀርባ (Background Thread) እናስጀምረዋለን
    def run_bot_polling():
        app = Application.builder().token(BOT_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("deposit", admin_deposit))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        app.add_handler(CallbackQueryHandler(lang_callback))
        
        print("የቴሌግራም ቦት በጀርባ ስራ ጀምሯል...")
        app.run_polling(close_loop=False)

    # ቦቱን በጀርባ Thread ማስነሳት
    bot_thread = threading.Thread(target=run_bot_polling, daemon=True)
    bot_thread.start()
    
    # የFlask API ሰርቨሩን በዋናው መስመር ማስነሳት (Renderን ሰላም ለመስጠት)
    print(f"እድል ቢንጎ የFlask API በፖርት {PORT} ላይ ስራ ጀምሯል...")
    api_app.run(host='0.0.0.0', port=PORT)

if __name__ == '__main__':
    main()
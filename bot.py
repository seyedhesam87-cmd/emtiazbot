import sqlite3
import threading
import os

from flask import Flask

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)


TOKEN = "8518374866:AAH1lQOv232coEfgOn4RRhkXl6MgMvkScmw"


users = [
    "سیدمرتضی",
    "امیرعلی",
    "سیدمحمدرضا",
    "علیرضا",
    "حیدر",
    "رضا",
    "محمدطاها",
    "سام"
]


# ---------------- RENDER WEB SERVER ----------------

web_app = Flask(__name__)


@web_app.route("/")
def home():
    return "Bot is running"


def run_web():
    web_app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )


threading.Thread(target=run_web).start()


# ---------------- DATABASE ----------------

db = sqlite3.connect("scores.db", check_same_thread=False)
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS scores(
    name TEXT PRIMARY KEY,
    point INTEGER DEFAULT 0
)
""")


for user in users:
    cur.execute(
        "INSERT OR IGNORE INTO scores(name, point) VALUES(?,0)",
        (user,)
    )

db.commit()


# ---------------- START ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🤖 ربات امتیازدهی فعال شد\n\n"
        "/add  ثبت یا تغییر امتیاز\n"
        "/score  نمایش امتیازات"
    )


# ---------------- ADD ----------------

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):

    buttons = [
        [
            InlineKeyboardButton(
                user,
                callback_data=f"user:{user}"
            )
        ]
        for user in users
    ]


    await update.message.reply_text(
        "👤 یک شخص را انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )



# ---------------- SCORE ----------------

async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):

    cur.execute(
        "SELECT * FROM scores ORDER BY point DESC"
    )

    data = cur.fetchall()

    text = "🏆 امتیازات:\n\n"

    for name, point in data:
        text += f"{name}: {point}\n"


    await update.message.reply_text(text)



# ---------------- BUTTONS ----------------

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    data = query.data


    if data.startswith("user:"):

        name = data.replace("user:", "")

        context.user_data["selected_user"] = name


        keyboard = [
            [
                InlineKeyboardButton(
                    "➕ افزایش",
                    callback_data="mode:add"
                ),

                InlineKeyboardButton(
                    "➖ کاهش",
                    callback_data="mode:sub"
                )
            ]
        ]


        await query.edit_message_text(
            f"✅ {name} انتخاب شد\n\nنوع عملیات را انتخاب کن:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


    elif data.startswith("mode:"):

        mode = data.split(":")[1]

        context.user_data["mode"] = mode


        await query.edit_message_text(
            "✏️ حالا مقدار امتیاز را به صورت عدد ارسال کن:"
        )



# ---------------- NUMBER HANDLER ----------------

async def add_point(update: Update, context: ContextTypes.DEFAULT_TYPE):

    selected = context.user_data.get("selected_user")

    mode = context.user_data.get("mode")


    if not selected or not mode:

        await update.message.reply_text(
            "اول یک کاربر را انتخاب کن (/add)"
        )

        return


    try:

        point = int(update.message.text)


        if mode == "sub":

            point = -abs(point)



        cur.execute(
            "UPDATE scores SET point = point + ? WHERE name=?",
            (point, selected)
        )

        db.commit()



        context.user_data.pop(
            "selected_user",
            None
        )

        context.user_data.pop(
            "mode",
            None
        )



        await update.message.reply_text(
            f"✅ ثبت شد\n\n"
            f"👤 {selected}\n"
            f"📊 تغییر: {point:+}"
        )



    except ValueError:

        await update.message.reply_text(
            "❌ فقط عدد وارد کن"
        )



# ---------------- MAIN ----------------

def main():

    app = Application.builder().token(TOKEN).build()


    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("add", add)
    )

    app.add_handler(
        CommandHandler("score", score)
    )


    app.add_handler(
        CallbackQueryHandler(button)
    )


    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            add_point
        )
    )


    print("Bot Started")


    app.run_polling()



if __name__ == "__main__":

    main()
import sqlite3

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
    "محمدطاها"
]


# دیتابیس
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


selected_user = {}



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🤖 ربات امتیاز دهی فعال شد\n\n"
        "/add  ثبت امتیاز\n"
        "/score  نمایش امتیازات"
    )



async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):

    buttons = []

    for user in users:
        buttons.append([
            InlineKeyboardButton(
                user,
                callback_data=f"user:{user}"
            )
        ])

    await update.message.reply_text(
        "شخص را انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )



async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):

    cur.execute(
        "SELECT * FROM scores ORDER BY point DESC"
    )

    data = cur.fetchall()

    text = "🏆 امتیازات:\n\n"

    for name, point in data:
        text += f"{name}: {point}\n"


    await update.message.reply_text(text)



async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()


    if query.data.startswith("user:"):

        name = query.data.replace("user:", "")

        selected_user[query.from_user.id] = name


        await query.edit_message_text(
            f"✅ {name} انتخاب شد\n\n"
            "حالا عدد امتیاز را بفرست:"
        )



async def add_point(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.message.from_user.id


    if user_id not in selected_user:
        return


    try:

        point = int(update.message.text)

        name = selected_user[user_id]


        cur.execute(
            "UPDATE scores SET point = point + ? WHERE name=?",
            (point, name)
        )

        db.commit()


        del selected_user[user_id]


        await update.message.reply_text(
            f"✅ ثبت شد\n\n"
            f"{name}\n"
            f"+{point} امتیاز"
        )


    except:

        await update.message.reply_text(
            "لطفاً فقط عدد بفرست"
        )




def main():

    app = Application.builder().token(TOKEN).build()


    app.add_handler(CommandHandler("start", start))

    app.add_handler(CommandHandler("add", add))

    app.add_handler(CommandHandler("score", score))

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
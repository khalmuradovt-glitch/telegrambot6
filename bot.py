import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

import os

TOKEN = os.getenv("TOKEN")
GOOGLE_SHEETS_URL = "https://script.google.com/macros/s/AKfycbxWKcas3Q1i3jIt3gp2t8vxfs3PhIzv7ecz1SBVROGbGvRdhX0cZeCXQXUN12qHYTs/exec"

users = {}

LANG = {

"ru":{
"name":"1️⃣ Имя и фамилия водителя",
"satisfied":"2️⃣ Вы довольны нашим сервисом?",
"yes":"👍 Да",
"no":"👎 Нет",
"like":"3️⃣ Что вам нравится в сервисе?",
"team":"👨‍🔧 Команда специалистов",
"system":"⚙️ Налаженная система",
"fast":"⚡ Быстрое реагирование",
"all":"⭐ Все из вышеперечисленных",
"comment":"3️⃣ Оставьте свои комментарии для улучшения сервиса",
"phone":"📱 Напишите номер телефона",
"rating":"4️⃣ Общая оценка сервиса",
"thanks":"Команда Unique Consulting благодарит вас за ваш ответ✅"
},

"en":{
"name":"1️⃣ Driver full name",
"satisfied":"2️⃣ Are you satisfied with our service?",
"yes":"👍 Yes",
"no":"👎 No",
"like":"3️⃣ What do you like about the service?",
"team":"👨‍🔧 Professional team",
"system":"⚙️ Well organized system",
"fast":"⚡ Fast response",
"all":"⭐ All of the above",
"comment":"3️⃣ Please leave your comment to improve the service",
"phone":"📱 Please type your phone number",
"rating":"4️⃣ Overall service rating",
"thanks":"Unique Consulting team thanks you for your answer✅"
},

"uz":{
"name":"1️⃣ Haydovchining ism familiyasi",
"satisfied":"2️⃣ Servisimizdan mamnunmisiz?",
"yes":"👍 Ha",
"no":"👎 Yo‘q",
"like":"3️⃣ Sizga servisda nima yoqadi?",
"team":"👨‍🔧 Mutaxassislar jamoasi",
"system":"⚙️ Yaxshi tashkil etilgan tizim",
"fast":"⚡ Tezkor javob",
"all":"⭐ Barchasi",
"comment":"3️⃣ Servisni yaxshilash uchun fikringizni yozing",
"phone":"📱 Telefon raqamingizni yozing",
"rating":"4️⃣ Servis umumiy bahosi",
"thanks":"Unique Consulting jamoasi nomidan javobingiz uchun rahmat✅"
}

}

# ---------- START ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = InlineKeyboardMarkup([
        [
        InlineKeyboardButton("🇷🇺 Русский",callback_data="lang_ru"),
        InlineKeyboardButton("🇬🇧 English",callback_data="lang_en"),
        InlineKeyboardButton("🇺🇿 O'zbek",callback_data="lang_uz")
        ]
    ])

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Select language / Tilni tanlang / Выберите язык",
        reply_markup=keyboard
    )

# ---------- CALLBACK ----------

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user=query.from_user.id
    chat=query.message.chat.id
    data=query.data

    if data.startswith("lang"):

        lang=data.split("_")[1]

        users[user]={
            "lang":lang,
            "step":"name",
            "data":{
                "user":query.from_user.username,
                "user_id":user
            }
        }

        await context.bot.send_message(
        chat_id=chat,
        text=LANG[lang]["name"]
        )

        return

    if user not in users:
        return

    state=users[user]
    lang=state["lang"]

    if data=="yes":

        state["data"]["satisfied"]="yes"

        keyboard=InlineKeyboardMarkup([
        [InlineKeyboardButton(LANG[lang]["team"],callback_data="like_team")],
        [InlineKeyboardButton(LANG[lang]["system"],callback_data="like_system")],
        [InlineKeyboardButton(LANG[lang]["fast"],callback_data="like_fast")],
        [InlineKeyboardButton(LANG[lang]["all"],callback_data="like_all")]
        ])

        await context.bot.send_message(
        chat_id=chat,
        text=LANG[lang]["like"],
        reply_markup=keyboard
        )

        return

    if data=="no":

        state["data"]["satisfied"]="no"
        state["step"]="comment"

        await context.bot.send_message(
        chat_id=chat,
        text=LANG[lang]["comment"]
        )

        return

    if data.startswith("like"):

        state["data"]["likes"]=data

        keyboard=InlineKeyboardMarkup([
        [
        InlineKeyboardButton("⭐1",callback_data="rate_1"),
        InlineKeyboardButton("⭐2",callback_data="rate_2"),
        InlineKeyboardButton("⭐3",callback_data="rate_3"),
        InlineKeyboardButton("⭐4",callback_data="rate_4"),
        InlineKeyboardButton("⭐5",callback_data="rate_5")
        ]
        ])

        await context.bot.send_message(
        chat_id=chat,
        text=LANG[lang]["rating"],
        reply_markup=keyboard
        )

        return

    if data.startswith("rate"):

        rating=data.split("_")[1]
        state["data"]["rating"]=rating

        payload=state["data"]

        try:
            requests.post(GOOGLE_SHEETS_URL,json=payload)
        except:
            pass

        await context.bot.send_message(
        chat_id=chat,
        text=LANG[lang]["thanks"]
        )

        del users[user]

# ---------- TEXT ----------

async def text(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user=update.effective_user.id
    chat=update.effective_chat.id
    msg=update.message.text

    if user not in users:
        return

    state=users[user]
    lang=state["lang"]

    if state["step"]=="name":

        state["data"]["driver"]=msg

        keyboard=InlineKeyboardMarkup([
        [
        InlineKeyboardButton(LANG[lang]["yes"],callback_data="yes"),
        InlineKeyboardButton(LANG[lang]["no"],callback_data="no")
        ]
        ])

        await context.bot.send_message(
        chat_id=chat,
        text=LANG[lang]["satisfied"],
        reply_markup=keyboard
        )

        state["step"]="satisfied"
        return

    if state["step"]=="comment":

        state["data"]["comment"]=msg
        state["step"]="phone"

        await context.bot.send_message(
        chat_id=chat,
        text=LANG[lang]["phone"]
        )

        return

    if state["step"]=="phone":

        state["data"]["phone"]=msg
        state["step"]="rating"

        keyboard=InlineKeyboardMarkup([
        [
        InlineKeyboardButton("⭐1",callback_data="rate_1"),
        InlineKeyboardButton("⭐2",callback_data="rate_2"),
        InlineKeyboardButton("⭐3",callback_data="rate_3"),
        InlineKeyboardButton("⭐4",callback_data="rate_4"),
        InlineKeyboardButton("⭐5",callback_data="rate_5")
        ]
        ])

        await context.bot.send_message(
        chat_id=chat,
        text=LANG[lang]["rating"],
        reply_markup=keyboard
        )

# ---------- RUN ----------

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text))

app.run_polling()

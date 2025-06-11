from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler

from gpt import *
from util import *

TELEGRAM_CHATBOT_TOKEN = "7776004057:AAHsozoY2O4LKQXQ3e9lS78TrnhvJfdzgLg"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = load_message('main')
    await send_photo(update, context, 'main')
    await send_text(update, context, msg)
    await show_main_menu(update, context, {
        "start": "головне меню бота",
        "profile": "генерація Tinder-профілю 😎",
        "opener": "повідомлення для знайомства 🥰",
        "message": "листування від вашого імені 😈",
        "date": "листування із зірками 🔥",
        "gpt": "поставити запитання чату GPT 🧠",
    })


async def answer_to_user_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if dialog.mode == 'gpt':
        await gpt_dialog(update, context)
    elif dialog.mode == 'date':
        await date_dialog(update, context)
    elif dialog.mode == 'message':
        await message_dialog(update, context)
    elif dialog.mode == 'profile':
        await profile_dialog(update, context)
    elif dialog.mode == 'opener':
        await opener_dialog(update, context)
    else:
        await send_text(update, context, "Вибач, я поки не розумію твоє питання!")


async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = 'gpt'
    await send_photo(update, context, 'gpt')
    msg = load_message('gpt')
    await send_text(update, context, msg)


async def gpt_dialog(update: Update, context):
    question = update.message.text
    prompt = load_prompt('gpt')
    answer = await chat_gpt.send_question(prompt, question)
    await send_text(update, context, answer)


async def date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = 'date'
    await send_photo(update, context, 'date')
    msg = load_message('date')
    await send_text_buttons(update, context, msg, {
        'date_grande': 'Аріана Гранде',
        'date_robbie': 'Марго Роббі',
        'date_zendaya': 'Зендея',
        'date_gosling': 'Райан Гослінг',
        'date_hardy': 'Том Харді',
    })


async def date_buttons(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()
    await send_photo(update, context, query)
    await send_text(update, context, 'Гарний вибір! Вперед! Запроси цю людину на побачення!')
    prompt = load_prompt(query)
    chat_gpt.set_prompt(prompt)


async def date_dialog(update, context):
    text = update.message.text
    msg = await send_text(update, context, 'Користувач набирає повідомлення...')
    answer = await chat_gpt.add_message(text)
    await msg.edit_text(answer)


async def message(update, context):
    dialog.mode = 'message'
    msg = load_message('message')
    await send_photo(update, context, 'message')
    await send_text_buttons(update, context, msg, {
        "message_next": 'Придумай наступне повідомлення',
        "message_date": 'Напиши як класно Запросити на побачення',
    })

    dialog.list.clear()


async def message_dialog(update, context):
    text = update.message.text
    dialog.list.append(text)


async def message_buttons(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()

    prompt = load_prompt(query)
    user_chat_history = "\n\n".join(dialog.list)

    msg = await send_text(update, context, 'Думаю над варіантами...')
    answer = await chat_gpt.send_question(prompt, user_chat_history)
    await msg.edit_text(answer)


async def profile(update, context):
    dialog.mode = 'profile'
    msg = load_message('profile')
    await send_photo(update, context, 'profile')
    await send_text(update, context, msg)

    dialog.counter = 0
    dialog.user.clear()
    await send_text(update, context, 'Як вас звати і скільки Вам років?')


async def profile_dialog(update, context):
    text = update.message.text
    dialog.counter += 1

    if dialog.counter == 1:
        dialog.user['name'] = text
        await send_text(update, context, "Ким ви працюєте?")
    if dialog.counter == 2:
        dialog.user['occupation'] = text
        await send_text(update, context, "У вас є хобі?")
    if dialog.counter == 3:
        dialog.user['hobby'] = text
        await send_text(update, context, "Що вам НЕ подобається в людях?")
    if dialog.counter == 4:
        dialog.user['annoys'] = text
        await send_text(update, context, "Мета знайомства?")
    if dialog.counter == 5:
        dialog.user['goals'] = text

        prompt = load_prompt('profile')
        user_info = dialog_user_info_to_str(dialog.user)
        message = await send_text(update, context, "Ми генеруємо ваш профіль. Зачекайте декілька секунд...")

        answer = await chat_gpt.send_question(prompt, user_info)
        await message.edit_text(answer)
        dialog.mode = None


async def opener(update, context):
    dialog.mode = 'opener'
    msg = load_message('opener')
    await send_photo(update, context, 'opener')
    await send_text(update, context, msg)

    dialog.counter = 0
    dialog.user.clear()
    await send_text(update, context, 'Яке імя дівчини?')


async def opener_dialog(update, context):
    text = update.message.text
    dialog.counter += 1

    if dialog.counter == 1:
        dialog.user['name'] = text
        await send_text(update, context, "Скільки років партнеру?")
    if dialog.counter == 2:
        dialog.user['age'] = text
        await send_text(update, context, "Оцініть зовнішність в 1 до 10?")
    if dialog.counter == 3:
        dialog.user['handsome'] = text
        await send_text(update, context, "Ким вона працює?")
    if dialog.counter == 4:
        dialog.user['occupation'] = text
        await send_text(update, context, "Мета знайомства?")
    if dialog.counter == 5:
        dialog.user['goals'] = text

        prompt = load_prompt('opener')
        user_info = dialog_user_info_to_str(dialog.user)
        message = await send_text(update, context, "Ми генеруємо повідомлення...")

        answer = await chat_gpt.send_question(prompt, user_info)
        await message.edit_text(answer)
        dialog.mode = None


dialog = Dialog()
dialog.mode = None
dialog.list = []
dialog.user = {}
dialog.counter = 0

CHAT_GPT_TOKEN = "gpt:AU54YW8RRi4TXANWp060hfjiJxU6btLIvPmqxAgYF0QLgPDwmNfdLT5NyC9Y8r_u4QZeQmwhzFJFkblB3T4yhgCdA9W2KZIQwDchnwN-SRJKHph3pqraKQNsAmcDeSXdm_4aNY-8_3oiLFalGXckzNJlfA-T"

chat_gpt = ChatGptService(CHAT_GPT_TOKEN)

app = ApplicationBuilder().token(TELEGRAM_CHATBOT_TOKEN).build()
app.add_handler(CommandHandler('start', start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer_to_user_text))
app.add_handler(CommandHandler('gpt', gpt))
app.add_handler(CommandHandler('date', date))
app.add_handler(CommandHandler('message', message))
app.add_handler(CommandHandler('profile', profile))
app.add_handler(CommandHandler('opener', opener))
app.add_handler(CallbackQueryHandler(date_buttons, pattern="date_.*"))
app.add_handler(CallbackQueryHandler(message_buttons, pattern="message_.*"))
app.run_polling()

from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler, MessageHandler, filters
from gpt import ChatGptService
from util import (load_message, send_text, send_image, show_main_menu, load_prompt, send_text_buttons,
                  Dialog, create_dictionary_for_talk_buttons, extract_prompts_for_talks_with_famous_people)
import credentials


async def default_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    query = update.callback_query.data
    if dialog.mode == "random" or dialog.mode == "talk":
        if query == "more_button":
            await random(update, context)
        elif query == "end_button":
            await start(update, context)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = "default"
    text = load_message('main')
    await send_image(update, context, 'main')
    await send_text(update, context, text)
    await show_main_menu(update, context, {
        'start': 'Головне меню',
        'random': 'Дізнатися випадковий цікавий факт 🧠',
        'gpt': 'Задати питання чату GPT 🤖',
        'talk': 'Поговорити з відомою особистістю 👤',
        'quiz': 'Взяти участь у квізі ❓'
    })


async def random(update:Update, context:ContextTypes.DEFAULT_TYPE):
    dialog.mode = "random"
    text = load_message("random")
    await send_image(update, context, "random")
    await send_text(update, context, text)
    prompt = load_prompt("random")
    content = await chat_gpt.send_question(prompt, "Дай цікавий факт")
    await send_text_buttons(update, context, content, {
        "more_button": "Хочу еще факт",
        "end_button": "Завершить"
    })


async def gpt(update:Update, context: ContextTypes.DEFAULT_TYPE):
    print("GPT mode")
    await send_text(update, context, "gpt")
    await send_text(update, context, load_message("gpt"))
    dialog.mode = "gpt"
    chat_gpt.set_prompt(load_message("gpt"))


async def talk(update:Update, context: ContextTypes.DEFAULT_TYPE):
    print("talk mode")
    dialog.mode = "talk"
    text = load_message("talk")
    await send_image(update, context, "talk")
    await send_text(update, context, text)
    await send_text_buttons(update, context, text, buttons=create_dictionary_for_talk_buttons())


async def handle_gpt_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if dialog.mode == "gpt" or dialog.mode == "talk":
#        print("зашли в handle_gpt_message")
        text = update.message.text
        answer = await chat_gpt.add_message(text)
        print("\nMessage GPT handler: \tОтвет Chat GPT: ", answer)
        if dialog.mode == "gpt":
            await send_text(update, context, answer)
        elif dialog.mode == "talk":
            await send_text_buttons(update, context, answer, {
                "end_button": "Завершить"
            })


async def app_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    query = update.callback_query.data
    if dialog.mode == "talk":
        prompt = load_prompt(query)
        chat_gpt.set_prompt(prompt)
        await send_text(update, context, "Личность выбрана. Начните разговор")


# async def quiz(update:Update, context: ContextTypes.DEFAULT_TYPE):
#     print("quiz mode")
#     pass


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("\nMessage handler: \tМой вопрос: ", update.message.text)
    if dialog.mode == "gpt":
        await handle_gpt_message(update, context)
    if dialog.mode == "talk":
#        print("зашли в handle_message")
        await handle_gpt_message(update, context)


dialog = Dialog()
dialog.mode = "default" #динамическое добавление атрибута экземпляру класса Dialog


chat_gpt = ChatGptService(credentials.ChatGPT_TOKEN)
app = ApplicationBuilder().token(credentials.BOT_TOKEN).build()

# Зареєструвати обробник команди можна так:
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("random", random))
app.add_handler(CommandHandler("gpt", gpt))
app.add_handler(CommandHandler("talk", talk))
# app.add_handler(CommandHandler("quiz", quiz))
app.add_handler(MessageHandler(filters.TEXT, handle_message))

# Зареєструвати обробник колбеку можна так:
app.add_handler(CallbackQueryHandler(app_button_handler, pattern='^talk_.*'))
app.add_handler(CallbackQueryHandler(default_callback_handler))
app.run_polling()

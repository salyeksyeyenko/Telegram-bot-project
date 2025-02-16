import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message, \
    BotCommand, MenuButtonCommands, BotCommandScopeChat, MenuButtonDefault
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes



# конвертує об'єкт user в рядок
def dialog_user_info_to_str(user_data) -> str:
    mapper = {
        'language_from': 'Язык оригинала',
        'language_to': 'Язык перевода',
        'text_to_translate': 'Текст для перевода'
    }
    return '\n'.join(map(lambda k, v: (mapper[k], v), user_data.items()))  #здесь есть ошибка: лямбда-функция ожидает два аргумента, но map передает только один кортеж


# надсилає в чат текстове повідомлення
async def send_text(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> Message:
    if text.count('_') % 2 != 0:
        message = f"Строка '{text}' является невалидной с точки зрения markdown. Воспользуйтесь методом send_html()"
        print(message)
        return await update.message.reply_text(message)

    text = text.encode('utf16', errors='surrogatepass').decode('utf16')
    return await context.bot.send_message(chat_id=update.effective_chat.id,
                                          text=text,
                                          parse_mode=ParseMode.MARKDOWN)


# надсилає в чат html повідомлення
async def send_html(update: Update, context: ContextTypes.DEFAULT_TYPE,
                    text: str) -> Message:
    text = text.encode('utf16', errors='surrogatepass').decode('utf16')
    return await context.bot.send_message(chat_id=update.effective_chat.id,
                                          text=text, parse_mode=ParseMode.HTML)


# надсилає в чат текстове повідомлення, та додає до нього кнопки
async def send_text_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE,
                            text: str, buttons: dict) -> Message:
    text = text.encode('utf16', errors='surrogatepass').decode('utf16')
    keyboard = []
    for key, value in buttons.items():
        button = InlineKeyboardButton(str(value), callback_data=str(key))
        keyboard.append([button])
    reply_markup = InlineKeyboardMarkup(keyboard)
    return await context.bot.send_message(
        update.effective_message.chat_id,
        text=text, reply_markup=reply_markup,
        message_thread_id=update.effective_message.message_thread_id)


# Надсилає в чат фото
async def send_image(update: Update, context: ContextTypes.DEFAULT_TYPE,
                     name: str) -> Message:
    with open(f'resources/images/{name}.jpg', 'rb') as image:
        return await context.bot.send_photo(chat_id=update.effective_chat.id,
                                            photo=image)


# Відображає команду та головне меню
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE,
                         commands: dict):
    command_list = [BotCommand(key, value) for key, value in commands.items()]
    await context.bot.set_my_commands(command_list, scope=BotCommandScopeChat(
        chat_id=update.effective_chat.id))
    await context.bot.set_chat_menu_button(menu_button=MenuButtonCommands(),
                                           chat_id=update.effective_chat.id)


# видаляємо команди для конкретного чату
async def hide_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.delete_my_commands(
        scope=BotCommandScopeChat(chat_id=update.effective_chat.id))
    await context.bot.set_chat_menu_button(menu_button=MenuButtonDefault(),
                                           chat_id=update.effective_chat.id)


# завантажує повідомлення з папки /resources/messages/
def load_message(name):
    with open("resources/messages/" + name + ".txt", "r",
              encoding="utf8") as file:
        return file.read()


# завантажує промпт з папки /resources/messages/
def load_prompt(name):
    with open("resources/prompts/" + name + ".txt", "r",
              encoding="utf8") as file:
        return file.read()


async def default_callback_handler(update: Update,
                                   context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    query = update.callback_query.data
    await send_html(update, context, f'You have pressed button with {query} callback')


# Формируем список из названий из всех промптов, которые начинаются на talk_
def extract_talk_file_names():
    directory = "resources/prompts/"
    all_files = os.listdir(directory)
    file_names = [file.split(".")[0] for file in all_files if file.startswith("talk_")]
    return file_names


# Формируем словарь с промптами, которые будут использованы для talk функционала
def extract_prompts_for_talks_with_famous_people():
    prompts = {}

    for name in extract_talk_file_names():
        prompt = load_prompt(name)
        # Поиск имени известной личности для дальнейшего использования в названиях кнопок
        text_frame = prompt[:30]
        start = text_frame.find("-") + 1
        end = text_frame.find(",", start)
        famous_person = text_frame[start:end].strip()
        prompts[famous_person] = prompt

    return prompts


# Словарь, который будет передаваться в функцию talk для создания кнопок с известными личностями
def create_dictionary_for_talk_buttons():
    file_names = extract_talk_file_names()
    famous_person_ua = list(extract_prompts_for_talks_with_famous_people().keys())
    combined_dictionary = dict(zip(file_names, famous_person_ua))
    return combined_dictionary



class Dialog:
    pass

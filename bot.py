from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
import json
import os

# Токен бота
TOKEN = '7999621432:AAHXPeZhdwikdek7IWzQ_8k-YRvLfWtwTmQ'

# Загрузка списка пользователей с ролями
def load_users():
    if os.path.exists("users.json"):
        with open("users.json", "r", encoding="utf-8") as file:
            return json.load(file)
    return {}

# Сохранение пользователей
def save_users(users):
    with open("users.json", "w", encoding="utf-8") as file:
        json.dump(users, file, ensure_ascii=False, indent=4)

# Пользователи с ролями
users = load_users()

# Кнопки меню
def main_menu():
    keyboard = [[InlineKeyboardButton("Моя роль", callback_data='role')],
               [InlineKeyboardButton("Добавить пользователя", callback_data='adduser')]]
    return InlineKeyboardMarkup(keyboard)

# Функция старта
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    if chat_id in users:
        role = users[chat_id]["role"]
        await update.message.reply_text(f"Привет, {users[chat_id]['name']}! Твоя роль: {role}.", reply_markup=main_menu())
    else:
        await update.message.reply_text("Привет! Ты ещё не зарегистрирован. Управляющий может добавить тебя.", reply_markup=main_menu())

# Обработка нажатий на кнопки
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'role':
        chat_id = str(query.message.chat_id)
        role = users.get(chat_id, {}).get("role", "неизвестная роль")
        await query.edit_message_text(f"Твоя роль: {role}", reply_markup=main_menu())
    elif query.data == 'adduser':
        await query.edit_message_text("Использование: /adduser <ID> <Имя> <Роль>", reply_markup=main_menu())

# Добавление нового пользователя (только управляющий)
async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    if users.get(chat_id, {}).get("role") == "управляющий":
        if len(context.args) == 3:
            user_id, name, role = context.args
            users[user_id] = {"name": name, "role": role}
            save_users(users)
            await update.message.reply_text(f"Пользователь {name} с ролью {role} добавлен!", reply_markup=main_menu())
        else:
            await update.message.reply_text("Использование: /adduser <ID> <Имя> <Роль>", reply_markup=main_menu())
    else:
        await update.message.reply_text("У вас нет прав на добавление пользователей.", reply_markup=main_menu())

# Настройка планировщика
scheduler = BackgroundScheduler()
scheduler.start()

# Создание приложения
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("adduser", add_user))
app.add_handler(CallbackQueryHandler(button))

print("Бот запущен...")
app.run_polling()

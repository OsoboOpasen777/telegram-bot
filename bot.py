from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
import json
import os
from datetime import datetime

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

# Список пользователей для времени
active_time_users = set()

# Кнопки меню с регистрацией и времени
def main_menu():
    keyboard = [[InlineKeyboardButton("Моя роль", callback_data='role')],
               [InlineKeyboardButton("Зарегистрироваться", callback_data='register')],
               [InlineKeyboardButton("Получать время", callback_data='start_time')],
               [InlineKeyboardButton("Остановить время", callback_data='stop_time')]]
    return InlineKeyboardMarkup(keyboard)

# Функция старта
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    if chat_id in users:
        role = users[chat_id]["role"]
        await update.message.reply_text(f"Привет, {users[chat_id]['name']}! Твоя роль: {role}.", reply_markup=main_menu())
    else:
        await update.message.reply_text("Привет! Ты ещё не зарегистрирован. Нажми кнопку 'Зарегистрироваться' ниже.", reply_markup=main_menu())

# Регистрация пользователя через кнопку
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = str(query.from_user.id)
    username = query.from_user.username or query.from_user.first_name or 'Пользователь'
    if query.data == 'register':
        if chat_id not in users:
            users[chat_id] = {"name": username, "role": "пользователь"}
            save_users(users)
            await query.message.reply_text(f"Ты успешно зарегистрирован как {username}.")
        else:
            await query.message.reply_text(f"Ты уже зарегистрирован как {users[chat_id]['name']}.")
    elif query.data == 'role':
        role = users.get(chat_id, {}).get("role", "неизвестная роль")
        await query.message.reply_text(f"Твоя роль: {role}")
    elif query.data == 'start_time':
        active_time_users.add(chat_id)
        await query.message.reply_text("Теперь ты будешь получать текущее время каждые 5 секунд.")
    elif query.data == 'stop_time':
        active_time_users.discard(chat_id)
        await query.message.reply_text("Оповещения с временем остановлены.")

# Функция для отправки текущего времени
async def send_time():
    current_time = datetime.now().strftime('%H:%M:%S')
    for chat_id in active_time_users:
        await app.bot.send_message(chat_id=chat_id, text=f"Текущее время: {current_time}")

# Настройка планировщика для отправки времени каждые 5 секунд
scheduler = BackgroundScheduler()
scheduler.add_job(lambda: asyncio.run(send_time()), 'interval', seconds=5)
scheduler.start()

# Создание приложения
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_button))

print("Бот запущен...")
app.run_polling()

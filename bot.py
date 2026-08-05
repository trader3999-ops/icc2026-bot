
import json
import logging
import os
from pathlib import Path
 
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
 
logging.basicConfig(level=logging.INFO)
 
BOT_TOKEN = os.environ.get("BOT_TOKEN", "ВАШ_ТОКЕН_СЮДА")
 
# Ваш личный chat_id или id группы, куда будут падать ВСЕ сообщения (общий центр)
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID", "0"))
 
# Название лагерей по коду ссылки: t.me/ВашБот?start=camp1
CAMPS = {
    "camp1": "Анор",
    "camp2": "Оқ Кема",
    "camp3": "Геолог",
    "camp4": "Зомин",
    "camp5": "Беруний",
    "camp6": "Лочин",
    "camp7": "Чорчинор",
    "camp8": "Боғишамол",
    "camp9": "Бухоро",
    "camp10": "Энержи",
    "camp11": "Умид Нихоллари",
    "camp12": "Нанай",
    "camp13": "Ишонч",
    "camp14": "Сирдарё",
    "camp15": "Амударё",
    "camp16": "Афсона",
    "camp17": "Билимдон",
    "camp18": "Риштон",
    "camp19": "Хумо",
    "camp20": "Қуёшли",
}
 
# chat_id директора (или группы дирекции) для каждого лагеря.
# Директор узнаёт свой chat_id, написав боту /whoami в личном чате.
# Если для лагеря директор ещё не указан — просто оставьте None,
# сообщения всё равно продолжат падать в ADMIN_CHAT_ID.
CAMP_ADMINS = {
    "camp1": None,   # например: 123456789
    "camp2": None,
    "camp3": None,
    "camp4": None,
    "camp5": None,
    "camp6": None,
    "camp7": None,
    "camp8": None,
    "camp9": None,
    "camp10": None,
    "camp11": None,
    "camp12": None,
    "camp13": None,
    "camp14": None,
    "camp15": None,
    "camp16": None,
    "camp17": None,
    "camp18": None,
    "camp19": None,
    "camp20": None,
}
 
GREETING_RU = (
    "🇷🇺 Здравствуйте! Вы отправляете материал от лагеря: {camp}.\n\n"
    "Пришлите, пожалуйста, короткое голосовое или видео (обычно достаточно около минуты). "
    "Расскажите не общий вывод, а один конкретный момент, который вам особенно запомнился:\n\n"
    "«Какое самое неожиданное наблюдение вы сделали после возвращения ребёнка из лагеря?»\n\n"
    "Если не заметили никаких изменений — это тоже ценный для нас ответ.\n\n"
    "Спасибо, что участвуете! 🌍"
)
 
GREETING_UZ = (
    "🇺🇿 Ассалому алайкум! Сиз {camp} оромгоҳидан материал юбормоқдасиз.\n\n"
    "Илтимос, қисқа овозли ёки видео хабар юборинг (одатда бир дақиқа етарли). "
    "Умумий хулоса эмас, сизга алоҳида ёдда қолган бир аниқ лаҳзани айтиб беринг:\n\n"
    "«Фарзандингиз оромгоҳдан қайтгандан кейин энг кутилмаган нимани сездингиз?»\n\n"
    "Агар ҳеч қандай ўзгаришни сезмаган бўлсангиз — бу ҳам биз учун қимматли жавоб.\n\n"
    "Иштирок этганингиз учун раҳмат! 🌍"
)
 
GREETING = GREETING_RU + "\n\n〰️〰️〰️\n\n" + GREETING_UZ
 
THANKS = (
    "🇷🇺 Спасибо огромное! Ваш ответ получен ✅\n\n"
    "🇺🇿 Катта раҳмат! Жавобингиз қабул қилинди ✅"
)
 
DATA_FILE = Path("user_camps.json")
 
 
def load_data():
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    return {}
 
 
def save_data(data):
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))
 
 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    camp_code = context.args[0] if context.args else None
    camp_name = CAMPS.get(camp_code, "Не указан")
 
    data = load_data()
    data[str(user.id)] = {
        "camp_code": camp_code,
        "camp_name": camp_name,
        "name": user.full_name,
        "username": user.username,
    }
    save_data(data)
 
    await update.message.reply_text(GREETING.format(camp=camp_name))
 
 
async def whoami(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Позволяет директору узнать свой chat_id, чтобы вписать его в CAMP_ADMINS."""
    chat = update.effective_chat
    await update.message.reply_text(
        f"🆔 Ваш chat_id: `{chat.id}`\n\n"
        f"Передайте этот номер администратору проекта, "
        f"чтобы он привязал его к вашему лагерю в CAMP_ADMINS.",
        parse_mode="Markdown",
    )
 
 
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = load_data()
    info = data.get(str(user.id), {})
    camp_name = info.get("camp_name", "Не указан (не был запущен /start по ссылке лагеря)")
    camp_code = info.get("camp_code")
 
    caption = (
        f"📩 Новое сообщение\n"
        f"Лагерь: {camp_name}\n"
        f"От: {user.full_name} (@{user.username or '—'})"
    )
 
    msg = update.message
 
    # Список получателей: общий админ-чат + (если указан) чат директора этого лагеря
    recipients = [ADMIN_CHAT_ID]
    director_chat_id = CAMP_ADMINS.get(camp_code)
    if director_chat_id:
        recipients.append(director_chat_id)
 
    for chat_id in recipients:
        if msg.voice:
            await context.bot.send_voice(chat_id, msg.voice.file_id, caption=caption)
        elif msg.video:
            await context.bot.send_video(chat_id, msg.video.file_id, caption=caption)
        elif msg.video_note:
            await context.bot.send_video_note(chat_id, msg.video_note.file_id)
            await context.bot.send_message(chat_id, caption)
        elif msg.audio:
            await context.bot.send_audio(chat_id, msg.audio.file_id, caption=caption)
        elif msg.text:
            await context.bot.send_message(chat_id, f"{caption}\n\nТекст: {msg.text}")
        else:
            return
 
    await update.message.reply_text(THANKS)
 
 
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("whoami", whoami))
    app.add_handler(
        MessageHandler(
            filters.VOICE | filters.VIDEO | filters.VIDEO_NOTE | filters.AUDIO | filters.TEXT,
            handle_media,
        )
    )
    app.run_polling()
 
 
if __name__ == "__main__":
    main()

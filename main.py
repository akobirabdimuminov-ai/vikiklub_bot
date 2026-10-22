import os
import time
from telebot import TeleBot, types
import database

TOKEN = os.getenv("BOT_TOKEN", "8490936302:AAFEmxGfQQAe0JujzYipmT-PnypTSkOgRIg")
ADMIN_ID = int(os.getenv("ADMIN_ID", "304538764"))
REQUIRED_CHANNELS = ["uzmu_vikiklub"]

bot = TeleBot(TOKEN)
database.init_db()

user_data = {}

def check_subscriptions(user_id):
    for channel in REQUIRED_CHANNELS:
        try:
            member = bot.get_chat_member(f"@{channel}", user_id)
            if member.status not in ['creator', 'administrator', 'member']:
                return False
        except Exception as e:
            print(f"Kanalni tekshirishda xatolik (@{channel}): {e}")
            return False
    return True

@bot.message_handler(commands=['start'])
def start_handler(message):
    try:
        user_id = message.from_user.id
        if database.is_user_registered(user_id):
            bot.send_message(user_id, "✅ Siz allaqachon ariza topshirgansiz!")
            return

        database.add_user(user_id)
        user_data[user_id] = {}

        msg = "👋 **Xush kelibsiz!**\n\nWikiKlubga a'zo bo'lish uchun anketani to'ldiramiz.\n\n1️⃣ **Ism va Familiyangizni kiriting:**\n_(Masalan: Akobir Abdimo'minov)_"
        sent_msg = bot.send_message(user_id, msg, parse_mode="Markdown")
        bot.register_next_step_handler(sent_msg, process_name)
    except Exception as e:
        print(f"Start handler xatosi: {e}")

def process_name(message):
    try:
        user_id = message.from_user.id
        if user_id not in user_data:
            user_data[user_id] = {}
        user_data[user_id]['full_name'] = message.text

        msg = "2️⃣ **Fakultetingiz, yo'nalishingiz va kursingizni kiriting:**\n_(Masalan: Iqtisodiyot va soliqqa tortish, 1-kurs)_"
        sent_msg = bot.send_message(user_id, msg, parse_mode="Markdown")
        bot.register_next_step_handler(sent_msg, process_faculty)
    except Exception as e:
        print(f"Name handler xatosi: {e}")

def process_faculty(message):
    try:
        user_id = message.from_user.id
        if user_id not in user_data:
            user_data[user_id] = {}
        user_data[user_id]['faculty'] = message.text

        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton(text="Ha ✅", callback_data="sat_yes"),
            types.InlineKeyboardButton(text="Yo'q ❌", callback_data="sat_no")
        )

        msg = "3️⃣ **Shanba kuni klubning yig'inlariga qatnasha olasizmi?**"
        bot.send_message(user_id, msg, reply_markup=markup, parse_mode="Markdown")
    except Exception as e:
        print(f"Faculty handler xatosi: {e}")

@bot.callback_query_handler(func=lambda call: call.data in ["sat_yes", "sat_no"])
def callback_saturday(call):
    try:
        user_id = call.from_user.id
        answer = "Ha ✅" if call.data == "sat_yes" else "Yo'q ❌"
        if user_id not in user_data:
            user_data[user_id] = {}
            
        user_data[user_id]['saturday_attend'] = answer
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass

        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton(text="Ha ✅", callback_data="lap_yes"),
            types.InlineKeyboardButton(text="Yo'q ❌", callback_data="lap_no")
        )
        msg = "4️⃣ **WikiKlubga qabul qilinsangiz, noutbuk olib kela olasizmi?**"
        bot.send_message(user_id, msg, reply_markup=markup, parse_mode="Markdown")
    except Exception as e:
        print(f"Saturday callback xatosi: {e}")

@bot.callback_query_handler(func=lambda call: call.data in ["lap_yes", "lap_no"])
def callback_laptop(call):
    try:
        user_id = call.from_user.id
        answer = "Ha ✅" if call.data == "lap_yes" else "Yo'q ❌"
        if user_id not in user_data:
            user_data[user_id] = {}
            
        user_data[user_id]['has_laptop'] = answer
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass

        msg = "5️⃣ **Aloqa uchun amaldagi telefon raqamingizni kiriting:**\n_(Masalan: +998911234567)_"
        sent_msg = bot.send_message(user_id, msg, parse_mode="Markdown")
        bot.register_next_step_handler(sent_msg, process_phone)
    except Exception as e:
        print(f"Laptop callback xatosi: {e}")

def process_phone(message):
    try:
        user_id = message.from_user.id
        if user_id not in user_data:
            user_data[user_id] = {}
        user_data[user_id]['phone_number'] = message.text

        msg = (
            "6️⃣ **Motivatsion xat yozing:**\n\n"
            "Nima uchun bu klubga qo'shilmoqchisiz? Maqsadlaringiz va rejalaringiz haqida yozing.\n"
            "_(O'rtacha 200 so'zdan iborat bo'lishi talab etiladi)_"
        )
        sent_msg = bot.send_message(user_id, msg, parse_mode="Markdown")
        bot.register_next_step_handler(sent_msg, process_motivation)
    except Exception as e:
        print(f"Phone handler xatosi: {e}")

def process_motivation(message):
    try:
        user_id = message.from_user.id
        if user_id not in user_data:
            user_data[user_id] = {}
            
        user_data[user_id]['motivation'] = message.text
        ask_for_channel_subscription(user_id)
    except Exception as e:
        print(f"Motivation handler xatosi: {e}")

def ask_for_channel_subscription(user_id):
    if check_subscriptions(user_id):
        finalize_registration(user_id)
    else:
        markup = types.InlineKeyboardMarkup()
        for ch in REQUIRED_CHANNELS:
            markup.add(types.InlineKeyboardButton(text=f"➕ A'zo bo'lish @{ch}", url=f"https://t.me/{ch}"))
        
        markup.add(types.InlineKeyboardButton(text="A'zolikni tekshirish 🔄", callback_data="check_final_sub"))

        bot.send_message(
            user_id,
            "🎯 **Anketangiz saqlandi!**\n\nArizani yakunlash uchun quyidagi kanalimizga a'zo bo'ling va tekshirish tugmasini bosing:",
            reply_markup=markup,
            parse_mode="Markdown"
        )

@bot.callback_query_handler(func=lambda call: call.data == "check_final_sub")
def callback_check_final(call):
    user_id = call.from_user.id
    try:
        bot.answer_callback_query(call.id, "Tekshirilmoqda... ⏳")
    except Exception:
        pass
    
    if check_subscriptions(user_id):
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        finalize_registration(user_id)
    else:
        bot.send_message(user_id, "❌ Kanalga a'zo bo'lmadingiz! Iltimos, kanalga a'zo bo'lib qayta urinib ko'ring.")

def finalize_registration(user_id):
    data = user_data.get(user_id)
    if not data or 'full_name' not in data:
        if database.is_user_registered(user_id):
            bot.send_message(user_id, "Siz allaqachon ro'yxatdan o'tgansiz.")
            return
        bot.send_message(user_id, "Xatolik yuz berdi. Iltimos qaytadan /start buyrug'ini bosing.")
        return

    database.save_registration(
        user_id, 
        data['full_name'], 
        data['faculty'], 
        data['saturday_attend'],
        data['has_laptop'],
        data['phone_number'],
        data['motivation']
    )

    bot.send_message(
        user_id,
        "🎉 **Tabriklaymiz! Arizangiz muvaffaqiyatli qabul qilindi va Adminga yuborildi.**\n\n"
        "Tez orada siz bilan bog'lanishadi!",
        parse_mode="Markdown"
    )

    admin_msg = (
        f"📥 **YANGI ARIZA KELDI!**\n\n"
        f"1️⃣ **F.I.SH:** {data['full_name']}\n"
        f"2️⃣ **Fakultet / Kurs:** {data['faculty']}\n"
        f"3️⃣ **Shanba yig'inlariga qatnashishi:** {data['saturday_attend']}\n"
        f"4️⃣ **Noutbuk olib kela oladimi:** {data['has_laptop']}\n"
        f"5️⃣ **Telefon raqami:** {data['phone_number']}\n\n"
        f"6️⃣ **Motivatsiya (Esse):**\n{data['motivation']}\n\n"
        f"🆔 ID: `{user_id}`\n"
        f"🔗 Profil: [Foydalanuvchi](tg://user?id={user_id})"
    )
    
    try:
        print(f"Adminga xabar yuborilmoqda: ADMIN_ID={ADMIN_ID}")
        bot.send_message(ADMIN_ID, admin_msg, parse_mode="Markdown")
        print("Adminga xabar muvaffaqiyatli yetib bordi!")
    except Exception as e:
        print(f"❌ ADMINGA XABAR YUBORISHDA XATOLIK: {e}")

if __name__ == '__main__':
    print("Bot Render.com serverida ishga tushdi...")
    while True:
        try:
            bot.polling(none_stop=True, interval=1, timeout=30)
        except Exception as e:
            print(f"Tarmoq uzilishi: {e}. Qayta ulanmoqda...")
            time.sleep(5)
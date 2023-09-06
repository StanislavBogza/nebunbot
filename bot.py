import telebot, time, random, sqlite3
import time
from datetime import datetime, timedelta
from telebot import types

telebot_token = '6372447942:AAEpuo6vUU-AtFpEhZexVz4vy2Q_TYeJs3M'
bot = telebot.TeleBot(token=telebot_token, parse_mode=None)

def conn_economy():
    conn = sqlite3.connect('economy.db')
    cursor = conn.cursor()
    return conn, cursor


def create_account(message):
    conn, cursor = conn_economy()
    user_id = message.from_user.id
    cursor.execute("SELECT last_generated FROM cont_curent WHERE user_id=?", (user_id,))
    last_generated = cursor.fetchone()

    if not last_generated or not last_generated[0]:
        # If there is no record or it's empty, it means the user has never generated currency before
        cursor.execute("INSERT OR IGNORE INTO cont_curent (user_id, first_name, username, balanta, last_generated) VALUES (?, ?, ?, ?, ?)",
                       (user_id, message.from_user.first_name, message.from_user.username, 1, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, f"💰 {message.from_user.first_name}, a generat cu succes 1 𝖓𝖊𝖑𝖊𝖚.", disable_notification=True)
    else:
        last_generated_time = datetime.strptime(last_generated[0], '%Y-%m-%d %H:%M:%S')
        if datetime.now() - last_generated_time >= timedelta(days=1):
            # Update the `last_generated` field for the current user
            cursor.execute("UPDATE cont_curent SET last_generated=? WHERE user_id=?", (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), user_id))
            conn.commit()
            conn.close()
            bot.send_message(message.chat.id, f"💰 {message.from_user.first_name}, ai generat cu succes 1 𝖓𝖊𝖑𝖊𝖚.", disable_notification=True)
        else:
            conn.close()
            bot.send_message(message.chat.id, f"⏳ {message.from_user.first_name}, poți genera 1 𝖓𝖊𝖑𝖊𝖚 o dată la 24 de ore. Mai așteaptă un pic!", disable_notification=True)
    


@bot.message_handler(commands=['start'])
def start_message_handler(message):
    bot.send_message(message.chat.id, "Noroc")
    bot.delete_message(message.chat.id, message.id)

    # Verificăm dacă există deja un tabel pentru acest utilizator
    conn, cursor = conn_economy()
    user_id = message.from_user.id
    table_name = f"{message.from_user.username}_transactions"

    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY AUTOINCREMENT, amount REAL, date_time TEXT)")
    conn.commit()
    conn.close()


@bot.message_handler(commands=['get']) 
def generate_money_handler(message):
    create_account(message)



@bot.message_handler(commands=['test'])
def test(message):
    bot.send_message('-1001896435951',"test")




@bot.message_handler(commands=['top'])
def top_richest_users(message):
    conn, cursor = conn_economy()
    cursor.execute("SELECT first_name, balanta FROM cont_curent WHERE first_name != 'Banca Nebună' ORDER BY balanta DESC LIMIT 10")
    top_users = cursor.fetchall()
    conn.close()

    if top_users:
        top_message = "🏆 Top cei mai bogați nebuni:\n\n"
        for idx, (username, balance) in enumerate(top_users, start=1):
            top_message += f"{idx}. {username}: {balance} 𝖓𝖊𝖑𝖊𝖎\n"

        bot.send_message(message.chat.id, top_message, disable_notification=True)
    else:
        bot.send_message(message.chat.id, "Încă nu există utilizatori cu balanțe înregistrate.", disable_notification=True)



@bot.message_handler(commands=['bal', 'balance', 'ebal', 'money', 'bani', 'euro', 'dolari', 'ruble', 'hrivne'])
def balance_message_handler(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    conn, cursor = conn_economy()
    cursor.execute("SELECT balanta FROM cont_curent WHERE user_id=?", (user_id,))
    result = cursor.fetchone()  # Obține prima înregistrare corespunzătoare
        

    if result:
        balance = result[0]  # Extrage balanța din rezultat
        bot.send_message(message.chat.id, f"🪙 {first_name}, pe cont ai {balance} 𝖓𝖊𝖑𝖊𝖎", disable_notification=True)

    else:
        create_account(message)
        bot.send_message(message.chat.id, f"💳 {first_name}, ți-am creat un portofel.", disable_notification=True)
    conn.close()

@bot.message_handler(func=lambda message: message.from_user.id == 4627168590)
def delete_message_handler(message):
    bot.delete_message(message.chat.id, message.message_id)

@bot.message_handler(commands=['pay', 'payment', 'trimite', 'send', 'donatie', 'sponsor']) 
def send_money_handler(message):
    try:
        # Descompunem mesajul pentru a obține suma și destinatarul
        command_parts = message.text.split()
        if len(command_parts) != 3:
            bot.send_message(message.chat.id, """🚫 Utilizare incorectă. Folosește:
/pay [suma] @destinatar""", disable_notification=True)
            return

        _, amount_str, recipient_usernamee = command_parts
        amount = float(amount_str)
        recipient_username = recipient_usernamee.replace("@", "")

        # Verificăm dacă suma este pozitivă
        if amount <= 0:
            bot.send_message(message.chat.id, " 🚫 Suma trebuie să fie mai mare decât zero.", disable_notification=True)
            return
        
        # Obținem ID-ul utilizatorului care trimite banii
        sender_id = message.from_user.id
        
        # Verificăm dacă utilizatorul are suficienți bani în portofel
        conn, cursor = conn_economy()
        cursor.execute("SELECT balanta FROM cont_curent WHERE user_id=?", (sender_id,))
        sender_balance = cursor.fetchone()[0]

        if sender_balance < amount:
            bot.send_message(message.chat.id, "❌ Nu ai suficienți bani pentru a trimite această sumă.", disable_notification=True)
    
        else:
            # Obținem Username destinatarului
            cursor.execute("SELECT * FROM cont_curent WHERE username=?", (recipient_username,))
            data = cursor.fetchone()

            if data:
                # Actualizăm balanțele ambilor utilizatori
                cursor.execute("UPDATE cont_curent SET balanta=balanta-? WHERE user_id=?", (amount, sender_id))
                cursor.execute("UPDATE cont_curent SET balanta=balanta+? WHERE username=?", (amount, recipient_username))
                conn.commit()
                bot.send_message(message.chat.id, f"✅ {message.from_user.first_name}, ai trimis {amount} 𝖓𝖊𝖑𝖊𝖎 către @{recipient_username}.", disable_notification=True)
                conn.close()
            else:
                bot.send_message(message.chat.id, f"Destinatarul nu există sau nu are un portofel creat.", disable_notification=True)
        conn.close()
    except Exception as e:
        print(f"Eroare {e}")
        conn.close()








try: #Aici botul ruleaza continuu
    if __name__ == '__main__':
        print('Botul Nebun ruleaza...')
        while True:
            try:
                bot.polling(none_stop=True, timeout=10)
            
            except Exception as e:
                print(f"A apărut o eroare: {e}")
                print("Retrying in 10 seconds...")
                time.sleep(10)
except ValueError:
    print('Ceva erori iaca')
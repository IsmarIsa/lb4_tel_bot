# This Python file uses the following encoding: utf-8
import telebot
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
TOKEN = "6856864039:AAG_rIfcGqEyJ0wUeSTJhUF8vmvnbH5XkEo"
rpc_user = 'kzcashrpc'
rpc_password = 'FlnS33p8F9GRrOks0hoxCmQt'

rpc_connection = AuthServiceProxy(f'http://{rpc_user}:{rpc_password}@127.0.0.1:8276')

bot = telebot.TeleBot(TOKEN)

# старт
@bot.message_handler(commands=['start'])
def send_message(message):
    bot.send_message(message.chat.id, "Привет")
# Обработчик команды getnewaddress
@bot.message_handler(commands=['getnewaddress'])
def get_new_address(message):
    new_address = rpc_connection.getnewaddress()
    bot.reply_to(message, f"Новый адрес кошелька: {new_address}")

# Обработчик команды getbalance
@bot.message_handler(commands=['getbalance'])
def get_balance(message):
    balance = float(rpc_connection.getbalance())
    bot.reply_to(message, f"Баланс кошелька: {balance}")

# Обработчик команды send
@bot.message_handler(commands=['send'])
def send_coins(message):
    global temp
    args = message.text.split()[1:]
    if len(args) != 3: # проверяем количество параметров
        bot.reply_to(message, "Подсказка: /send адрес_отправителя адрес_получателя сумма")
        return
    sender_address, receiver_address, amount = args

    try:
        inputs = rpc_connection.listunspent(0, 9999, [sender_address]) # получаем неиспользованные входы
    except JSONRPCException:
        bot.reply_to(message, f"Неправильный адрес кошелька отправителя")
        return

    # ищем подходящий вход
    for i in inputs:
        temp = i
        if float(float(temp.get("amount"))) > (float(amount)+0.001):
            break
    if float(float(temp.get("amount"))) < (float(amount)+0.001):
        bot.reply_to(message, "Недостаточно средств")
        return

    change = float(temp.get("amount")) - float(amount) - 0.001 #
    inputForTransaction = {"txid":temp.get("txid"), "vout": temp.get("vout")}
    try:
        createTransaction = rpc_connection.createrawtransaction([inputForTransaction], {receiver_address:amount, sender_address:format(change,".8g")})
    except JSONRPCException:
        bot.reply_to(message, f"Что-то пошло не так")
        return
    signTransaction = rpc_connection.signrawtransaction(createTransaction)
    receivedHex = signTransaction.get("hex")
    txid = rpc_connection.sendrawtransaction(receivedHex)
    bot.reply_to(message, f"Монеты успешно отправлены. ID: {txid}")

@bot.message_handler(content_types=['text'])
def send_message(message):
    bot.send_message(message.chat.id, message.text)


if __name__ == '__main__':
    bot.infinity_polling()

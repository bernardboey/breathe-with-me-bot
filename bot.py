import time
import random
import threading
import os

import dotenv
import telebot
from flask import Flask, request

dotenv.load_dotenv()
bot_token = os.environ["BOT_TOKEN"]

bot = telebot.TeleBot(token=bot_token)
server = Flask(__name__)

ENCOURAGEMENT_MESSAGES = [
    "Relax, focus on your breathing!",
    "You're doing great!",
    "Stay with me!",
    "Forget about everything else, and focus inwards."
]
breathe_sessions = {}
HELP_TEXT = ("I can help you regulate your breathing, by sending you regularly timed messages. Breathe along with me!\n"
             "\n"
             "You can control me by sending these commands:\n"
             "\n"
             "/breathe - start breathing with me\n"
             "/stop - stop breathing\n"
             "/faster - increase breathing rate\n"
             "/slower - decrease breathing rate\n"
             "\n"
             "Created with love by @bernard_boey")
DEFAULT_DURATION = 0.6

class BreatheSession:
    def __init__(self, message):
        self.max_count = 4
        self.duration = DEFAULT_DURATION
        self.stop = True
        self.id = message.chat.id

    def breathe(self):
        self.stop = False
        bot.send_message(self.id, "Okay! Stop anytime by telling me /stop")
        time.sleep(1)
        bot.send_message(self.id, "You can also tell me /faster or /slower")
        time.sleep(1)
        bot.send_message(self.id, "Get ready to breathe with me....")
        time.sleep(2)
        counter = 1
        while not self.stop and counter < 100:
            bot.send_message(self.id, "Breathe in......")
            time.sleep(self.duration)
            for i in range(2, self.max_count + 1):
                if self.stop:
                    break
                bot.send_message(self.id, f"...{i}")
                time.sleep(self.duration)
            if self.stop:
                break
            bot.send_message(self.id, "hold...")
            time.sleep(self.duration)
            for i in range(2, self.max_count + 1):
                if self.stop:
                    break
                bot.send_message(self.id, f"...{i}")
                time.sleep(self.duration)
            if self.stop:
                break
            bot.send_message(self.id, "Breathe out......")
            time.sleep(self.duration)
            for i in range(2, self.max_count + 1):
                if self.stop:
                    break
                bot.send_message(self.id, f"...{i}")
                time.sleep(self.duration)
            if self.stop:
                break
            bot.send_message(self.id, "hold...")
            time.sleep(self.duration)
            for i in range(2, self.max_count + 1):
                if self.stop:
                    break
                bot.send_message(self.id, f"...{i}")
                time.sleep(self.duration)
            if counter % 15 == 0:
                bot.send_message(self.id, "Rmb, you can /stop anytime, or go /faster or /slower.")
            if counter % 7 == 0:
                chosen_message = random.choice(ENCOURAGEMENT_MESSAGES)
                bot.send_message(self.id, chosen_message)
            counter += 1
        bot.send_message(self.id, "Okay. I have stopped. Hope you feel better! :-)")
        time.sleep(1)
        bot.send_message(self.id, "You can start again anytime by typing /breathe or /yes")

    def stop_breathing(self):
        self.stop = True

    def increase_duration(self):
        if self.duration >= 1.5:
            bot.send_message(self.id, f"Already at slowest rate ({1 + DEFAULT_DURATION - self.duration:.1f}x)")
        else:
            self.duration += 0.1
            bot.send_message(self.id, f"Okay, breathing slower ({1 + DEFAULT_DURATION - self.duration:.1f}x)")

    def decrease_duration(self):
        if self.duration <= 0.2:
            bot.send_message(self.id, f"Already at fastest rate ({1 + DEFAULT_DURATION - self.duration:.1f}x)")
        else:
            self.duration -= 0.1
            bot.send_message(self.id, f"Okay, breathing faster ({1 + DEFAULT_DURATION - self.duration:.1f}x)")


@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "Hello! Would you like to breathe with me? Type /yes or /breathe to begin")


@bot.message_handler(commands=["help"])
def send_help(message):
    bot.reply_to(message, HELP_TEXT)


@bot.message_handler(commands=["breathe", "yes"])
@bot.message_handler(func=lambda msg: msg.text is not None and msg.text.lower() in ("breathe", "yes"))
def start_breathing(message):
    if message.chat.id not in breathe_sessions.keys():
        breathe_sessions[message.chat.id] = BreatheSession(message)
        breathe_thread = threading.Thread(target=breathe_sessions[message.chat.id].breathe)
        breathe_thread.start()


@bot.message_handler(commands=["stop"])
@bot.message_handler(func=lambda msg: msg.text is not None and msg.text.lower() in ("stop", "no"))
def stop_breathing(message):
    if message.chat.id in breathe_sessions.keys():
        tmp = breathe_sessions.pop(message.chat.id)
        tmp.stop_breathing()
        del tmp


@bot.message_handler(commands=["slower", "slow"])
@bot.message_handler(func=lambda msg: msg.text is not None and msg.text.lower() in ("slower", "slow"))
def increase_duration(message):
    # print(breathe_sessions)
    # print(message.chat.id)
    if message.chat.id in breathe_sessions.keys():
        breathe_sessions[message.chat.id].increase_duration()


@bot.message_handler(commands=["faster", "fast"])
@bot.message_handler(func=lambda msg: msg.text is not None and msg.text.lower() in ("faster", "fast"))
def decrease_duration(message):
    # print(breathe_sessions)
    # print(message.chat.id)
    if message.chat.id in breathe_sessions.keys():
        breathe_sessions[message.chat.id].decrease_duration()


@server.route('/' + bot_token, methods=['POST'])
def get_message():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://breathe-with-me-bb.herokuapp.com/' + bot_token)
    return "!", 200


if __name__ == "__main__":
    bot.polling()
    # server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 8443)))

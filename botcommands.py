from model import nutriBot
from typing import final
from telegram import *
from telegram.ext import *
import asyncio
from database import *

TOKEN : final = "7605325284:AAG6PE47tSPBGwUM6vxLdxxVoe-TpFKtnvk"
BOT_USERNAME : final = "@nutri_mind_bot"

# Conversation states
NAME, GENDER, AGE, HEIGHT, WEIGHT, PASSWORD = range(6)

async def start(update: Update, context: CallbackContext):
    """Handles the /start command."""
    await update.message.reply_text('Hello, I am NutriMind Bot. I assist with nutrition-related queries.')

async def help(update: Update, context: CallbackContext):
    """Handles the /help command."""
    await update.message.reply_text('Use /signup to create an account. I can store and verify your credentials.')

async def signup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Starts the signup process."""
    user_id = update.message.chat.id  
    context.user_data["user_id"] = user_id  

    print(f"[DEBUG] Signup initiated for user {user_id}")  

    await update.message.reply_text("Please enter your name:")
    return NAME  # Move to next step

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receives the user's name."""
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Please enter your gender (Male/Female/Other):")
    return GENDER

async def get_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receives the user's gender."""
    context.user_data["gender"] = update.message.text
    await update.message.reply_text("Please enter your age:")
    return AGE

async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receives the user's age."""
    context.user_data["age"] = update.message.text
    await update.message.reply_text("Please enter your height (in cm):")
    return HEIGHT

async def get_height(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receives the user's height."""
    context.user_data["height"] = update.message.text
    await update.message.reply_text("Please enter your weight (in kg):")
    return WEIGHT

async def get_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receives the user's weight."""
    context.user_data["weight"] = update.message.text
    await update.message.reply_text("Please enter your password:")
    return PASSWORD

async def save_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receives the password and stores the user credentials in the database."""
    password = update.message.text
    user_id = context.user_data.get("user_id")  
    name = context.user_data.get("name")
    gender = context.user_data.get("gender")
    age = context.user_data.get("age")
    height = context.user_data.get("height")
    weight = context.user_data.get("weight")

    if user_id and name and gender and age and height and weight:
        print(f"[DEBUG] Saving user {user_id} with name: {name}, gender: {gender}, age: {age}, height: {height}, weight: {weight}")

        # Store user in database
        await asyncio.to_thread(store_user, user_id, name, gender, age, height, weight)

        if user_exists(user_id):  # Ensure user was stored
            await asyncio.to_thread(store_password, user_id, password)
            await update.message.reply_text("Signup successful! ✅")
            print(f"[SUCCESS] User {user_id} stored in DB.")
        else:
            await update.message.reply_text("Error storing user. Try again.")
            print(f"[ERROR] Failed to store user {user_id} in DB.")

    else:
        await update.message.reply_text("Something went wrong. Please try again.")
        print("[ERROR] Missing user details.")

    return ConversationHandler.END  

async def handle_message(update: Update, context: CallbackContext):
    mess_Type = update.message.chat.type
    text = update.message.text
    print(f'User : {update.message.chat.id} in {mess_Type} : {text}')
    
    if mess_Type == 'group':
        if BOT_USERNAME in text:
            text = text.replace(BOT_USERNAME,'').strip()
            response = nutriBot(text)
            await update.message.reply_text(response)
        else:
            return
    else:
        response = nutriBot(text)
        await update.message.reply_text(response)
        
async def Error(update: Update, context: CallbackContext):
    print(f"update : {update} caused error : {context.error}")
    
conv_handler = ConversationHandler(
    entry_points=[CommandHandler("signup", signup)],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_gender)],
        AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
        HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_height)],
        WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_weight)],
        PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_password)],
    },
    fallbacks=[],
)

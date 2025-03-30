from model import nutriBot
from typing import final
from telegram import *
from telegram.ext import *
import asyncio
from database import store_user, user_exists, get_user_password, update_user_info
from finaldepth import estimate_calories
from calorie_calc import CalorieCalculator
from creatAI import chat
import os

TOKEN: final = "7605325284:AAG6PE47tSPBGwUM6vxLdxxVoe-TpFKtnvk"
BOT_USERNAME: final = "@nutri_mind_bot"

# Conversation states
NAME, GENDER, AGE, HEIGHT, WEIGHT, PASSWORD, EDIT_FIELD, PASSWORD_CONFIRM, EDIT_VALUE = range(9)

calorie = CalorieCalculator('nutrient.csv')
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat.id
    print(f"[DEBUG] Start command triggered for user {user_id}")

    if user_exists(user_id):
        await update.message.reply_text("Welcome back! Use /edit_profile to update your height or weight.")
        return ConversationHandler.END
    
    context.user_data["signup_in_progress"] = True  
    await update.message.reply_text('Hello, I am NutriMind Bot. Let’s get started with signup!\nPlease enter your name:')
    
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    user_id = update.message.chat.id
    context.user_data["name"] = update.message.text
    print(f"[DEBUG] Received Name: {context.user_data['name']} for user {user_id}")  

    await update.message.reply_text("Enter your gender:")
    return GENDER

async def get_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["gender"] = update.message.text
    await update.message.reply_text("Enter your age:")
    return AGE

async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["age"] = update.message.text
    await update.message.reply_text("Please enter your height (in cm):")
    return HEIGHT

async def get_height(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["height"] = update.message.text
    await update.message.reply_text("Please enter your weight (in kg):")
    return WEIGHT

async def get_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["weight"] = update.message.text
    await update.message.reply_text("Please enter your password:")
    return PASSWORD

async def save_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    password = update.message.text  # Get password input
    context.user_data["password"] = password  # ✅ Store password in user_data

    user_id = update.message.chat.id  # Get user ID

    if not user_id:  # ✅ Check if user_id is missing
        await update.message.reply_text("Something went wrong. Please restart the signup process.")
        return ConversationHandler.END  # End the conversation if user_id is missing

    # Fetch other stored user details
    name = context.user_data.get("name")
    gender = context.user_data.get("gender")
    age = context.user_data.get("age")
    height = context.user_data.get("height")
    weight = context.user_data.get("weight")

    print(f"[DEBUG] Data in context before saving: {context.user_data}")  # Debugging

    if all([name, gender, age, height, weight, password]):  # ✅ Ensure all fields exist
        # Store user in the database
        await asyncio.to_thread(store_user, user_id, name, gender, age, height, weight, password)
        await update.message.reply_text("Signup successful! ✅")

        context.user_data.pop("signup_in_progress", None)  # ✅ Keep other data intact
    else:
        await update.message.reply_text("Something went wrong. Please try again.")

    return ConversationHandler.END

async def edit_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["edit_in_progress"] = True  
    await update.message.reply_text("Which field would you like to edit? (Height/Weight)")
    return EDIT_FIELD

async def get_edit_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    field = update.message.text.lower()
    if field not in ["height", "weight"]:
        await update.message.reply_text("Invalid field. Please enter either 'Height' or 'Weight'.")
        return EDIT_FIELD
    context.user_data["edit_field"] = field
    await update.message.reply_text("Please enter your password to confirm:")
    return PASSWORD_CONFIRM

async def confirm_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat.id
    password = update.message.text
    stored_password = get_user_password(user_id)

    if stored_password and stored_password == password:
        await update.message.reply_text(f"Password confirmed! ✅ Now enter your new {context.user_data['edit_field']}:")
        return EDIT_VALUE
    else:
        await update.message.reply_text("❌ Incorrect password! Update canceled.")
        return ConversationHandler.END

async def get_edit_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    value = update.message.text
    user_id = update.message.chat.id
    field = context.user_data.get("edit_field")

    if not value.isdigit():
        await update.message.reply_text("Please enter a valid number.")
        return EDIT_VALUE

    await asyncio.to_thread(update_user_info, user_id, field, value)
    await update.message.reply_text(f"Your {field} has been updated to {value}!")
    
    context.user_data.pop("edit_in_progress", None)
    return ConversationHandler.END

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("signup_in_progress") or context.user_data.get("edit_in_progress"):
        return  
    text = update.message.text
    response = nutriBot(text)  
    await update.message.reply_text(response)

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],  
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

edit_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("edit_profile", edit_profile)],
    states={
        EDIT_FIELD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_edit_field)],
        PASSWORD_CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_password)],
        EDIT_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_edit_value)],
    },
    fallbacks=[],
)
async def download_image(update: Update, context: CallbackContext):
    if not update.message or not update.message.photo:
        return  # Ignore if no photo received
    photo = update.message.photo[-1]  # Get the highest resolution photo
    file_id = photo.file_id
    file = await context.bot.get_file(file_id)
    file_path = os.path.join("/home/cv/frosthack/images", "img.jpg")
    await file.download_to_drive(file_path)
    tup = estimate_calories()
    results = calorie.calculate_calories(tup[0],tup[1])
    response = chat(f""" Food Information: Name: {results['food_name']} 
    - Calories: {results['calories']} kcal (per 100g)
    Macronutrients (per 100g):
    - Carbohydrates: {results['macronutrients']['carbohydrates_g']}g
    - Protein: {results['macronutrients']['protein_g']}g
    - Fat: {results['macronutrients']['fat_g']}g ""","you are a nutritionist generate a Natural language response to given data, try giving a consise response")
    await update.message.reply_text(response)



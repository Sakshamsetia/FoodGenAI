from typing import final
from telegram import *
from telegram.ext import *
from botcommands import *

TOKEN: final = "7605325284:AAG6PE47tSPBGwUM6vxLdxxVoe-TpFKtnvk"
BOT_USERNAME: final = "@nutri_mind_bot"

def main():
    app = Application.builder().token(TOKEN).build()

    # Add handlers
    app.add_handler(conv_handler)
    app.add_handler(edit_conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO,download_image))

    # Start the bot
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
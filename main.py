from typing import final
from telegram import *
from botcommands import *

TOKEN : final = "7605325284:AAG6PE47tSPBGwUM6vxLdxxVoe-TpFKtnvk"
BOT_USERNAME : final = "@nutri_mind_bot"


#Commands
    
if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start",start))
    app.add_handler(CommandHandler("help",help))
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND , handle_message))
    app.run_polling(allowed_updates=Update.ALL_TYPES)
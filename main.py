import os
import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import (
    ApiIdInvalid, PhoneNumberInvalid, PhoneCodeInvalid,
    PhoneCodeExpired, SessionPasswordNeeded, PasswordHashInvalid,
    UserNotParticipant
)
from telethon import TelegramClient
from telethon.errors import (
    ApiIdInvalidError, PhoneNumberInvalidError, PhoneCodeInvalidError,
    PhoneCodeExpiredError, SessionPasswordNeededError, PasswordHashInvalidError
)
from telethon.sessions import StringSession
from dotenv import load_dotenv
from flask import Flask
import threading

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot configuration
API_ID = int(os.getenv("API_ID", "123456"))
API_HASH = os.getenv("API_HASH", "abcdef123456")
BOT_TOKEN = os.getenv("BOT_TOKEN", "123456:ABC-DEF")
DATABASE_URL = os.getenv("DATABASE_URL", "")
MUST_JOIN = os.getenv("MUST_JOIN", "")
PORT = int(os.getenv("PORT", 8080))

# Text messages
START_TEXT = """
**🤖 Welcome to Advanced String Session Generator!**

I can generate **Pyrogram** and **Telethon** string sessions for you.

**Features:**
• Pyrogram v2 Sessions
• Telethon Sessions  
• Bot String Sessions
• User String Sessions
• Secure & Fast Generation

**Click /generate to create your session!**

**🔧 Supported Libraries:**
- Pyrogram
- Telethon
- Pyrogram Bot
- Telethon Bot

**📚 Tutorial:** [Click Here](https://docs.pyrogram.org/)
**💬 Support:** @StarkBotsChat
"""

HELP_TEXT = """
**📖 String Session Bot Help**

**How to Generate Session:**
1. Click /generate or "Generate Session"
2. Choose library type
3. Enter API_ID from https://my.telegram.org
4. Enter API_HASH from https://my.telegram.org
5. Enter phone number (for user) or bot token (for bot)
6. Complete authentication

**📚 Supported Libraries:**
- **Pyrogram**: Modern Telegram MTProto API framework
- **Telethon**: Full-featured Telegram client library  
- **Pyrogram Bot**: For bot accounts using Pyrogram
- **Telethon Bot**: For bot accounts using Telethon

**⚠️ Security Notes:**
• Never share your string session
• Store it securely
• Regenerate if compromised

**Need Help?** @StarkBotsChat
"""

ABOUT_TEXT = """
**👨‍💻 About String Session Bot**

**Version:** 2.0 Advanced
**Framework:** Pyrogram
**Deploy:** Render Compatible

**Features:**
• Multi-library support
• Secure session generation
• Fast & reliable
• Free to use

**Developer:** @StarkProgrammer
**Source Code:** [GitHub](https://github.com)
**Support:** @StarkBotsChat

**🔗 Useful Links:**
• [Pyrogram Documentation](https://docs.pyrogram.org/)
• [Telethon Documentation](https://docs.telethon.dev/)
• [MTProto Documentation](https://core.telegram.org/api)
"""

# Button layouts
START_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("🚀 Generate Session", callback_data="generate")],
    [
        InlineKeyboardButton("📖 Help", callback_data="help"),
        InlineKeyboardButton("👨‍💻 About", callback_data="about")
    ],
    [InlineKeyboardButton("🔧 Source Code", url="https://github.com")]
])

HOME_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("🏠 Home", callback_data="home")]
])

ASK_QUES = "**Please choose the Python library you want to generate string session for:**"
BUTTONS_QUES = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("Pyrogram", callback_data="pyrogram"),
        InlineKeyboardButton("Telethon", callback_data="telethon"),
    ],
    [
        InlineKeyboardButton("Pyrogram Bot", callback_data="pyrogram_bot"),
        InlineKeyboardButton("Telethon Bot", callback_data="telethon_bot"),
    ],
    [InlineKeyboardButton("🏠 Home", callback_data="home")]
])

# User states
user_states = {}

# Initialize Pyrogram client
app = Client(
    "string_session_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True
)

# Start Command
@app.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in user_states:
        del user_states[user_id]
    
    await message.reply_text(
        START_TEXT,
        reply_markup=START_BUTTONS,
        disable_web_page_preview=True
    )

# Help Command
@app.on_message(filters.command("help") & filters.private)
async def help_command(client: Client, message: Message):
    await message.reply_text(
        HELP_TEXT,
        reply_markup=HOME_BUTTONS,
        disable_web_page_preview=True
    )

# About Command
@app.on_message(filters.command("about") & filters.private)
async def about_command(client: Client, message: Message):
    await message.reply_text(
        ABOUT_TEXT,
        reply_markup=HOME_BUTTONS,
        disable_web_page_preview=True
    )

# Generate Command
@app.on_message(filters.command("generate") & filters.private)
async def generate_command(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in user_states:
        del user_states[user_id]
    
    await message.reply_text(ASK_QUES, reply_markup=BUTTONS_QUES)

# Cancel Command
@app.on_message(filters.command("cancel") & filters.private)
async def cancel_command(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in user_states:
        del user_states[user_id]
        await message.reply_text("❌ Process cancelled! Use /generate to start again.")

# Callback Query Handler
@app.on_callback_query()
async def callback_handler(client: Client, callback_query: CallbackQuery):
    query = callback_query.data.lower()
    user_id = callback_query.from_user.id
    
    if query == "home":
        if user_id in user_states:
            del user_states[user_id]
        await callback_query.message.edit_text(
            START_TEXT,
            reply_markup=START_BUTTONS,
            disable_web_page_preview=True
        )
    elif query == "help":
        await callback_query.message.edit_text(
            HELP_TEXT,
            reply_markup=HOME_BUTTONS,
            disable_web_page_preview=True
        )
    elif query == "about":
        await callback_query.message.edit_text(
            ABOUT_TEXT,
            reply_markup=HOME_BUTTONS,
            disable_web_page_preview=True
        )
    elif query == "generate":
        await callback_query.message.edit_text(ASK_QUES, reply_markup=BUTTONS_QUES)
    elif query in ["pyrogram", "telethon", "pyrogram_bot", "telethon_bot"]:
        await callback_query.answer()
        telethon = query.startswith("telethon")
        is_bot = query.endswith("_bot")
        
        # Initialize user state
        user_states[user_id] = {
            "step": "api_id",
            "telethon": telethon,
            "is_bot": is_bot
        }
        
        await callback_query.message.edit_text(
            "**Please send your API_ID:**\n\nGet from https://my.telegram.org\n\nType /cancel to stop"
        )

# Message handler for session generation
@app.on_message(filters.private & filters.text & ~filters.command(["start", "help", "about", "cancel", "generate"]))
async def message_handler(client: Client, message: Message):
    user_id = message.from_user.id
    
    if user_id not in user_states:
        return
    
    state = user_states[user_id]
    user_input = message.text
    
    try:
        if state["step"] == "api_id":
            try:
                api_id = int(user_input)
                user_states[user_id] = {
                    "step": "api_hash",
                    "api_id": api_id,
                    "telethon": state["telethon"],
                    "is_bot": state["is_bot"]
                }
                await message.reply_text("**Please send your API_HASH:**\n\nGet from https://my.telegram.org\n\nType /cancel to stop")
            except ValueError:
                await message.reply_text("❌ Invalid API_ID! Must be an integer. Please start again with /generate")
                del user_states[user_id]
                
        elif state["step"] == "api_hash":
            user_states[user_id] = {
                "step": "auth_data",
                "api_id": state["api_id"],
                "api_hash": user_input,
                "telethon": state["telethon"],
                "is_bot": state["is_bot"]
            }
            
            if not state["is_bot"]:
                prompt = "**Send your PHONE_NUMBER with country code:**\nExample: `+1234567890`\n\nType /cancel to stop"
            else:
                prompt = "**Send your BOT_TOKEN:**\nExample: `12345:abcdefghijklmnopqrstuvwxyz`\n\nType /cancel to stop"
                
            await message.reply_text(prompt)
            
        elif state["step"] == "auth_data":
            await process_auth_data(client, message, state, user_input)
            
        elif state["step"] == "otp":
            otp_code = user_input.replace(" ", "")
            await process_otp_code(client, message, state, otp_code)
            
        elif state["step"] == "password":
            await process_password(client, message, state, user_input)
            
    except Exception as e:
        logger.error(f"Message handler error: {e}")
        await message.reply_text("❌ An error occurred. Please start again with /generate")
        if user_id in user_states:
            del user_states[user_id]

async def process_auth_data(client: Client, message: Message, state: dict, auth_data: str):
    user_id = message.from_user.id
    ty = "Telethon" if state["telethon"] else "Pyrogram v2"
    if state["is_bot"]:
        ty += " Bot"
    
    await message.reply_text(f"**Starting {ty} Session Generation...**")
    
    if not state["is_bot"]:
        await message.reply_text("📤 Sending OTP...")
    else:
        await message.reply_text("🤖 Logging in as Bot...")
    
    # Initialize client
    if state["telethon"]:
        tg_client = TelegramClient(StringSession(), state["api_id"], state["api_hash"])
    else:
        if state["is_bot"]:
            tg_client = Client(
                f"bot_{user_id}", 
                api_id=state["api_id"], 
                api_hash=state["api_hash"], 
                bot_token=auth_data,
                in_memory=True
            )
        else:
            tg_client = Client(
                f"user_{user_id}",
                api_id=state["api_id"],
                api_hash=state["api_hash"],
                in_memory=True
            )
    
    try:
        await tg_client.connect()
        
        if not state["is_bot"]:
            # User authentication
            if state["telethon"]:
                sent_code = await tg_client.send_code_request(auth_data)
            else:
                sent_code = await tg_client.send_code(auth_data)
            
            user_states[user_id] = {
                "step": "otp",
                "api_id": state["api_id"],
                "api_hash": state["api_hash"],
                "telethon": state["telethon"],
                "is_bot": state["is_bot"],
                "tg_client": tg_client,
                "auth_data": auth_data,
                "phone_code_hash": sent_code.phone_code_hash if not state["telethon"] else None
            }
            
            await message.reply_text(
                "**Send the OTP received on Telegram:**\n\n"
                "If OTP is `12345`, send as: `1 2 3 4 5`\n\n"
                "Type /cancel to stop"
            )
            
        else:
            # Bot authentication
            try:
                if state["telethon"]:
                    await tg_client.start(bot_token=auth_data)
                else:
                    await tg_client.sign_in_bot(auth_data)
                
                # Generate session for bot
                await generate_session_string(client, message, tg_client, state["telethon"], state["is_bot"])
                await tg_client.disconnect()
                if user_id in user_states:
                    del user_states[user_id]
                    
            except Exception as e:
                await message.reply_text(f"❌ Invalid BOT_TOKEN: {e}\nPlease start again with /generate")
                await tg_client.disconnect()
                if user_id in user_states:
                    del user_states[user_id]
                    
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}\nPlease start again with /generate")
        if user_id in user_states:
            del user_states[user_id]

async def process_otp_code(client: Client, message: Message, state: dict, otp_code: str):
    user_id = message.from_user.id
    tg_client = state["tg_client"]
    
    try:
        if state["telethon"]:
            await tg_client.sign_in(state["auth_data"], otp_code)
        else:
            await tg_client.sign_in(state["auth_data"], state["phone_code_hash"], otp_code)
        
        # Generate session string
        await generate_session_string(client, message, tg_client, state["telethon"], state["is_bot"])
        await tg_client.disconnect()
        if user_id in user_states:
            del user_states[user_id]
            
    except (SessionPasswordNeeded, SessionPasswordNeededError):
        user_states[user_id] = {
            "step": "password",
            "api_id": state["api_id"],
            "api_hash": state["api_hash"],
            "telethon": state["telethon"],
            "is_bot": state["is_bot"],
            "tg_client": tg_client
        }
        await message.reply_text("**🔒 Account has 2FA. Send your password:**\n\nType /cancel to stop")
        
    except (PhoneCodeInvalid, PhoneCodeInvalidError):
        await message.reply_text("❌ Invalid OTP code! Please start again with /generate")
        await tg_client.disconnect()
        if user_id in user_states:
            del user_states[user_id]
    except (PhoneCodeExpired, PhoneCodeExpiredError):
        await message.reply_text("❌ OTP code expired! Please start again with /generate")
        await tg_client.disconnect()
        if user_id in user_states:
            del user_states[user_id]
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}\nPlease start again with /generate")
        await tg_client.disconnect()
        if user_id in user_states:
            del user_states[user_id]

async def process_password(client: Client, message: Message, state: dict, password: str):
    user_id = message.from_user.id
    tg_client = state["tg_client"]
    
    try:
        if state["telethon"]:
            await tg_client.sign_in(password=password)
        else:
            await tg_client.check_password(password=password)
        
        # Generate session string
        await generate_session_string(client, message, tg_client, state["telethon"], state["is_bot"])
        await tg_client.disconnect()
        if user_id in user_states:
            del user_states[user_id]
            
    except (PasswordHashInvalid, PasswordHashInvalidError):
        await message.reply_text("❌ Invalid password! Please start again with /generate")
        await tg_client.disconnect()
        if user_id in user_states:
            del user_states[user_id]
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}\nPlease start again with /generate")
        await tg_client.disconnect()
        if user_id in user_states:
            del user_states[user_id]

async def generate_session_string(client: Client, message: Message, tg_client, telethon: bool, is_bot: bool):
    # Determine session type
    ty = "Telethon" if telethon else "Pyrogram v2"
    if is_bot:
        ty += " Bot"
    
    # Generate session string
    if telethon:
        session_string = tg_client.session.save()
    else:
        session_string = await tg_client.export_session_string()
    
    # Send session string
    session_text = f"""
**✅ {ty.upper()} STRING SESSION**

```{session_string}```

**⚠️ Important:**
• Keep this string safe and secure!
• Don't share with anyone!
• This can be used to access your account.

**Generated by @StringSessionBot**
"""
    
    try:
        # Try to send to saved messages first
        if not is_bot:
            await tg_client.send_message("me", session_text)
        # Also send via bot
        await client.send_message(message.chat.id, session_text)
        await message.reply_text("**✅ Session generated successfully! Check your saved messages and this chat.**")
    except Exception as e:
        # If failed, send in current chat
        await message.reply_text(session_text)
        await message.reply_text("**✅ Session generated successfully!**")

# Must Join Handler
@app.on_message(filters.private & filters.incoming, group=-1)
async def must_join_handler(client: Client, message: Message):
    if not MUST_JOIN:
        return
        
    try:
        await client.get_chat_member(MUST_JOIN, message.from_user.id)
    except UserNotParticipant:
        try:
            chat = await client.get_chat(MUST_JOIN)
            invite_link = chat.invite_link if chat.invite_link else f"https://t.me/{chat.username}"
            
            await message.reply_text(
                f"**Please join our channel first to use this bot.**\n\n"
                f"After joining, send /start again.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Join Channel", url=invite_link)]
                ])
            )
            await message.stop_propagation()
        except Exception as e:
            logger.error(f"Error in must_join: {e}")

# Simple Flask server for PORT binding
def create_flask_app():
    flask_app = Flask(__name__)
    
    @flask_app.route('/')
    def home():
        return "🤖 String Session Bot is Running!"
    
    @flask_app.route('/health')
    def health():
        return "OK"
    
    return flask_app

def run_flask():
    flask_app = create_flask_app()
    flask_app.run(host='0.0.0.0', port=PORT, debug=False)

if __name__ == "__main__":
    # Start Flask server in background thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info(f"Flask server started on port {PORT}")
    
    # Start the bot
    logger.info("Starting String Session Bot...")
    print("Bot is starting...")
    
    try:
        app.run()
    except Exception as e:
        logger.error(f"Bot failed to start: {e}")
        print(f"Error: {e}")

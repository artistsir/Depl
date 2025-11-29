import os
import logging
import asyncio
from pyrogram import Client, filters, idle
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import (
    ApiIdInvalid, PhoneNumberInvalid, PhoneCodeInvalid,
    PhoneCodeExpired, SessionPasswordNeeded, PasswordHashInvalid
)
from telethon import TelegramClient
from telethon.sessions import StringSession
from aiohttp import web

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get environment variables
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
MUST_JOIN = os.environ.get("MUST_JOIN", "")
PORT = int(os.environ.get("PORT", 8080))

# Validate required environment variables
if not API_ID or not API_HASH or not BOT_TOKEN:
    logger.error("Please set API_ID, API_HASH, and BOT_TOKEN environment variables")
    exit(1)

# User states for session generation
user_sessions = {}

# Initialize Pyrogram client
app = Client(
    "string_session_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True
)

# Text messages
START_TEXT = """
**🤖 Welcome to String Session Generator Bot!**

I can generate **Pyrogram** and **Telethon** string sessions for your user accounts and bots.

**🔧 Supported Libraries:**
- Pyrogram (User & Bot)
- Telethon (User & Bot)

**Click Generate Session to start!**

**Developed with ❤️ by @StarkBots**
"""

HELP_TEXT = """
**📖 Help Guide**

**Steps to Generate Session:**

1. Choose library type (Pyrogram/Telethon)
2. Enter API_ID from https://my.telegram.org
3. Enter API_HASH from https://my.telegram.org
4. Enter phone number (user) or bot token (bot)
5. Complete authentication
6. Get your string session!

**Need Help?** @StarkBotsChat
"""

ABOUT_TEXT = """
**👨‍💻 About This Bot**

**Version:** 2.0
**Framework:** Pyrogram
**Platform:** Render

**Developer:** @StarkProgrammer
**Support:** @StarkBotsChat
"""

# Button layouts
START_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("🚀 Generate Session", callback_data="generate")],
    [
        InlineKeyboardButton("📖 Help", callback_data="help"),
        InlineKeyboardButton("👨‍💻 About", callback_data="about")
    ]
])

HOME_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("🏠 Home", callback_data="home")]
])

LIBRARY_BUTTONS = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("Pyrogram", callback_data="pyrogram"),
        InlineKeyboardButton("Telethon", callback_data="telethon")
    ],
    [
        InlineKeyboardButton("Pyrogram Bot", callback_data="pyrogram_bot"),
        InlineKeyboardButton("Telethon Bot", callback_data="telethon_bot")
    ],
    [InlineKeyboardButton("🏠 Home", callback_data="home")]
])

# Start Command
@app.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id
    # Clear any existing session data
    if user_id in user_sessions:
        del user_sessions[user_id]
    
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
    if user_id in user_sessions:
        del user_sessions[user_id]
    
    await message.reply_text(
        "**Choose the library you want to generate string session for:**",
        reply_markup=LIBRARY_BUTTONS
    )

# Cancel Command
@app.on_message(filters.command("cancel") & filters.private)
async def cancel_command(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in user_sessions:
        del user_sessions[user_id]
        await message.reply_text("❌ Process cancelled!")
    else:
        await message.reply_text("❌ No active process to cancel!")

# Callback Query Handler
@app.on_callback_query()
async def callback_handler(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    query = callback_query.data
    
    if query == "home":
        if user_id in user_sessions:
            del user_sessions[user_id]
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
        await callback_query.message.edit_text(
            "**Choose the library you want to generate string session for:**",
            reply_markup=LIBRARY_BUTTONS
        )
    
    elif query in ["pyrogram", "telethon", "pyrogram_bot", "telethon_bot"]:
        await callback_query.answer()
        
        # Initialize user session
        user_sessions[user_id] = {
            "library": query,
            "step": "api_id"
        }
        
        await callback_query.message.edit_text(
            "**Please send your API_ID:**\n\n"
            "Get it from https://my.telegram.org\n\n"
            "Type /cancel to stop the process."
        )

# Message handler for session generation
@app.on_message(filters.private & filters.text & ~filters.command(["start", "help", "about", "cancel", "generate"]))
async def message_handler(client: Client, message: Message):
    user_id = message.from_user.id
    
    if user_id not in user_sessions:
        return
    
    session_data = user_sessions[user_id]
    user_input = message.text.strip()
    
    try:
        if session_data["step"] == "api_id":
            # Validate API_ID
            try:
                api_id = int(user_input)
                session_data["api_id"] = api_id
                session_data["step"] = "api_hash"
                
                await message.reply_text(
                    "**Please send your API_HASH:**\n\n"
                    "Get it from https://my.telegram.org\n\n"
                    "Type /cancel to stop the process."
                )
            except ValueError:
                await message.reply_text("❌ Invalid API_ID! It must be a number. Please start again with /generate")
                del user_sessions[user_id]
        
        elif session_data["step"] == "api_hash":
            # Store API_HASH
            session_data["api_hash"] = user_input
            session_data["step"] = "auth_data"
            
            library = session_data["library"]
            is_bot = "bot" in library
            
            if is_bot:
                await message.reply_text(
                    "**Please send your BOT_TOKEN:**\n\n"
                    "Get it from @BotFather\n\n"
                    "Format: `1234567890:ABCDEFGhijklmnopqrstuvwxyz`\n\n"
                    "Type /cancel to stop the process."
                )
            else:
                await message.reply_text(
                    "**Please send your PHONE_NUMBER:**\n\n"
                    "Include country code.\n"
                    "Example: `+1234567890`\n\n"
                    "Type /cancel to stop the process."
                )
        
        elif session_data["step"] == "auth_data":
            # Store phone number or bot token
            session_data["auth_data"] = user_input
            await process_session_generation(client, message, session_data)
            
        elif session_data["step"] == "otp":
            # Process OTP
            await process_otp(client, message, session_data, user_input)
            
        elif session_data["step"] == "password":
            # Process 2FA password
            await process_password(client, message, session_data, user_input)
            
    except Exception as e:
        logger.error(f"Error in message handler: {e}")
        await message.reply_text("❌ An error occurred. Please start again with /generate")
        if user_id in user_sessions:
            del user_sessions[user_id]

async def process_session_generation(client: Client, message: Message, session_data: dict):
    user_id = message.from_user.id
    library = session_data["library"]
    is_bot = "bot" in library
    is_telethon = "telethon" in library
    
    try:
        await message.reply_text("🔄 Starting session generation...")
        
        # Initialize the appropriate client
        if is_telethon:
            tg_client = TelegramClient(StringSession(), session_data["api_id"], session_data["api_hash"])
        else:
            if is_bot:
                tg_client = Client(
                    "bot_session",
                    api_id=session_data["api_id"],
                    api_hash=session_data["api_hash"],
                    bot_token=session_data["auth_data"],
                    in_memory=True
                )
            else:
                tg_client = Client(
                    "user_session", 
                    api_id=session_data["api_id"],
                    api_hash=session_data["api_hash"],
                    in_memory=True
                )
        
        await tg_client.connect()
        session_data["tg_client"] = tg_client
        
        if is_bot:
            # Bot authentication
            try:
                if is_telethon:
                    await tg_client.start(bot_token=session_data["auth_data"])
                else:
                    await tg_client.sign_in_bot(session_data["auth_data"])
                
                # Generate session string
                await generate_final_session(client, message, session_data)
                
            except Exception as e:
                await message.reply_text(f"❌ Invalid bot token: {e}\nPlease start again with /generate")
                await tg_client.disconnect()
                if user_id in user_sessions:
                    del user_sessions[user_id]
        else:
            # User authentication - send OTP
            try:
                if is_telethon:
                    await tg_client.send_code_request(session_data["auth_data"])
                else:
                    sent_code = await tg_client.send_code(session_data["auth_data"])
                    session_data["phone_code_hash"] = sent_code.phone_code_hash
                
                session_data["step"] = "otp"
                
                await message.reply_text(
                    "**OTP sent successfully!**\n\n"
                    "Please send the OTP you received on Telegram.\n\n"
                    "If OTP is `12345`, please send it as: `1 2 3 4 5`\n\n"
                    "Type /cancel to stop the process."
                )
                
            except (ApiIdInvalid, PhoneNumberInvalid):
                await message.reply_text("❌ Invalid API_ID/API_HASH or phone number! Please start again with /generate")
                await tg_client.disconnect()
                if user_id in user_sessions:
                    del user_sessions[user_id]
                
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}\nPlease start again with /generate")
        if user_id in user_sessions:
            del user_sessions[user_id]

async def process_otp(client: Client, message: Message, session_data: dict, otp_code: str):
    user_id = message.from_user.id
    tg_client = session_data["tg_client"]
    is_telethon = "telethon" in session_data["library"]
    
    try:
        otp_code = otp_code.replace(" ", "")
        
        if is_telethon:
            await tg_client.sign_in(session_data["auth_data"], code=otp_code)
        else:
            await tg_client.sign_in(session_data["auth_data"], session_data["phone_code_hash"], otp_code)
        
        # Generate session string
        await generate_final_session(client, message, session_data)
        
    except SessionPasswordNeeded:
        session_data["step"] = "password"
        await message.reply_text(
            "**Your account has two-step verification enabled.**\n\n"
            "Please send your password:\n\n"
            "Type /cancel to stop the process."
        )
    except (PhoneCodeInvalid, PhoneCodeExpired):
        await message.reply_text("❌ Invalid or expired OTP code! Please start again with /generate")
        await tg_client.disconnect()
        if user_id in user_sessions:
            del user_sessions[user_id]
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}\nPlease start again with /generate")
        await tg_client.disconnect()
        if user_id in user_sessions:
            del user_sessions[user_id]

async def process_password(client: Client, message: Message, session_data: dict, password: str):
    user_id = message.from_user.id
    tg_client = session_data["tg_client"]
    is_telethon = "telethon" in session_data["library"]
    
    try:
        if is_telethon:
            await tg_client.sign_in(password=password)
        else:
            await tg_client.check_password(password=password)
        
        # Generate session string
        await generate_final_session(client, message, session_data)
        
    except PasswordHashInvalid:
        await message.reply_text("❌ Invalid password! Please start again with /generate")
        await tg_client.disconnect()
        if user_id in user_sessions:
            del user_sessions[user_id]
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}\nPlease start again with /generate")
        await tg_client.disconnect()
        if user_id in user_sessions:
            del user_sessions[user_id]

async def generate_final_session(client: Client, message: Message, session_data: dict):
    user_id = message.from_user.id
    tg_client = session_data["tg_client"]
    library = session_data["library"]
    is_telethon = "telethon" in library
    
    try:
        # Generate session string
        if is_telethon:
            session_string = tg_client.session.save()
        else:
            session_string = await tg_client.export_session_string()
        
        # Prepare session info
        library_name = "Telethon" if is_telethon else "Pyrogram"
        if "bot" in library:
            library_name += " Bot"
        
        session_text = f"""
**✅ {library_name.upper()} STRING SESSION**

```{session_string}```

**⚠️ Keep this string safe and secure!**
**Don't share with anyone!**

**Generated by @StringSessionBot**
"""
        
        # Send session to user
        await message.reply_text(session_text)
        await message.reply_text("✅ **Session generated successfully!**")
        
        # Try to send to saved messages
        try:
            if "bot" not in library:
                await tg_client.send_message("me", "**Your String Session:**\n\n" + session_string)
        except:
            pass
            
    except Exception as e:
        await message.reply_text(f"❌ Error generating session: {str(e)}")
    finally:
        # Cleanup
        await tg_client.disconnect()
        if user_id in user_sessions:
            del user_sessions[user_id]

# Web server for Render port binding
async def health_check(request):
    return web.Response(text="🤖 String Session Bot is running!")

async def start_web_server():
    web_app = web.Application()
    web_app.router.add_get('/', health_check)
    web_app.router.add_get('/health', health_check)
    
    runner = web.AppRunner(web_app)
    await runner.setup()
    
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    
    logger.info(f"🌐 Web server started on port {PORT}")
    return runner

# Start the bot
async def main():
    logger.info("Starting String Session Bot...")
    print("🤖 Bot is starting...")
    
    try:
        # Start web server for Render
        web_runner = await start_web_server()
        
        # Start the bot
        await app.start()
        print("✅ Bot started successfully!")
        
        # Get bot info
        bot = await app.get_me()
        print(f"🤖 Bot: @{bot.username}")
        print("🚀 Bot is now running...")
        print(f"🌐 Web server running on port {PORT}")
        
        # Keep the bot running
        await idle()
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        print(f"❌ Error: {e}")
    finally:
        await app.stop()
        print("🛑 Bot stopped")

if __name__ == "__main__":
    # Run the bot
    asyncio.run(main())

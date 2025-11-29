import os
import logging
import asyncio
from pyrogram import Client, filters, idle
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

**📚 How to use:**
1. Click **Generate Session**
2. Choose library type
3. Follow the instructions
4. Get your string session!

**⚠️ Important:**
• Keep your string session secure
• Never share it with anyone
• Store it safely

**Developed with ❤️ by @StarkBots**
"""

HELP_TEXT = """
**📖 Help Guide**

**Steps to Generate Session:**

**For User Accounts:**
1. Choose Pyrogram/Telethon
2. Get API_ID & API_HASH from https://my.telegram.org
3. Enter your phone number
4. Enter received OTP
5. Get your string session!

**For Bot Accounts:**
1. Choose Pyrogram Bot/Telethon Bot  
2. Get API_ID & API_HASH from https://my.telegram.org
3. Enter your bot token from @BotFather
4. Get your bot string session!

**Need Help?** @StarkBotsChat
"""

ABOUT_TEXT = """
**👨‍💻 About This Bot**

**Version:** 2.0
**Framework:** Pyrogram
**Platform:** Render

**Features:**
• Fast & Secure Session Generation
• Pyrogram v2 & Telethon Support
• User & Bot Session Support
• Free to Use

**Developer:** @StarkProgrammer
**Support:** @StarkBotsChat

**Source Code:** [GitHub](https://github.com)
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
@app.on_message(filters.private & filters.text & ~filters.command(["start", "help", "about", "cancel"]))
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
                del user_sessions[user_id]
        else:
            # User authentication - send OTP
            try:
                if is_telethon:
                    sent_code = await tg_client.send_code_request(session_data["auth_data"])
                else:
                    sent_code = await tg_client.send_code(session_data["auth_data"])
                
                session_data["step"] = "otp"
                session_data["phone_code_hash"] = sent_code.phone_code_hash if not is_telethon else None
                
                await message.reply_text(
                    "**OTP sent successfully!**\n\n"
                    "Please send the OTP you received on Telegram.\n\n"
                    "If OTP is `12345`, please send it as: `1 2 3 4 5`\n\n"
                    "Type /cancel to stop the process."
                )
                
            except (ApiIdInvalid, ApiIdInvalidError):
                await message.reply_text("❌ Invalid API_ID or API_HASH! Please start again with /generate")
                await tg_client.disconnect()
                del user_sessions[user_id]
            except (PhoneNumberInvalid, PhoneNumberInvalidError):
                await message.reply_text("❌ Invalid phone number! Please start again with /generate")
                await tg_client.disconnect()
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
            await tg_client.sign_in(session_data["auth_data"], otp_code)
        else:
            await tg_client.sign_in(session_data["auth_data"], session_data["phone_code_hash"], otp_code)
        
        # Generate session string
        await generate_final_session(client, message, session_data)
        
    except (SessionPasswordNeeded, SessionPasswordNeededError):
        session_data["step"] = "password"
        await message.reply_text(
            "**Your account has two-step verification enabled.**\n\n"
            "Please send your password:\n\n"
            "Type /cancel to stop the process."
        )
    except (PhoneCodeInvalid, PhoneCodeInvalidError):
        await message.reply_text("❌ Invalid OTP code! Please start again with /generate")
        await tg_client.disconnect()
        del user_sessions[user_id]
    except (PhoneCodeExpired, PhoneCodeExpiredError):
        await message.reply_text("❌ OTP code has expired! Please start again with /generate")
        await tg_client.disconnect()
        del user_sessions[user_id]
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}\nPlease start again with /generate")
        await tg_client.disconnect()
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
        
    except (PasswordHashInvalid, PasswordHashInvalidError):
        await message.reply_text("❌ Invalid password! Please start again with /generate")
        await tg_client.disconnect()
        del user_sessions[user_id]
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}\nPlease start again with /generate")
        await tg_client.disconnect()
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

**⚠️ Important Notes:**
• This string can be used to access your account
• Keep it safe and secure
• Don't share with anyone
• Store it in a secure place

**Generated by @StringSessionBot**
"""
        
        # Send session to user
        await message.reply_text(session_text)
        await message.reply_text("✅ **Session generated successfully!**")
        
        # Try to send to saved messages
        try:
            if "bot" not in library:
                if is_telethon:
                    await tg_client.send_message("me", session_text)
                else:
                    await tg_client.send_message("me", session_text)
        except:
            pass
            
    except Exception as e:
        await message.reply_text(f"❌ Error generating session: {str(e)}")
    finally:
        # Cleanup
        await tg_client.disconnect()
        if user_id in user_sessions:
            del user_sessions[user_id]

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

# Start the bot
if __name__ == "__main__":
    logger.info("Starting String Session Bot...")
    print("Bot is starting...")
    
    try:
        app.start()
        print("Bot started successfully!")
        logger.info("Bot started successfully")
        idle()
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        print(f"Error: {e}")
    finally:
        app.stop()
        print("Bot stopped")

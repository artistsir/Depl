import os
import logging
import asyncio
import threading
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import (
    ApiIdInvalid, PhoneNumberInvalid, PhoneCodeInvalid,
    PhoneCodeExpired, SessionPasswordNeeded, PasswordHashInvalid,
    ChatAdminRequired, UserNotParticipant, ChatWriteForbidden
)
from telethon import TelegramClient
from telethon.errors import (
    ApiIdInvalidError, PhoneNumberInvalidError, PhoneCodeInvalidError,
    PhoneCodeExpiredError, SessionPasswordNeededError, PasswordHashInvalidError
)
from telethon.sessions import StringSession
from dotenv import load_dotenv

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
    await message.reply_text(ASK_QUES, reply_markup=BUTTONS_QUES)

# Callback Query Handler
@app.on_callback_query()
async def callback_handler(client: Client, callback_query: CallbackQuery):
    query = callback_query.data.lower()
    
    if query == "home":
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
        await generate_session(client, callback_query.message, telethon, is_bot)

async def generate_session(client: Client, message: Message, telethon=False, is_bot=False):
    try:
        # Determine session type
        if telethon:
            ty = "Telethon"
        else:
            ty = "Pyrogram v2"
        if is_bot:
            ty += " Bot"
        
        user_id = message.chat.id
        await message.reply_text(f"**Starting {ty} Session Generation...**")
        
        # Get API ID
        api_id_msg = await client.ask(
            user_id, 
            "**Please send your API_ID:**\n\nGet from https://my.telegram.org\n\nType /cancel to stop",
            filters=filters.text,
            timeout=300
        )
        if await is_cancelled(api_id_msg):
            return
            
        try:
            api_id = int(api_id_msg.text)
        except ValueError:
            await api_id_msg.reply("❌ Invalid API_ID! Must be an integer. Please start again with /generate")
            return
        
        # Get API HASH
        api_hash_msg = await client.ask(
            user_id,
            "**Please send your API_HASH:**\n\nGet from https://my.telegram.org\n\nType /cancel to stop", 
            filters=filters.text,
            timeout=300
        )
        if await is_cancelled(api_hash_msg):
            return
        api_hash = api_hash_msg.text
        
        # Get phone number or bot token
        if not is_bot:
            prompt = "**Send your PHONE_NUMBER with country code:**\nExample: `+1234567890`\n\nType /cancel to stop"
        else:
            prompt = "**Send your BOT_TOKEN:**\nExample: `12345:abcdefghijklmnopqrstuvwxyz`\n\nType /cancel to stop"
            
        auth_msg = await client.ask(user_id, prompt, filters=filters.text, timeout=300)
        if await is_cancelled(auth_msg):
            return
        auth_data = auth_msg.text
        
        # Initialize client
        if not is_bot:
            await message.reply_text("📤 Sending OTP...")
        else:
            await message.reply_text("🤖 Logging in as Bot...")
            
        if telethon:
            tg_client = TelegramClient(StringSession(), api_id, api_hash)
        else:
            if is_bot:
                tg_client = Client(
                    f"bot_{user_id}", 
                    api_id=api_id, 
                    api_hash=api_hash, 
                    bot_token=auth_data,
                    in_memory=True
                )
            else:
                tg_client = Client(
                    f"user_{user_id}",
                    api_id=api_id,
                    api_hash=api_hash,
                    in_memory=True
                )
        
        await tg_client.connect()
        
        # Authentication process
        if not is_bot:
            # User authentication
            if telethon:
                sent_code = await tg_client.send_code_request(auth_data)
            else:
                sent_code = await tg_client.send_code(auth_data)
            
            # Ask for OTP
            otp_msg = await client.ask(
                user_id,
                "**Send the OTP received on Telegram:**\n\nIf OTP is `12345`, send as: `1 2 3 4 5`\n\nType /cancel to stop",
                filters=filters.text,
                timeout=600
            )
            if await is_cancelled(otp_msg):
                await tg_client.disconnect()
                return
                
            otp_code = otp_msg.text.replace(" ", "")
            
            try:
                if telethon:
                    await tg_client.sign_in(auth_data, otp_code)
                else:
                    await tg_client.sign_in(auth_data, sent_code.phone_code_hash, otp_code)
                    
            except (SessionPasswordNeeded, SessionPasswordNeededError):
                password_msg = await client.ask(
                    user_id,
                    "**🔒 Account has 2FA. Send your password:**\n\nType /cancel to stop",
                    filters=filters.text,
                    timeout=300
                )
                if await is_cancelled(password_msg):
                    await tg_client.disconnect()
                    return
                    
                try:
                    if telethon:
                        await tg_client.sign_in(password=password_msg.text)
                    else:
                        await tg_client.check_password(password_msg.text)
                except (PasswordHashInvalid, PasswordHashInvalidError):
                    await password_msg.reply("❌ Invalid password! Please start again with /generate")
                    await tg_client.disconnect()
                    return
                    
        else:
            # Bot authentication
            try:
                if telethon:
                    await tg_client.start(bot_token=auth_data)
                else:
                    await tg_client.sign_in_bot(auth_data)
            except Exception as e:
                await message.reply_text(f"❌ Invalid BOT_TOKEN: {e}\nPlease start again with /generate")
                await tg_client.disconnect()
                return
        
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
            await client.send_message(user_id, session_text)
            await message.reply_text("**✅ Session generated successfully! Check your saved messages and this chat.**")
        except Exception as e:
            # If failed, send in current chat
            await message.reply_text(session_text)
            await message.reply_text("**✅ Session generated successfully!**")
        
        await tg_client.disconnect()
        
    except (ApiIdInvalid, ApiIdInvalidError):
        await message.reply_text("❌ Invalid API_ID/API_HASH combination! Please start again with /generate")
    except (PhoneNumberInvalid, PhoneNumberInvalidError):
        await message.reply_text("❌ Invalid phone number! Please start again with /generate")
    except (PhoneCodeInvalid, PhoneCodeInvalidError):
        await message.reply_text("❌ Invalid OTP code! Please start again with /generate")
    except (PhoneCodeExpired, PhoneCodeExpiredError):
        await message.reply_text("❌ OTP code expired! Please start again with /generate")
    except asyncio.TimeoutError:
        await message.reply_text("⏰ Timeout! Please try again with /generate")
    except Exception as e:
        error_msg = f"❌ An error occurred: {str(e)}\n\nPlease try again with /generate"
        await message.reply_text(error_msg)
        logger.error(f"Session generation error: {e}")

async def is_cancelled(msg: Message):
    if msg.text and msg.text.startswith('/cancel'):
        await msg.reply_text("❌ Process cancelled! Use /generate to start again.")
        return True
    return False

# Must Join Handler (Improved)
@app.on_message(filters.private & filters.incoming, group=-1)
async def must_join_handler(client: Client, message: Message):
    if not MUST_JOIN or MUST_JOIN.strip() == "":
        return
        
    try:
        must_join = MUST_JOIN.strip()
        
        # Check if user is in the channel/group
        try:
            await client.get_chat_member(must_join, message.from_user.id)
            return  # User is member, allow access
        except UserNotParticipant:
            pass  # User not member, show join button
        except Exception as e:
            logger.error(f"Error checking membership: {e}")
            return  # Don't block on other errors
        
        # Get invite link
        try:
            chat = await client.get_chat(must_join)
            if chat.username:
                link = f"https://t.me/{chat.username}"
            else:
                link = chat.invite_link
        except Exception as e:
            logger.error(f"Error getting chat info: {e}")
            return
            
        await message.reply(
            f"**⚠️ Access Required!**\n\n"
            f"You must join our channel to use this bot.\n"
            f"After joining, click /start again!",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✨ Join Channel ✨", url=link)],
                [InlineKeyboardButton("🔄 Refresh", callback_data="refresh_join")]
            ])
        )
        await message.stop_propagation()
        
    except Exception as e:
        logger.error(f"Must join handler error: {e}")
        # Don't block users if there's an error
        return

# Refresh callback for join check
@app.on_callback_query(filters.regex("refresh_join"))
async def refresh_join_handler(client: Client, callback_query: CallbackQuery):
    if not MUST_JOIN or MUST_JOIN.strip() == "":
        await callback_query.message.delete()
        return
        
    try:
        await client.get_chat_member(MUST_JOIN.strip(), callback_query.from_user.id)
        # User has joined, show start menu
        await callback_query.message.delete()
        await start_command(client, callback_query.message)
    except UserNotParticipant:
        await callback_query.answer("❌ You haven't joined yet! Please join the channel first.", show_alert=True)
    except Exception as e:
        await callback_query.answer("❌ Error checking membership. Please try again.", show_alert=True)

# Simple HTTP Server for Render Port Binding
from http.server import HTTPServer, BaseHTTPRequestHandler

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Bot is running!')
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        logger.info(f"HTTP {self.address_string()} - {format % args}")

def run_http_server():
    try:
        server = HTTPServer(('0.0.0.0', PORT), HealthHandler)
        logger.info(f"HTTP Server running on port {PORT}")
        server.serve_forever()
    except Exception as e:
        logger.error(f"HTTP Server error: {e}")

if __name__ == "__main__":
    # Start HTTP server in background thread for Render port binding
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()
    logger.info(f"Started HTTP server on port {PORT} for Render")
    
    # Start the bot
    logger.info("Starting Advanced String Session Bot...")
    
    try:
        app.run()
    except Exception as e:
        logger.error(f"Bot failed to start: {e}")
    finally:
        logger.info("Bot stopped")

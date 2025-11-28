from flask import Flask, request, jsonify, render_template_string
import subprocess
import os
import threading
import time
import logging
import sys

app = Flask(__name__)

# Global variables
bot_process = None
bot_running = False

# ✅ YAHAN APNA BOT TOKEN DALEN
BOT_TOKEN = "8072839594:AAGLrkL4L2DVkzAiG1lhvyqGlq_DAYoaQpQ"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# HTML template for web interface
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Telegram Bot Deployer</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .form-group { margin: 25px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }
        label { display: block; margin-bottom: 8px; font-weight: bold; color: #333; }
        input, textarea, button { width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ddd; border-radius: 5px; font-size: 14px; }
        textarea { height: 300px; font-family: 'Courier New', monospace; font-size: 12px; }
        button { background: #007bff; color: white; border: none; cursor: pointer; font-size: 16px; }
        button:hover { background: #0056b3; }
        button.stop { background: #dc3545; }
        button.stop:hover { background: #c82333; }
        .status { padding: 15px; border-radius: 5px; margin: 15px 0; font-weight: bold; }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
        .warning { background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
        pre { background: #1e1e1e; color: #00ff00; padding: 15px; border-radius: 5px; overflow: auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Telegram Bot Deployer</h1>
        <div class="status info">
            ✅ Your Bot Token: {{ token_display }}<br>
            📍 Single File Solution - main.py
        </div>
        
        <div class="form-group">
            <h3>📤 Upload Your Bot Code</h3>
            <form action="/upload" method="post" enctype="multipart/form-data">
                <label for="file">Upload bot.py file:</label>
                <input type="file" id="file" name="file" accept=".py" required>
                <button type="submit">🚀 Upload & Deploy</button>
            </form>
            
            <h4>Or paste your Python code:</h4>
            <form action="/upload_code" method="post">
                <label for="code">Paste your Python bot code (BOT_TOKEN already included):</label>
                <textarea id="code" name="code" placeholder="# Your Telegram bot code here\n# BOT_TOKEN = 'YOUR_TOKEN' - Already set in main.py">{{ sample_code }}</textarea>
                <button type="submit">🚀 Deploy Code</button>
            </form>
        </div>

        <div class="form-group">
            <h3>📊 Bot Status</h3>
            <div class="status {{ status_class }}">{{ status_message }}</div>
            <div>
                <form action="/restart" method="post" style="display:inline;">
                    <button type="submit">🔄 Restart Bot</button>
                </form>
                <form action="/stop" method="post" style="display:inline;">
                    <button type="submit" class="stop">🛑 Stop Bot</button>
                </form>
            </div>
        </div>

        {% if logs %}
        <div class="form-group">
            <h3>📝 Recent Logs</h3>
            <pre>{{ logs }}</pre>
        </div>
        {% endif %}
    </div>
</body>
</html>
'''

def create_default_bot():
    """Default bot template create karta hai"""
    bot_code = f'''
import logging
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ✅ BOT TOKEN (Auto-set from main.py)
BOT_TOKEN = "{BOT_TOKEN}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    user = update.effective_user
    await update.message.reply_html(
        f"👋 Hello {{user.mention_html()}}!\\\\n"
        f"🤖 Bot successfully deployed on Render!\\\\n"
        f"🚀 Powered by main.py single file solution\\\\n"
        f"📝 Token: {{BOT_TOKEN[:10]}}..."
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo the user message"""
    await update.message.reply_text(f"🤖 You said: {{update.message.text}}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    help_text = """
Available Commands:
/start - Start the bot
/help - Show this help message
/status - Check bot status

Just send any message and I'll echo it back!
"""
    await update.message.reply_text(help_text)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Status command"""
    await update.message.reply_text("✅ Bot is running perfectly on Render!\\\\n🚀 Single file main.py solution")

def main():
    """Main function to run the bot"""
    try:
        # Create application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("status", status))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
        
        # Start the bot
        print("🤖 Starting Telegram Bot...")
        print(f"✅ Token: {{BOT_TOKEN[:10]}}...")
        print("🚀 Single File Solution - main.py")
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Error starting bot: {{e}}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
    
    with open('bot.py', 'w') as f:
        f.write(bot_code)
    print("✅ Default bot template created!")

def run_bot():
    """Bot ko run karta hai"""
    global bot_process, bot_running
    try:
        if os.path.exists('bot.py'):
            print("🚀 Starting bot.py...")
            bot_process = subprocess.Popen([sys.executable, 'bot.py'], 
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.STDOUT,
                                         text=True)
            bot_running = True
            print("✅ Bot started successfully")
            
            # Read bot output in background
            def read_output():
                while True:
                    output = bot_process.stdout.readline()
                    if output == '' and bot_process.poll() is not None:
                        break
                    if output:
                        print(f"BOT: {output.strip()}")
            
            threading.Thread(target=read_output, daemon=True).start()
            
        else:
            print("❌ bot.py not found")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")

@app.route('/')
def home():
    """Home page"""
    token_display = f"{BOT_TOKEN[:10]}...{BOT_TOKEN[-5:]}" if BOT_TOKEN else "Not set"
    status_msg = "✅ Bot is running" if bot_running else "❌ Bot is stopped"
    status_class = "success" if bot_running else "error"
    
    # Sample code for textarea
    sample_code = '''# Your Telegram bot code here
# BOT_TOKEN is automatically set from main.py

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Use this BOT_TOKEN variable in your code
BOT_TOKEN = "YOUR_TOKEN_HERE"  # Auto-replaced with actual token

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Your custom bot is working! 🚀")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.run_polling()

if __name__ == "__main__":
    main()'''
    
    # Get recent logs
    logs = ""
    try:
        # Simple log collection from recent prints
        logs = "Logs will appear here when bot is running..."
    except:
        pass
    
    return render_template_string(HTML_TEMPLATE, 
                                token_display=token_display,
                                status_message=status_msg,
                                status_class=status_class,
                                sample_code=sample_code,
                                logs=logs)

@app.route('/upload', methods=['POST'])
def upload_bot():
    """Bot file upload handler"""
    global bot_process, bot_running
    
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '' or not file.filename.endswith('.py'):
        return jsonify({"error": "Please upload a valid .py file"}), 400
    
    try:
        # Stop existing bot
        if bot_process and bot_running:
            bot_process.terminate()
            bot_running = False
            time.sleep(2)
        
        # Read uploaded file content
        file_content = file.read().decode('utf-8')
        
        # Replace BOT_TOKEN placeholder with actual token
        file_content = file_content.replace('"YOUR_TOKEN_HERE"', f'"{BOT_TOKEN}"')
        file_content = file_content.replace("'YOUR_TOKEN_HERE'", f"'{BOT_TOKEN}'")
        file_content = file_content.replace("YOUR_TOKEN_HERE", BOT_TOKEN)
        
        # Save the modified file
        with open('bot.py', 'w') as f:
            f.write(file_content)
        
        # Start the new bot
        threading.Thread(target=run_bot).start()
        time.sleep(3)
        
        return jsonify({
            "message": "✅ Bot deployed successfully!",
            "status": "running",
            "token_set": True
        })
    except Exception as e:
        return jsonify({"error": f"❌ Deployment failed: {str(e)}"}), 500

@app.route('/upload_code', methods=['POST'])
def upload_code():
    """Code paste handler"""
    global bot_process, bot_running
    
    code = request.form.get('code', '').strip()
    if not code:
        return jsonify({"error": "No code provided"}), 400
    
    try:
        # Stop existing bot
        if bot_process and bot_running:
            bot_process.terminate()
            bot_running = False
            time.sleep(2)
        
        # Replace BOT_TOKEN placeholder with actual token
        code = code.replace('"YOUR_TOKEN_HERE"', f'"{BOT_TOKEN}"')
        code = code.replace("'YOUR_TOKEN_HERE'", f"'{BOT_TOKEN}'")
        code = code.replace("YOUR_TOKEN_HERE", BOT_TOKEN)
        
        # Save code to bot.py
        with open('bot.py', 'w') as f:
            f.write(code)
        
        # Start the new bot
        threading.Thread(target=run_bot).start()
        time.sleep(3)
        
        return jsonify({
            "message": "✅ Bot code deployed successfully!",
            "status": "running"
        })
    except Exception as e:
        return jsonify({"error": f"❌ Deployment failed: {str(e)}"}), 500

@app.route('/restart', methods=['POST'])
def restart_bot():
    """Bot restart handler"""
    global bot_process, bot_running
    
    if bot_process and bot_running:
        bot_process.terminate()
        bot_running = False
        time.sleep(2)
    
    if os.path.exists('bot.py'):
        threading.Thread(target=run_bot).start()
        return jsonify({"message": "✅ Bot restarted successfully"})
    else:
        create_default_bot()
        threading.Thread(target=run_bot).start()
        return jsonify({"message": "✅ Default bot created and started"})

@app.route('/stop', methods=['POST'])
def stop_bot():
    """Bot stop handler"""
    global bot_process, bot_running
    
    if bot_process and bot_running:
        bot_process.terminate()
        bot_running = False
        return jsonify({"message": "✅ Bot stopped successfully"})
    else:
        return jsonify({"error": "❌ Bot is not running"}), 400

@app.route('/status')
def status():
    """Status check"""
    return jsonify({
        "bot_running": bot_running,
        "bot_file_exists": os.path.exists('bot.py'),
        "token_set": bool(BOT_TOKEN)
    })

# Server start pe default bot create karo
if __name__ == '__main__':
    print("🚀 Starting Telegram Bot Deployer...")
    print(f"✅ Bot Token: {BOT_TOKEN[:10]}...")
    
    # Ensure default bot exists
    if not os.path.exists('bot.py'):
        create_default_bot()
    
    # Start bot automatically
    threading.Thread(target=run_bot).start()
    
    # Start Flask server
    app.run(host='0.0.0.0', port=5000, debug=False)

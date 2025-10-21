# UDP DDoS Tester Bot

A powerful Python-based UDP DDoS testing tool with Telegram bot interface for testing game server resilience. Features 5000 concurrent threads for maximum stress testing.

## Features

- 🚀 **High-Power UDP Flood Testing**: Sends 5000 concurrent threads to target IP:port
- 🤖 **Telegram Bot Interface**: Easy-to-use commands and interactive menu system
- 👑 **Admin System**: Dedicated admin user (ID: 6300435094) with approval controls
- 👥 **User Management**: Admin can approve/remove authorized users
- 📊 **Real-time Monitoring**: View running attacks and comprehensive logs
- ⏱️ **Configurable Duration**: 1-300 seconds attack duration
- 🛑 **Instant Stop Control**: Stop all your attacks immediately
- 📝 **Comprehensive Logging**: Detailed attack logs and user activity monitoring

## Commands

### User Commands
- `/start` - Show main menu with interactive buttons
- `/attack ip:port:duration` - Start UDP attack (e.g., `/attack 192.168.1.1:8080:60`)
- `/stop` - Stop all your running attacks immediately
- `/running` - Show currently running attacks
- `/logs` - Display recent attack logs

### Admin Commands (User ID: 6300435094)
- `/approve user_id` - Approve new users to use the bot
- `/admin` - Show admin panel with user list and system status

## Setup Instructions

### 1. Create Telegram Bot

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot` and follow instructions
3. Save the bot token

### 2. Local Development

```bash
# Clone or download the files
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export BOT_TOKEN="your_bot_token_here"
export ADMIN_USER_ID="your_telegram_user_id"  # Optional

# Run the bot
python script.py
```

### 3. Deploy on Render

1. **Create a new Web Service on Render**
2. **Connect your repository** or upload files
3. **Configure environment variables**:
   - `BOT_TOKEN`: Your Telegram bot token
   - `ADMIN_USER_ID`: Your Telegram user ID (optional)
4. **Set build command**: `pip install -r requirements.txt`
5. **Set start command**: `python script.py`
6. **Deploy**

### 4. Get Your Telegram User ID

1. Message [@userinfobot](https://t.me/userinfobot) on Telegram
2. Copy your user ID
3. Contact admin (ID: 6300435094) to get approved, or use `/approve your_user_id` if you're admin

## Usage

1. **Start the bot**: Send `/start` to your bot
2. **Get approved**: Contact admin (ID: 6300435094) to get access
3. **Start an attack**: 
   ```
   /attack 192.168.1.1:8080:60
   ```
   This will send 5000 UDP packets per second to 192.168.1.1:8080 for 60 seconds

4. **Stop attacks**: Use `/stop` to immediately stop all your attacks
5. **Monitor attacks**: Use `/running` to see active attacks
6. **View logs**: Use `/logs` to see recent attack history

### Admin Usage
- **Approve users**: `/approve 123456789` to approve new users
- **Admin panel**: `/admin` to view all users and system status

## Key Improvements

### 🚀 **4x More Powerful DDoS Testing**
- **5000 threads** (upgraded from 1250)
- **Maximum stress testing** for your game servers
- **Higher packet throughput** for better resilience testing

### 🛑 **Instant Stop Control**
- **`/stop` command** - Stop all your attacks immediately
- **Menu button** - Easy access to stop functionality
- **User isolation** - Only stops your own attacks

### 👑 **Admin System**
- **Dedicated admin** (User ID: 6300435094)
- **User approval system** - Admin controls who can use the bot
- **Admin panel** - Full system monitoring and user management

## Security Features

- **Admin-Only User Management**: Only admin (ID: 6300435094) can approve users
- **User Authorization**: Only authorized users can use the bot
- **Attack Limits**: Maximum 5-minute duration per attack
- **Input Validation**: IP address and port validation
- **User Isolation**: Users can only stop their own attacks
- **Comprehensive Logging**: All attacks and admin actions are logged with user information

## File Structure

```
├── script.py              # Main bot and DDoS testing code
├── requirements.txt       # Python dependencies
├── config.py             # Configuration settings
├── README.md             # This file
├── authorized_users.json # Authorized users (auto-created)
└── ddos_logs.log         # Attack logs (auto-created)
```

## Technical Details

- **Threading**: Uses 5000 concurrent threads for maximum packet throughput
- **Protocol**: UDP packets with random data payload
- **Packet Size**: 1024 bytes per packet
- **Rate Limiting**: 1ms delay between packets to prevent system overload
- **Memory Efficient**: Daemon threads that clean up automatically
- **Stop Control**: Instant attack termination with user-specific stopping
- **Admin System**: Hardcoded admin user with full control over user management

## Safety Notes

⚠️ **Important**: This tool is for testing your own servers only. Using it against systems you don't own is illegal and unethical.

- Only test your own game servers
- Use appropriate attack durations
- Monitor your server resources during testing
- Stop attacks if server becomes unresponsive

## Troubleshooting

### Bot not responding
- Check if BOT_TOKEN is set correctly
- Verify the bot is running (check logs)
- Ensure you're authorized (use `/add` command)

### Attack not starting
- Verify IP address format (e.g., 192.168.1.1)
- Check port number (1-65535)
- Ensure duration is 1-300 seconds
- Check if you're authorized (contact admin: 6300435094)

### Can't stop attacks
- Use `/stop` command to stop all your attacks
- Only stops attacks by your user ID
- Contact admin if you need help stopping other users' attacks

### High CPU usage
- The tool uses 5000 threads which is very CPU intensive
- Monitor system resources during attacks
- Use `/stop` command if system becomes unresponsive
- Consider running on a powerful server for best performance

## Support

For issues or questions:
1. Check the logs in `ddos_logs.log`
2. Verify all environment variables are set
3. Ensure you're using the correct command format
4. Check if you're authorized to use the bot

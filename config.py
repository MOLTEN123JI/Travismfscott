import os

# Configuration settings
BOT_TOKEN = os.getenv('BOT_TOKEN', '8266888318:AAGCcn95Hj0flaypDcyEEM0KjLfPPC2FPvw')
ADMIN_USER_ID = os.getenv('ADMIN_USER_ID', 6300435094)

# Attack settings (optimized for free plan)
MAX_THREADS = 1000  # Reduced for free plan compatibility
MAX_DURATION = 300  # 5 minutes max
MIN_DURATION = 1    # 1 second min

# Logging settings
LOG_FILE = 'ddos_logs.log'
AUTHORIZED_USERS_FILE = 'authorized_users.json'

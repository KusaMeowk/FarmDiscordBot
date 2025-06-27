"""
Enhanced Logging System for Clean Console Output
Removes traceback, adds colors, and provides professional formatting
"""

import logging
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

# Sửa lỗi Unicode trên Windows
def setup_unicode_safe_logging():
    """Setup logging an toàn với Unicode trên Windows"""
    
    # Force UTF-8 encoding cho stdout
    if sys.platform == "win32":
        # Cố gắng set console encoding
        try:
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
        except Exception:
            # Nếu không được, tạo custom handler để remove emoji
            pass

def safe_log_message(message: str) -> str:
    """Làm sạch message để tránh lỗi encoding"""
    try:
        # Test encode với console encoding
        if sys.platform == "win32":
            message.encode('cp1252')
        return message
    except UnicodeEncodeError:
        # Remove emoji và ký tự Unicode đặc biệt
        import re
        # Remove emoji pattern
        emoji_pattern = re.compile("["
                                 u"\U0001F600-\U0001F64F"  # emoticons
                                 u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                 u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                 u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                 u"\U00002500-\U00002BEF"  # chinese char
                                 u"\U00002702-\U000027B0"
                                 u"\U00002702-\U000027B0"
                                 u"\U000024C2-\U0001F251"
                                 u"\U0001f926-\U0001f937"
                                 u"\U00010000-\U0010ffff"
                                 u"\u2640-\u2642" 
                                 u"\u2600-\u2B55"
                                 u"\u200d"
                                 u"\u23cf"
                                 u"\u23e9"
                                 u"\u231a"
                                 u"\ufe0f"  # dingbats
                                 u"\u3030"
                                 "]+", flags=re.UNICODE)
        
        # Replace emoji với text alternatives
        replacements = {
            "🚀": "[START]",
            "✅": "[OK]",
            "❌": "[ERROR]",
            "⚠️": "[WARNING]",
            "🔧": "[CONFIG]",
            "📊": "[DATA]",
            "🤖": "[AI]",
            "🎀": "[LATINA]",
            "💖": "[HEART]",
            "🌤️": "[WEATHER]",
            "🎯": "[TARGET]",
            "💰": "[MONEY]",
            "🔑": "[KEY]",
            "💾": "[CACHE]",
            "🟢": "[ON]",
            "🔴": "[OFF]",
            "🔍": "[SEARCH]",
            "🧪": "[TEST]",
            "📋": "[LIST]",
            "🎉": "[EVENT]",
            "⏸️": "[PAUSE]",
            "🧹": "[CLEANUP]"
        }
        
        # Apply replacements
        clean_message = message
        for emoji, replacement in replacements.items():
            clean_message = clean_message.replace(emoji, replacement)
        
        # Remove remaining emoji
        clean_message = emoji_pattern.sub('', clean_message)
        
        return clean_message

class SafeFormatter(logging.Formatter):
    """Custom formatter để xử lý Unicode an toàn"""
    
    def format(self, record):
        # Format record bình thường
        formatted = super().format(record)
        # Clean message để tránh lỗi encoding
        return safe_log_message(formatted)

def setup_enhanced_logging():
    """Setup logging system với Unicode safety"""
    
    # Setup Unicode safety first
    setup_unicode_safe_logging()
    
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler với SafeFormatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Use safe formatter
    console_format = SafeFormatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    
    # File handler (UTF-8 safe)
    file_handler = logging.FileHandler(
        logs_dir / f"bot_{datetime.now().strftime('%Y%m%d')}.log",
        encoding='utf-8',
        mode='a'
    )
    file_handler.setLevel(logging.DEBUG)
    
    file_format = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-15s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    
    # Add handlers
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Set specific logger levels
    logging.getLogger('discord').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('aiohttp').setLevel(logging.WARNING)
    
    # Test logging
    logger = logging.getLogger("enhanced_logging")
    logger.info("Enhanced logging system initialized successfully")
    
    return root_logger

class CleanFormatter(logging.Formatter):
    """Custom formatter for clean, colorized console output"""
    
    # ANSI Color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green  
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    # Emoji for different log levels
    EMOJIS = {
        'DEBUG': '🔍',
        'INFO': 'ℹ️',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '💥'
    }
    
    def __init__(self, use_colors: bool = True, use_emojis: bool = True):
        super().__init__()
        self.use_colors = use_colors
        self.use_emojis = use_emojis
    
    def format(self, record):
        # Get color and emoji for log level
        color = self.COLORS.get(record.levelname, self.COLORS['RESET']) if self.use_colors else ''
        reset = self.COLORS['RESET'] if self.use_colors else ''
        emoji = self.EMOJIS.get(record.levelname, '') if self.use_emojis else ''
        
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')
        
        # Clean module name
        module = record.name.split('.')[-1] if '.' in record.name else record.name
        
        # Format base message
        if emoji:
            base_message = f"{color}[{timestamp}] {emoji} {module}: {record.getMessage()}{reset}"
        else:
            base_message = f"{color}[{timestamp}] {record.levelname:<7} {module}: {record.getMessage()}{reset}"
        
        # Handle clean error info
        if record.levelname == 'ERROR' and hasattr(record, 'clean_error'):
            base_message += f"\n{color}         └─ {record.clean_error}{reset}"
        
        return base_message

class EnhancedLogger:
    """Enhanced logger with clean error reporting"""
    
    @staticmethod
    def setup(
        level: int = logging.INFO,
        use_colors: bool = True,
        use_emojis: bool = True,
        suppress_third_party: bool = True
    ):
        """Setup enhanced logging configuration"""
        
        # Remove default handlers
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        
        # Create console handler with clean formatter
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(CleanFormatter(use_colors, use_emojis))
        console_handler.setLevel(level)
        
        # Configure root logger
        logging.basicConfig(
            level=level,
            handlers=[console_handler],
            force=True
        )
        
        # Suppress noisy third-party loggers
        if suppress_third_party:
            third_party_loggers = [
                'discord',
                'discord.http', 
                'discord.gateway',
                'discord.client',
                'aiosqlite',
                'asyncio',
                'urllib3',
                'requests'
            ]
            
            for logger_name in third_party_loggers:
                logging.getLogger(logger_name).setLevel(logging.WARNING)
    
    @staticmethod
    def log_error_clean(logger_instance, message: str, error: Exception = None):
        """Log error with clean format (no traceback)"""
        if error:
            # Create custom log record with clean error info
            record = logging.LogRecord(
                name=logger_instance.name,
                level=logging.ERROR,
                pathname="",
                lineno=0,
                msg=message,
                args=(),
                exc_info=None
            )
            # Add clean error description
            record.clean_error = f"{type(error).__name__}: {str(error)}"
            logger_instance.handle(record)
        else:
            logger_instance.error(message)
    
    @staticmethod
    def get_logger(name: str):
        """Get a logger instance"""
        return logging.getLogger(name)

# Convenience functions
def setup_logging(level: int = logging.INFO, **kwargs):
    """Quick setup function"""
    return EnhancedLogger.setup(level=level, **kwargs)

def log_error(logger, message: str, error: Exception = None):
    """Quick error logging function"""
    return EnhancedLogger.log_error_clean(logger, message, error)

def get_logger(name: str):
    """Quick logger getter"""
    return EnhancedLogger.get_logger(name)

# Pre-configured loggers for common use cases
def get_bot_logger():
    """Get logger for main bot"""
    return get_logger('bot')

def get_database_logger():
    """Get logger for database operations"""
    return get_logger('database')

def get_feature_logger(feature_name: str):
    """Get logger for specific features"""
    return get_logger(f'features.{feature_name}')

def get_ai_logger():
    """Get logger for AI systems"""
    return get_logger('ai')

# Example usage and configuration
if __name__ == "__main__":
    # Test the enhanced logging
    setup_enhanced_logging()
    
    logger = get_logger("test")
    
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    log_error(logger, "This is a clean error", ValueError("Test error"))
    logger.debug("This is a debug message")
    
    print("\n--- Testing without colors/emojis ---")
    setup_logging(use_colors=False, use_emojis=False)
    
    logger2 = get_logger("test2")
    logger2.info("Plain info message")
    log_error(logger2, "Plain error message", RuntimeError("Plain test error")) 
"""
Enhanced logging utilities for Spanish Pronunciation Deck Creator
"""

import logging
import os
import sys
from datetime import datetime
from aqt import mw
from aqt.utils import showInfo, showCritical

class AddonLogger:
    """Enhanced logger for Anki addon with multiple output targets"""
    
    def __init__(self, addon_name="spanish_pronunciation_addon"):
        self.addon_name = addon_name
        self.logger = logging.getLogger(addon_name)
        self.logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        self._setup_file_logger()
        self._setup_console_logger()
        
    def _setup_file_logger(self):
        """Set up file logging to addon directory"""
        try:
            # Get addon directory
            addon_dir = os.path.join(mw.pm.addonFolder(), self.addon_name)
            if not os.path.exists(addon_dir):
                os.makedirs(addon_dir)
            
            log_file = os.path.join(addon_dir, "debug.log")
            
            # Create file handler with rotation
            file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            
            # Detailed format for file
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
            
            self.log_file_path = log_file
            
        except Exception as e:
            print(f"Failed to setup file logging: {e}")
            self.log_file_path = None
    
    def _setup_console_logger(self):
        """Set up console logging for debug console"""
        try:
            # Console handler for Anki debug console
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            
            # Simpler format for console
            console_formatter = logging.Formatter(
                '[Spanish Pronunciation] %(levelname)s: %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)
            
        except Exception as e:
            print(f"Failed to setup console logging: {e}")
    
    def debug(self, msg, *args, **kwargs):
        """Debug level logging"""
        self.logger.debug(msg, *args, **kwargs)
        
    def info(self, msg, *args, **kwargs):
        """Info level logging"""
        self.logger.info(msg, *args, **kwargs)
        print(f"[Spanish Pronunciation] INFO: {msg}")  # Also print to debug console
        
    def warning(self, msg, *args, **kwargs):
        """Warning level logging"""
        self.logger.warning(msg, *args, **kwargs)
        print(f"[Spanish Pronunciation] WARNING: {msg}")
        
    def error(self, msg, *args, **kwargs):
        """Error level logging"""
        self.logger.error(msg, *args, **kwargs)
        print(f"[Spanish Pronunciation] ERROR: {msg}")
        
    def critical(self, msg, *args, **kwargs):
        """Critical level logging"""
        self.logger.critical(msg, *args, **kwargs)
        print(f"[Spanish Pronunciation] CRITICAL: {msg}")
    
    def user_info(self, msg, also_log=True):
        """Show info to user and optionally log it"""
        if also_log:
            self.info(f"User notification: {msg}")
        showInfo(msg)
    
    def user_error(self, msg, also_log=True):
        """Show error to user and optionally log it"""
        if also_log:
            self.error(f"User error: {msg}")
        showCritical(msg)
    
    def log_exception(self, msg="Exception occurred"):
        """Log exception with full traceback"""
        self.logger.exception(msg)
        print(f"[Spanish Pronunciation] EXCEPTION: {msg}")
    
    def log_function_entry(self, func_name, *args, **kwargs):
        """Log function entry with parameters"""
        args_str = ", ".join([str(arg) for arg in args])
        kwargs_str = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
        params = ", ".join(filter(None, [args_str, kwargs_str]))
        self.debug(f"Entering {func_name}({params})")
    
    def log_function_exit(self, func_name, result=None):
        """Log function exit with result"""
        if result is not None:
            self.debug(f"Exiting {func_name} with result: {result}")
        else:
            self.debug(f"Exiting {func_name}")
    
    def log_system_info(self):
        """Log system and Anki environment information"""
        try:
            import platform
            from anki import version as anki_version
            
            self.info("=== System Information ===")
            self.info(f"Platform: {platform.platform()}")
            self.info(f"Python: {platform.python_version()}")
            self.info(f"Anki Version: {anki_version}")
            
            if hasattr(mw, 'pm') and mw.pm:
                profile_name = mw.pm.name if hasattr(mw.pm, 'name') else "Unknown"
                self.info(f"Anki Profile: {profile_name}")
                self.info(f"Addon Directory: {mw.pm.addonFolder()}")
            
            if self.log_file_path:
                self.info(f"Log File: {self.log_file_path}")
            
            self.info("=== End System Information ===")
            
        except Exception as e:
            self.error(f"Failed to log system info: {e}")
    
    def get_log_file_path(self):
        """Get the path to the log file"""
        return getattr(self, 'log_file_path', None)
    
    def open_log_file(self):
        """Open log file in default text editor"""
        if self.log_file_path and os.path.exists(self.log_file_path):
            try:
                os.startfile(self.log_file_path)  # Windows
            except:
                try:
                    import subprocess
                    subprocess.run(['open', self.log_file_path])  # macOS
                except:
                    try:
                        subprocess.run(['xdg-open', self.log_file_path])  # Linux
                    except:
                        self.user_info(f"Log file location: {self.log_file_path}")

# Global logger instance
addon_logger = None

def get_logger():
    """Get or create the global logger instance"""
    global addon_logger
    if addon_logger is None:
        addon_logger = AddonLogger()
    return addon_logger
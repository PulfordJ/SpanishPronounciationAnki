"""
Spanish Pronunciation Deck Creator Addon - Enhanced Debug Version
Downloads and executes the Spanish pronunciation deck creation script with comprehensive logging
"""

import os
import tempfile
import urllib.request
import subprocess
import sys
import time
import traceback
import threading
from aqt import mw
from aqt.utils import showInfo, showCritical, askUser
from aqt.qt import QAction, QMenu, QTimer
from anki.hooks import addHook

# Import our enhanced logger
from .logger import get_logger

# GitHub raw URLs for the required files
SCRIPT_URL = "https://raw.githubusercontent.com/PulfordJ/SpanishPronounciationAnki/master/create_spanish_decks_via_ankiconnect.py"
DECKS_DATA_URL = "https://raw.githubusercontent.com/PulfordJ/SpanishPronounciationAnki/master/decks_data.py"

def get_config():
    """Get addon configuration with enhanced logging"""
    logger = get_logger()
    try:
        config = mw.addonManager.getConfig(__name__)
        logger.debug(f"Loaded configuration: {config}")
        return config
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return {
            "script_url": SCRIPT_URL,
            "decks_data_url": DECKS_DATA_URL,
            "timeout_seconds": 300,
            "auto_confirm": False,
            "debug_mode": True
        }

def download_and_execute_script():
    """Download and execute script in a completely separate process"""
    logger = get_logger()
    logger.log_function_entry("download_and_execute_script")
    
    try:
        # Create a standalone runner script
        runner_script = _create_standalone_runner()
        
        # Create subprocess log files
        subprocess_log_path = _get_subprocess_log_path()
        subprocess_stdout_path = subprocess_log_path.replace('.log', '_stdout.log')
        subprocess_stderr_path = subprocess_log_path.replace('.log', '_stderr.log')
        
        logger.info(f"Subprocess logs will be written to:")
        logger.info(f"  Combined log: {_get_process_log_path()}")
        logger.info(f"  Stdout log: {subprocess_stdout_path}")
        logger.info(f"  Stderr log: {subprocess_stderr_path}")
        
        # Start the process completely detached from Anki with log file redirection
        import subprocess
        
        # Set up environment for Unicode support
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['PYTHONLEGACYWINDOWSSTDIO'] = '0'
        
        with open(subprocess_stdout_path, 'w', encoding='utf-8') as stdout_file, \
             open(subprocess_stderr_path, 'w', encoding='utf-8') as stderr_file:
            
            process = subprocess.Popen(
                [sys.executable, runner_script],
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0,
                start_new_session=True,  # Completely detach from parent
                stdout=stdout_file,
                stderr=stderr_file,
                env=env
            )
        
        logger.info(f"Started independent process PID: {process.pid}")
        
        # Get log file paths for user
        process_log_file = _get_process_log_path()
        
        showInfo(f"Spanish pronunciation deck creation started in independent process!\n\n"
                f"Process PID: {process.pid}\n\n"
                f"Log files:\n"
                f"• Main: {process_log_file}\n"
                f"• Stdout: {subprocess_stdout_path}\n"
                f"• Stderr: {subprocess_stderr_path}\n\n"
                f"Anki will remain fully responsive.\n"
                f"Use 'Open Process Log' from the debug menu to monitor progress.")
        
        # Addon exits immediately, process runs independently
        
    except Exception as e:
        logger.error(f"Failed to start independent process: {e}")
        logger.log_exception("Process creation failed")
        showCritical(f"Failed to start process: {str(e)}")

def _get_process_log_path():
    """Get the path where the independent process will log"""
    import tempfile
    return os.path.join(tempfile.gettempdir(), "spanish_pronunciation_process.log")

def _get_subprocess_log_path():
    """Get the base path for subprocess stdout/stderr logs"""
    import tempfile
    return os.path.join(tempfile.gettempdir(), "spanish_pronunciation_subprocess.log")

def _create_standalone_runner():
    """Create a standalone Python script that runs independently"""
    import tempfile
    
    # Get configuration
    config = get_config()
    script_url = config.get("script_url", SCRIPT_URL)
    decks_data_url = config.get("decks_data_url", DECKS_DATA_URL)
    timeout = config.get("timeout_seconds", 300)
    
    log_path = _get_process_log_path()
    
    # Create the standalone runner script
    runner_content = f'''#!/usr/bin/env python3
"""
Standalone Spanish Pronunciation Deck Creator Runner
This runs completely independently of Anki
"""

import os
import sys
import time
import tempfile
import urllib.request
import subprocess
import logging
import traceback
from datetime import datetime

# Configuration
SCRIPT_URL = "{script_url}"
DECKS_DATA_URL = "{decks_data_url}"
TIMEOUT = {timeout}
LOG_PATH = r"{log_path}"

def setup_logging():
    """Setup logging to file"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_PATH, mode='w', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)  # Also log to console
        ]
    )
    return logging.getLogger(__name__)

def main():
    logger = setup_logging()
    logger.info("=== Spanish Pronunciation Deck Creator - Independent Process ===")
    logger.info(f"Process PID: {{os.getpid()}}")
    logger.info(f"Python executable: {{sys.executable}}")
    logger.info(f"Working directory: {{os.getcwd()}}")
    logger.info(f"Log file: {{LOG_PATH}}")
    
    start_time = time.time()
    temp_dir = None
    
    try:
        logger.info("Starting download phase...")
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        logger.info(f"Created temporary directory: {{temp_dir}}")
        
        # Download main script
        script_path = os.path.join(temp_dir, "create_spanish_decks_via_ankiconnect.py")
        logger.info(f"Downloading main script from: {{SCRIPT_URL}}")
        
        with urllib.request.urlopen(SCRIPT_URL) as response:
            script_content = response.read().decode('utf-8')
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            logger.info(f"Main script downloaded successfully ({{len(script_content)}} bytes)")
        
        # Download decks data
        decks_data_path = os.path.join(temp_dir, "decks_data.py")
        logger.info(f"Downloading decks data from: {{DECKS_DATA_URL}}")
        
        with urllib.request.urlopen(DECKS_DATA_URL) as response:
            decks_data_content = response.read().decode('utf-8')
            with open(decks_data_path, 'w', encoding='utf-8') as f:
                f.write(decks_data_content)
            logger.info(f"Decks data downloaded successfully ({{len(decks_data_content)}} bytes)")
        
        logger.info("Download phase completed successfully")
        
        # Execute the script
        logger.info("Starting script execution...")
        execution_start = time.time()
        
        # Use the same Python executable that's running this script
        cmd = [sys.executable, script_path]
        
        logger.info(f"Executing: {{' '.join(cmd)}}")
        logger.info(f"Working directory: {{temp_dir}}")
        
        # Set up environment for proper Unicode handling
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['PYTHONLEGACYWINDOWSSTDIO'] = '0'  # Use new Windows console behavior
        
        # Run with real-time output logging
        process = subprocess.Popen(
            cmd,
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
            env=env,
            encoding='utf-8',
            errors='replace'  # Replace problematic characters instead of failing
        )
        
        logger.info(f"Script subprocess started with PID: {{process.pid}}")
        
        # Read output in real-time
        stdout_lines = []
        stderr_lines = []
        
        # Monitor process output
        while True:
            stdout_line = process.stdout.readline()
            stderr_line = process.stderr.readline()
            
            if stdout_line:
                logger.info(f"SCRIPT OUTPUT: {{stdout_line.rstrip()}}")
                stdout_lines.append(stdout_line.rstrip())
            
            if stderr_line:
                logger.warning(f"SCRIPT ERROR: {{stderr_line.rstrip()}}")
                stderr_lines.append(stderr_line.rstrip())
            
            # Check if process is done
            if process.poll() is not None:
                # Read any remaining output
                remaining_stdout, remaining_stderr = process.communicate()
                if remaining_stdout:
                    for line in remaining_stdout.splitlines():
                        logger.info(f"SCRIPT OUTPUT: {{line}}")
                        stdout_lines.append(line)
                if remaining_stderr:
                    for line in remaining_stderr.splitlines():
                        logger.warning(f"SCRIPT ERROR: {{line}}")
                        stderr_lines.append(line)
                break
            
            if not stdout_line and not stderr_line:
                time.sleep(0.1)  # Small delay to prevent busy waiting
        
        returncode = process.returncode
        execution_time = time.time() - execution_start
        
        logger.info(f"Script execution completed with return code: {{returncode}}")
        logger.info(f"Execution time: {{execution_time:.2f}} seconds")
        
        if returncode == 0:
            logger.info("✅ SUCCESS: Spanish pronunciation decks created successfully!")
            if stdout_lines:
                logger.info("Final output summary:")
                for line in stdout_lines[-10:]:  # Last 10 lines
                    logger.info(f"  {{line}}")
        else:
            logger.error(f"❌ FAILED: Script execution failed with return code {{returncode}}")
            if stderr_lines:
                logger.error("Error details:")
                for line in stderr_lines[-10:]:  # Last 10 lines
                    logger.error(f"  {{line}}")
        
    except Exception as e:
        logger.error(f"❌ EXCEPTION: {{e}}")
        logger.error(traceback.format_exc())
        
    finally:
        # Cleanup
        if temp_dir and os.path.exists(temp_dir):
            try:
                import shutil
                shutil.rmtree(temp_dir)
                logger.info(f"Cleaned up temporary directory: {{temp_dir}}")
            except Exception as e:
                logger.warning(f"Failed to clean up {{temp_dir}}: {{e}}")
        
        total_time = time.time() - start_time
        logger.info(f"Total process time: {{total_time:.2f}} seconds")
        logger.info("=== Process completed ===")

if __name__ == "__main__":
    main()
'''
    
    # Write the runner script to a temporary file
    runner_fd, runner_path = tempfile.mkstemp(suffix='.py', prefix='spanish_pronunciation_runner_')
    try:
        with os.fdopen(runner_fd, 'w', encoding='utf-8') as f:
            f.write(runner_content)
        
        logger = get_logger()
        logger.info(f"Created standalone runner script: {{runner_path}}")
        return runner_path
        
    except Exception as e:
        os.close(runner_fd)
        raise


def open_log_file():
    """Open the debug log file"""
    logger = get_logger()
    logger.info("Opening log file...")
    logger.open_log_file()

def open_process_log():
    """Open the independent process log file"""
    logger = get_logger()
    log_path = _get_process_log_path()
    
    if os.path.exists(log_path):
        logger.info(f"Opening process log: {log_path}")
        try:
            if sys.platform == 'win32':
                os.startfile(log_path)
            elif sys.platform == 'darwin':
                subprocess.run(['open', log_path])
            else:
                subprocess.run(['xdg-open', log_path])
        except Exception as e:
            logger.error(f"Failed to open process log: {e}")
            showCritical(f"Failed to open log file: {log_path}\n\nError: {e}")
    else:
        showInfo(f"Process log file not found: {log_path}\n\nThe independent process may not have started yet or may have completed.")
        logger.warning(f"Process log file not found: {log_path}")

def open_subprocess_stdout_log():
    """Open the subprocess stdout log file"""
    logger = get_logger()
    log_path = _get_subprocess_log_path().replace('.log', '_stdout.log')
    
    if os.path.exists(log_path):
        logger.info(f"Opening subprocess stdout log: {log_path}")
        try:
            if sys.platform == 'win32':
                os.startfile(log_path)
            elif sys.platform == 'darwin':
                subprocess.run(['open', log_path])
            else:
                subprocess.run(['xdg-open', log_path])
        except Exception as e:
            logger.error(f"Failed to open subprocess stdout log: {e}")
            showCritical(f"Failed to open log file: {log_path}\n\nError: {e}")
    else:
        showInfo(f"Subprocess stdout log file not found: {log_path}\n\nThe process may not have started yet.")
        logger.warning(f"Subprocess stdout log file not found: {log_path}")

def open_subprocess_stderr_log():
    """Open the subprocess stderr log file"""
    logger = get_logger()
    log_path = _get_subprocess_log_path().replace('.log', '_stderr.log')
    
    if os.path.exists(log_path):
        logger.info(f"Opening subprocess stderr log: {log_path}")
        try:
            if sys.platform == 'win32':
                os.startfile(log_path)
            elif sys.platform == 'darwin':
                subprocess.run(['open', log_path])
            else:
                subprocess.run(['xdg-open', log_path])
        except Exception as e:
            logger.error(f"Failed to open subprocess stderr log: {e}")
            showCritical(f"Failed to open log file: {log_path}\n\nError: {e}")
    else:
        showInfo(f"Subprocess stderr log file not found: {log_path}\n\nThe process may not have started yet.")
        logger.warning(f"Subprocess stderr log file not found: {log_path}")

def show_debug_info():
    """Show debug information dialog"""
    logger = get_logger()
    
    try:
        config = get_config()
        log_path = logger.get_log_file_path()
        
        debug_info = f"""Spanish Pronunciation Deck Creator - Debug Info

Configuration:
- Script URL: {config.get('script_url', 'Not set')}
- Timeout: {config.get('timeout_seconds', 'Not set')} seconds
- Auto Confirm: {config.get('auto_confirm', 'Not set')}
- Debug Mode: {config.get('debug_mode', 'Not set')}

Logging:
- Log File: {log_path if log_path else 'Not available'}
- Logger Active: {logger is not None}

System:
- Python: {sys.version}
- Platform: {sys.platform}
- Anki Profile: {mw.pm.name if hasattr(mw.pm, 'name') else 'Unknown'}

Actions:
- Use Tools > Open Log File to view detailed logs
- Use Tools > Test Logger to verify logging works
"""
        
        logger.info("Showing debug info to user")
        showInfo(debug_info)
        
    except Exception as e:
        logger.error(f"Failed to show debug info: {e}")
        logger.user_error(f"Failed to show debug info: {str(e)}")

def test_logger():
    """Test the logging system"""
    logger = get_logger()
    
    logger.info("=== Logger Test Started ===")
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    try:
        # Intentional error for testing
        raise ValueError("This is a test exception")
    except Exception:
        logger.log_exception("Test exception logging")
    
    logger.info("=== Logger Test Completed ===")
    logger.user_info("Logger test completed. Check debug console and log file for messages.")

def setup_menu():
    """Add menu items to Tools menu with debug options"""
    logger = get_logger()
    logger.info("Setting up menu items...")
    
    try:
        # Main action
        main_action = QAction("Create Spanish Pronunciation Deck", mw)
        main_action.triggered.connect(download_and_execute_script)
        mw.form.menuTools.addAction(main_action)
        
        # Create debug submenu
        debug_menu = QMenu("Spanish Pronunciation Debug", mw)
        
        # Debug actions
        log_action = QAction("Open Addon Log File", mw)
        log_action.triggered.connect(open_log_file)
        debug_menu.addAction(log_action)
        
        debug_menu.addSeparator()
        
        process_log_action = QAction("Open Process Log File", mw)
        process_log_action.triggered.connect(open_process_log)
        debug_menu.addAction(process_log_action)
        
        stdout_log_action = QAction("Open Subprocess Stdout Log", mw)
        stdout_log_action.triggered.connect(open_subprocess_stdout_log)
        debug_menu.addAction(stdout_log_action)
        
        stderr_log_action = QAction("Open Subprocess Stderr Log", mw)
        stderr_log_action.triggered.connect(open_subprocess_stderr_log)
        debug_menu.addAction(stderr_log_action)
        
        debug_menu.addSeparator()
        
        info_action = QAction("Show Debug Info", mw)
        info_action.triggered.connect(show_debug_info)
        debug_menu.addAction(info_action)
        
        test_action = QAction("Test Logger", mw)
        test_action.triggered.connect(test_logger)
        debug_menu.addAction(test_action)
        
        # Add debug menu to Tools
        mw.form.menuTools.addMenu(debug_menu)
        
        logger.info("Menu setup completed successfully")
        logger.debug("Added main action and debug submenu")
        
    except Exception as e:
        logger.error(f"Failed to setup menu: {e}")
        logger.log_exception("Menu setup failed")

def on_profile_loaded():
    """Called when Anki profile is loaded"""
    logger = get_logger()
    logger.info("=== Spanish Pronunciation Deck Creator Addon Loaded ===")
    logger.info(f"Addon initialized at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    setup_menu()
    
    # Log initial state
    config = get_config()
    logger.info(f"Addon configuration loaded: {config}")

# Setup the addon when Anki starts
addHook("profileLoaded", on_profile_loaded)
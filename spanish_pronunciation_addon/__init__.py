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
    """Download the Spanish pronunciation script and execute it asynchronously"""
    logger = get_logger()
    logger.log_function_entry("download_and_execute_script")
    
    # Run the actual work in a separate thread to avoid blocking Anki's main thread
    def async_execution():
        _download_and_execute_script_impl()
    
    # Start execution in background thread
    execution_thread = threading.Thread(target=async_execution, daemon=True)
    execution_thread.start()
    
    logger.info("Script execution started in background thread")
    showInfo("Spanish pronunciation deck creation started in background.\n\nCheck the debug log for progress updates.\n\nThis will run asynchronously so Anki remains responsive.")

def _show_info_thread_safe(message):
    """Show info dialog in a thread-safe way"""
    def show_on_main_thread():
        showInfo(message)
    
    # Use QTimer to execute on main thread
    QTimer.singleShot(0, show_on_main_thread)

def _show_error_thread_safe(message):
    """Show error dialog in a thread-safe way"""
    def show_on_main_thread():
        showCritical(message)
    
    # Use QTimer to execute on main thread
    QTimer.singleShot(0, show_on_main_thread)

def _download_and_execute_script_impl():
    """Internal implementation that does the actual work"""
    logger = get_logger()
    
    start_time = time.time()
    temp_path = None
    
    try:
        # Log system information
        logger.log_system_info()
        
        # Get configuration
        config = get_config()
        script_url = config.get("script_url", SCRIPT_URL)
        decks_data_url = config.get("decks_data_url", DECKS_DATA_URL)
        timeout = config.get("timeout_seconds", 300)
        auto_confirm = config.get("auto_confirm", False)
        
        logger.info(f"Starting Spanish pronunciation deck creation")
        logger.info(f"Script URL: {script_url}")
        logger.info(f"Decks Data URL: {decks_data_url}")
        logger.info(f"Timeout: {timeout} seconds")
        logger.info(f"Auto confirm: {auto_confirm}")
        
        # Ask user for confirmation unless auto_confirm is enabled
        if not auto_confirm:
            logger.debug("Asking user for confirmation")
            confirmation_msg = ("This will download and run the Spanish Pronunciation Deck Creator script.\n\n"
                               "Make sure you have AnkiConnect addon installed and Anki is running.\n\n"
                               "Do you want to continue?")
            
            if not askUser(confirmation_msg):
                logger.info("User cancelled the operation")
                return
            
            logger.info("User confirmed the operation")
        else:
            logger.info("Auto-confirmation enabled, skipping user prompt")
        
        # Download phase
        logger.info("Starting file downloads...")
        
        download_start = time.time()
        
        # Create temporary directory for both files
        temp_dir = tempfile.mkdtemp()
        logger.debug(f"Created temporary directory: {temp_dir}")
        
        # Download main script
        script_path = os.path.join(temp_dir, "create_spanish_decks_via_ankiconnect.py")
        logger.debug(f"Downloading main script from: {script_url}")
        
        try:
            with urllib.request.urlopen(script_url) as response:
                script_content = response.read().decode('utf-8')
                with open(script_path, 'w', encoding='utf-8') as f:
                    f.write(script_content)
                logger.info(f"Main script downloaded successfully ({len(script_content)} bytes)")
        
        except urllib.error.URLError as e:
            logger.error(f"Failed to download main script: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error downloading main script: {e}")
            raise
        
        # Download decks_data.py
        decks_data_path = os.path.join(temp_dir, "decks_data.py")
        logger.debug(f"Downloading decks data from: {decks_data_url}")
        
        try:
            with urllib.request.urlopen(decks_data_url) as response:
                decks_data_content = response.read().decode('utf-8')
                with open(decks_data_path, 'w', encoding='utf-8') as f:
                    f.write(decks_data_content)
                logger.info(f"Decks data downloaded successfully ({len(decks_data_content)} bytes)")
        
        except urllib.error.URLError as e:
            logger.error(f"Failed to download decks data: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error downloading decks data: {e}")
            raise
        
        download_time = time.time() - download_start
        logger.info(f"All downloads completed successfully in {download_time:.2f} seconds")
        
        temp_path = script_path  # Main script path for execution
        
        # Execution phase
        logger.info("Starting script execution...")
        execution_start = time.time()
        
        # Prepare execution environment
        execution_env = os.environ.copy()
        execution_cmd = [sys.executable, temp_path]
        
        # Set working directory to temp_dir so script can find decks_data.py
        execution_cwd = temp_dir
        
        logger.debug(f"Execution command: {' '.join(execution_cmd)}")
        logger.debug(f"Working directory: {execution_cwd}")
        logger.debug(f"Python executable: {sys.executable}")
        logger.debug(f"Temporary directory contains: {os.listdir(temp_dir)}")
        
        # Test subprocess execution with a simple command first
        logger.info("Testing subprocess execution with simple Python command...")
        try:
            test_cmd = [sys.executable, "-c", "print('Hello from subprocess'); import sys; print(f'Python version: {sys.version}', file=sys.stderr)"]
            test_process = subprocess.Popen(
                test_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=execution_cwd,
                encoding='utf-8',
                errors='replace'
            )
            
            test_stdout, test_stderr = test_process.communicate(timeout=10)
            logger.info(f"Test subprocess completed with return code: {test_process.returncode}")
            logger.debug(f"Test stdout: {test_stdout.strip()}")
            logger.debug(f"Test stderr: {test_stderr.strip()}")
            
            if test_process.returncode != 0:
                logger.warning("Test subprocess failed, but continuing with main script...")
            else:
                logger.info("Test subprocess successful, proceeding with main script")
                
        except Exception as e:
            logger.error(f"Test subprocess failed: {e}")
            logger.warning("Test failed but continuing with main script anyway...")
        
        try:
            # Run the script in a subprocess to avoid blocking Anki
            logger.info(f"Executing script with {timeout} second timeout...")
            
            # Set UTF-8 encoding for subprocess to handle Unicode characters
            execution_env['PYTHONIOENCODING'] = 'utf-8'
            
            # Use Popen for real-time logging
            process = subprocess.Popen(
                execution_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=execution_env,
                cwd=execution_cwd,
                encoding='utf-8',
                errors='replace',
                bufsize=1,  # Line buffered
                universal_newlines=True
            )
            
            logger.info("Subprocess started, monitoring output...")
            logger.debug(f"Process PID: {process.pid}")
            
            # Monitor process output in real-time
            stdout_lines = []
            stderr_lines = []
            
            
            def read_stdout():
                """Read stdout in a separate thread"""
                try:
                    for line in iter(process.stdout.readline, ''):
                        if line:
                            line = line.rstrip('\n\r')
                            safe_line = line.encode('ascii', errors='replace').decode('ascii')
                            logger.info(f"SUBPROCESS STDOUT: {safe_line}")
                            stdout_lines.append(line)
                        if process.poll() is not None:
                            break
                except Exception as e:
                    logger.error(f"Error reading stdout: {e}")
                finally:
                    if process.stdout:
                        process.stdout.close()
            
            def read_stderr():
                """Read stderr in a separate thread"""
                try:
                    for line in iter(process.stderr.readline, ''):
                        if line:
                            line = line.rstrip('\n\r')
                            safe_line = line.encode('ascii', errors='replace').decode('ascii')
                            logger.warning(f"SUBPROCESS STDERR: {safe_line}")
                            stderr_lines.append(line)
                        if process.poll() is not None:
                            break
                except Exception as e:
                    logger.error(f"Error reading stderr: {e}")
                finally:
                    if process.stderr:
                        process.stderr.close()
            
            # Start reader threads
            stdout_thread = threading.Thread(target=read_stdout)
            stderr_thread = threading.Thread(target=read_stderr)
            stdout_thread.daemon = True
            stderr_thread.daemon = True
            
            stdout_thread.start()
            stderr_thread.start()
            
            # Wait for process to complete or timeout with periodic status checks
            try:
                # Check process status periodically
                check_interval = 5  # seconds
                elapsed = 0
                
                while process.poll() is None and elapsed < timeout:
                    logger.debug(f"Process {process.pid} still running after {elapsed}s...")
                    logger.debug(f"Stdout thread alive: {stdout_thread.is_alive()}")
                    logger.debug(f"Stderr thread alive: {stderr_thread.is_alive()}")
                    
                    # Wait for a short interval or until process completes
                    try:
                        returncode = process.wait(timeout=check_interval)
                        break  # Process completed
                    except subprocess.TimeoutExpired:
                        elapsed += check_interval
                        continue
                
                if process.poll() is None:
                    # Process is still running after timeout
                    raise subprocess.TimeoutExpired(execution_cmd, timeout)
                
                returncode = process.returncode
                execution_time = time.time() - execution_start
                logger.info(f"Script execution completed with return code: {returncode}")
                logger.debug(f"Execution time: {execution_time:.2f} seconds")
                
                # Wait for reader threads to finish
                stdout_thread.join(timeout=5)
                stderr_thread.join(timeout=5)
                
            except subprocess.TimeoutExpired:
                execution_time = time.time() - execution_start
                logger.error(f"Process timed out after {timeout} seconds (actual: {execution_time:.2f}s)")
                logger.info("Terminating subprocess...")
                process.terminate()
                
                # Wait a bit for graceful termination
                try:
                    process.wait(timeout=10)
                    logger.info("Subprocess terminated gracefully")
                except subprocess.TimeoutExpired:
                    logger.warning("Subprocess did not terminate gracefully, killing...")
                    process.kill()
                    process.wait()
                    logger.warning("Subprocess killed")
                
                # Wait for reader threads to finish
                stdout_thread.join(timeout=5)
                stderr_thread.join(timeout=5)
                
                _show_error_thread_safe(f"Script execution timed out after {timeout} seconds.")
                return
            
            # Combine output for further processing
            result_stdout = '\n'.join(stdout_lines)
            result_stderr = '\n'.join(stderr_lines)
            
            logger.debug(f"Total stdout lines: {len(stdout_lines)}")
            logger.debug(f"Total stderr lines: {len(stderr_lines)}")
            
            # Handle results with safe Unicode handling
            if returncode == 0:
                success_msg = f"Spanish pronunciation deck creation completed successfully!\n\n"
                if result_stdout.strip():
                    try:
                        # Clean output for display, replacing problematic Unicode characters
                        clean_output = result_stdout.encode('ascii', errors='replace').decode('ascii')
                        success_msg += f"Output:\n{clean_output}"
                    except Exception as e:
                        logger.warning(f"Error processing output for display: {e}")
                        success_msg += f"Output: {len(result_stdout)} characters (contains Unicode characters)"
                else:
                    success_msg += "No output from script."
                
                logger.info("Script execution successful")
                _show_info_thread_safe(success_msg)
                
            else:
                error_msg = f"Script execution failed with return code {returncode}!\n\n"
                
                if result_stderr.strip():
                    try:
                        clean_stderr = result_stderr.encode('ascii', errors='replace').decode('ascii')
                        error_msg += f"Error:\n{clean_stderr}\n\n"
                    except Exception as e:
                        logger.warning(f"Error processing stderr for display: {e}")
                        error_msg += f"Error: {len(result_stderr)} characters (contains Unicode characters)\n\n"
                
                if result_stdout.strip():
                    try:
                        clean_stdout = result_stdout.encode('ascii', errors='replace').decode('ascii')
                        error_msg += f"Output:\n{clean_stdout}"
                    except Exception as e:
                        logger.warning(f"Error processing stdout for display: {e}")
                        error_msg += f"Output: {len(result_stdout)} characters (contains Unicode characters)"
                
                logger.error(f"Script execution failed with return code {returncode}")
                _show_error_thread_safe(error_msg)
        
        except Exception as e:
            execution_time = time.time() - execution_start
            logger.error(f"Script execution failed with exception after {execution_time:.2f}s: {e}")
            logger.log_exception("Script execution exception")
            _show_error_thread_safe(f"Error executing script: {str(e)}")
        
    except urllib.error.URLError as e:
        logger.error(f"Network error during download: {e}")
        _show_error_thread_safe(f"Failed to download script: {str(e)}\n\nPlease check your internet connection.")
        
    except Exception as e:
        logger.error(f"Unexpected error in main function: {e}")
        logger.log_exception("Unexpected error in download_and_execute_script")
        _show_error_thread_safe(f"Unexpected error: {str(e)}")
        
    finally:
        # Clean up temporary directory and files
        if 'temp_dir' in locals():
            try:
                import shutil
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                    logger.debug(f"Cleaned up temporary directory: {temp_dir}")
                else:
                    logger.debug(f"Temporary directory already removed: {temp_dir}")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary directory {temp_dir}: {e}")
        
        total_time = time.time() - start_time
        logger.info(f"Total operation time: {total_time:.2f} seconds")
        logger.log_function_exit("download_and_execute_script")

def open_log_file():
    """Open the debug log file"""
    logger = get_logger()
    logger.info("Opening log file...")
    logger.open_log_file()

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
        log_action = QAction("Open Log File", mw)
        log_action.triggered.connect(open_log_file)
        debug_menu.addAction(log_action)
        
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
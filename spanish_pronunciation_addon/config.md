# Spanish Pronunciation Deck Creator Configuration - Enhanced Debug Version

## Basic Settings

- **script_url**: The URL to download the main Spanish pronunciation script from
- **decks_data_url**: The URL to download the decks_data.py file from
- **timeout_seconds**: Maximum time to wait for script execution (default: 300 seconds)
- **auto_confirm**: If true, skips confirmation dialog before running script (default: false)

## Debug Settings

- **debug_mode**: Enable enhanced debugging features (default: true)
- **log_level**: Logging level - DEBUG, INFO, WARNING, ERROR, CRITICAL (default: DEBUG)
- **log_to_file**: Write logs to file in addon directory (default: true)
- **log_to_console**: Show logs in Anki debug console (default: true)
- **show_system_info**: Log system information when script runs (default: true)

## Debug Features

### Enhanced Logging
- Detailed function entry/exit logging
- Execution timing for all operations
- System environment information
- Full stdout/stderr capture from script execution
- Exception tracing with full stack traces

### Debug Menu
Access via **Tools > Spanish Pronunciation Debug**:

1. **Open Log File** - Opens the debug.log file in your default text editor
2. **Show Debug Info** - Shows current configuration and system information
3. **Test Logger** - Runs a test of all logging levels

### Log File Location
- **Windows**: `%APPDATA%\Anki2\addons21\spanish_pronunciation_addon\debug.log`
- **Mac**: `~/Library/Application Support/Anki2/addons21/spanish_pronunciation_addon/debug.log`
- **Linux**: `~/.local/share/Anki2/addons21/spanish_pronunciation_addon/debug.log`

## Usage

### Main Function
1. Go to **Tools > Create Spanish Pronunciation Deck**
2. Confirm when prompted (unless auto_confirm is enabled)
3. Monitor progress in debug console
4. Check detailed logs in log file

### Debug Console
Open **Tools > Debug Console** to see real-time logging output

### Command Prompt Logging (Windows)
1. Launch Anki from command prompt: `"C:\Program Files\Anki\anki.exe"`
2. See addon output directly in terminal

## Requirements

Before using this addon, ensure you have:

1. **AnkiConnect addon** installed and enabled
2. **Anki** running and accessible
3. **Internet connection** to download the script

## Troubleshooting

### Basic Issues
- If the script fails, ensure AnkiConnect is installed and Anki is running
- Check your internet connection if download fails
- The script may take several minutes to complete depending on deck size

### Debug Information
1. Use **Tools > Spanish Pronunciation Debug > Show Debug Info** for system status
2. Check **Tools > Spanish Pronunciation Debug > Open Log File** for detailed logs
3. Use **Tools > Spanish Pronunciation Debug > Test Logger** to verify logging works
4. Monitor **Tools > Debug Console** for real-time output

### Log Analysis
The debug.log file contains:
- Timestamps for all operations
- Function entry/exit points
- Download progress and timing
- Script execution details
- Error messages with full context
- System environment information

### Common Error Patterns
- **URLError**: Network connectivity issues
- **TimeoutExpired**: Script taking longer than configured timeout
- **FileNotFoundError**: Temporary file cleanup issues
- **Permission errors**: File system access problems

Set `log_level` to `INFO` or `WARNING` to reduce log verbosity if needed.
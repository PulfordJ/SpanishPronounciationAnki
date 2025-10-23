# Spanish Pronunciation Deck Creator - Anki Addon

This Anki addon automatically downloads and executes the Spanish pronunciation deck creation script from the [SpanishPronounciationAnki](https://github.com/PulfordJ/SpanishPronounciationAnki) repository.

## Features

- Downloads the latest version of the Spanish pronunciation script
- Integrates seamlessly with Anki through the Tools menu
- Creates Spanish pronunciation flashcards with text-to-speech
- Handles deck and model creation automatically
- Provides user feedback and error handling

## Installation

1. Copy the `spanish_pronunciation_addon` folder to your Anki addons directory
2. Restart Anki
3. Ensure you have the AnkiConnect addon installed

## Usage

1. Open Anki
2. Go to **Tools > Create Spanish Pronunciation Deck**
3. Confirm the action when prompted
4. Wait for the script to download and execute
5. Review the results in the completion message

## Requirements

- Anki 2.1.49 or later
- AnkiConnect addon
- Internet connection
- Python 3.6 or later

## What it Does

The script will:
- Create a custom Anki model for Spanish pronunciation cards
- Set up deck structure for Spanish learning
- Add flashcards with text-to-speech functionality
- Filter out duplicate cards automatically
- Provide detailed logging of the process

## Configuration

You can modify the addon behavior by editing the config.json file:
- `script_url`: Change the source URL for the script
- `timeout_seconds`: Adjust execution timeout
- `auto_confirm`: Skip confirmation dialog

## Troubleshooting

If you encounter issues:
1. Ensure AnkiConnect is installed and working
2. Check your internet connection
3. Verify Anki is running and accessible
4. Check the Anki debug console for detailed error messages

## Credits

This addon is a wrapper for the excellent work by PulfordJ in the [SpanishPronounciationAnki](https://github.com/PulfordJ/SpanishPronounciationAnki) repository.
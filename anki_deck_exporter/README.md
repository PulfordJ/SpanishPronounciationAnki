# Spanish Deck Exporter Plugin

This Anki plugin provides API endpoints to export Spanish pronunciation decks as .apkg files programmatically.

## Features

- Export specific decks as .apkg files via API
- Integration with AnkiConnect (if available)
- Standalone HTTP server fallback
- Configurable export paths and allowed decks
- Automatic timestamping of exports

## Installation

1. Copy the `anki_deck_exporter` folder to your Anki addons directory:
   - Windows: `%APPDATA%\Anki2\addons21\`
   - macOS: `~/Library/Application Support/Anki2/addons21/`
   - Linux: `~/.local/share/Anki2/addons21/`

2. Restart Anki

3. The plugin will automatically start and integrate with AnkiConnect if available, or start its own API server on port 8766

## API Endpoints

### Export Deck
**Endpoint:** `/exportDeckApkg` (POST)

**Request:**
```json
{
    "deck_name": "Spanish Pronunciation Trainer",
    "output_path": "/path/to/output.apkg"  // optional
}
```

**Response:**
```json
{
    "success": true,
    "file_path": "/path/to/exported/deck.apkg",
    "file_size": 1234567,
    "deck_name": "Spanish Pronunciation Trainer",
    "export_time": 1640995200
}
```

### List Exportable Decks
**Endpoint:** `/listExportableDecks` (POST)

**Response:**
```json
{
    "success": true,
    "decks": [
        {
            "name": "Spanish Pronunciation Trainer",
            "id": 1234567890,
            "card_count": 500,
            "modified": 1640995200
        }
    ]
}
```

## Configuration

Edit the plugin configuration in Anki's addon settings or modify `config.json`:

- `export_path`: Default directory for exports (empty = temp directory)
- `allowed_decks`: List of deck names that can be exported
- `enable_api`: Enable/disable API functionality
- `api_port`: Port for standalone server (default: 8766)

## Usage from Python Script

```python
import requests

# Export deck
response = requests.post('http://localhost:8766/exportDeckApkg', json={
    'deck_name': 'Spanish Pronunciation Trainer',
    'output_path': './Spanish_Deck.apkg'
})

result = response.json()
if result['success']:
    print(f"Exported to: {result['file_path']}")
else:
    print(f"Error: {result['error']}")
```
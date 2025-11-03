"""
Spanish Deck Exporter Plugin for Anki
Provides API endpoint to export decks as .apkg files programmatically
"""

from .deck_exporter import DeckExporter

# Initialize the plugin
deck_exporter = DeckExporter()
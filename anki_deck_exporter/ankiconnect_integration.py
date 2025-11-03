"""
AnkiConnect Integration for Deck Exporter
Extends existing AnkiConnect functionality
"""

import json
import os
import tempfile
import time
from typing import Dict, Any, Optional

from anki.exporting import AnkiPackageExporter
from aqt import mw


def register_deck_export_actions():
    """Register deck export actions with AnkiConnect"""
    
    # Import AnkiConnect's action registry
    try:
        # Try to import AnkiConnect's webBindings
        import sys
        ankiconnect_path = None
        
        # Find AnkiConnect addon
        for addon_name in mw.addonManager.allAddons():
            addon_meta = mw.addonManager.addonMeta(addon_name)
            if addon_meta.get('name', '').lower() == 'ankiconnect':
                ankiconnect_path = mw.addonManager.addonsFolder(addon_name)
                break
        
        if ankiconnect_path:
            sys.path.insert(0, ankiconnect_path)
            from . import AnkiConnect
            
            # Get the existing action map
            if hasattr(AnkiConnect, 'actions') and hasattr(AnkiConnect.actions, 'actions'):
                actions = AnkiConnect.actions.actions
                
                # Add our custom actions
                actions['exportDeckApkg'] = export_deck_apkg
                actions['listExportableDecks'] = list_exportable_decks
                
                return True
        
        return False
        
    except Exception as e:
        print(f"Failed to register with AnkiConnect: {e}")
        return False


def export_deck_apkg(deck_name: str, output_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Export a deck as .apkg file
    
    Args:
        deck_name: Name of the deck to export
        output_path: Optional custom output path
        
    Returns:
        Dict with success status and file path
    """
    try:
        # Get plugin config
        config = mw.addonManager.getConfig(__name__) or {}
        allowed_decks = config.get("allowed_decks", ["Spanish Pronunciation Trainer"])
        export_path = config.get("export_path", tempfile.gettempdir())
        
        # Validate deck name
        if deck_name not in allowed_decks:
            allowed = ", ".join(allowed_decks)
            return {
                "success": False,
                "error": f"Deck '{deck_name}' not in allowed decks. Allowed: {allowed}"
            }
        
        # Find the deck
        deck_id = mw.col.decks.id(deck_name, create=False)
        if not deck_id:
            return {
                "success": False,
                "error": f"Deck '{deck_name}' not found"
            }
        
        # Determine output path
        if not output_path:
            timestamp = int(time.time())
            filename = f"{deck_name.replace(' ', '_').replace('::', '_')}_{timestamp}.apkg"
            output_path = os.path.join(export_path, filename)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Create exporter
        exporter = AnkiPackageExporter(mw.col)
        exporter.did = deck_id
        exporter.includeMedia = True
        exporter.includeSched = False
        exporter.includeDecks = True
        
        # Export the deck
        exporter.exportInto(output_path)
        
        # Verify file was created
        if not os.path.exists(output_path):
            return {
                "success": False,
                "error": "Export completed but file was not created"
            }
        
        file_size = os.path.getsize(output_path)
        
        return {
            "success": True,
            "file_path": output_path,
            "file_size": file_size,
            "deck_name": deck_name,
            "export_time": time.time()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Export failed: {str(e)}"
        }


def list_exportable_decks() -> Dict[str, Any]:
    """
    List all decks that can be exported
    
    Returns:
        Dict with available decks and their info
    """
    try:
        # Get plugin config
        config = mw.addonManager.getConfig(__name__) or {}
        allowed_decks = config.get("allowed_decks", ["Spanish Pronunciation Trainer"])
        
        available_decks = []
        
        for deck_name in allowed_decks:
            deck_id = mw.col.decks.id(deck_name, create=False)
            if deck_id:
                # Get deck info
                deck_info = mw.col.decks.get(deck_id)
                card_count = mw.col.db.scalar(
                    "SELECT count() FROM cards WHERE did = ? OR did IN (SELECT id FROM decks WHERE name LIKE ?)", 
                    deck_id, deck_name + "::%"
                )
                
                available_decks.append({
                    "name": deck_name,
                    "id": deck_id,
                    "card_count": card_count,
                    "modified": deck_info.get("mod", 0)
                })
        
        return {
            "success": True,
            "decks": available_decks
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to list decks: {str(e)}"
        }
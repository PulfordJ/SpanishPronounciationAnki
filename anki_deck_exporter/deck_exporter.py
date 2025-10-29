"""
Deck Exporter Plugin for Anki
Extends AnkiConnect with deck export functionality
"""

import json
import os
import tempfile
import time
from typing import Dict, Any, Optional

from anki.exporting import AnkiPackageExporter
from aqt import mw
from aqt.utils import showInfo

# Import AnkiConnect if available
try:
    from .ankiconnect import ankiconnect
    ANKICONNECT_AVAILABLE = True
except ImportError:
    ANKICONNECT_AVAILABLE = False


class DeckExporter:
    def __init__(self):
        self.config = self._load_config()
        if ANKICONNECT_AVAILABLE:
            self._register_ankiconnect_actions()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load plugin configuration"""
        default_config = {
            "export_path": tempfile.gettempdir(),
            "allowed_decks": ["Spanish Pronunciation Trainer"],
            "enable_api": True
        }
        
        # Try to load from Anki's config system
        config = mw.addonManager.getConfig(__name__)
        if config:
            default_config.update(config)
        
        return default_config
    
    def _register_ankiconnect_actions(self):
        """Register custom actions with AnkiConnect"""
        if not ANKICONNECT_AVAILABLE:
            return
        
        # Add our custom action to AnkiConnect
        ankiconnect.addAction('exportDeckApkg', self.export_deck_apkg)
        ankiconnect.addAction('listExportableDecks', self.list_exportable_decks)
    
    def export_deck_apkg(self, deck_name: str, output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Export a deck as .apkg file
        
        Args:
            deck_name: Name of the deck to export
            output_path: Optional custom output path
            
        Returns:
            Dict with success status and file path
        """
        try:
            # Validate deck name
            if deck_name not in self.config.get("allowed_decks", []):
                allowed = ", ".join(self.config.get("allowed_decks", []))
                return {
                    "success": False,
                    "error": f"Deck '{deck_name}' not in allowed decks. Allowed: {allowed}"
                }
            
            # Find the deck
            deck_id = mw.col.decks.id(deck_name)
            if not deck_id:
                return {
                    "success": False,
                    "error": f"Deck '{deck_name}' not found"
                }
            
            # Determine output path
            if not output_path:
                timestamp = int(time.time())
                filename = f"{deck_name.replace(' ', '_')}_{timestamp}.apkg"
                output_path = os.path.join(self.config["export_path"], filename)
            
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
    
    def list_exportable_decks(self) -> Dict[str, Any]:
        """
        List all decks that can be exported
        
        Returns:
            Dict with available decks and their info
        """
        try:
            allowed_decks = self.config.get("allowed_decks", [])
            available_decks = []
            
            for deck_name in allowed_decks:
                deck_id = mw.col.decks.id(deck_name, create=False)
                if deck_id:
                    # Get deck info
                    deck_info = mw.col.decks.get(deck_id)
                    card_count = mw.col.db.scalar(
                        "SELECT count() FROM cards WHERE did = ?", deck_id
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


# Fallback implementation if AnkiConnect is not available
class StandaloneAPI:
    """Standalone HTTP server for deck export API"""
    
    def __init__(self, deck_exporter: DeckExporter, port: int = 8766):
        self.deck_exporter = deck_exporter
        self.port = port
        self.server = None
    
    def start_server(self):
        """Start HTTP server for API endpoints"""
        try:
            from http.server import HTTPServer, BaseHTTPRequestHandler
            import threading
            
            class APIHandler(BaseHTTPRequestHandler):
                def do_POST(self):
                    if self.path == '/exportDeckApkg':
                        self._handle_export_request()
                    elif self.path == '/listExportableDecks':
                        self._handle_list_request()
                    else:
                        self._send_error(404, "Endpoint not found")
                
                def _handle_export_request(self):
                    try:
                        content_length = int(self.headers['Content-Length'])
                        post_data = self.rfile.read(content_length)
                        data = json.loads(post_data.decode('utf-8'))
                        
                        deck_name = data.get('deck_name')
                        output_path = data.get('output_path')
                        
                        if not deck_name:
                            self._send_error(400, "deck_name is required")
                            return
                        
                        result = self.server.deck_exporter.export_deck_apkg(deck_name, output_path)
                        self._send_json_response(result)
                        
                    except Exception as e:
                        self._send_error(500, f"Internal error: {str(e)}")
                
                def _handle_list_request(self):
                    try:
                        result = self.server.deck_exporter.list_exportable_decks()
                        self._send_json_response(result)
                    except Exception as e:
                        self._send_error(500, f"Internal error: {str(e)}")
                
                def _send_json_response(self, data):
                    response = json.dumps(data).encode('utf-8')
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Content-Length', str(len(response)))
                    self.end_headers()
                    self.wfile.write(response)
                
                def _send_error(self, code, message):
                    error_response = json.dumps({"success": False, "error": message}).encode('utf-8')
                    self.send_response(code)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Content-Length', str(len(error_response)))
                    self.end_headers()
                    self.wfile.write(error_response)
                
                def log_message(self, format, *args):
                    # Suppress default logging
                    pass
            
            self.server = HTTPServer(('localhost', self.port), APIHandler)
            self.server.deck_exporter = self.deck_exporter
            
            # Start server in a separate thread
            server_thread = threading.Thread(target=self.server.serve_forever)
            server_thread.daemon = True
            server_thread.start()
            
            return True
            
        except Exception as e:
            print(f"Failed to start API server: {e}")
            return False


# Initialize the plugin
def init_plugin():
    """Initialize the deck exporter plugin"""
    global deck_exporter_instance
    
    deck_exporter_instance = DeckExporter()
    
    # If AnkiConnect is not available, start standalone server
    if not ANKICONNECT_AVAILABLE:
        standalone_api = StandaloneAPI(deck_exporter_instance)
        if standalone_api.start_server():
            showInfo("Spanish Deck Exporter: API server started on port 8766")
        else:
            showInfo("Spanish Deck Exporter: Failed to start API server")


# Initialize when Anki starts
if mw:
    init_plugin()
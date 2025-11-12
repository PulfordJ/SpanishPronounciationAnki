"""
Spanish Deck Export and GitHub Release Automation
Exports Anki deck and creates GitHub releases automatically
"""

import requests
import os
import json
import time
import subprocess
from datetime import datetime
from typing import Dict, Any, Optional
import create_spanish_decks_via_ankiconnect

# Configuration
ANKI_EXPORT_URL = "http://localhost:8765"  # AnkiConnect URL
DECK_NAME = "Spanish Pronunciation Trainer"
GITHUB_REPO = "PulfordJ/SpanishPronounciationAnki"  # Update this
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Set this environment variable


def invoke_ankiconnect(action: str, **params) -> Dict[str, Any]:
    """Send request to AnkiConnect API"""
    response = requests.post(ANKI_EXPORT_URL, json={
        "action": action,
        "version": 6,
        "params": params
    })
    response.raise_for_status()
    result = response.json()
    if result.get("error"):
        raise Exception(result["error"])
    return result.get("result")


def export_deck(output_path: Optional[str] = None) -> Dict[str, Any]:
    """Export Spanish pronunciation deck as .apkg file"""
    try:
        print("🔍 Checking if deck export API is available...")
        
        # Try to export using our custom plugin first
        try:
            result = invoke_ankiconnect("exportDeckApkg", 
                                      deck_name=DECK_NAME, 
                                      output_path=output_path)
            if result.get("success"):
                print(f"✅ Deck exported successfully: {result['file_path']}")
                return result
        except Exception as e:
            print(f"⚠️ Custom export failed: {e}")
        
        # Fallback: Use direct HTTP request to plugin server
        try:
            export_response = requests.post("http://localhost:8766/exportDeckApkg", 
                                          json={"deck_name": DECK_NAME, "output_path": output_path})
            if export_response.status_code == 200:
                result = export_response.json()
                if result.get("success"):
                    print(f"✅ Deck exported via plugin server: {result['file_path']}")
                    return result
        except Exception as e:
            print(f"⚠️ Plugin server export failed: {e}")
        
        # If both fail, provide instructions
        raise Exception(
            "Could not export deck automatically. Please ensure:\n"
            "1. Anki is running\n"
            "2. AnkiConnect addon is installed\n"
            "3. Spanish Deck Exporter plugin is installed\n"
            "4. The 'Spanish Pronunciation Trainer' deck exists"
        )
        
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_deck_stats() -> Dict[str, Any]:
    """Get statistics about the deck"""
    try:
        # Get deck info
        deck_names = invoke_ankiconnect("deckNames")
        
        # Find our deck and subdecks
        spanish_decks = [name for name in deck_names if name.startswith(DECK_NAME)]
        
        total_cards = 0
        deck_info = {}
        
        for deck in spanish_decks:
            try:
                cards = invoke_ankiconnect("findCards", query=f'deck:"{deck}"')
                card_count = len(cards)
                total_cards += card_count
                
                # Get subdeck name
                subdeck = deck.replace(DECK_NAME + "::", "") if "::" in deck else "Main"
                deck_info[subdeck] = card_count
                
            except Exception as e:
                print(f"⚠️ Could not get stats for deck {deck}: {e}")
        
        return {
            "total_cards": total_cards,
            "subdecks": deck_info,
            "deck_count": len(spanish_decks)
        }
        
    except Exception as e:
        print(f"⚠️ Could not get deck statistics: {e}")
        return {"total_cards": 0, "subdecks": {}, "deck_count": 0}


def create_github_release(apkg_file_path: str, version: str, deck_stats: Dict[str, Any]) -> bool:
    """Create a GitHub release with the .apkg file"""
    
    if not GITHUB_TOKEN:
        print("❌ GITHUB_TOKEN environment variable not set")
        return False
    
    try:
        # Prepare release data
        release_data = {
            "tag_name": version,
            "name": f"Spanish Pronunciation Trainer v{version}",
            "body": generate_release_notes(deck_stats),
            "draft": False,
            "prerelease": False
        }
        
        # Create the release
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        print(f"🚀 Creating GitHub release {version}...")
        response = requests.post(
            f"https://api.github.com/repos/{GITHUB_REPO}/releases",
            headers=headers,
            json=release_data
        )
        
        if response.status_code != 201:
            print(f"❌ Failed to create release: {response.text}")
            return False
        
        release_info = response.json()
        upload_url = release_info["upload_url"].split("{")[0]  # Remove template part
        
        # Upload the .apkg file
        print(f"📤 Uploading {os.path.basename(apkg_file_path)}...")
        
        with open(apkg_file_path, "rb") as f:
            file_data = f.read()
        
        upload_response = requests.post(
            f"{upload_url}?name={os.path.basename(apkg_file_path)}",
            headers={
                **headers,
                "Content-Type": "application/octet-stream"
            },
            data=file_data
        )
        
        if upload_response.status_code != 201:
            print(f"❌ Failed to upload file: {upload_response.text}")
            return False
        
        print(f"✅ Release created successfully: {release_info['html_url']}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create GitHub release: {e}")
        return False


def generate_release_notes(deck_stats: Dict[str, Any]) -> str:
    """Generate release notes with deck statistics"""
    
    notes = f"""# Spanish Pronunciation Trainer

**Release Date:** {datetime.now().strftime("%Y-%m-%d")}

## 📊 Deck Statistics

- **Total Cards:** {deck_stats['total_cards']:,}
- **Number of Subdecks:** {deck_stats['deck_count']}

### Subdeck Breakdown:
"""
    
    for subdeck, count in deck_stats.get('subdecks', {}).items():
        notes += f"- **{subdeck}:** {count:,} cards\n"
    
    notes += """
## 🚀 Features

- **Text-to-Speech:** Both European Spanish (es_ES) and Latin American Spanish (es_US)
- **Comprehensive Coverage:** Grammar, vocabulary, phrases, and pronunciation
- **Organized Categories:** Well-structured subdecks for focused learning
- **Auto-Generated:** Programmatically created and maintained

## 📥 Installation

1. Download the `.apkg` file from this release
2. Open Anki
3. Go to File → Import
4. Select the downloaded `.apkg` file
5. Start learning!

## 🔄 Updates

This deck is automatically updated and released when new content is added.

---

*Generated automatically with ❤️*
"""
    
    return notes


def get_next_version() -> str:
    """Get the next version number based on current date"""
    return datetime.now().strftime("v%Y.%m.%d.%H%M")


def main():
    """Main export and release workflow"""
    print("🎯 Starting Spanish Deck Export and Release Process...")
    
    # Generate version
    version = get_next_version()
    timestamp = int(time.time())
    
    # Define output path
    output_filename = f"Spanish_Pronunciation_Trainer_{version.replace('.', '_')}.apkg"
    output_path = os.path.join(os.getcwd(), output_filename)
    
    try:
        # Step 0: Create/update Spanish decks via AnkiConnect
        print(f"\n🧩 Step 0: Creating/updating Spanish decks via AnkiConnect...")
        create_spanish_decks_via_ankiconnect.main()
        print("✅ Spanish decks creation/update completed")
        
        # Step 1: Export deck
        print(f"\n📦 Step 1: Exporting deck to {output_filename}")
        export_result = export_deck(output_path)
        
        if not export_result.get("success"):
            print(f"❌ Export failed: {export_result.get('error')}")
            return
        
        # Use the actual file path from export result
        actual_file_path = export_result.get("file_path", output_path)
        
        # Step 2: Get deck statistics
        print(f"\n📊 Step 2: Gathering deck statistics...")
        deck_stats = get_deck_stats()
        print(f"   Total cards: {deck_stats['total_cards']:,}")
        print(f"   Subdecks: {deck_stats['deck_count']}")
        
        # Step 3: Create GitHub release
        print(f"\n🚀 Step 3: Creating GitHub release {version}...")
        
        if GITHUB_TOKEN and GITHUB_REPO != "your-username/spanish-pronunciation-trainer":
            success = create_github_release(actual_file_path, version, deck_stats)
            if success:
                print("✅ GitHub release created successfully!")
            else:
                print("❌ GitHub release failed")
        else:
            print("⚠️ Skipping GitHub release (GITHUB_TOKEN not set or repo not configured)")
            print(f"   File available at: {actual_file_path}")
        
        print(f"\n🎉 Process completed! Deck exported to: {actual_file_path}")
        
    except Exception as e:
        print(f"❌ Process failed: {e}")


if __name__ == "__main__":
    main()
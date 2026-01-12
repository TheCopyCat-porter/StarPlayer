#!/usr/bin/env python3
import os
import json

def scan_games_folder():
    """Scan the Games folder and return list of game directories"""
    games_path = "Games"
    
    if not os.path.exists(games_path):
        print("❌ Games folder not found!")
        return []
    
    # Get all directories in Games folder
    games = [
        d for d in os.listdir(games_path)
        if os.path.isdir(os.path.join(games_path, d))
        and not d.startswith('.')  # Ignore hidden folders
    ]
    
    return sorted(games)

def update_html_file(games):
    """Update index.html with the new games list"""
    html_file = "index.html"
    
    if not os.path.exists(html_file):
        print("❌ index.html not found!")
        return False
    
    # Read the HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create the JavaScript array
    games_js = ',\n            '.join([f'"{game}"' for game in games])
    games_array = f'const games = [\n            {games_js}\n        ];'
    
    # Find and replace the games array
    import re
    pattern = r'const games = \[.*?\];'
    
    if re.search(pattern, content, re.DOTALL):
        new_content = re.sub(pattern, games_array, content, flags=re.DOTALL)
        
        # Write back to file
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True
    else:
        print("❌ Could not find games array in HTML!")
        return False

def main():
    print("🎮 StarPlayer Game Scanner")
    print("=" * 50)
    
    # Scan for games
    print("\n📁 Scanning Games folder...")
    games = scan_games_folder()
    
    if not games:
        print("⚠️  No games found in Games folder!")
        return
    
    print(f"✅ Found {len(games)} games:")
    for i, game in enumerate(games[:10], 1):
        print(f"   {i}. {game}")
    
    if len(games) > 10:
        print(f"   ... and {len(games) - 10} more")
    
    # Update HTML
    print("\n📝 Updating index.html...")
    if update_html_file(games):
        print("✅ Successfully updated index.html!")
        print(f"\n🎯 Total games: {len(games)}")
    else:
        print("❌ Failed to update index.html")
        print("\n💡 Manual fallback - copy this into your HTML:")
        print("\nconst games = [")
        for game in games:
            print(f'    "{game}",')
        print("];")

if __name__ == "__main__":
    main()

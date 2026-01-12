#!/usr/bin/env python3
import os

# Web-ports games on GitHub that can use jsDelivr CDN
WEB_PORTS_GAMES = {
    "hollow-knight": {
        "repo": "web-ports/hollow-knight",
        "title": "Hollow Knight",
        "data_parts": 42,
        "wasm_parts": 2,
        "company": "Team Cherry",
        "total_mb": "860.36"
    },
    "cuphead": {
        "repo": "web-ports/cuphead",
        "title": "Cuphead",
        "data_parts": 35,
        "wasm_parts": 2,
        "company": "Studio MDHR",
        "total_mb": "720.50"
    },
    "balatro": {
        "repo": "web-ports/balatro",
        "title": "Balatro",
        "data_parts": 15,
        "wasm_parts": 1,
        "company": "LocalThunk",
        "total_mb": "320.00"
    },
    "undertale-yellow": {
        "repo": "web-ports/undertale-yellow",
        "title": "Undertale Yellow",
        "data_parts": 25,
        "wasm_parts": 2,
        "company": "Team UTY",
        "total_mb": "550.00"
    },
    "karlson": {
        "repo": "web-ports/karlson",
        "title": "Karlson",
        "data_parts": 10,
        "wasm_parts": 1,
        "company": "Dani",
        "total_mb": "180.00"
    }
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en-us">
<head>
    <base href="https://cdn.jsdelivr.net/gh/{repo}@latest/">
    <meta charset="utf-8">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>{title}</title>
    <link rel="shortcut icon" href="TemplateData/favicon.ico">
    <link rel="stylesheet" href="TemplateData/style.css">
    <style>
        html, body {{
            margin: 0;
            padding: 0;
            height: 100%;
            overflow: hidden;
            background: #231F20;
        }}
        #unity-container {{
            width: 100%;
            height: 100%;
            position: fixed;
            top: 0;
            left: 0;
        }}
        #loading-text {{
            color: white;
            font-size: 48px;
            font-family: 'Segoe UI', sans-serif;
            text-align: center;
            margin-top: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }}
    </style>
</head>
<body>
    <div id="loading-text">LOADING...</div>
    <div hidden id="unity-container" class="unity-desktop">
        <canvas id="unity-canvas"></canvas>
        <div id="unity-loading-bar">
            <div id="unity-logo"></div>
            <div id="unity-progress-bar-empty">
                <div id="unity-progress-bar-full"></div>
            </div>
        </div>
        <div id="unity-mobile-warning">WebGL builds are not supported on mobile devices.</div>
    </div>
    <script>
        const loadingText = document.querySelector("#loading-text");
        let loadedBytes = 0;

        async function fetchWithProgress(url) {{
            const response = await fetch(url);
            const reader = response.body.getReader();
            const chunks = [];
            let received = 0;
            
            while (true) {{
                const {{ done, value }} = await reader.read();
                if (done) break;
                received += value.length;
                loadedBytes += value.length;
                chunks.push(value);
                
                const mbDone = (loadedBytes / (1024 * 1024)).toFixed(2);
                loadingText.textContent = `LOADING... ${{mbDone}} MB / {total_mb} MB`;
            }}
            
            const fullBuffer = new Uint8Array(received);
            let offset = 0;
            for (const chunk of chunks) {{
                fullBuffer.set(chunk, offset);
                offset += chunk.length;
            }}
            return fullBuffer.buffer;
        }}

        async function mergeFiles(fileParts) {{
            const buffers = await Promise.all(fileParts.map(part => fetchWithProgress(part)));
            return URL.createObjectURL(new Blob(buffers));
        }}

        function getParts(file, start, end) {{
            const parts = [];
            for (let i = start; i <= end; i++) {{
                parts.push(file + ".part" + i);
            }}
            return parts;
        }}

        (async () => {{
            const [dataUrl, wasmUrl] = await Promise.all([
                mergeFiles(getParts("Build/{game_id}.data", 1, {data_parts})),
                mergeFiles(getParts("Build/{game_id}.wasm", 1, {wasm_parts}))
            ]);

            const config = {{
                dataUrl: dataUrl,
                frameworkUrl: "Build/{game_id}.framework.js",
                codeUrl: wasmUrl,
                streamingAssetsUrl: "StreamingAssets",
                companyName: "{company}",
                productName: "{title}",
                productVersion: "1.0"
            }};

            const container = document.querySelector("#unity-container");
            container.hidden = false;
            const canvas = document.querySelector("#unity-canvas");
            const loadingBar = document.querySelector("#unity-loading-bar");
            const progressBarFull = document.querySelector("#unity-progress-bar-full");

            if (/iPhone|iPad|iPod|Android/i.test(navigator.userAgent)) {{
                container.className = "unity-mobile";
                config.devicePixelRatio = 1;
            }} else {{
                function resizeCanvas() {{
                    canvas.width = window.innerWidth;
                    canvas.height = window.innerHeight;
                }}
                resizeCanvas();
                window.addEventListener('resize', resizeCanvas);
            }}

            loadingBar.style.display = "block";

            const script = document.createElement("script");
            script.src = "Build/{game_id}.loader.js";
            script.onload = () => {{
                createUnityInstance(canvas, config, (progress) => {{
                    progressBarFull.style.width = 100 * progress + "%";
                }}).then(() => {{
                    loadingText.remove();
                    loadingBar.style.display = "none";
                }}).catch((err) => {{
                    alert("Error loading game: " + err);
                }});
            }};
            document.body.appendChild(script);
        }})();
    </script>
</body>
</html>"""

def generate_cdn_games():
    """Generate CDN-based HTML files for all web-ports games"""
    
    # Create Games directory if it doesn't exist
    os.makedirs("Games", exist_ok=True)
    
    print("🎮 Generating CDN-based game files...")
    print("=" * 60)
    
    for game_id, info in WEB_PORTS_GAMES.items():
        # Create game folder
        game_folder = f"Games/{game_id}"
        os.makedirs(game_folder, exist_ok=True)
        
        # Generate HTML file
        html_content = HTML_TEMPLATE.format(
            repo=info["repo"],
            title=info["title"],
            game_id=game_id.replace("-", ""),  # Remove hyphens for build files
            data_parts=info["data_parts"],
            wasm_parts=info["wasm_parts"],
            company=info["company"],
            total_mb=info["total_mb"]
        )
        
        # Write to file
        with open(f"{game_folder}/index.html", "w") as f:
            f.write(html_content)
        
        print(f"✅ {info['title']}: Games/{game_id}/index.html")
    
    print("\n" + "=" * 60)
    print(f"✨ Generated {len(WEB_PORTS_GAMES)} games!")
    print("\n📝 Add these to your games array:")
    print("\nconst games = [")
    for game_id in WEB_PORTS_GAMES.keys():
        print(f'    "{game_id}",')
    print("];")
    
    print("\n💾 Total space used: ~" + str(len(WEB_PORTS_GAMES) * 5) + "KB")
    print("    (vs ~5GB if downloaded locally!)")

if __name__ == "__main__":
    generate_cdn_games()

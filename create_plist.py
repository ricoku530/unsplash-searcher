import os

os.makedirs("dist/UnsplashSearch.app/Contents", exist_ok=True)

with open("dist/UnsplashSearch.app/Contents/Info.plist", "w", encoding="utf-8") as f:
    f.write("""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
<key>CFBundleName</key><string>UnsplashSearch</string>
<key>CFBundleDisplayName</key><string>UnsplashSearch</string>
<key>CFBundleIdentifier</key><string>com.unsplashsearch.app</string>
<key>CFBundleVersion</key><string>1.0.0</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>CFBundleExecutable</key><string>UnsplashSearch</string>
<key>LSMinimumSystemVersion</key><string>10.14</string>
<key>NSHighResolutionCapable</key><true/>
</dict>
</plist>""")

#!/bin/bash

echo "========================================"
echo "Creating Zyxel Captive Portal ZIP"
echo "========================================"
echo

# Check if we're in the correct directory
if [ ! -f "ua_agree.html" ]; then
    echo "❌ ERROR: ua_agree.html not found!"
    echo "Please run this script from the ua directory"
    exit 1
fi

# Remove old ZIP if it exists
if [ -f "zyxel_captive_portal.zip" ]; then
    echo "🗑️  Removing old ZIP file..."
    rm "zyxel_captive_portal.zip"
fi

# Check if required files exist
echo "🔍 Checking required files..."
missing_files=""

required_files=(
    "ua_agree.html"
    "ua_welcome.html"
    "script.js"
    "ua.css"
)

required_dirs=(
    "css_m"
    "images"
    "images_m"
    "js"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files="$missing_files $file"
    fi
done

for dir in "${required_dirs[@]}"; do
    if [ ! -d "$dir" ]; then
        missing_files="$missing_files $dir/"
    fi
done

if [ -n "$missing_files" ]; then
    echo "❌ ERROR: Missing required files:$missing_files"
    exit 1
fi

echo "✅ All required files found"

# Create the ZIP file
echo
echo "📦 Creating ZIP file..."
echo "Including:"
echo "- HTML files (ua_agree.html, ua_welcome.html)"
echo "- JavaScript (script.js)"
echo "- CSS files (ua.css, css_m/)"
echo "- Images (images/, images_m/)"
echo "- JavaScript libraries (js/)"
echo

# Use zip command (available on macOS and most Linux)
zip -r zyxel_captive_portal.zip \
    ua_agree.html \
    ua_welcome.html \
    script.js \
    ua.css \
    css_m/ \
    images/ \
    images_m/ \
    js/ \
    -x "*.DS_Store" "*Thumbs.db" "*.backup" "*~"

if [ $? -ne 0 ]; then
    echo "❌ ERROR: Failed to create ZIP file"
    echo "Make sure 'zip' command is available"
    exit 1
fi

# Check ZIP file size  
echo
echo "========================================"
echo "📦 ZIP Creation Complete!"
echo "========================================"

if [ -f "zyxel_captive_portal.zip" ]; then
    file_size=$(stat -f%z "zyxel_captive_portal.zip" 2>/dev/null || stat -c%s "zyxel_captive_portal.zip" 2>/dev/null)
    size_mb=$((file_size / 1024 / 1024))
    
    echo "File: zyxel_captive_portal.zip"
    echo "Size: $file_size bytes ($size_mb MB)"
    echo
    
    if [ $size_mb -gt 5 ]; then
        echo "⚠️  WARNING: ZIP file is larger than 5MB"
        echo "Zyxel may have upload size limits"
        echo "Consider optimizing images if upload fails"
    else
        echo "✅ ZIP file size looks good for upload"
    fi
else
    echo "❌ ERROR: ZIP file was not created"
    exit 1
fi

echo
echo "📋 Ready to upload to Zyxel USG Flex 200:"
echo "1. Access Zyxel admin interface"
echo "2. Navigate to Captive Portal settings"
echo "3. Upload: zyxel_captive_portal.zip" 
echo "4. Configure guest network to use the portal"
echo
echo "📍 Location: $(pwd)/zyxel_captive_portal.zip"
echo "========================================"
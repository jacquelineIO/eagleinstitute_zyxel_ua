# Captive Portal Image Troubleshooting Guide

## Common Image Loading Issues and Solutions

### 1. External Images Problem
**Issue**: The logo references an external URL that guests can't access before authentication
```html
<img src="https://auix.org/wp-content/uploads/2024/04/eagle-institute.png">
```

**Solution**: Download and include the image locally
```bash
# Download the image
curl -o images/eagle-institute.png https://auix.org/wp-content/uploads/2024/04/eagle-institute.png

# Update HTML to use local image
<img src="images/eagle-institute.png" alt="Eagle Institute logo">
```

### 2. Path Variables Not Replaced
**Issue**: Zyxel might not replace `$Z` path variable correctly

**Solution**: Create a fallback mechanism
```javascript
function getImagePath(filename) {
    var path = "$Z";
    // Fallback to relative path if variable not replaced
    if (path === "$Z" || !path) {
        return "images/" + filename;
    }
    return path + "/images/" + filename;
}
```

### 3. File Size Optimization

**Check current image sizes:**
```bash
# List all images with sizes
find images images_m -type f -exec ls -lh {} \;
```

**Optimize images before deployment:**
```bash
# Install image optimization tools
# For PNG files
optipng -o5 images/*.png images_m/*.png

# For JPEG files  
jpegoptim --max=85 images/*.jpg images_m/*.jpg

# Convert large PNGs to JPEG where appropriate
convert images/large-photo.png -quality 85 images/large-photo.jpg
```

### 4. ZIP Package Structure

**Correct structure for Zyxel:**
```
captive_portal.zip
├── ua_agree.html
├── ua_agree_m.html
├── ua_welcome.html
├── ua_welcome_m.html
├── ua.css
├── script.js
├── css_m/
│   └── *.css
├── images/
│   └── *.png, *.jpg, *.ico
└── images_m/
    └── *.png, *.jpg
```

**Create ZIP with correct structure:**
```bash
# From the ua directory
zip -r captive_portal.zip \
  ua_agree.html ua_agree_m.html \
  ua_welcome.html ua_welcome_m.html \
  ua.css script.js \
  css_m/ images/ images_m/ \
  -x "*.DS_Store" -x "__MACOSX"
```

### 5. Image Serving Test

**Add diagnostic JavaScript to ua_agree.html:**
```javascript
// Add this temporarily for debugging
function testImages() {
    var images = document.getElementsByTagName('img');
    for (var i = 0; i < images.length; i++) {
        images[i].onerror = function() {
            console.error('Failed to load: ' + this.src);
            // Log to a visible element for debugging
            var errorDiv = document.getElementById('image-errors');
            if (!errorDiv) {
                errorDiv = document.createElement('div');
                errorDiv.id = 'image-errors';
                errorDiv.style.cssText = 'position:fixed;bottom:0;left:0;background:red;color:white;padding:10px;z-index:9999';
                document.body.appendChild(errorDiv);
            }
            errorDiv.innerHTML += 'Failed: ' + this.src + '<br>';
        };
    }
}
window.onload = testImages;
```

### 6. Alternative Image Embedding

**For critical images, use Base64 encoding:**
```python
import base64

def image_to_base64(image_path):
    with open(image_path, 'rb') as img_file:
        b64_string = base64.b64encode(img_file.read()).decode()
        mime_type = 'image/png' if image_path.endswith('.png') else 'image/jpeg'
        return f'data:{mime_type};base64,{b64_string}'

# Convert logo to base64
logo_base64 = image_to_base64('images/logo.png')
print(f'<img src="{logo_base64}" alt="Logo">')
```

### 7. Zyxel-Specific Settings

**Check these Zyxel USG Flex 200 settings:**

1. **Maximum upload size**: Usually under `Configuration > Captive Portal > Settings`
2. **Allowed file types**: Ensure PNG, JPG, ICO, SVG are allowed
3. **Cache settings**: Clear Zyxel's cache after upload
4. **URL filtering**: Ensure external domains aren't blocked

### 8. Minimal Image Set

**If size is an issue, use only essential images:**
```
Required:
- logo.ico (favicon)
- eagle-institute.png (main logo)

Optional (can use CSS instead):
- Arrow icons → Use CSS triangles
- Background patterns → Use CSS gradients
- Decorative elements → Remove or use CSS

CSS alternatives example:
/* Replace arrow image with CSS */
.arrow-down::after {
    content: '';
    display: inline-block;
    width: 0;
    height: 0;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #333;
}
```

### 9. Testing Checklist

Before deploying to Zyxel:

- [ ] All images are under 500KB each
- [ ] Total ZIP size is under 2MB
- [ ] No external image URLs (all local)
- [ ] Images use web-safe formats (PNG, JPG, GIF)
- [ ] Paths are relative (no absolute paths)
- [ ] Test ZIP extraction locally
- [ ] Verify image paths match HTML references

### 10. Debug Mode

Add this to temporarily show all image sources:
```html
<!-- Add to bottom of ua_agree.html for debugging -->
<div id="debug-panel" style="display:none; position:fixed; bottom:0; right:0; background:white; border:1px solid black; padding:10px; max-width:300px; max-height:200px; overflow:auto; font-size:11px;">
    <button onclick="this.parentElement.style.display='none'">Close</button>
    <h4>Image Debug Info</h4>
    <div id="debug-images"></div>
</div>
<script>
// Show debug panel with Ctrl+Shift+D
document.addEventListener('keydown', function(e) {
    if (e.ctrlKey && e.shiftKey && e.key === 'D') {
        var panel = document.getElementById('debug-panel');
        panel.style.display = 'block';
        var imgs = document.getElementsByTagName('img');
        var debug = document.getElementById('debug-images');
        debug.innerHTML = '';
        for (var i = 0; i < imgs.length; i++) {
            debug.innerHTML += imgs[i].src + ' - ' + 
                (imgs[i].complete && imgs[i].naturalHeight !== 0 ? 'OK' : 'FAILED') + '<br>';
        }
    }
});
</script>
```

## Quick Fix Script

```bash
#!/bin/bash
# fix_images.sh - Run before creating ZIP

# 1. Download external images
echo "Downloading external images..."
curl -o images/eagle-institute.png https://auix.org/wp-content/uploads/2024/04/eagle-institute.png

# 2. Optimize images
echo "Optimizing images..."
find images images_m -name "*.png" -exec optipng -o2 {} \;
find images images_m -name "*.jpg" -exec jpegoptim --max=85 {} \;

# 3. Check sizes
echo "Image sizes:"
du -sh images/ images_m/

# 4. Create clean ZIP
echo "Creating captive_portal.zip..."
rm -f captive_portal.zip
zip -r captive_portal.zip \
  ua_agree.html ua_agree_m.html \
  ua_welcome.html ua_welcome_m.html \
  ua.css script.js \
  css_m/ images/ images_m/ \
  -x "*.DS_Store" -x "__MACOSX" -x "Thumbs.db"

echo "ZIP size: $(du -h captive_portal.zip | cut -f1)"
echo "Done! Upload captive_portal.zip to Zyxel"
```

## Contact Zyxel Support

If issues persist, provide Zyxel support with:
1. Firmware version of USG Flex 200
2. Browser console errors (F12 → Console)
3. Network tab showing failed image requests
4. Size of your ZIP file
5. List of image files and their formats
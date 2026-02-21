#!/usr/bin/env python3
"""
Bonny Selects - Comprehensive PWA Icon Generator
Generates all necessary favicon and app icons for every browser and device
"""

import os
from PIL import Image
import sys
from pathlib import Path

def find_logo_in_static(static_dir='app/static'):
    """
    Find logo image in app/static directory
    Looks for common image file names
    """
    if not os.path.exists(static_dir):
        print(f"❌ Error: {static_dir} directory not found")
        return None
    
    # List of common logo filenames to search for
    possible_names = [
        'ChatGPT_Image_Feb_21__2026__12_15_12_AM.png',
        'logo.png',
        'logo.jpg',
        'logo.jpeg',
        'bonny.png',
        'bonny.jpg',
        'bs.png',
        'bs.jpg',
    ]
    
    # First, check for exact filenames
    for filename in possible_names:
        filepath = os.path.join(static_dir, filename)
        if os.path.exists(filepath):
            return filepath
    
    # If not found, search for any PNG or JPG files
    print(f"🔍 Searching for image files in {static_dir}...\n")
    
    image_files = []
    for file in os.listdir(static_dir):
        if file.lower().endswith(('.png', '.jpg', '.jpeg')) and not file.startswith('favicon'):
            image_files.append(os.path.join(static_dir, file))
    
    if not image_files:
        return None
    
    if len(image_files) == 1:
        return image_files[0]
    
    # If multiple images, let user choose
    print("Multiple images found in app/static:")
    for i, filepath in enumerate(image_files, 1):
        print(f"  {i}. {os.path.basename(filepath)}")
    
    choice = input("\nSelect image number (or press Enter for first): ").strip()
    
    if not choice:
        return image_files[0]
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(image_files):
            return image_files[idx]
    except ValueError:
        pass
    
    return image_files[0]

def create_directories(base_path='app/static'):
    """Create necessary directories for all icon types"""
    favicon_dir = os.path.join(base_path, 'favicon')
    icons_dir = os.path.join(base_path, 'icons')
    
    os.makedirs(favicon_dir, exist_ok=True)
    os.makedirs(icons_dir, exist_ok=True)
    
    return favicon_dir, icons_dir

def generate_icon(source_image, output_path, size, background_color=(255, 255, 255), format='PNG'):
    """
    Generate a single icon with specified size
    Handles images with transparency
    """
    try:
        # Open the source image
        img = Image.open(source_image).convert('RGBA')
        
        # Create new image with background color
        background = Image.new('RGBA', (size, size), background_color + (255,))
        
        # Calculate padding and resize logo
        padding = int(size * 0.1)  # 10% padding
        max_logo_size = size - (padding * 2)
        
        img.thumbnail((max_logo_size, max_logo_size), Image.Resampling.LANCZOS)
        
        # Center the logo
        offset = ((size - img.width) // 2, (size - img.height) // 2)
        background.paste(img, offset, img)
        
        # Save based on format
        if format.upper() == 'ICO':
            background = background.convert('RGB')
            background.save(output_path, 'ICO')
        elif format.upper() == 'JPG':
            background = background.convert('RGB')
            background.save(output_path, 'JPEG', quality=95)
        else:  # PNG
            background = background.convert('RGB')
            background.save(output_path, 'PNG', quality=95)
        
        return True
    except Exception as e:
        print(f"❌ Error creating {output_path}: {e}")
        return False

def generate_maskable_icon(source_image, output_path, size, background_color=(212, 175, 55)):
    """
    Create maskable icon for Android Adaptive Icons
    Logo fits within safe zone for proper display
    """
    try:
        img = Image.open(source_image).convert('RGBA')
        
        # Create background with brand color
        background = Image.new('RGBA', (size, size), background_color + (255,))
        
        # Safe zone ratio for Android adaptive icons
        safe_zone_ratio = 0.66
        max_logo_size = int(size * safe_zone_ratio)
        
        img.thumbnail((max_logo_size, max_logo_size), Image.Resampling.LANCZOS)
        
        # Center the logo
        offset = ((size - img.width) // 2, (size - img.height) // 2)
        background.paste(img, offset, img)
        
        background = background.convert('RGB')
        background.save(output_path, 'PNG', quality=95)
        return True
    except Exception as e:
        print(f"❌ Error creating maskable icon {output_path}: {e}")
        return False

def generate_all_favicons(logo_path, favicon_dir):
    """Generate all favicon sizes"""
    print("🔗 Generating Favicons (for browser tabs, bookmarks)...")
    
    # Favicon sizes: (size, filename, format)
    favicon_sizes = [
        (16, 'favicon-16x16.png', 'PNG'),
        (32, 'favicon-32x32.png', 'PNG'),
        (48, 'favicon-48x48.png', 'PNG'),
        (64, 'favicon-64x64.png', 'PNG'),
    ]
    
    success_count = 0
    for size, filename, fmt in favicon_sizes:
        output_path = os.path.join(favicon_dir, filename)
        if generate_icon(logo_path, output_path, size, (255, 255, 255), fmt):
            print(f"  ✓ {filename}")
            success_count += 1
    
    # Generate ICO favicon (for legacy browser support)
    ico_path = os.path.join(favicon_dir, 'favicon.ico')
    if generate_icon(logo_path, ico_path, 32, (255, 255, 255), 'ICO'):
        print(f"  ✓ favicon.ico")
        success_count += 1
    
    # Generate Apple touch icon
    apple_path = os.path.join(favicon_dir, 'apple-touch-icon.png')
    if generate_icon(logo_path, apple_path, 180, (255, 255, 255), 'PNG'):
        print(f"  ✓ apple-touch-icon.png (180x180)")
        success_count += 1
    
    print(f"  Generated: {success_count} favicon files\n")
    return success_count > 0

def generate_all_app_icons(logo_path, icons_dir):
    """Generate all app icon sizes for different devices and purposes"""
    print("🎨 Generating App Icons (PWA, Android, iOS, Windows)...")
    
    # App icon sizes: (size, filename, is_maskable, format)
    # Standard sizes for web and various platforms
    app_icon_sizes = [
        # Small icons (for lists, notifications)
        (16, 'icon-16x16.png', False, 'PNG'),
        (32, 'icon-32x32.png', False, 'PNG'),
        
        # Medium icons (for toolbars, menus)
        (48, 'icon-48x48.png', False, 'PNG'),
        (64, 'icon-64x64.png', False, 'PNG'),
        (72, 'icon-72x72.png', False, 'PNG'),
        
        # Large icons (for home screens, app stores)
        (96, 'icon-96x96.png', False, 'PNG'),
        (128, 'icon-128x128.png', False, 'PNG'),
        (144, 'icon-144x144.png', False, 'PNG'),
        (152, 'icon-152x152.png', False, 'PNG'),
        (167, 'icon-167x167.png', False, 'PNG'),  # iPad
        (180, 'icon-180x180.png', False, 'PNG'),  # iPhone
        (192, 'icon-192x192.png', False, 'PNG'),  # Standard PWA
        (256, 'icon-256x256.png', False, 'PNG'),
        (384, 'icon-384x384.png', False, 'PNG'),
        (512, 'icon-512x512.png', False, 'PNG'),  # PWA splash screen
        (1024, 'icon-1024x1024.png', False, 'PNG'),  # App store
    ]
    
    success_count = 0
    for size, filename, is_maskable, fmt in app_icon_sizes:
        output_path = os.path.join(icons_dir, filename)
        if generate_icon(logo_path, output_path, size, (255, 255, 255), fmt):
            print(f"  ✓ {filename}")
            success_count += 1
    
    print(f"  Generated: {success_count} standard app icons\n")
    
    # Generate maskable icons for Android Adaptive Icons
    print("📱 Generating Maskable Icons (Android Adaptive)...")
    maskable_sizes = [
        (72, 'icon-72x72-maskable.png'),
        (96, 'icon-96x96-maskable.png'),
        (128, 'icon-128x128-maskable.png'),
        (144, 'icon-144x144-maskable.png'),
        (152, 'icon-152x152-maskable.png'),
        (192, 'icon-192x192-maskable.png'),
        (256, 'icon-256x256-maskable.png'),
        (384, 'icon-384x384-maskable.png'),
        (512, 'icon-512x512-maskable.png'),
    ]
    
    maskable_count = 0
    for size, filename in maskable_sizes:
        output_path = os.path.join(icons_dir, filename)
        if generate_maskable_icon(logo_path, output_path, size, (212, 175, 55)):
            print(f"  ✓ {filename}")
            maskable_count += 1
    
    print(f"  Generated: {maskable_count} maskable icons\n")
    
    # Also generate JPG versions for web optimization
    print("📸 Generating JPG Versions (web optimization)...")
    jpg_sizes = [
        (192, 'icon-192x192.jpg'),
        (256, 'icon-256x256.jpg'),
        (384, 'icon-384x384.jpg'),
        (512, 'icon-512x512.jpg'),
    ]
    
    jpg_count = 0
    for size, filename in jpg_sizes:
        output_path = os.path.join(icons_dir, filename)
        if generate_icon(logo_path, output_path, size, (255, 255, 255), 'JPG'):
            print(f"  ✓ {filename}")
            jpg_count += 1
    
    print(f"  Generated: {jpg_count} JPG icons\n")
    
    return success_count > 0

def generate_manifest_html(base_path='app/static'):
    """Generate HTML snippet for manifest and favicon links"""
    html_snippet = '''<!-- PWA Manifest and Favicon Links -->
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Bonny Selects">
<meta name="theme-color" content="#0a0a0a">

<!-- Manifest for PWA -->
<link rel="manifest" href="/manifest.json">

<!-- Favicons -->
<link rel="icon" type="image/png" sizes="16x16" href="/static/favicon/favicon-16x16.png">
<link rel="icon" type="image/png" sizes="32x32" href="/static/favicon/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="48x48" href="/static/favicon/favicon-48x48.png">
<link rel="icon" type="image/png" sizes="64x64" href="/static/favicon/favicon-64x64.png">
<link rel="icon" type="image/x-icon" href="/static/favicon/favicon.ico">

<!-- Apple Touch Icon -->
<link rel="apple-touch-icon" href="/static/favicon/apple-touch-icon.png">

<!-- Android Chrome Icons -->
<link rel="icon" type="image/png" sizes="192x192" href="/static/icons/icon-192x192.png">
<link rel="icon" type="image/png" sizes="512x512" href="/static/icons/icon-512x512.png">

<!-- Windows Tile -->
<meta name="msapplication-TileColor" content="#0a0a0a">
<meta name="msapplication-TileImage" content="/static/icons/icon-144x144.png">
'''
    
    html_file = os.path.join(base_path, 'html_head_snippet.txt')
    try:
        with open(html_file, 'w') as f:
            f.write(html_snippet)
        return True
    except Exception as e:
        print(f"⚠ Warning: Could not create HTML snippet: {e}")
        return False

def print_summary(favicon_dir, icons_dir, base_path='app/static'):
    """Print generation summary and next steps"""
    print("=" * 60)
    print("✅ ICON GENERATION COMPLETE!")
    print("=" * 60)
    print()
    
    print("📁 Generated Directories:")
    print(f"  {favicon_dir}/")
    print(f"  {icons_dir}/")
    print()
    
    print("📋 Generated Files:")
    print()
    print("🔗 Favicons (for browser tabs, bookmarks):")
    for file in os.listdir(favicon_dir):
        print(f"    favicon/{file}")
    print()
    
    print("🎨 App Icons (for home screens, app stores):")
    icon_files = sorted(os.listdir(icons_dir))
    for file in icon_files:
        print(f"    icons/{file}")
    print()
    
    print("=" * 60)
    print("📋 NEXT STEPS:")
    print("=" * 60)
    print()
    print("1️⃣  Add this to your HTML <head> tag:")
    print()
    html_file = os.path.join(base_path, 'html_head_snippet.txt')
    if os.path.exists(html_file):
        with open(html_file, 'r') as f:
            print(f.read())
    print()
    print("2️⃣  Update your app/__init__.py with init_updated.py")
    print("    - Adds routes for /manifest.json")
    print("    - Adds routes for /sw.js")
    print()
    print("3️⃣  Make sure these files exist in app/static/:")
    print("    - manifest.json")
    print("    - sw.js")
    print()
    print("4️⃣  Restart Flask:")
    print("    python -m flask run")
    print()
    print("5️⃣  Test on mobile:")
    print("    - iOS: Safari → Share → Add to Home Screen")
    print("    - Android: Chrome → Menu → Install app")
    print()
    print("=" * 60)
    print("Your app now has professional PWA icons for all browsers! 🎉")
    print("=" * 60)

def main():
    """Main entry point"""
    # Check if app/static exists
    if not os.path.exists('app/static'):
        print("❌ Error: app/static directory not found")
        print("Make sure you're running this script from your project root directory")
        print("\nExpected structure:")
        print("  BonnySelect/")
        print("  ├── app/")
        print("  │   └── static/")
        print("  ├── generate_icons.py")
        print("  └── ...")
        sys.exit(1)
    
    # Find logo in app/static
    logo_path = find_logo_in_static()
    
    if not logo_path:
        print("❌ Error: No image files found in app/static/")
        print("\nPlease place your logo image in app/static/ and run this script again")
        print("\nSupported formats: PNG, JPG, JPEG")
        sys.exit(1)
    
    print()
    print("🎨 Bonny Selects - Comprehensive Icon Generator")
    print("=" * 60)
    print(f"📸 Using logo: {os.path.basename(logo_path)}\n")
    
    # Create directories
    favicon_dir, icons_dir = create_directories()
    print(f"📁 Created directories:")
    print(f"   {favicon_dir}/")
    print(f"   {icons_dir}/")
    print()
    
    # Generate all icons
    favicon_ok = generate_all_favicons(logo_path, favicon_dir)
    icons_ok = generate_all_app_icons(logo_path, icons_dir)
    html_ok = generate_manifest_html()
    
    print()
    
    if favicon_ok and icons_ok:
        print_summary(favicon_dir, icons_dir)
    else:
        print("⚠ Warning: Some icons may not have been generated successfully")

if __name__ == '__main__':
    main()
from PIL import Image, ImageDraw, ImageFont
import os

# Create icons directory if it doesn't exist
icons_dir = "app/static/icons"
os.makedirs(icons_dir, exist_ok=True)

# Icon specifications
icons = {
    "shop-icon.png": {
        "emoji": "🛍️",
        "size": 192
    },
    "about-icon.png": {
        "emoji": "📖",
        "size": 192
    }
}

for filename, config in icons.items():
    # Create image
    img = Image.new('RGBA', (config['size'], config['size']), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Add emoji as simple text (using unicode)
    emoji = config['emoji']
    
    # Create a temporary text image to measure
    temp_img = Image.new('RGBA', (config['size'], config['size']), (255, 255, 255, 0))
    temp_draw = ImageDraw.Draw(temp_img)
    
    # Draw emoji in center
    # Using larger font size for visibility
    try:
        # Try to use default font, size doesn't matter much for emoji
        font_size = int(config['size'] * 0.7)
        # Just draw the emoji using ImageDraw
        draw.text(
            (config['size']//2, config['size']//2),
            emoji,
            fill=(212, 175, 55, 255),  # Gold color
            anchor="mm",
            font=None  # Uses default font
        )
    except:
        # Fallback if font issues
        draw.text(
            (config['size']//2 - 20, config['size']//2 - 20),
            emoji,
            fill=(212, 175, 55, 255)
        )
    
    # Save
    filepath = os.path.join(icons_dir, filename)
    img.save(filepath)
    print(f"✓ Created {filename}")

print("\n✓ Icons created successfully!")
print(f"Location: {icons_dir}")

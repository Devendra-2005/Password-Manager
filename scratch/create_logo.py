import os
from PIL import Image, ImageDraw, ImageFont

def generate_logo():
    os.makedirs("assets", exist_ok=True)
    os.makedirs(os.path.join("assets", "icons"), exist_ok=True)

    size = (128, 128)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw rounded shield background
    # Background circle/rounded rect
    draw.ellipse([4, 4, 124, 124], fill="#2563EB")
    
    # Inner shield accent
    shield_pts = [(64, 24), (100, 40), (100, 72), (64, 104), (28, 72), (28, 40)]
    draw.polygon(shield_pts, fill="#FFFFFF")

    # Inner lock shape
    # Lock body
    draw.rectangle([48, 56, 80, 84], fill="#2563EB")
    # Lock arch
    draw.arc([52, 44, 76, 68], start=180, end=0, fill="#2563EB", width=5)

    img.save(os.path.join("assets", "logo.png"), "PNG")
    print("Logo generated successfully!")

if __name__ == "__main__":
    generate_logo()

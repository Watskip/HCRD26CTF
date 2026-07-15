from PIL import Image, ImageDraw

def create_hacker_sprite(filename, color_body, color_eye):
    # 48x48 pixel art canvas
    img = Image.new('RGBA', (48, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    
    # Body (Hoodie/Cloak)
    d.rectangle([12, 16, 36, 44], fill=color_body) # Main body
    d.rectangle([16, 12, 32, 16], fill=color_body) # Hood top
    
    # Face area (shadowed)
    d.rectangle([16, 20, 32, 28], fill="#111111")
    
    # Glowing Eyes
    d.rectangle([20, 22, 22, 24], fill=color_eye) # Left eye
    d.rectangle([26, 22, 28, 24], fill=color_eye) # Right eye
    
    # Digital artifact/trim
    d.rectangle([12, 40, 36, 44], fill="#000000") # bottom shadow
    d.rectangle([16, 16, 32, 18], fill="#000000") # inner hood shadow
    
    img.save(filename)

# Player Character: Cyber Hacker (Green trim, Dark Gray body)
create_hacker_sprite("/home/leury/Desktop/ctf/hackconrd-ctf-webgame/files/src/frontend/assets/player.png", "#2c3e50", "#00ffcc")

# Merchant Character: Dark Web Vendor (Purple trim, Black body)
create_hacker_sprite("/home/leury/Desktop/ctf/hackconrd-ctf-webgame/files/src/frontend/assets/merchant.png", "#1a1a1a", "#9b59b6")

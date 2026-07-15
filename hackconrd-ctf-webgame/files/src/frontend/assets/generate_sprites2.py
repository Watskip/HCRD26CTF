from PIL import Image, ImageDraw

def create_hacker_sprite(filename, main_color, eye_color):
    img = Image.new('RGBA', (48, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    
    # Body (A stylized square robot/hacker avatar)
    d.rectangle([10, 10, 38, 38], fill=main_color) # Head/Body
    d.rectangle([14, 14, 34, 26], fill="#111") # Visor area
    
    # Eyes in the visor
    d.rectangle([18, 18, 22, 22], fill=eye_color) # Left eye
    d.rectangle([26, 18, 30, 22], fill=eye_color) # Right eye
    
    # Details/Antenna
    d.rectangle([22, 4, 26, 10], fill="#555")
    d.rectangle([20, 2, 28, 4], fill=eye_color) # Antenna tip
    
    # Base/Wheels
    d.rectangle([14, 38, 20, 44], fill="#555")
    d.rectangle([28, 38, 34, 44], fill="#555")
    
    img.save(filename)

# Create 100% original pixel art robots
create_hacker_sprite("/home/leury/Desktop/ctf/hackconrd-ctf-webgame/files/src/frontend/assets/player.png", "#2c3e50", "#00ffcc")
create_hacker_sprite("/home/leury/Desktop/ctf/hackconrd-ctf-webgame/files/src/frontend/assets/merchant.png", "#8e44ad", "#f1c40f")

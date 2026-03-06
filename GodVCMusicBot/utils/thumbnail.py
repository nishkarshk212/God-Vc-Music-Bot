from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
from pathlib import Path

async def generate_thumb(title, user, thumb_url):
    yt = Image.open(BytesIO(requests.get(thumb_url).content)).resize((1280, 720))
    assets_dir = Path(__file__).resolve().parent.parent / "assets"
    draw = ImageDraw.Draw(yt)
    try:
        overlay = Image.open(assets_dir / "overlay.png")
        yt.paste(overlay, (0, 0), overlay)
    except Exception:
        pass
    try:
        font = ImageFont.truetype(str(assets_dir / "fonts" / "font.ttf"), 60)
    except Exception:
        font = ImageFont.load_default()
    draw.text((70, 580), title[:40], font=font, fill="white")
    draw.text((70, 650), f"Requested by {user}", font=font, fill="white")
    path = "final_thumb.png"
    yt.save(path)
    return path

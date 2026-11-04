"""Reproduce reviewed Hordes figures from pinned public source excerpts.

Run manually with Pillow and imageio-ffmpeg installed. Source files remain private.
The site build uses the committed responsive WebP assets and needs no media tools.
"""
from pathlib import Path
import hashlib
import subprocess
import urllib.request

from PIL import Image, ImageDraw
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / '_private/media-raw/hordes-of-azeroth'
OUT = ROOT / 'assets/hordes-of-azeroth'
SOURCES = {
    'author-gameplay.mp4': ('https://github.com/user-attachments/assets/3a82f020-7192-48dc-b6be-f6316bda0225', '78b109295b01fb24a6549392dc85ebe31948368632ccb591a863a889d8fd4296'),
    'installation-error.png': ('https://github.com/user-attachments/assets/b3455916-3394-45c0-ae45-d96f3df93969', 'ea7d4e485c4176fdc43e583e3c642d836df2703b973fb26baa90da447e24f59c'),
}


def build():
    RAW.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (url, digest) in SOURCES.items():
        source = RAW / name
        if not source.exists():
            source.write_bytes(urllib.request.urlopen(url, timeout=90).read())
        assert hashlib.sha256(source.read_bytes()).hexdigest() == digest, name
    for name, seconds in [('run-choice', 5), ('combat', 15)]:
        source = RAW / (name + '.png')
        subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-ss', str(seconds), '-i', str(RAW / 'author-gameplay.mp4'), '-frames:v', '1', str(source)], check=True, capture_output=True)
    for name in ['run-choice', 'combat', 'installation-error']:
        image = Image.open(RAW / (name + '.png')).convert('RGB')
        for width in [800, 1280]:
            image.resize((width, round(image.height * width / image.width)), Image.Resampling.LANCZOS).save(OUT / f'{name}-{width}.webp', quality=88)
    # Original shield/waypoint mark. No game or publisher logo is used.
    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#30271f"/><path d="M14 12h36v24L32 54 14 36z" fill="none" stroke="#edc277" stroke-width="4"/><path d="M24 24h16v8H24zm4 8h8v12h-8z" fill="#edc277"/></svg>'
    (OUT / 'logo.svg').write_text(svg, encoding='utf8')
    image = Image.new('RGBA', (512, 512), '#30271f')
    draw = ImageDraw.Draw(image)
    draw.line([(112, 96), (400, 96), (400, 288), (256, 432), (112, 288), (112, 96)], fill='#edc277', width=32, joint='curve')
    draw.rectangle((192, 192, 320, 256), fill='#edc277')
    draw.rectangle((224, 256, 288, 352), fill='#edc277')
    for size in [16, 32, 48, 64, 180, 256, 512]:
        name = 'apple-touch-icon.png' if size == 180 else f'icon-{size}.png'
        image.resize((size, size), Image.Resampling.LANCZOS).save(OUT / name)
    image.save(OUT / 'favicon.ico', sizes=[(16, 16), (32, 32), (48, 48)])


if __name__ == '__main__':
    build()

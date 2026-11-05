"""Generate the profile banner with Pillow. No external image assets."""
from pathlib import Path
import math
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets'
OUT.mkdir(exist_ok=True)
FONT_DIR = Path(os.environ.get('PROFILE_FONT_DIR', '/usr/share/fonts/truetype/dejavu'))
W, H = 1280, 380
BG = '#0b111b'
INK = '#edf4fb'
MUTED = '#91a2b8'
MINT = '#6ee7c1'
LILAC = '#b7adff'

def font(size, bold=False, mono=False):
    name = 'DejaVuSansMono' if mono else 'DejaVuSans'
    return ImageFont.truetype(str(FONT_DIR / (name + ('-Bold' if bold else '') + '.ttf')), size)

def text(draw, xy, value, size, fill=INK, bold=False, mono=False):
    draw.text(xy, value, fill=fill, font=font(size, bold, mono))

base = Image.new('RGB', (W,H), BG)
d = ImageDraw.Draw(base)
# Restrained grid, darker than the typography.
for x in range(780,W,32):
    for y in range(28,H,32):
        d.ellipse((x,y,x+1,y+1),fill='#223144')
d.rounded_rectangle((1,1,W-2,H-2), radius=20, outline='#263549', width=2)
d.line((56,49,87,49), fill=MINT, width=3)
text(d,(101,36),'SOFTWARE DEVELOPER',17,MUTED,mono=True)
text(d,(54,91),'Sreenandh M',60,bold=True)
text(d,(58,177),'Web apps, APIs,',27,INK)
text(d,(58,215),'and the bits in between.',27,INK)
text(d,(58,321),'KERALA, INDIA',15,MUTED,mono=True)

# A small application stack on the right, with one animated connection.
d.rounded_rectangle((846,47,1227,333), radius=17, fill='#111c2b', outline='#293c54', width=2)
d.line((847,95,1226,95), fill='#293c54', width=1)
for i,col in enumerate(['#6ee7c1','#b7adff','#49617c']):
    d.ellipse((867+i*19,67,875+i*19,75),fill=col)
text(d,(1000,60),'app /',17,MUTED,mono=True)
for y,label,detail,col in [(120,'UI','React / Next.js',MINT),(190,'API','Node.js / Express',LILAC),(260,'DATA','SQL / MongoDB','#81b8ff')]:
    d.rounded_rectangle((872,y,1201,y+52), radius=9, fill='#152235',outline='#304159',width=1)
    text(d,(890,y+14),label,17,col,bold=True,mono=True)
    text(d,(960,y+16),detail,15,'#c2cede',mono=True)
for y in [172,242]:
    d.line((1036,y,1036,y+18),fill='#52617a',width=2)

PHRASES = ['React + Next.js', 'Node.js + Express', 'Python + SQL']

def render(n):
    im = base.copy()
    dr = ImageDraw.Draw(im)
    phase, local = divmod(n,36)
    phrase = PHRASES[phase % len(PHRASES)]
    if local >= 27:
        nxt = PHRASES[(phase+1) % len(PHRASES)]
        shown = nxt[:round(len(nxt)*(local-27)/8)]
    elif local >= 22:
        shown = phrase[:max(0,round(len(phrase)*(27-local)/5))]
    else:
        shown = phrase
    text(dr,(80,275),shown,23,MINT,mono=True)
    text(dr,(58,275),'>',23,MINT,mono=True)
    if (n // 5) % 2 == 0 or local >=22:
        cw = dr.textlength(shown,font=font(23,mono=True))
        dr.rectangle((83+cw,280,94+cw,300), fill=MINT)
    # Move a small signal between the stack layers.
    prog = (n % 36)/36
    yy=167+prog*102
    dr.ellipse((1032,yy-4,1040,yy+4),fill=MINT)
    # Gentle status pulse, not a fake availability indicator.
    radius=3+round((math.sin(n*math.tau/36)+1))
    dr.ellipse((1198-radius,71-radius,1198+radius,71+radius),fill=LILAC)
    return im

frames = [render(n) for n in range(108)]
frames[0].save(OUT/'header-static.png', optimize=True)
# A shared palette avoids colour flicker between GIF frames.
palette=frames[0].quantize(colors=128)
indexed=[frame.quantize(palette=palette,dither=Image.Dither.NONE) for frame in frames]
indexed[0].save(OUT/'header.gif',save_all=True,append_images=indexed[1:],duration=[80,80,90]*36,loop=0,optimize=True,disposal=1)
mobile_frames=[frame.crop((0,0,800,H)) for frame in frames]
for frame in mobile_frames:
    md=ImageDraw.Draw(frame)
    md.line((799,20,799,H-20),fill='#263549',width=2)
mobile_frames[0].save(OUT/'header-mobile-static.png',optimize=True)
mobile_indexed=[frame.quantize(palette=palette,dither=Image.Dither.NONE) for frame in mobile_frames]
mobile_indexed[0].save(OUT/'header-mobile.gif',save_all=True,append_images=mobile_indexed[1:],duration=[80,80,90]*36,loop=0,optimize=True,disposal=1)
print('Created',OUT/'header.gif')
print('Created',OUT/'header-static.png')

"""Anota capturas reais do Studio: círculo no ponto de clique, seta, rótulo, recorte."""
from PIL import Image, ImageDraw, ImageFont
import os
SP = os.path.dirname(os.path.abspath(__file__))
VERM=(232,60,60); VERM_S=(232,60,60,70); BRANCO=(255,255,255); PRETO=(20,20,24)

def _fonte(t):
    for c in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf",
              "/System/Library/Fonts/SFNSRounded.ttf","/Library/Fonts/Arial Bold.ttf"):
        if os.path.exists(c):
            try: return ImageFont.truetype(c, t)
            except Exception: pass
    return ImageFont.load_default()

def circulo(im, x, y, r=46, larg=7):
    d = ImageDraw.Draw(im, "RGBA")
    d.ellipse([x-r-larg, y-r-larg, x+r+larg, y+r+larg], outline=(255,255,255,190), width=larg+6)
    d.ellipse([x-r, y-r, x+r, y+r], outline=VERM, width=larg)
    return im

def seta(im, x0,y0, x1,y1, larg=7):
    import math
    d = ImageDraw.Draw(im, "RGBA")
    d.line([x0,y0,x1,y1], fill=(255,255,255,200), width=larg+6)
    d.line([x0,y0,x1,y1], fill=VERM, width=larg)
    ang = math.atan2(y1-y0, x1-x0); L=26; A=0.5
    pts=[(x1,y1),(x1-L*math.cos(ang-A), y1-L*math.sin(ang-A)),
         (x1-L*math.cos(ang+A), y1-L*math.sin(ang+A))]
    d.polygon(pts, fill=VERM)
    return im

def rotulo(im, x, y, texto, tam=34):
    d = ImageDraw.Draw(im, "RGBA"); f=_fonte(tam)
    cx = d.textbbox((0,0), texto, font=f)
    w,h = cx[2]-cx[0], cx[3]-cx[1]
    pad=14
    d.rounded_rectangle([x-pad, y-pad, x+w+pad, y+h+pad*1.6], radius=12, fill=VERM)
    d.text((x,y), texto, font=f, fill=BRANCO)
    return im

def numero(im, x, y, n, tam=54):
    d = ImageDraw.Draw(im, "RGBA"); f=_fonte(tam)
    r = tam
    d.ellipse([x-r,y-r,x+r,y+r], fill=VERM, outline=BRANCO, width=5)
    t=str(n); bb=d.textbbox((0,0),t,font=f)
    d.text((x-(bb[2]-bb[0])/2, y-(bb[3]-bb[1])/2-6), t, font=f, fill=BRANCO)
    return im

def recorte(caminho, box, saida, escala=1.0):
    im = Image.open(caminho).convert("RGB").crop(box)
    if escala!=1.0:
        im = im.resize((int(im.width*escala), int(im.height*escala)), Image.LANCZOS)
    im.save(saida); return saida

def abrir(caminho):
    return Image.open(caminho).convert("RGB")

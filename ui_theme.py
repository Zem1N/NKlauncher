import datetime
import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont, ImageFilter

PALETTE = {
    "bg": "#111613",
    "side": "#151c18",
    "card": "#19221d",
    "pill": "#202b25",
    "input": "#1d2721",
    "border": "#28382f",
    "accent": "#2ecc71",
    "hover": "#27ae60",
    "text": "#ffffff",
    "muted": "#8fa396"
}

def make_hero_banner(w=1100, h=140):
    w, h = max(720, int(w)), max(115, int(h))
    im = Image.new("RGB", (w, h), "#1b1c26")
    dr = ImageDraw.Draw(im)

    # Вечерний фиолетово-терракотовый закат как на референсе
    for y in range(h):
        t = y / float(h)
        if t < 0.58:
            k = t / 0.58
            r = int(28 + k * 54)
            g = int(26 + k * 24)
            b = int(42 + k * 14)
        else:
            k = (t - 0.58) / 0.42
            r = int(82 - k * 54)
            g = int(50 - k * 22)
            b = int(56 - k * 30)
        dr.line((0, y, w, y), fill=(r, g, b))

    scene = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sdr = ImageDraw.Draw(scene)

    # Тёплое квадратное солнце Minecraft справа на горизонте
    sx = int(w * 0.83)
    sy = int(h * 0.16)
    sw, sh = 38, 42
    sdr.rectangle((sx - 18, sy - 14, sx + sw + 18, sy + sh + 14), fill=(215, 115, 45, 38))
    sdr.rectangle((sx - 6, sy - 6, sx + sw + 6, sy + sh + 6), fill=(225, 130, 50, 75))
    sdr.rectangle((sx, sy, sx + sw, sy + sh), fill=(218, 128, 48, 225))

    # Дальние мягкие воксельные холмы
    far_pts = [
        (0, h),
        (0, int(h * 0.62)),
        (int(w * 0.25), int(h * 0.58)),
        (int(w * 0.48), int(h * 0.64)),
        (int(w * 0.72), int(h * 0.56)),
        (w, int(h * 0.52)),
        (w, h)
    ]
    sdr.polygon(far_pts, fill=(32, 46, 36, 215))

    # Ближний тёмно-зелёный рельеф с чётким скосом
    near_pts = [
        (0, h),
        (0, int(h * 0.72)),
        (int(w * 0.52), int(h * 0.66)),
        (int(w * 0.68), int(h * 0.82)),
        (int(w * 0.86), int(h * 0.72)),
        (w, int(h * 0.68)),
        (w, h)
    ]
    sdr.polygon(near_pts, fill=(22, 34, 26, 250))

    # Мягкое размытие фона в стиле depth-of-field
    scene = scene.filter(ImageFilter.GaussianBlur(radius=4.5))
    im = Image.alpha_composite(im.convert("RGBA"), scene)

    # Плавное затемнение слева под текст (как на скриншоте)
    fade = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    fdr = ImageDraw.Draw(fade)
    for x in range(w):
        k = max(0.0, 1.0 - (x / float(w)) * 1.38)
        fdr.line((x, 0, x, h), fill=(24, 25, 27, int(238 * k) + 12))
    final = Image.alpha_composite(im, fade).convert("RGB")

    td = ImageDraw.Draw(final)
    hr = datetime.datetime.now().hour
    greet = "Good morning, Crafter!" if 5 <= hr < 12 else ("Good afternoon, Crafter!" if hr < 18 else "Good evening, Crafter!")
    try:
        f_sub = ImageFont.truetype("arialbd.ttf", 11)
        f_title = ImageFont.truetype("ariblk.ttf", 25)
        f_desc = ImageFont.truetype("arial.ttf", 13)
    except Exception:
        f_sub = f_title = f_desc = ImageFont.load_default()

    td.text((28, 22), "NKLAUNCHER EDITION", fill="#2ecc71", font=f_sub)
    td.text((28, 44), greet, fill="#ffffff", font=f_title)
    td.text((28, 86), "Play with friends, install CurseForge mods & customize your 3D skin in one click.", fill="#c8d0cc", font=f_desc)

    return ctk.CTkImage(light_image=final, dark_image=final, size=(w, h))

def slide_up_reveal(widget, distance=42, steps=11, delay=14):
    try:
        container = widget.master
        if not container or not container.winfo_exists():
            return
        w = max(widget.winfo_width(), container.winfo_width() - 230)
        h = max(widget.winfo_height(), container.winfo_height() - 96)
        if w < 100 or h < 100:
            return
        widget.grid_forget()

        def step(i):
            if not widget.winfo_exists():
                return
            t = i / float(steps)
            ease = 1.0 - (1.0 - t) ** 3
            offset_y = int(distance * (1.0 - ease))
            if i < steps:
                widget.place(x=230, y=offset_y, width=w, height=h)
                widget.after(delay, lambda: step(i + 1))
            else:
                widget.place_forget()
                widget.grid(row=0, column=1, sticky="nsew")

        step(0)
    except Exception:
        try:
            widget.place_forget()
            widget.grid(row=0, column=1, sticky="nsew")
        except Exception:
            pass

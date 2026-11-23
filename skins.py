import os
import json
import zipfile
from PIL import Image
import customtkinter as ctk

SKIN_FILE = r"C:\MyMinecraftLauncherData\custom_skin.png"

def build_skin_preview(png_path):
    skin = Image.open(png_path).convert("RGBA")
    if skin.size not in ((64, 64), (64, 32)):
        skin = skin.resize((64, 64), Image.Resampling.NEAREST)

    canvas = Image.new("RGBA", (64, 128), (0, 0, 0, 0))
    head = skin.crop((8, 8, 16, 16)).resize((32, 32), Image.Resampling.NEAREST)
    hat = skin.crop((40, 8, 48, 16)).resize((34, 34), Image.Resampling.NEAREST)
    body = skin.crop((20, 20, 28, 32)).resize((32, 48), Image.Resampling.NEAREST)
    arm_l = skin.crop((44, 20, 48, 32)).resize((16, 48), Image.Resampling.NEAREST)
    arm_r = skin.crop((36, 52, 40, 64)).resize((16, 48), Image.Resampling.NEAREST) if skin.height == 64 else arm_l.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    leg_l = skin.crop((4, 20, 8, 32)).resize((16, 48), Image.Resampling.NEAREST)
    leg_r = skin.crop((20, 52, 24, 64)).resize((16, 48), Image.Resampling.NEAREST) if skin.height == 64 else leg_l.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

    canvas.paste(head, (16, 0), head)
    canvas.paste(hat, (15, 0), hat)
    canvas.paste(body, (16, 32), body)
    canvas.paste(arm_l, (0, 32), arm_l)
    canvas.paste(arm_r, (48, 32), arm_r)
    canvas.paste(leg_l, (16, 80), leg_l)
    canvas.paste(leg_r, (32, 80), leg_r)

    final = canvas.resize((100, 200), Image.Resampling.NEAREST)
    return ctk.CTkImage(light_image=final, dark_image=final, size=(100, 200))

def _enable_pack_in_options(game_dir, zip_name):
    os.makedirs(game_dir, exist_ok=True)
    opt_file = os.path.join(game_dir, "options.txt")
    entry = f"file/{zip_name}"
    active = list(("vanilla",))

    if os.path.exists(opt_file):
        try:
            with open(opt_file, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if line.startswith("resourcePacks:"):
                        active = json.loads(line.split(":", 1).pop().strip())
                        break
        except Exception:
            active = list(("vanilla",))

    if entry not in active:
        active.append(entry)

    lines = list()
    found = False
    if os.path.exists(opt_file):
        with open(opt_file, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line.startswith("resourcePacks:"):
                    lines.append(f"resourcePacks:{json.dumps(active, ensure_ascii=False)}\n")
                    found = True
                else:
                    lines.append(line)
    if not found:
        lines.append(f"resourcePacks:{json.dumps(active, ensure_ascii=False)}\n")

    with open(opt_file, "w", encoding="utf-8") as f:
        f.writelines(lines)

def apply_skin_to_game(png_path, game_dir):
    os.makedirs(game_dir, exist_ok=True)

    img = Image.open(png_path).convert("RGBA")
    if img.size not in ((64, 64), (64, 32)):
        img = img.resize((64, 64), Image.Resampling.NEAREST)
    img.save(SKIN_FILE)

    rp_dir = os.path.join(game_dir, "resourcepacks")
    os.makedirs(rp_dir, exist_ok=True)
    zip_name = "NKLauncher_SkinPack.zip"
    zip_path = os.path.join(rp_dir, zip_name)

    mcmeta = json.dumps({
        "pack": {
            "description": "NKLauncher Skin",
            "min_format": 65,
            "max_format": 120
        }
    }, indent=2)

    default_names = ("steve", "alex", "ari", "efe", "kai", "makena", "noor", "sunny", "zuri")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("pack.mcmeta", mcmeta)
        for name in default_names:
            zf.write(SKIN_FILE, f"assets/minecraft/textures/entity/player/wide/{name}.png")
            zf.write(SKIN_FILE, f"assets/minecraft/textures/entity/player/slim/{name}.png")
        zf.write(SKIN_FILE, "assets/minecraft/textures/entity/steve.png")
        zf.write(SKIN_FILE, "assets/minecraft/textures/entity/alex.png")

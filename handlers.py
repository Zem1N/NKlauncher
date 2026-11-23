import os, shutil, zipfile
from tkinter import filedialog, simpledialog
from PIL import Image
import customtkinter as ctk
import engine, accounts, skins, pack_manager

def sync_packs_dropdown(app):
    packs = engine.list_packs()
    app.pack_menu.configure(values=packs)
    if app.pack_menu.get() not in packs and packs:
        app.pack_menu.set(packs[0])

def on_pack_select(app, pack_name):
    refresh_mods_list(app)

def on_loader_change(app, loader):
    refresh_mods_list(app)

def add_mod_dialog(app):
    paths = filedialog.askopenfilenames(title="Select Files", filetypes=[("Minecraft Files", "*.jar *.zip *.png")])
    if paths:
        process_files(app, paths)

def _is_valid_skin(png_path):
    try:
        with Image.open(png_path) as im:
            w, h = im.size
            return (w == h or w == h * 2) and 64 <= w <= 1024
    except Exception:
        return False

def _detect_zip_target(zip_path, game_dir):
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            if any(i.startswith("shaders/") or "/shaders/" in i for i in zf.namelist()):
                return os.path.join(game_dir, "shaderpacks"), "Shader"
    except Exception:
        pass
    return os.path.join(game_dir, "resourcepacks"), "Resourcepack"

def show_drop_animation(app, count, copy_task):
    ov = ctk.CTkFrame(app, width=430, height=175, corner_radius=18, fg_color="#181a19", border_width=2, border_color="#2ecc71")
    ov.place(relx=0.5, rely=0.5, anchor="center")
    ov.pack_propagate(False)
    ov.lift()

    ilbl = ctk.CTkLabel(ov, text="📥", font=ctk.CTkFont(size=34))
    ilbl.pack(pady=(18, 4))
    tlbl = ctk.CTkLabel(ov, text=f"Installing files ({count})...", font=ctk.CTkFont("Arial Black", 15, "bold"))
    tlbl.pack(pady=(0, 8))
    pbar = ctk.CTkProgressBar(ov, width=330, height=8, progress_color="#2ecc71")
    pbar.pack(pady=(4, 10))
    pbar.set(0)
    slbl = ctk.CTkLabel(ov, text="Detecting file types and applying...", font=ctk.CTkFont(size=12), text_color="#888888")
    slbl.pack()

    def step1(k=1):
        if k < 14:
            pbar.set(k / 20)
            app.after(20, lambda: step1(k + 1))
        else:
            step2(15, copy_task())

    def step2(k, added):
        if k <= 20:
            pbar.set(k / 20)
            app.after(20, lambda: step2(k + 1, added))
        else:
            if added:
                ilbl.configure(text="✅")
                tlbl.configure(text=f"Installed: {len(added)} file(s)!", text_color="#2ecc71")
                slbl.configure(text=next(iter(added))[:45])
                refresh_mods_list(app)
            else:
                ilbl.configure(text="⚠️")
                tlbl.configure(text="Unsupported file or skin size", text_color="#e74c3c")
                slbl.configure(text="Drop .jar, .zip or 64x64 .png skin")
            app.after(1600, ov.destroy)

    app.after(20, step1)

def process_files(app, paths):
    clean = []
    for p in paths:
        if isinstance(p, bytes):
            try:
                clean.append(p.decode("cp1251"))
            except Exception:
                clean.append(p.decode("utf-8", errors="ignore"))
        else:
            clean.append(str(p))

    valid = [p for p in clean if os.path.exists(p) and (p.lower().endswith((".jar", ".zip")) or (p.lower().endswith(".png") and _is_valid_skin(p)))]

    def do_copy():
        pack = app.pack_menu.get()
        m_dir = engine.get_active_mods_dir(pack)
        g_dir = engine.get_active_game_dir(pack)
        added = []
        for p in valid:
            fn, low = os.path.basename(p), p.lower()
            if low.endswith(".jar"):
                os.makedirs(m_dir, exist_ok=True)
                shutil.copy2(p, os.path.join(m_dir, fn))
                added.append(f"[Mod] {fn}")
            elif low.endswith(".png"):
                os.makedirs(g_dir, exist_ok=True)
                try:
                    skins.apply_skin_to_game(p, g_dir)
                except Exception:
                    pass
                acc_s = os.path.join(engine.MINECRAFT_DIR, "custom_skin.png")
                shutil.copy2(p, acc_s)
                if hasattr(app, "update_skin_preview"):
                    app.update_skin_preview(acc_s)
                added.append(f"[Skin] {fn}")
            else:
                d_dir, kind = _detect_zip_target(p, g_dir)
                os.makedirs(d_dir, exist_ok=True)
                shutil.copy2(p, os.path.join(d_dir, fn))
                added.append(f"[{kind}] {fn}")
        return added

    show_drop_animation(app, len(valid) if valid else len(clean), do_copy)

def get_installed_target_dir(app):
    cat, pack = getattr(app, "installed_category", "Mods"), app.pack_menu.get()
    if cat == "Mods":
        return engine.get_active_mods_dir(pack)
    return os.path.join(engine.get_active_game_dir(pack), "resourcepacks" if cat == "Resourcepacks" else "shaderpacks")

def refresh_mods_list(app):
    for w in app.mods_scroll.winfo_children():
        w.destroy()
    cat, t_dir = getattr(app, "installed_category", "Mods"), get_installed_target_dir(app)
    g_dir = engine.get_active_game_dir(app.pack_menu.get())
    os.makedirs(t_dir, exist_ok=True)
    ext = ".jar" if cat == "Mods" else (".zip", ".rar")
    icon = "🧩" if cat == "Mods" else ("🎨" if cat == "Resourcepacks" else "✨")
    active_rps = pack_manager.get_active_resourcepacks(g_dir) if cat == "Resourcepacks" else []
    active_sh = pack_manager.get_active_shader(g_dir) if cat == "Shaders" else ""

    files = [f for f in os.listdir(t_dir) if f.lower().endswith(ext)]
    if not files:
        ctk.CTkLabel(app.mods_scroll, text=f"No {cat.lower()} installed yet.", font=ctk.CTkFont(size=14), text_color="#777777").pack(pady=40)
        return

    for f in files:
        row = ctk.CTkFrame(app.mods_scroll, fg_color="#2b2b2b", corner_radius=10)
        row.pack(fill="x", padx=10, pady=4)
        ctk.CTkLabel(row, text=f"{icon} {f}", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=15, pady=10)
        ctk.CTkButton(row, text="Delete", width=75, fg_color="#e74c3c", command=lambda fn=f, d=t_dir: [os.remove(os.path.join(d, fn)), refresh_mods_list(app)]).pack(side="right", padx=(6, 15))
        if cat in ("Resourcepacks", "Shaders"):
            is_on = (f"file/{f}" in active_rps) if cat == "Resourcepacks" else (active_sh == f)
            cmd = (lambda fn=f: [pack_manager.toggle_resourcepack(g_dir, fn), refresh_mods_list(app)]) if cat == "Resourcepacks" else (lambda fn=f: [pack_manager.toggle_shader(g_dir, fn), refresh_mods_list(app)])
            ctk.CTkButton(row, text="Active ✓" if is_on else "Enable", width=85, fg_color="#2ecc71" if is_on else "#3a3a3a", text_color="#111111" if is_on else "#ffffff", font=ctk.CTkFont(weight="bold"), command=cmd).pack(side="right", padx=4)

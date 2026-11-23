import os
import shutil
from tkinter import messagebox
import customtkinter as ctk
import engine, ui_theme

C = ui_theme.PALETTE

def build_packs_tab(app):
    app.packs_frame.configure(fg_color=C["bg"])

    top = ctk.CTkFrame(app.packs_frame, fg_color="transparent")
    top.pack(fill="x", padx=26, pady=(20, 12))

    ctk.CTkLabel(
        top,
        text="📦 MODPACK PROFILES",
        font=ctk.CTkFont(family="Arial Black", size=22, weight="bold"),
        text_color="#ffffff"
    ).pack(side="left")

    bar = ctk.CTkFrame(app.packs_frame, fg_color=C["card"], corner_radius=14, border_width=1, border_color=C["border"])
    bar.pack(fill="x", padx=26, pady=(0, 14))

    app.new_pack_entry = ctk.CTkEntry(
        bar,
        placeholder_text="New modpack name (e.g. Survival 1.21.4)...",
        height=38,
        corner_radius=10,
        fg_color=C["input"],
        border_color=C["border"],
        font=ctk.CTkFont(size=13)
    )
    app.new_pack_entry.pack(side="left", fill="x", expand=True, padx=(14, 8), pady=12)
    app.new_pack_entry.bind("<Return>", lambda _: create_pack(app))

    ctk.CTkButton(
        bar,
        text="+ Create Modpack",
        width=155,
        height=38,
        corner_radius=10,
        fg_color=C["accent"],
        hover_color=C["hover"],
        text_color="#09130c",
        font=ctk.CTkFont(size=13, weight="bold"),
        command=lambda: create_pack(app)
    ).pack(side="right", padx=(6, 14), pady=12)

    app.packs_scroll = ctk.CTkScrollableFrame(
        app.packs_frame,
        corner_radius=16,
        fg_color=C["card"],
        border_width=1,
        border_color=C["border"]
    )
    app.packs_scroll.pack(fill="both", expand=True, padx=26, pady=(0, 18))
    refresh_packs_list(app)

def _sync_dropdown(app, select_name=None):
    packs = engine.list_packs()
    if hasattr(app, "pack_menu"):
        app.pack_menu.configure(values=packs)
        if select_name and select_name in packs:
            app.pack_menu.set(select_name)
        elif app.pack_menu.get() not in packs and packs:
            app.pack_menu.set(packs[0])

def create_pack(app):
    raw = app.new_pack_entry.get().strip()
    clean = "".join(ch for ch in raw if ch not in r'\/:*?"<>|').strip()
    if not clean:
        messagebox.showwarning("Modpacks", "Enter a valid modpack name!")
        return

    pack_dir = os.path.join(engine.PACKS_DIR, clean)
    if os.path.exists(pack_dir):
        messagebox.showinfo("Modpacks", f"Modpack '{clean}' already exists.")
        return

    for sub in ("mods", "shaderpacks", "resourcepacks"):
        os.makedirs(os.path.join(pack_dir, sub), exist_ok=True)

    app.new_pack_entry.delete(0, "end")
    _sync_dropdown(app, select_name=clean)
    refresh_packs_list(app)
    app.refresh_mods_list()
    app.set_status(f"Created modpack: {clean}")

def select_pack(app, name):
    _sync_dropdown(app, select_name=name)
    refresh_packs_list(app)
    app.refresh_mods_list()
    app.set_status(f"Active modpack: {name}")

def delete_pack(app, name):
    if not messagebox.askyesno("Delete Modpack", f"Delete modpack '{name}' and all its mods?"):
        return
    shutil.rmtree(os.path.join(engine.PACKS_DIR, name), ignore_errors=True)
    _sync_dropdown(app)
    refresh_packs_list(app)
    app.refresh_mods_list()
    app.set_status(f"Deleted modpack: {name}")

def refresh_packs_list(app):
    if not hasattr(app, "packs_scroll"):
        return
    for w in app.packs_scroll.winfo_children():
        w.destroy()

    active = app.pack_menu.get() if hasattr(app, "pack_menu") else ""
    all_packs = engine.list_packs()

    for name in all_packs:
        base_dir = os.path.join(engine.PACKS_DIR, name)
        mods_dir = os.path.join(base_dir, "mods")
        mod_count = len([f for f in os.listdir(mods_dir) if f.endswith(".jar")]) if os.path.isdir(mods_dir) else 0
        is_active = (name == active)

        card = ctk.CTkFrame(
            app.packs_scroll,
            fg_color=C["pill"],
            corner_radius=12,
            border_width=1,
            border_color=C["accent"] if is_active else C["border"]
        )
        card.pack(fill="x", padx=12, pady=6)

        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, padx=16, pady=12)

        badge = "  ● ACTIVE" if is_active else ""
        ctk.CTkLabel(
            info,
            text=f"{name}{badge}",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=C["accent"] if is_active else "#ffffff"
        ).pack(anchor="w")

        ctk.CTkLabel(
            info,
            text=f"Installed mods: {mod_count}   •   Folder: {name}",
            font=ctk.CTkFont(size=12),
            text_color=C["muted"]
        ).pack(anchor="w", pady=(2, 0))

        btns = ctk.CTkFrame(card, fg_color="transparent")
        btns.pack(side="right", padx=14)

        if not is_active:
            ctk.CTkButton(
                btns,
                text="Select",
                width=85,
                height=34,
                corner_radius=8,
                fg_color=C["accent"],
                hover_color=C["hover"],
                text_color="#09130c",
                font=ctk.CTkFont(size=12, weight="bold"),
                command=lambda n=name: select_pack(app, n)
            ).pack(side="left", padx=4)

        ctk.CTkButton(
            btns,
            text="Folder",
            width=75,
            height=34,
            corner_radius=8,
            fg_color="#26332c",
            hover_color="#314239",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda d=base_dir: (os.makedirs(d, exist_ok=True), os.startfile(d))
        ).pack(side="left", padx=4)

        if len(all_packs) > 1:
            ctk.CTkButton(
                btns,
                text="✕",
                width=36,
                height=34,
                corner_radius=8,
                fg_color="#3a1e22",
                hover_color="#c0392b",
                font=ctk.CTkFont(size=13, weight="bold"),
                command=lambda n=name: delete_pack(app, n)
            ).pack(side="left", padx=(4, 0))

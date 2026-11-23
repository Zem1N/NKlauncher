import io
import ssl
import threading
import urllib.request
from tkinter import messagebox
from PIL import Image, ImageDraw
import customtkinter as ctk
import mod_catalog

_ICON_CACHE = {}

def _make_placeholder_icon():
    im = Image.new("RGBA", (48, 48), (45, 45, 48, 255))
    dr = ImageDraw.Draw(im)
    dr.rounded_rectangle((0, 0, 47, 47), radius=10, outline=(70, 70, 75, 255), width=2)
    return ctk.CTkImage(light_image=im, dark_image=im, size=(48, 48))

def _load_icon_async(app, url, lbl):
    if not url:
        return
    if url in _ICON_CACHE:
        lbl.configure(image=_ICON_CACHE[url])
        return

    def task():
        try:
            ctx = ssl._create_unverified_context()
            req = urllib.request.Request(url, headers={"User-Agent": "NKLauncher/1.0"})
            with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
                raw = resp.read()
            im = Image.open(io.BytesIO(raw)).convert("RGBA").resize((48, 48), Image.Resampling.LANCZOS)
            cimg = ctk.CTkImage(light_image=im, dark_image=im, size=(48, 48))
            _ICON_CACHE[url] = cimg
            app.after(0, lambda: lbl.configure(image=cimg) if lbl.winfo_exists() else None)
        except Exception:
            pass

    threading.Thread(target=task, daemon=True).start()

def build_catalog_tab(app):
    top = ctk.CTkFrame(app.catalog_frame, fg_color="transparent")
    top.pack(fill="x", padx=28, pady=(20, 10))

    ctk.CTkLabel(
        top,
        text="MODS & SHADERS CATALOG",
        font=ctk.CTkFont(family="Arial Black", size=22, weight="bold")
    ).pack(side="left")

    bar = ctk.CTkFrame(app.catalog_frame, fg_color="#1e1e1e", corner_radius=12)
    bar.pack(fill="x", padx=28, pady=(0, 12))

    app.cat_source_menu = ctk.CTkOptionMenu(
        bar,
        values=["Modrinth", "CurseForge"],
        width=130,
        height=36,
        corner_radius=8,
        fg_color="#2ecc71",
        button_color="#27ae60",
        text_color="#111111",
        font=ctk.CTkFont(size=13, weight="bold"),
        command=lambda _: run_search(app, reset=True)
    )
    app.cat_source_menu.pack(side="left", padx=(12, 6), pady=10)

    app.cat_type_menu = ctk.CTkOptionMenu(
        bar,
        values=["Mods", "Shaders", "Resource Packs"],
        width=150,
        height=36,
        corner_radius=8,
        font=ctk.CTkFont(size=13, weight="bold"),
        command=lambda _: run_search(app, reset=True)
    )
    app.cat_type_menu.pack(side="left", padx=6, pady=10)

    app.cat_search_entry = ctk.CTkEntry(
        bar,
        placeholder_text="Search mods, shaders, resource packs...",
        height=36,
        corner_radius=8,
        font=ctk.CTkFont(size=13)
    )
    app.cat_search_entry.pack(side="left", fill="x", expand=True, padx=6, pady=10)
    app.cat_search_entry.bind("<Return>", lambda _: run_search(app, reset=True))

    app.cat_ver_filter = ctk.CTkCheckBox(
        bar,
        text="Match Game Version",
        font=ctk.CTkFont(size=12, weight="bold"),
        command=lambda: run_search(app, reset=True)
    )
    app.cat_ver_filter.select()
    app.cat_ver_filter.pack(side="left", padx=8, pady=10)

    ctk.CTkButton(
        bar,
        text="Search",
        width=90,
        height=36,
        corner_radius=8,
        fg_color="#2ecc71",
        hover_color="#27ae60",
        text_color="#111111",
        font=ctk.CTkFont(size=13, weight="bold"),
        command=lambda: run_search(app, reset=True)
    ).pack(side="right", padx=(6, 12), pady=10)

    app.cat_scroll = ctk.CTkScrollableFrame(app.catalog_frame, corner_radius=16, fg_color="#222222")
    app.cat_scroll.pack(fill="both", expand=True, padx=28, pady=(0, 18))
    app._cat_offset = 0

def run_search(app, reset=True):
    if reset:
        app._cat_offset = 0
        for w in app.cat_scroll.winfo_children():
            w.destroy()
        ctk.CTkLabel(app.cat_scroll, text="Loading catalog...", text_color="#888888").pack(pady=30)

    query = app.cat_search_entry.get().strip()
    category = app.cat_type_menu.get()
    source = app.cat_source_menu.get()
    ver = app.version_menu.get() if app.cat_ver_filter.get() else ""
    loader = app.loader_menu.get()
    offset = app._cat_offset

    def task():
        try:
            items = mod_catalog.search_items(
                query=query,
                category=category,
                game_version=ver,
                loader=loader,
                index=offset,
                source=source
            )
            app.after(0, lambda: _render_results(app, items, category, reset))
        except Exception as e:
            app.after(0, lambda err=e: _render_error(app, str(err)))

    threading.Thread(target=task, daemon=True).start()

def _render_error(app, msg):
    for w in app.cat_scroll.winfo_children():
        w.destroy()
    ctk.CTkLabel(app.cat_scroll, text=f"Catalog Error: {msg}", text_color="#e74c3c").pack(pady=30)

def _render_results(app, items, category, reset):
    if reset:
        for w in app.cat_scroll.winfo_children():
            w.destroy()
    else:
        for w in app.cat_scroll.winfo_children():
            if getattr(w, "_is_more_btn", False):
                w.destroy()

    if not items and reset:
        ctk.CTkLabel(
            app.cat_scroll,
            text=f"Nothing found in {category}. Try unchecking 'Match Game Version'!",
            text_color="#888888"
        ).pack(pady=30)
        return

    ph_icon = _make_placeholder_icon()

    for item in items:
        card = ctk.CTkFrame(app.cat_scroll, fg_color="#2b2b2b", corner_radius=12)
        card.pack(fill="x", padx=10, pady=5)

        icon_lbl = ctk.CTkLabel(card, text="", image=ph_icon, width=48, height=48)
        icon_lbl.pack(side="left", padx=(12, 6), pady=10)

        icon_url = item.get("icon_url") or item.get("logo")
        if icon_url:
            _load_icon_async(app, icon_url, icon_lbl)

        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, padx=8, pady=10)

        dl_k = f"{item['downloads'] / 1_000_000:.1f}M" if item["downloads"] >= 1_000_000 else f"{item['downloads'] // 1000}K"
        ctk.CTkLabel(
            info,
            text=f"{item['name']}   •   by {item['author']}   ({dl_k} downloads)",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#ffffff"
        ).pack(anchor="w")

        ctk.CTkLabel(
            info,
            text=item["summary"][:110] + ("..." if len(item["summary"]) > 110 else ""),
            font=ctk.CTkFont(size=12),
            text_color="#aaaaaa"
        ).pack(anchor="w", pady=(2, 0))

        btn = ctk.CTkButton(
            card,
            text="Install",
            width=95,
            height=34,
            corner_radius=8,
            fg_color="#2ecc71",
            hover_color="#27ae60",
            text_color="#111111",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        btn.configure(command=lambda it=item, b=btn, cat=category: _install_item(app, it, b, cat))
        btn.pack(side="right", padx=14)

    if len(items) >= 18:
        app._cat_offset += len(items)
        more_btn = ctk.CTkButton(
            app.cat_scroll,
            text="Load More ▼",
            height=36,
            fg_color="#333333",
            hover_color="#444444",
            command=lambda: run_search(app, reset=False)
        )
        more_btn._is_more_btn = True
        more_btn.pack(pady=10)

def _install_item(app, item, btn, category):
    btn.configure(text="Installing...", state="disabled")
    ver = app.version_menu.get()
    loader = app.loader_menu.get()
    pack = app.pack_menu.get()

    def task():
        try:
            t_dir = mod_catalog.get_target_dir(category, pack)
            mod_catalog.download_item_by_id(item["id"], ver, loader, category, t_dir)
            app.after(0, lambda: [
                btn.configure(text="✓ Installed", fg_color="#3498db", text_color="#ffffff"),
                app.refresh_mods_list(),
                app.set_status(f"Installed {item['name']} -> {category}")
            ])
        except Exception as e:
            app.after(0, lambda err=e: [
                btn.configure(text="Install", state="normal"),
                messagebox.showerror("Install Error", str(err))
            ])

    threading.Thread(target=task, daemon=True).start()

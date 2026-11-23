import os, customtkinter as ctk
import engine, lang, skin3d, ver_menu, features_pro, ui_theme

C = ui_theme.PALETTE

def build_sidebar(app):
    app.sidebar = ctk.CTkFrame(app, width=230, corner_radius=0, fg_color=C["side"], border_width=1, border_color=C["border"])
    app.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
    app.sidebar.grid_propagate(False)
    app.sidebar.grid_columnconfigure(0, weight=1)
    app.sidebar.grid_rowconfigure(11, weight=1)

    logo = ctk.CTkFrame(app.sidebar, fg_color="transparent")
    logo.grid(row=0, column=0, padx=20, pady=(22, 6), sticky="ew")
    ctk.CTkLabel(logo, text="NK", font=ctk.CTkFont("Arial Black", 24, "bold"), text_color=C["accent"]).pack(side="left")
    ctk.CTkLabel(logo, text="Launcher", font=ctk.CTkFont("Arial Black", 24, "bold"), text_color="#ffffff").pack(side="left")

    pill = ctk.CTkFrame(app.sidebar, fg_color=C["input"], corner_radius=8, border_width=1, border_color=C["border"])
    pill.grid(row=1, column=0, padx=18, pady=(0, 18), sticky="ew")
    app.acc_status_lbl = ctk.CTkLabel(pill, text="⚪ Offline Mode", font=ctk.CTkFont(size=11, weight="bold"), text_color="#9aa5b4")
    app.acc_status_lbl.pack(padx=10, pady=5, anchor="w")

    app.nav_btns = {}
    items = [
        ("home", "⌂  Home"),
        ("accounts", "👤  Accounts"),
        ("coop", "✦  Friends & Coop"),
        ("packs", "📦  Modpacks"),
        ("catalog", "🧩  Catalog"),
        ("mods", "📁  Installed"),
        ("settings", "⚙  Settings")
    ]
    slots = []
    for idx, (k, label) in enumerate(items, 2):
        slot = ctk.CTkFrame(app.sidebar, height=40, fg_color="transparent")
        slot.grid(row=idx, column=0, padx=14, pady=3, sticky="ew")
        btn = ctk.CTkButton(
            slot,
            text=label,
            height=40,
            corner_radius=10,
            fg_color="transparent",
            hover_color="#1f2c24",
            text_color="#d0d7de",
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=lambda x=k: getattr(app, f"show_{x}")()
        )
        btn.place(x=0, y=0, relwidth=1.0)
        slots.append((slot, btn, list((0,))))
        app.nav_btns[k] = btn
        setattr(app, f"btn_{k}", btn)

    def _hover_loop():
        try:
            px, py = app.sidebar.winfo_pointerxy()
            for slot, btn, st in slots:
                if not slot.winfo_exists():
                    continue
                sx, sy = slot.winfo_rootx(), slot.winfo_rooty()
                inside = (sx <= px <= sx + slot.winfo_width() and sy <= py <= sy + slot.winfo_height())
                target = 14 if inside else 0
                cur = st[0]
                if cur != target:
                    nxt = cur + 2 if target > cur else cur - 2
                    st[0] = nxt
                    btn.place(x=nxt, y=0, relwidth=1.0)
        except Exception:
            pass
        app.after(14, _hover_loop)

    app.after(100, _hover_loop)

    lcard = ctk.CTkFrame(app.sidebar, fg_color="#161a21", corner_radius=12, border_width=1, border_color=C["border"])
    lcard.grid(row=9, column=0, rowspan=2, padx=16, pady=(18, 10), sticky="ew")
    ctk.CTkLabel(lcard, text="MOD LOADER", font=ctk.CTkFont(size=10, weight="bold"), text_color="#768390").pack(anchor="w", padx=12, pady=(8, 2))
    app.loader_menu = ctk.CTkOptionMenu(
        lcard,
        values=["Vanilla", "Fabric", "Forge", "NeoForge", "Quilt"],
        height=34,
        corner_radius=8,
        fg_color="#212631",
        button_color=C["accent"],
        button_hover_color=C["hover"],
        font=ctk.CTkFont(size=13, weight="bold"),
        command=app.on_loader_change
    )
    app.loader_menu.pack(fill="x", padx=10, pady=(0, 10))
    ctk.CTkLabel(app.sidebar, text="NKLauncher v1.0 PRO", font=ctk.CTkFont(size=11, weight="bold"), text_color="#4c5664").grid(row=12, column=0, padx=20, pady=12)

def build_home_tab(app):
    app.home_frame.configure(fg_color=C["bg"])
    box = ctk.CTkFrame(app.home_frame, height=135, corner_radius=16, fg_color=C["card"], border_width=1, border_color=C["border"])
    box.pack(fill="x", padx=26, pady=(20, 14))
    box.pack_propagate(False)

    lbl = ctk.CTkLabel(box, text="", image=ui_theme.make_hero_banner(1100, 135))
    lbl.place(x=0, y=0, relwidth=1, relheight=1)
    lw = list((1100,))
    def _upd_banner(w=None):
        cur_w = w or box.winfo_width()
        if cur_w > 200 and abs(cur_w - lw) > 10:
            lw = cur_w
            lbl.configure(image=ui_theme.make_hero_banner(cur_w, 135))
    box.bind(chr(60)+"Configure"+chr(62), lambda ev: _upd_banner(ev.width))
    app.after(200, _upd_banner)

    grid = ctk.CTkFrame(app.home_frame, fg_color="transparent")
    grid.pack(fill="both", expand=True, padx=26, pady=(0, 14))
    grid.grid_columnconfigure(0, weight=1)
    grid.grid_columnconfigure(1, weight=0)
    grid.grid_rowconfigure(0, weight=1)

    info = ctk.CTkFrame(grid, corner_radius=16, fg_color=C["card"], border_width=1, border_color=C["border"])
    info.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
    hdr = ctk.CTkFrame(info, fg_color="transparent")
    hdr.pack(fill="x", padx=20, pady=(16, 8))
    ctk.CTkLabel(hdr, text="⚡ QUICK HIGHLIGHTS", font=ctk.CTkFont(size=13, weight="bold"), text_color=C["accent"]).pack(side="left")
    ctk.CTkLabel(hdr, text="READY", font=ctk.CTkFont(size=10, weight="bold"), text_color=C["accent"], fg_color="#163826", corner_radius=6, padx=8, pady=2).pack(side="right")

    for k in ("feat_1", "feat_2", "feat_3"):
        row = ctk.CTkFrame(info, fg_color=C["pill"], corner_radius=10)
        row.pack(fill="x", padx=20, pady=3)
        ctk.CTkLabel(row, text=lang.t(k), font=ctk.CTkFont(size=12), text_color="#d0d7de").pack(anchor="w", padx=12, pady=6)
    features_pro.build_server_monitor_widget(info, app)

    sc = ctk.CTkFrame(grid, width=240, corner_radius=16, fg_color=C["card"], border_width=1, border_color=C["border"])
    sc.grid(row=0, column=1, sticky="ns")
    sc.grid_propagate(False)
    ctk.CTkLabel(sc, text="3D SKIN STUDIO", font=ctk.CTkFont(size=12, weight="bold"), text_color=C["accent"]).pack(pady=(14, 2))

    wrap = ctk.CTkFrame(sc, fg_color="#131a16", corner_radius=12, border_width=1, border_color=C["border"])
    wrap.pack(padx=16, pady=4)
    app.skin_viewer = skin3d.Skin3DViewer(wrap, width=180, height=225, bg="#131a16")
    app.skin_viewer.pack(padx=4, pady=4)
    sp = os.path.join(engine.MINECRAFT_DIR, "custom_skin.png")
    if os.path.exists(sp):
        app.skin_viewer.set_skin(sp)

    app.skin_info_lbl = ctk.CTkLabel(sc, text="Drag to rotate • Look follows cursor", font=ctk.CTkFont(size=10), text_color="#6e7781")
    app.skin_info_lbl.pack(pady=(2, 2))
    app.btn_skin_up = ctk.CTkButton(
        sc,
        text="Upload Skin (.png)",
        height=36,
        corner_radius=10,
        fg_color=C["accent"],
        hover_color=C["hover"],
        text_color="#0b140e",
        font=ctk.CTkFont(size=12, weight="bold"),
        command=app.upload_skin_dialog
    )
    app.btn_skin_up.pack(fill="x", padx=16, pady=(2, 14))

def build_bottom_bar(app):
    bot = ctk.CTkFrame(app, height=96, corner_radius=0, fg_color=C["side"], border_width=1, border_color=C["border"])
    bot.grid(row=1, column=1, sticky="ew")
    bot.grid_columnconfigure(3, weight=1)
    for col, (txt, px) in enumerate((("USERNAME", 24), ("MODPACK PROFILE", 6), ("VERSION", 6))):
        ctk.CTkLabel(bot, text=txt, font=ctk.CTkFont(size=10, weight="bold"), text_color="#6e7781").grid(row=0, column=col, padx=(px, 6), pady=(10, 0), sticky="w")

    app.nick_entry = ctk.CTkEntry(
        bot,
        placeholder_text="Nickname",
        width=155,
        height=38,
        corner_radius=10,
        fg_color=C["input"],
        border_color="#2a313d",
        font=ctk.CTkFont(size=13, weight="bold")
    )
    app.nick_entry.grid(row=1, column=0, padx=(24, 6), pady=(2, 4))

    packs = engine.list_packs()
    app.pack_menu = ctk.CTkOptionMenu(
        bot,
        values=packs,
        width=155,
        height=38,
        corner_radius=10,
        fg_color=C["input"],
        button_color="#252c38",
        font=ctk.CTkFont(size=12, weight="bold"),
        command=lambda _: app.refresh_mods_list()
    )
    app.pack_menu.grid(row=1, column=1, padx=6, pady=(2, 4))

    app.version_menu = ver_menu.ScrollableVersionMenu(bot, values=engine.AVAILABLE_VERSIONS, width=145, height=38)
    app.version_menu.grid(row=1, column=2, padx=6, pady=(2, 4))

    app.play_btn = ctk.CTkButton(
        bot,
        text="▶   PLAY MINECRAFT",
        height=50,
        corner_radius=14,
        fg_color=C["accent"],
        hover_color=C["hover"],
        text_color="#09130c",
        font=ctk.CTkFont("Arial Black", 17, "bold"),
        command=app.start_launch_thread
    )
    app.play_btn.grid(row=0, column=3, rowspan=2, padx=(16, 24), pady=(12, 4), sticky="ew")

    app.status_label = ctk.CTkLabel(bot, text="Ready to launch", font=ctk.CTkFont(size=11, weight="bold"), text_color=C["muted"])
    app.status_label.grid(row=2, column=0, columnspan=2, padx=24, pady=(0, 8), sticky="w")

    app.progress_bar = ctk.CTkProgressBar(bot, height=6, corner_radius=3, fg_color="#1c212b", progress_color=C["accent"])
    app.progress_bar.set(0)
    app.progress_bar.grid(row=2, column=2, columnspan=2, padx=(6, 24), pady=(0, 8), sticky="ew")

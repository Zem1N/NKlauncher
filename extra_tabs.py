import customtkinter as ctk, features_pro, features_pro, features_pro

def build_mods_tab(app):
    app.installed_category = "Mods"

    top = ctk.CTkFrame(app.mods_frame, fg_color="transparent")
    top.pack(fill="x", padx=35, pady=(30, 12))
    ctk.CTkLabel(top, text="INSTALLED CONTENT", font=ctk.CTkFont(family="Arial Black", size=22, weight="bold")).pack(side="left")

    cat_switch = ctk.CTkSegmentedButton(
        top,
        values=["Mods", "Resourcepacks", "Shaders"],
        height=36,
        font=ctk.CTkFont(size=13, weight="bold"),
        selected_color="#2ecc71",
        selected_hover_color="#27ae60",
        command=lambda val: [setattr(app, "installed_category", val), app.refresh_mods_list()]
    )
    cat_switch.set("Mods")
    cat_switch.pack(side="right")

    sub_bar = ctk.CTkFrame(app.mods_frame, fg_color="transparent")
    sub_bar.pack(fill="x", padx=35, pady=(0, 12))

    ctk.CTkButton(sub_bar, text="+ Add File (.jar / .zip)", height=34, corner_radius=8, fg_color="#2ecc71", text_color="#111111", font=ctk.CTkFont(size=12, weight="bold"), command=app.add_mod_dialog).pack(side="left")
    ctk.CTkButton(sub_bar, text="Open Active Folder", height=34, corner_radius=8, fg_color="#333333", font=ctk.CTkFont(size=12, weight="bold"), command=app.open_installed_folder).pack(side="right")

    app.mods_scroll = ctk.CTkScrollableFrame(app.mods_frame, corner_radius=16, fg_color="#222222")
    app.mods_scroll.pack(fill="both", expand=True, padx=35, pady=(0, 30))

def build_settings_tab(app):
    features_pro.build_pro_settings_section(app.settings_frame, app)
    ctk.CTkLabel(app.settings_frame, text="SETTINGS", font=ctk.CTkFont(family="Arial Black", size=22, weight="bold")).pack(anchor="w", padx=35, pady=(30, 15))

    ram_card = ctk.CTkFrame(app.settings_frame, corner_radius=16, fg_color="#222222")
    ram_card.pack(fill="x", padx=35, pady=10)
    app.ram_title = ctk.CTkLabel(ram_card, text="RAM Allocation: 4 GB", font=ctk.CTkFont(size=15, weight="bold"))
    app.ram_title.pack(anchor="w", padx=25, pady=(15, 5))
    sl = ctk.CTkSlider(ram_card, from_=2, to=16, number_of_steps=14, progress_color="#2ecc71", command=app.update_ram_label)
    sl.set(4)
    sl.pack(fill="x", padx=25, pady=(0, 15))

    dir_card = ctk.CTkFrame(app.settings_frame, corner_radius=16, fg_color="#222222")
    dir_card.pack(fill="x", padx=35, pady=10)
    ctk.CTkCheckBox(dir_card, text="Fullscreen mode (1920x1080)", variable=app.fullscreen_var, font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=25, pady=18)
    ctk.CTkButton(dir_card, text="Open Game Folder", height=36, fg_color="#333333", command=app.open_game_folder).pack(side="right", padx=25, pady=18)

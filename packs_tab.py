import customtkinter as ctk

def build_packs_tab(app):
    app.packs_frame.grid_columnconfigure(0, weight=1)
    app.packs_frame.grid_rowconfigure(1, weight=1)

    top_bar = ctk.CTkFrame(app.packs_frame, fg_color="transparent")
    top_bar.grid(row=0, column=0, padx=35, pady=(30, 15), sticky="ew")

    ctk.CTkLabel(top_bar, text="МОИ СБОРКИ", font=ctk.CTkFont(family="Arial Black", size=22, weight="bold")).pack(side="left")

    create_btn = ctk.CTkButton(top_bar, text="+ Создать сборку", height=40, corner_radius=10, font=ctk.CTkFont(size=14, weight="bold"), fg_color="#2ecc71", text_color="#111111", hover_color="#27ae60", command=app.open_create_pack_modal)
    create_btn.pack(side="right")

    app.packs_scroll = ctk.CTkScrollableFrame(app.packs_frame, corner_radius=16, fg_color="#222222")
    app.packs_scroll.grid(row=1, column=0, padx=35, pady=(0, 30), sticky="nsew")

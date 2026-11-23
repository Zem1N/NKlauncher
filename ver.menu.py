import customtkinter as ctk

class ScrollableVersionMenu(ctk.CTkFrame):
    def __init__(self, master, values, command=None, width=145, height=38):
        super().__init__(master, fg_color="transparent", width=width, height=height)
        self.values = values if values else list(("26.3",))
        self.current = next(iter(self.values))
        self.command = command
        self.popup = None
        self.btn = ctk.CTkButton(self, text=f"{self.current}  ▼", width=width, height=height, corner_radius=8, font=ctk.CTkFont(size=13, weight="bold"), fg_color="#2ecc71", text_color="#111111", hover_color="#27ae60", command=self.toggle)
        self.btn.pack()

    def get(self): return self.current
    def set(self, val): self.current = val; self.btn.configure(text=f"{val}  ▼")

    def toggle(self):
        if self.popup and self.popup.winfo_exists():
            self.popup.destroy(); return
        self.popup = ctk.CTkToplevel(self)
        self.popup.overrideredirect(True)
        self.popup.attributes("-topmost", True)
        x, y = self.winfo_rootx(), self.winfo_rooty() - 310
        self.popup.geometry(f"190x300+{x}+{max(10, y)}")

        box = ctk.CTkFrame(self.popup, fg_color="#181818", border_width=2, border_color="#2ecc71", corner_radius=10)
        box.pack(fill="both", expand=True)

        qvar = ctk.StringVar()
        ent = ctk.CTkEntry(box, textvariable=qvar, placeholder_text="Search version...", height=30)
        ent.pack(fill="x", padx=8, pady=(8, 4)); ent.focus_set()

        scr = ctk.CTkScrollableFrame(box, fg_color="#222222", corner_radius=8)
        scr.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        def draw(*_):
            for w in scr.winfo_children(): w.destroy()
            q = qvar.get().strip().lower()
            for v in [x for x in self.values if q in x.lower()][:150]:
                cur = (v == self.current)
                ctk.CTkButton(scr, text=v, height=28, anchor="w", fg_color="#2ecc71" if cur else "transparent", text_color="#111111" if cur else "#ffffff", command=lambda val=v: self.pick(val)).pack(fill="x", pady=1)

        qvar.trace_add("write", draw); draw()
        self.popup.bind("<FocusOut>", lambda _: self.after(150, lambda: self.popup.destroy() if self.popup and self.popup.winfo_exists() and not self.popup.focus_get() else None))

    def pick(self, val):
        self.set(val)
        if self.popup and self.popup.winfo_exists(): self.popup.destroy()
        if self.command: self.command(val)

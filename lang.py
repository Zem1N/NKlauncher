import datetime

TEXTS = {
    "offline": "⚪ Offline Mode",
    "nav_home": "Home",
    "nav_accounts": "Accounts",
    "nav_coop": "Friends & Coop",
    "nav_packs": "Modpacks",
    "nav_mods": "CurseForge",
    "nav_installed": "Installed",
    "nav_settings": "Settings",
    "loader_lbl": "MOD LOADER",
    "banner_sub": "NKLAUNCHER EDITION",
    "banner_desc": "Play with friends, install CurseForge mods & customize your 3D skin in one click.",
    "feat_title": "QUICK FEATURES",
    "feat_1": "• Drag & drop .jar mods, .zip packs, shaders or .png skins anywhere",
    "feat_2": "• Play singleplayer worlds together via Friends & Coop (e4mc)",
    "feat_3": "• Interactive 3D skin preview that tracks your mouse cursor",
    "skin_title": "3D SKIN PREVIEW",
    "skin_empty": "Drop .png skin here",
    "skin_btn": "Upload Skin (.png)",
    "nick_lbl": "USERNAME",
    "pack_lbl": "ACTIVE MODPACK",
    "ver_lbl": "GAME VERSION",
    "play_btn": "PLAY",
    "status_ready": "Ready to launch"
}

def t(key):
    return TEXTS.get(key, key)

def get_time_greeting():
    h = datetime.datetime.now().hour
    if 5 <= h < 12:
        return "Good morning, Crafter!"
    elif 12 <= h < 18:
        return "Good afternoon, Crafter!"
    elif 18 <= h < 23:
        return "Good evening, Crafter!"
    return "Good night, Crafter!"

SPLASH_TIPS = {
    "en": [
        "Tip: Rotate the 3D skin on the Home screen with your mouse!",
        "Tip: Switch Modrinth and CurseForge right in the Catalog tab.",
        "Tip: Create isolated modpacks so mods never conflict.",
        "Tip: Open your world to friends in Friends and Coop.",
        "Tip: Drag and drop .jar mods or .zip shaders onto the launcher."
    ],
    "ru": [
        "Совет: Вращай 3D-скин на главном экране мышкой — голова следит за курсором!",
        "Совет: Переключай источники Modrinth и CurseForge прямо вверху Каталога.",
        "Совет: Создавай отдельные модпаки, чтобы моды разных версий не конфликтовали.",
        "Совет: Вкладка Друзья и Кооп позволяет открыть одиночный мир в 1 клик!",
        "Совет: Перетаскивай .jar моды или .zip шейдеры прямо в окно лаунчера."
    ]
}

def get_tips():
    cur = globals().get("CURRENT_LANG", "ru")
    return SPLASH_TIPS.get(cur, SPLASH_TIPS["en"])

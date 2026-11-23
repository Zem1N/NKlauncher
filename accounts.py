import os
import json
import hashlib
import shutil
import engine

ACCOUNTS_FILE = os.path.join(engine.MINECRAFT_DIR, "accounts.json")
ACCOUNTS_DIR = os.path.join(engine.MINECRAFT_DIR, "accounts")

def _hash_pwd(password):
    if not password:
        return ""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def load_accounts():
    os.makedirs(engine.MINECRAFT_DIR, exist_ok=True)
    if not os.path.exists(ACCOUNTS_FILE):
        return {}
    try:
        with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_accounts(data):
    os.makedirs(engine.MINECRAFT_DIR, exist_ok=True)
    with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def register_account(username, password=""):
    clean_name = "".join(c for c in username if c.isalnum() or c in ("_", "-")).strip()
    if not clean_name:
        raise Exception("Никнейм может содержать только буквы, цифры, _ и -")
    data = load_accounts()
    if clean_name in data:
        raise Exception("Аккаунт с таким ником уже существует!")
    data[clean_name] = {"password_hash": _hash_pwd(password)}
    save_accounts(data)
    os.makedirs(os.path.join(ACCOUNTS_DIR, clean_name), exist_ok=True)
    return clean_name

def verify_password(username, password):
    data = load_accounts()
    if username not in data:
        return False
    saved_hash = data[username].get("password_hash", "")
    if not saved_hash:
        return True
    return saved_hash == _hash_pwd(password)

def has_password(username):
    data = load_accounts()
    return bool(data.get(username, {}).get("password_hash", ""))

def delete_account(username):
    data = load_accounts()
    if username in data:
        del data[username]
        save_accounts(data)
    acc_path = os.path.join(ACCOUNTS_DIR, username)
    if os.path.exists(acc_path):
        shutil.rmtree(acc_path, ignore_errors=True)

def get_account_game_dir(username, pack_name):
    """Возвращает изолированную папку для миров и данных текущего аккаунта и сборки"""
    if not username or username == "Оффлайн (Без аккаунта)":
        base = engine.MINECRAFT_DIR
    else:
        base = os.path.join(ACCOUNTS_DIR, username)
        
    if pack_name and pack_name != "Стандартный режим":
        return os.path.join(base, "modpacks", pack_name)
    return base

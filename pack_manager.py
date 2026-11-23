import os
import json

def get_active_resourcepacks(game_dir):
    opt_file = os.path.join(game_dir, "options.txt")
    if not os.path.exists(opt_file):
        return ["vanilla"]
    try:
        with open(opt_file, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line.startswith("resourcePacks:"):
                    return json.loads(line.split(":", 1).strip())
    except Exception:
        pass
    return ["vanilla"]

def toggle_resourcepack(game_dir, filename):
    os.makedirs(game_dir, exist_ok=True)
    opt_file = os.path.join(game_dir, "options.txt")
    entry = f"file/{filename}"
    active = get_active_resourcepacks(game_dir)

    if entry in active:
        active.remove(entry)
    else:
        active.append(entry)

    lines, found = [], False
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

def get_active_shader(game_dir):
    iris_cfg = os.path.join(game_dir, "config", "iris.properties")
    if os.path.exists(iris_cfg):
        with open(iris_cfg, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line.startswith("shaderPack="):
                    return line.split("=", 1).strip()
    return ""

def toggle_shader(game_dir, filename):
    cfg_dir = os.path.join(game_dir, "config")
    os.makedirs(cfg_dir, exist_ok=True)
    iris_cfg = os.path.join(cfg_dir, "iris.properties")
    new_val = "" if get_active_shader(game_dir) == filename else filename
    enable_val = "false" if new_val == "" else "true"

    with open(iris_cfg, "w", encoding="utf-8") as f:
        f.write(f"shaderPack={new_val}\nenableShaders={enable_val}\n")

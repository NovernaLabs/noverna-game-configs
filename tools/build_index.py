"""Builds index.json from games/*/game.json: every file of every config with its target path, size and SHA-256.

Noverna Studio downloads index.json, matches games by Steam app ID or Unreal project name and fetches only the files it needs,
checking each one against the SHA-256 listed here. Run this after adding or changing a game:

    python tools/build_index.py
"""

import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
GAMES = ROOT / "games"
FORMAT = 1
FRAMEWORKS = {"ue4ss"}
STORES = {None, "steam", "gamepass", "epic"}


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1 << 16), b""):
            digest.update(block)
    return digest.hexdigest()


def build():
    games = []
    for game_file in sorted(GAMES.glob("*/game.json")):
        folder = game_file.parent
        game = json.loads(game_file.read_text(encoding="utf-8"))
        configs = []
        for config in game.get("configs", []):
            if config.get("framework") not in FRAMEWORKS:
                fail(f"{game_file}: unknown framework {config.get('framework')!r}")
            if config.get("store") not in STORES:
                fail(f"{game_file}: unknown store {config.get('store')!r}")
            source = folder / config["folder"]
            if not source.is_dir():
                fail(f"{game_file}: folder {config['folder']!r} is missing")
            files = []
            for path in sorted(p for p in source.rglob("*") if p.is_file()):
                files.append({
                    "path": path.relative_to(ROOT).as_posix(),
                    "target": path.relative_to(source).as_posix(),
                    "size": path.stat().st_size,
                    "sha256": sha256(path),
                })
            if not files:
                fail(f"{game_file}: config {config['folder']!r} has no files")
            entry = {key: value for key, value in config.items() if key != "folder"}
            entry["files"] = files
            configs.append(entry)
        games.append({
            "id": folder.name,
            "name": game["name"],
            "steamAppIds": game.get("steamAppIds", []),
            "unrealProjects": game.get("unrealProjects", []),
            "configs": configs,
        })

    index = {"format": FORMAT, "games": games}
    (ROOT / "index.json").write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"index.json: {len(games)} games, {sum(len(c['files']) for g in games for c in g['configs'])} files")


if __name__ == "__main__":
    build()

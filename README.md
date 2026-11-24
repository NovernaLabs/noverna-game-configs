# Noverna Game Configs

Game-specific settings that mod frameworks need for some games, published for [Noverna Studio](https://github.com/NovernaLabs/noverna-studio-releases) and anyone else who mods these games.

Some games ship a modified engine. Then a framework like [UE4SS](https://github.com/UE4SS-RE/RE-UE4SS) reads the game's memory at the wrong places and crashes, for example as soon as it touches an enum. The fix is usually a small file with the right offsets or signatures. This repository collects those files in one place, with their source, so that nobody has to search issue trackers for them.

Noverna Studio downloads `index.json`, finds the entry for a game by its Steam app ID or Unreal project name, fetches only the files it needs and checks each one against the SHA-256 in the index. It uses them in its own session profiles, adds them when it installs a framework, and offers to put them into the game folder. Your own files in the game folder always win.

## Structure

```
index.json                 catalog for Noverna Studio (generated, don't edit by hand)
games/<game>/game.json     name, Steam app IDs, Unreal project names, configs with their source
games/<game>/ue4ss/        files that go next to UE4SS.dll (the "ue4ss" folder next to the game's Shipping exe)
games/<game>/ue4ss-steam/  store-specific variants (also ue4ss-gamepass)
games/<game>/NOTES.md      notes from the original source, if any
tools/build_index.py       regenerates index.json
```

A `game.json` looks like this:

```json
{
  "name": "Palworld",
  "steamAppIds": ["1623730"],
  "unrealProjects": ["Pal"],
  "configs": [
    {
      "framework": "ue4ss",
      "store": null,
      "folder": "ue4ss",
      "source": "https://github.com/UE4SS-RE/RE-UE4SS/issues/802",
      "notes": "Palworld 0.4.1.5 moved UEnum::Names by 8 bytes.",
      "testedWith": ["4.0.0"]
    }
  ]
}
```

- `steamAppIds` and `unrealProjects` decide which installed game an entry belongs to. Without either, the entry is listed but never applied automatically.
- `store` is `null` for all versions of the game, or `steam`, `gamepass`, `epic` for a store-specific variant.
- `UE4SS-settings.ini` in a config is merged into the existing settings key by key; all other files are copied as they are.

## Contributing

1. Add or change `games/<game>/game.json` and the files.
2. Name the source (an issue, a forum post, your own testing) and the framework versions you tested with.
3. Run `python tools/build_index.py` and commit `index.json` with your change.

Files in `UE4SS_Signatures/` are Lua scripts that UE4SS runs inside the game. Changes to them are reviewed with that in mind; only data and these signature scripts are accepted, never binaries.

## Licenses

The repository is MIT licensed (see `LICENSE`). The configs from UE4SS's `zCustomGameConfigs.zip` are MIT licensed by their authors, see `THIRD_PARTY_NOTICES.md`.

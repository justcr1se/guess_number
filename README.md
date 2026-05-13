# Knight Mod

A Minecraft Forge **1.18.2** mod that adds a full knight armor set, a knight sword,
and a knight dagger.

## Items & stats

| Item               | Armor | Durability | Damage | Attack speed |
|--------------------|------:|-----------:|-------:|-------------:|
| Knight Helmet      | 7     | 1512       | —      | —            |
| Knight Chestplate  | 15    | 4096       | —      | —            |
| Knight Leggings    | 12    | 3200       | —      | —            |
| Knight Boots       | 5     | 2000       | —      | —            |
| Knight Sword       | —     | 3000       | 20     | 1.6          |
| Knight Dagger      | —     | 1500       | 9      | 3.0          |

Note: Minecraft displays attack damage as `weapon damage + 1` (player base damage),
so the `SwordItem` constructor receives `damage - 1`, and the attack-speed argument
is `target_speed - 4.0` (player base attack speed).

## Build

Requires JDK 17.

```bash
./gradlew build
```

The built jar will be in `build/libs/knightmod-1.0.0.jar`. Drop it into the
`mods/` folder of a Minecraft 1.18.2 instance running Forge `40.2.x`.

If `gradlew` is missing, run `gradle wrapper --gradle-version 7.5.1` once with a
system Gradle, or set up the project in IntelliJ IDEA which will generate the
wrapper automatically.

## Textures

The PNG textures under `src/main/resources/assets/knightmod/textures` are
simple programmatically-generated placeholders so the mod compiles and runs
out of the box. They are produced by `generate_textures.py` (run once;
not required at build time). Feel free to replace them with higher quality
artwork — any CC0 medieval set from
[OpenGameArt.org](https://opengameart.org/) drops in directly so long as the
filenames match:

- `item/knight_helmet.png`, `item/knight_chestplate.png`,
  `item/knight_leggings.png`, `item/knight_boots.png`
- `item/knight_sword.png`, `item/knight_dagger.png`
- `models/armor/knight_layer_1.png` (helmet + chestplate + boots worn texture)
- `models/armor/knight_layer_2.png` (leggings worn texture)

All items appear in the **Combat** creative tab.

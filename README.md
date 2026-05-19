# Endstone Essentials Plugin

Plugin for Endstone that adds classic *Essentials*-style features such as `/home`, `/tpa`, `/rtp`, `/back`, `/spawn`, and other utilities designed to improve the server experience.

## Features

* Home system (`/sethome`, `/home`, `/delhome`)
* Player teleportation requests (`/tpa`, `/tpaccept`, `/tpdeny`)
* Random teleportation (`/rtp`) with configurable radius
* Return to your last location (`/back`)
* Spawn system (`/spawn`, `/setspawn`)
* Dynamic scoreboard with placeholders (online players, ping, TPS, economy)
* Integration with JWEconomy to display balance on the scoreboard
* Hot configuration reload (`/essreload`)
* RTP fall protection
* Automatic saving of the last position on death or teleport

## Commands

| Command      | Description                                             |
| ------------ | ------------------------------------------------------- |
| `/sethome`   | Set your home                                           |
| `/home`      | Open a form to teleport to your homes                   |
| `/delhome`   | Delete a home                                           |
| `/tpa`       | Open a form to request teleportation                    |
| `/tpaccept`  | Accept a TPA request                                    |
| `/tpdeny`    | Deny a TPA request                                      |
| `/back`      | Return to your last position before a teleport or death |
| `/spawn`     | Teleport to the server spawn                            |
| `/setspawn`  | Set the spawn point                                     |
| `/rtp`       | Random teleport in the Overworld                        |
| `/essreload` | Reload the plugin configuration                         |

## Installation

1. Download the plugin
2. Place the file in your Endstone server `plugins/` folder
3. Restart the server

## Dependencies

* **Endstone** v0.11 or higher
* **[JWEconomy](https://endgit.dev/plugins/jweconomy)** (optional): Used to display balance on the scoreboard

## Configuration

The plugin will automatically generate configuration files in the corresponding folder:

* `config.yml`: General configuration (spawn, RTP, etc.)
* `scoreboard.yml`: Scoreboard configuration (title, lines, placeholders)

### Scoreboard Placeholders

| Placeholder | Description                             |
| ----------- | --------------------------------------- |
| `%online%`  | Connected players                       |
| `%ping%`    | Player ping in ms                       |
| `%tps%`     | Current server TPS                      |
| `%balance%` | JWEconomy balance (requires the plugin) |

### RTP Configuration

In `config.yml` you can adjust the RTP radius values:

```yaml
rtp:
  min_radius: 1000
  max_radius: 5000
```

### Roadmap

| Feature  | Description                                                      |
| -------- | ---------------------------------------------------------------- |
| `warps`  | Public warp system (Probably will not be added)                  |
| `invsee` | Monitor player inventories                                       |
| `vanish` | Become invisible/invulnerable and disappear from the player list |

### Contributions

Contributions are welcome. You can fork the repository and submit a pull request with your improvements.

### License

This project is licensed under a non-commercial use license. You are free to use, modify, and share the code, but selling or using it for commercial purposes without the author's permission is not allowed.

### Author

Developed by MakiTazo

> If you have suggestions or find bugs, feel free to open an issue.
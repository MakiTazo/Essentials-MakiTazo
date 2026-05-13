# Endstone Essentials Plugin

Plugin para Endstone que añade funcionalidades clásicas estilo *Essentials* como `/home`, `/tpa`, `/rtp`, `/back`, `/spawn` y más utilidades pensadas para mejorar la experiencia en servidores.

## Características

* Sistema de homes (`/sethome`, `/home`, `/delhome`)
* Teletransportación entre jugadores (`/tpa`, `/tpaccept`, `/tpdeny`)
* Teletransporte aleatorio (`/rtp`) con radio configurable
* Volver a la última posición (`/back`)
* Sistema de spawn (`/spawn`, `/setspawn`)
* Scoreboard dinámico con placeholders (online, ping, TPS, economía)
* Integración con JWEconomy para mostrar balance en scoreboard
* Recarga de configuración en caliente (`/essreload`)
* Protección contra caídas en RTP
* Guardado automático de última posición al morir o teletransportarse

## Comandos

| Comando         | Descripción                                    |
| --------------- | ---------------------------------------------- |
| `/sethome`      | Establece tu hogar                             |
| `/home`         | Abre formulario para teletransportarte a tus homes |
| `/delhome`      | Elimina un home                                |
| `/tpa`          | Abre formulario para solicitar teletransporte  |
| `/tpaccept`     | Acepta una solicitud de TPA                    |
| `/tpdeny`       | Rechaza una solicitud de TPA                   |
| `/back`         | Vuelve a tu última posición antes de un teleport o muerte |
| `/spawn`        | Teletransporte al spawn del servidor           |
| `/setspawn`     | Establece el punto de spawn                    |
| `/rtp`          | Teletransporte aleatorio en el Overworld       |
| `/essreload`    | Recarga la configuración del plugin            |

## Instalación

1. Descarga el plugin
2. Coloca el archivo en la carpeta `plugins/` de tu servidor Endstone
3. Reinicia el servidor

## Dependencias

* **Endstone** v0.11 o superior
* **[JWEconomy](https://endgit.dev/plugins/jweconomy)** (opcional): Para mostrar el balance en el scoreboard

## Configuración

El plugin generará automáticamente los archivos de configuración en la carpeta correspondiente:

* `config.yml`: Configuración general (spawn, RTP, etc.)
* `scoreboard.yml`: Configuración del scoreboard (título, líneas, placeholders)

### Placeholders del Scoreboard

| Placeholder  | Descripción                  |
| ------------ | ---------------------------- |
| `%online%`   | Jugadores conectados         |
| `%ping%`     | Ping del jugador en ms       |
| `%tps%`      | TPS actual del servidor      |
| `%balance%`  | Balance de JWEconomy (requiere el plugin) |

### Configuración de RTP

En `config.yml` puedes ajustar los radios del RTP:

```yaml
rtp:
  min_radius: 1000
  max_radius: 5000
```
### Roadmap
| Placeholder | Descripción                                                       |
|-------------|-------------------------------------------------------------------|
| `warps`     | Sistema de warps públicos (Probablemente no se añada)             |
| `invsee`    | Para monitorizar inventarios                                      |
| `vanish`    | Desaparece de la lista de jugadores y eres invisible/Invulnerable |

### Contribuciones
Las contribuciones son bienvenidas. Puedes hacer un fork del repositorio y enviar un pull request con tus mejoras.

### Licencia
Este proyecto está bajo una licencia de uso no comercial. Puedes usar, modificar y compartir el código libremente, pero no está permitido venderlo ni utilizarlo con fines comerciales sin autorización del autor.

### Autor
Desarrollado por MakiTazo

> Si tienes sugerencias o encuentras errores, puedes abrir un issue.
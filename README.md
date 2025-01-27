# Constellation wallpaper generator

Creates a (dynamic) wallpaper based on the time of day from a constellation provided as SVG (stored in `./resources/constellations`). It uses `ipify.org` and `ip-api.com` to infer current latitude and longiture, and `suntime` to create a wallpaper schedule. By default it uses the `kanagawa` palette.


## Installation

```
pip install -r requirements.txt
```

## Usage


1. To generate a series of static wallpapers
```
python main.py <constellation> -a
```
2. To run it as a daemon
```
python main.py <constellation> -a -d
```

An example `systemd` service has been provide
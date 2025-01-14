import yaml
import tomllib
import json
import os
from colour import Color
from copy import deepcopy

class Palette(dict):

    magic = {
        "black"     : "#000000",
        "red"       : "#ff0000",
        "yellow"    : "#ffff00",
        "green"     : "#00ff00",
        "cyan"      : "#00ffff",
        "blue"      : "#0000ff",
        "magenta"   : "#ff00ff",
        "white"     : "#ffffff"
    }

    def __init__(self,
                 palette_file: str,
                 bgr_lum : float = 0.1,
                 fil_lum : float = 0.7,
                 str_lum : float = 0.8) -> None:
        
        colours = self.load_from_file(palette_file)

        
        self.palette = {}
        for key in colours["colors"]["normal"]:
            self.palette[key] = Color(colours["colors"]["normal"][key])

        self.background = deepcopy(self.palette)
        self.fill = deepcopy(self.palette)
        self.stroke = deepcopy(self.palette)

        for key in self.palette:
            self.background[key].luminance  = bgr_lum
            self.fill[key].luminance        = fil_lum
            self.stroke[key].luminance      = str_lum


    def __repr__(self) -> str:
        return f"{self.palette}"
    

    def load_from_file(self,palette_file : str) -> None:
        ext = os.path.splitext(palette_file)
        
        match ext[1]:
            case "yaml" | ".yml":
                with open(palette_file,'r') as file:
                    return yaml.safe_load(file)
            case ".toml":
                with open(palette_file,'rb') as file:
                    return tomllib.load(file)


    def create_transform(self,
                         background_colour="black",
                         line_colour = "white") -> dict:

        colours = {}

        for colour in self.magic:

            hex = self.magic[colour]
            match colour:
                case "white":
                    colours[hex] = self.background[background_colour].hex
                case "black":
                    colours[hex] = self.stroke[line_colour].hex
                case _:
                    colours[hex] = self.fill[colour].hex

        return colours
            

if __name__ == "__main__":
    palette = Palette("palettes/kanagawa.yml")
    print(palette.palette)
    print(palette.background)
    print(palette.fill)
    print(palette.stroke)
    

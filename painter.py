import yaml
import tomllib
import json
import os
from colour import Color
from copy import deepcopy

import colorsys as clr


# def hsv_to_hsl(hsv):
#     h, s, v = hsv
#     rgb = clr.hsv_to_rgb(h/360, s/100, v/100)
#     r, g, b = rgb
#     h, l, s = clr.rgb_to_hls(r, g, b)
#     return h*360, s*100, l*100




 


class ColorHSV(Color):

    @staticmethod
    def rgb2hsv(rgb):
        r, g, b = rgb
        h, s, v = clr.rgb_to_hsv(r, g, b)
        return h,s,v

    @staticmethod
    def hsv2rgb(hsv):
        h, s, v = hsv
        r,g,b = clr.hsv_to_rgb(h, s, v)     
        return r,g,b  


    def set_value(self,v):
        hsv = self.rgb2hsv(self.rgb)
        hsv_new = hsv[0],hsv[1],v
        rgb_new = self.hsv2rgb(hsv_new)
        self.set_rgb(rgb_new)


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
            self.palette[key] = ColorHSV(colours["colors"]["normal"][key])

        self.background = deepcopy(self.palette)
        self.fill = deepcopy(self.palette)
        self.stroke = deepcopy(self.palette)

        for key in self.palette:
            
            self.background[key].set_value(bgr_lum)
            self.fill[key].set_value(fil_lum)
            self.stroke[key].set_value(str_lum) 


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
                         line_colour = "white",
                         squash_fill_colours: bool = False) -> dict:

        colours = {}

        for colour in self.magic:

            hex = self.magic[colour]
            match colour:
                case "white":
                    colours[hex] = self.background[background_colour].hex
                case "black":
                    colours[hex] = self.stroke[line_colour].hex
                case _:
                    if squash_fill_colours:
                        colours[hex] = self.stroke[line_colour].hex
                    else:
                        colours[hex] = self.fill[colour].hex

        return colours
            

if __name__ == "__main__":
    palette = Palette("palettes/kanagawa.yml")
    print(palette.palette)
    print(palette.background)
    print(palette.fill)
    print(palette.stroke)
    

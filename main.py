import artist as a
import painter as p
import schedule as s
import random
from copy import deepcopy
from datetime import datetime, timedelta
import time
import os
import subprocess

import svgmanip as svg

def draw(canvas_width : int,
         canvas_height : int,
         scale_factor : float,
         star_count : int, 
         constellation: str) -> a.Canvas:

    star_sizes = [0.005,0.025]

    canvas = a.Canvas(canvas_width,canvas_height)
    constellation = svg.Element(f"resources/constellations/{constellation}.svg")
    star = svg.Element("resources/star.svg")
    constellation_scaled,factor = canvas.scale_object(constellation,scale=scale_factor)

    x,y = canvas.get_centre_coordinates(constellation_scaled,factor)
    canvas.place_object(constellation_scaled,x,y,layer="foreground")

    for i in range(star_count):
        scale = random.uniform(star_sizes[0],star_sizes[1])
        x = random.uniform(0,canvas_width)
        y = random.uniform(0,canvas_height)
        star_scaled,factor = canvas.scale_object(star,scale)
        star_scaled = canvas.set_object_alpha(star_scaled,fill_alpha=0.2,stroke_alpha=0)
        canvas.place_object(star_scaled,x,y,layer="detail")
    
    return canvas


if __name__ == "__main__":
    
    star_count = 20
    

    canvas_width = 3440
    canvas_height = 1440

    canvas =  draw(canvas_width,
                   canvas_height,
                   scale_factor=0.7,
                   star_count=50,
                   constellation="canis-major")  

    schedule = s.ColourSchedule(0,0)

    
    while(True):

        now = datetime.now()
        next = now.replace(microsecond=0, second=0, minute=0) + timedelta(hours=1)
        delta = (next - now).total_seconds()

        colours = schedule.schedule[now.hour]
        print(f"Hour : {now.hour}\t\t{colours}" )
        target = deepcopy(canvas)

        palette = p.Palette("./palettes/spaceduck.yml",
                                bgr_lum=colours["bgr_lum"],
                                fil_lum=colours["fil_lum"],
                                str_lum=colours["str_lum"])

        colours = palette.create_transform(background_colour=colours["bg_col"],line_colour=colours["fg_col"])
        
        target.transform_colours(colours)

        target.export(f"output/constellation.png")
        
        abspath = os.path.abspath(f"output/constellation.png")

        subprocess.call(["gsettings","set","org.gnome.desktop.background","picture-uri",
                         f"file://{abspath}"])
        subprocess.call(["gsettings","set","org.gnome.desktop.background","picture-uri-dark",
                         f"file://{abspath}"])

        print(f"Sleeping for {delta} seconds until {next}")
        time.sleep(delta)


# TODO
# https://www.reddit.com/r/gnome/comments/x5zkdq/cannot_change_wallpaper_via_gsettings/
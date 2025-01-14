import artist
import painter
import random

import svgmanip as svg

def draw(canvas_width : int,
         canvas_height : int,
         scale_factor : float,
         star_count : int, 
         constellation: str) -> artist.Canvas:

    star_sizes = [0.005,0.025]

    canvas = artist.Canvas(canvas_width,canvas_height)
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


    palette = painter.Palette("./palettes/kanagawa.yml",
                              bgr_lum=0.3,
                              fil_lum=0.8,
                              str_lum=0.0)

    colours = palette.create_transform(background_colour="blue",line_colour="white")
    
    canvas.transform_colours(colours)


    canvas.dump("output/canvas.svg")
    canvas.export("output/test.png")
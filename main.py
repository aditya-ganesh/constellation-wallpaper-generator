import artist as a
import painter as p
import schedule as s
import random
from copy import deepcopy
from datetime import datetime, timedelta
import time
import os
import subprocess
import argparse
import requests
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

def geolocate() -> tuple:
    lat,lon = 0,0
    res = requests.get("https://api64.ipify.org/?format=json")
    ip = None

    if res:
        ip = res.json()["ip"]
        print(f"Public IP address is : {ip}")
    
    if ip:
        res = requests.get(f"http://ip-api.com/json/{ip}")
        print(res)
        if res:
            loc = res.json()
            lat,lon = loc["lat"],loc["lon"]
            print("IP based location is {},{},{}\nLat : {}\tLon : {}".format(
                loc["city"],
                loc["regionName"],
                loc["country"],
                lat,
                lon
            ))

    return lat,lon

if __name__ == "__main__":
    

    parser = argparse.ArgumentParser()

    parser.add_argument("constellation")
    parser.add_argument("--width",default=3440)
    parser.add_argument("--height",default=1440)
    parser.add_argument("-s","--scale",default=0.7)
    parser.add_argument("-n","--star-count",default=50)
    parser.add_argument("-d","--daemon",action="store_true")
    parser.add_argument("-p","--palette",default="kanagawa.yml")
    parser.add_argument("-a","--auto-location",action="store_true")
    parser.add_argument("--lat",default=0)
    parser.add_argument("--lon",default=0)

    args = parser.parse_args()


    canvas =  draw(args.width,
                   args.height,
                   scale_factor=args.scale,
                   star_count=args.star_count,
                   constellation=args.constellation)  


    if args.auto_location:
        lat,lon = geolocate()
    else:
        lat,lon = float(args.lat),float(args.lon)

    schedule = s.ColourSchedule(lat,lon)

    print(f"Colour schedule is calculated as : {schedule}")

    if not args.daemon:

        for hour,colours in schedule.schedule.items():
            print(f"Hour : {hour}\t\t{colours}" )
            palette = p.Palette(f"./palettes/{args.palette}",
                                    bgr_lum=colours["bgr_lum"],
                                    fil_lum=colours["fil_lum"],
                                    str_lum=colours["str_lum"])
            
            target = deepcopy(canvas)
            colours = palette.create_transform(background_colour=colours["bg_col"],line_colour=colours["fg_col"])
            
            target.transform_colours(colours)
            os.makedirs("output/static",exist_ok=True)
            target.export(f"output/static/constellation_{hour}.png")

    else:
        while(True):

            now = datetime.now()
            next = now.replace(microsecond=0, second=0, minute=0) + timedelta(hours=1)
            delta = (next - now).total_seconds()

            # If it's a new day, redo the schedule
            if now.hour == 0:
                schedule = s.ColourSchedule(args.lat,args.long)

            colours = schedule.schedule[now.hour]
            
            print(f"Hour : {now.hour}\t\t{colours}" )
            target = deepcopy(canvas)

            palette = p.Palette(f"./palettes/{args.palette}",
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


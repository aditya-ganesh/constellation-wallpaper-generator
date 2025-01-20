from suntime import Sun,SunTimeException
from datetime import datetime


class ColourSchedule:

    def __init__(self,lat: float, long: float) -> None:
        self.lat = lat
        self.long = long

        try:
            stime = Sun(lat,long)
            self.sunrise = stime.get_sunrise_time()
            self.sunset = stime.get_sunset_time()
            self.daylight_hours = self.sunset.hour - self.sunrise.hour
            self.nighttime_hours = self.sunrise.hour + (24 - self.sunset.hour)
            self.midnight_sun = False
            self.polar_night = False
        except SunTimeException:
            if self.is_summer(lat):
                self.sunrise = datetime.now().replace(hour=0,minute=0,second=0)
                self.sunset = datetime.now().replace(hour=23,minute=59,second=59)
                self.daylight_hours = 24
                self.nighttime_hours = 0
                self.midnight_sun = True
                self.polar_night = False
            else:
                self.sunrise = datetime.now().replace(hour=23,minute=59,second=59)
                self.sunset = datetime.now().replace(hour=23,minute=59,second=59)
                self.daylight_hours = 0
                self.nighttime_hours = 24 
                self.midnight_sun = False
                self.polar_night = True


        self.schedule = self.create_schedule()  
        self.tag_schedule_colours()             


    def __repr__(self) -> str:
        str = ""
        str += "Lat\t:\t:{}\n".format(self.lat)    
        str += "Long\t:\t:{}\n".format(self.long)    
        str += "Rise\t:\t:{}\n".format(self.sunrise)
        str += "Set\t:\t:{}\n".format(self.sunset)    
        str += "Day\t:\t:{}\n".format(self.daylight_hours)    
        str += "Night\t:\t:{}\n".format(self.nighttime_hours)
        str += "\n"
        
        for key,val in self.schedule.items():
            str += f"\t\t{key}\t:\t{val}\n"

        return str
    
    def tag_schedule_colours(self) -> None:
        
        for hour,phase in self.schedule.items():
            match phase:
                case "night":
                    bg_col = "black"
                    fg_col = "white"
                    bgr_lum = 0
                    fil_lum = 0.6
                    str_lum = 0.7
                case "dawn" | "dusk":
                    bg_col = "magenta"
                    fg_col = "white"
                    bgr_lum = 0.1
                    fil_lum = 0.6
                    str_lum = 0.6                    
                case "day":
                    bg_col = "blue"
                    fg_col = "black"
                    bgr_lum = 0.2
                    fil_lum = 1
                    str_lum = 0.0  
            
            self.schedule[hour] = {
                "phase"     : phase,
                "bg_col"    : bg_col,
                "fg_col"    : fg_col,
                "bgr_lum"   : bgr_lum,
                "fil_lum"   : fil_lum,
                "str_lum"   : str_lum
            }



    def create_schedule(self) -> dict:
        hours = list(range(24))
        schedule = {}

        if self.polar_night:
            for hour in hours:
                schedule[hour] = "night"
        elif self.midnight_sun:
            for hour in hours:
                schedule[hour] = "day"
        else:
            for hour in hours:
                if hour < self.sunrise.hour:
                    schedule[hour] = "night"
                elif hour == self.sunrise.hour:
                    schedule[hour] = "dawn"
                elif hour < self.sunset.hour:
                    schedule[hour] = "day"
                elif hour == self.sunset.hour:
                    schedule[hour] = "dusk"
                else:
                    schedule[hour] = "night"
        
        return schedule
            
    
    @staticmethod
    def is_summer(lat: float) -> bool:

        time = datetime.now()

        if time.month in range(3,9):
            return True if lat > 0 else False
        else:
            return False if lat > 0 else True
        
if __name__ == "__main__":
    schedule = ColourSchedule(0,0)
    print(schedule)
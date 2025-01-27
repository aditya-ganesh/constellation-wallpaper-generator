from suntime import Sun,SunTimeException
from datetime import datetime


class ColourSchedule:

    def __init__(self,lat: float, long: float) -> None:
        self.lat = lat
        self.long = long
        self.tz = datetime.now().tzinfo

        try:
            stime = Sun(lat,long)
            self.sunrise = stime.get_sunrise_time().astimezone(self.tz)
            self.sunset = stime.get_sunset_time().astimezone(self.tz)
            self.dawn = self.sunrise.hour
            self.dusk = self.sunset.hour
            self.daylight_hours = self.sunset.hour - self.sunrise.hour - 1
            self.nighttime_hours = self.sunrise.hour + (24 - self.sunset.hour) - 1
            self.midnight_sun = False
            self.polar_night = False
            self.midday_hour = self.sunrise.hour + int(self.daylight_hours/2)
            self.midnight_hour = (self.sunset.hour + int(self.nighttime_hours/2)) % 24

        except SunTimeException:
            if self.is_summer(lat):
                self.sunrise = datetime.now().replace(hour=0,minute=0,second=0)
                self.sunset = datetime.now().replace(hour=23,minute=59,second=59)
                self.dawn = 0
                self.dusk = 23
                self.daylight_hours = 24
                self.nighttime_hours = 0
                self.midnight_sun = True
                self.polar_night = False
                self.midday_hour = 12
                self.midnight_hour = 0

            else:
                self.sunrise = datetime.now().replace(hour=23,minute=59,second=59)
                self.sunset = datetime.now().replace(hour=23,minute=59,second=59)
                self.dawn = 23
                self.dusk = 0
                self.daylight_hours = 0
                self.nighttime_hours = 24 
                self.midnight_sun = False
                self.polar_night = True
                self.midday_hour = 0
                self.midnight_hour = 12
            

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
        str += "Midday\t:\t:{}\n".format(self.midday_hour)    
        str += "Midnight\t:\t:{}\n".format(self.midnight_hour)
        str += "\n"
        
        for key,val in self.schedule.items():
            str += f"\t\t{key}\t:\t{val}\n"

        return str
    
    def tag_schedule_colours(self) -> None:
        
        min_day_lum = 0.15
        max_day_lum = 0.4
        max_night_lum = 0.1
        transition_lum = 0.15

        
        daylight_intensities = []
        # Increase daylight intensities in steps until midday, then decrease
        if self.daylight_hours > 0:
            day_lum_step = 2*(max_day_lum-min_day_lum)/self.daylight_hours
            ascending_intensities = [min_day_lum + i*day_lum_step for i in range(0,self.daylight_hours//2)]
            if self.daylight_hours % 2 == 0:
                daylight_intensities = ascending_intensities.copy()
                daylight_intensities.extend(reversed(ascending_intensities))
            else:
                daylight_intensities = ascending_intensities.copy()
                daylight_intensities.append(max_day_lum)
                daylight_intensities.extend(reversed(ascending_intensities))

        # Decrease nighttime intensities in steps until midnight, then increase
        if self.nighttime_hours > 0:
            night_lum_step = 2*max_night_lum/self.nighttime_hours
            descending_intensities = [max_night_lum - i*night_lum_step for i in range(0,self.nighttime_hours//2)]
            if self.polar_night:
                nighttime_intensities = []
                nighttime_intensities.extend(reversed(descending_intensities))
                nighttime_intensities.extend(descending_intensities)

            else:

                if self.nighttime_hours % 2 == 0:
                    nighttime_intensities = descending_intensities.copy()
                    nighttime_intensities.extend(reversed(descending_intensities))
                else:
                    nighttime_intensities = descending_intensities.copy()
                    nighttime_intensities.append(0)
                    nighttime_intensities.extend(reversed(descending_intensities))            

        intensities = {}
        for i in range(24):
            intensities[i] = 0

        intensities[self.dawn] = transition_lum
        intensities[self.dusk] = transition_lum

        for i in range(self.daylight_hours):
            hour = self.sunrise.hour + i + 1
            intensities[hour] = daylight_intensities[i]
        
        for i in range(self.nighttime_hours):
            hour = (self.sunset.hour + i + 1) % 24
            intensities[hour] = nighttime_intensities[i]

        for hour,phase in self.schedule.items():
            bgr_lum = intensities[hour]

            if bgr_lum < 0.25:
                str_lum = 0.7
                fil_lum = 0.6
                fg_col = "white"
            else:
                str_lum = 0.0
                fg_col = "black"
                fil_lum = 1 


            match phase:
                case "night":
                    bg_col = "black"

                case "dawn" | "dusk":
                    bg_col = "magenta"
                                   
                case "day":
                    bg_col = "blue"
                    

            
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
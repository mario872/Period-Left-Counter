from flask import *
import ics
from datetime import datetime as dt
from datetime import date
from datetime import timedelta
from markupsafe import escape
from fileinput import filename
import random
import os

timezone_hours_ahead = 11

def fix_timetable_format(timetable, name):
    with open(name, 'w') as timetable_ics:
        timetable.pop(1)
        timetable.pop(2)
        timetable_ics.writelines(timetable)
    return timetable

possible_names = ['ENG', 'MAT', 'SCI', 'HIS', 'GEO', 'LA', 'ART', 'MUS', 'TEC', 'GIFTed', 'GIFTed2', 'PDHPE', 'Sport']

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/success', methods=['POST'])   
def success():   
    if request.method == 'POST':   
        file = request.files['file']
        if file.filename.endswith('.ics'):
            file.filename = file.filename.replace(' ', '_')
            if not file.filename in os.listdir():
                file.save('timetables/' + file.filename)
                if random.randint(0, 500) == 500:
                    return render_template("rickroll.html")
                else:
                    return render_template("success.html", name=file.filename)
            else:
                return render_template('failure.html', name=file.filename)
        else:
            return render_template("failure.html", name=file.filename)

@app.route("/timetable")
def timetable_redirect():
    return render_template("timetable_selection.html", view='timetable')

@app.route("/timetable/<timetable_name>")
def timetable(timetable_name):
    try:
        calendar_ics = open('timetables/' + timetable_name + '.ics', 'r')
    except FileNotFoundError:
        return render_template('file_not_found.html')
    try:
        calendar_ics_list = calendar_ics.readlines()
        calendar_ics.close()
            
        calendar = ''
        for item  in calendar_ics_list:
            calendar += item

        calendar = ics.Calendar(calendar)
    except ValueError:
        calendar_ics = fix_timetable_format(calendar_ics_list, timetable_name + '.ics')
        calendar = ''
        for item  in calendar_ics:
            calendar += item

        calendar = ics.Calendar(calendar)
        
    events = list(calendar.events)
    events = sorted(events)
    
    timedatelist = []
    lessons_left = {'ENG': 0, 'MAT': 0, 'SCI': 0, 'HIS': 0, 'GEO': 0, 'LA': 0, 'ART': 0, 'MUS': 0, 'TEC': 0, 'GIFTed': 0, 'GIFTed2': 0, 'PDHPE': 0, 'Sport': 0}
    for item in events:
        if (dt.fromisoformat(str(item.end))+timedelta(hours=timezone_hours_ahead)).replace(tzinfo=None) < dt.now():
            pass
        else:
            timedatelist.append((dt.fromisoformat(str(item.end))+timedelta(hours=timezone_hours_ahead)).replace(tzinfo=None))
            
    timedatelist = sorted(timedatelist)
    for i in range(len(events) - len(timedatelist), len(events)):
        for item in possible_names:
            if item in events[i].name:
                lessons_left[item] += 1
                
    update = dt.now()
    next_period = timedatelist[0]

    return render_template('timetable.html', left=lessons_left, update=update, next_period=next_period, filename=timetable_name)

@app.route("/countdown")
def countdown_selection():
    return render_template('timetable_selection.html', view='countdown')

@app.route("/countdown/<timetable_name>")
def countdown(timetable_name):
    try:
        calendar_ics = open('timetables/' + timetable_name + '.ics', 'r')
    except FileNotFoundError:
        return render_template('file_not_found.html')
    try:
        calendar_ics_list = calendar_ics.readlines()
        calendar_ics.close()
            
        calendar = ''
        for item  in calendar_ics_list:
            calendar += item

        calendar = ics.Calendar(calendar)
    except ValueError:
        calendar_ics = fix_timetable_format(calendar_ics_list, timetable_name + '.ics')
        calendar = ''
        for item  in calendar_ics:
            calendar += item

        calendar = ics.Calendar(calendar)
        
    events = list(calendar.events)
    events = sorted(events)
    
    timedatelist = []
    
    time_left = {'days-left': 0, 'minutes-left': 0, 'seconds-left': 0, 'minutes-left-today': 0, 'seconds-left-today': 0, 'minutes-left-period': 0, 'seconds-left-period': 0}
    time_left_values = ['days-left', 'minutes-left', 'seconds-left', 'minutes-left-today', 'seconds-left-today', 'minutes-left-period', 'seconds-left-period']
    timedatelist = []
    
    for item in events:
        if (dt.fromisoformat(str(item.end))+timedelta(hours=timezone_hours_ahead)).replace(tzinfo=None) < dt.now():
            pass
        else:
            timedatelist.append((dt.fromisoformat(str(item.end))+timedelta(hours=timezone_hours_ahead)).replace(tzinfo=None))
            
    timedatelist = sorted(timedatelist)
    weekday = date.today().weekday()   
    if weekday == 2:
        end_day_hour = 14
        end_day_minute = 45  
    elif weekday == 5 or weekday == 6:
        end_day_hour = 0
        end_day_minute = 0  
    else:
        end_day_hour = 15
        end_day_minute = 5

    end_year_day = 15
    end_year_month = 12

    now = dt.now()

    
    end_of_school_year = dt(year=int(now.strftime('%Y')), month=end_year_month, day=end_year_day, hour=end_day_hour, minute=end_day_minute, second=0)
    end_of_day = dt(year=int(now.strftime('%Y')), month=int(now.strftime('%m')), day=int(now.strftime('%d')), hour=end_day_hour, minute=end_day_minute, second=0)

    time_left['days-left'] = str(round(int(end_of_school_year.strftime('%j')) - int(now.strftime('%j')), 2))
    time_left['minutes-left'] = str(round((end_of_school_year - now).total_seconds() /60, 2))
    time_left['seconds-left'] = str(int(round((end_of_school_year - now).total_seconds(), 0)))
    time_left['minutes-left-today'] = str(round((end_of_day - now).total_seconds() /60, 2))
    time_left['seconds-left-today'] = str(int(round((end_of_day - now).total_seconds(), 0)))
    
    
    res = min(timedatelist, key=lambda sub: abs(sub - now))
    if res < now:
        res = timedatelist[timedatelist.index(res) + 1]
    time_left['minutes-left-period'] = str(int(round((res - now).total_seconds() / 60, 2)))
    time_left['seconds-left-period'] = str(int(round((res - now).total_seconds(), 0)))

    for item in time_left_values:
        if float(time_left[item]) < 0.0:
            time_left[item] = str(0)

    update = dt.now()

    return render_template('countdown.html', time_left=time_left, update=update, filename=timetable_name)


if __name__ == '__main__':
    app.run('127.0.0.1', 5000)
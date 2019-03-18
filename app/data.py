import  pytz
import datetime

def get_date():
    jamaica = pytz.timezone("America/Jamaica")
    return datetime.datetime.now(jamaica)

def get_file_extension(filename):
    return filename.split(".")[-1]

def format_date(datetimeObject):
    return datetimeObject.strftime("%B %d, %Y")
    
    
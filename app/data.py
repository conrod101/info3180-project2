import  pytz
import datetime
from datetime import datetime



def get_file_extension(filename):
    return filename.split(".")[-1]

def format_date(datetimeObject):
    """Returns current date formatted as 'Month Day, Year' """
    return datetimeObject.strftime("%B %d, %Y")
    
def current_date():
    """Returns current date formatted as 'Month Day, Year' """
    jamaica = pytz.timezone("America/Jamaica")
    date    = datetime.now(jamaica)
    return date
    
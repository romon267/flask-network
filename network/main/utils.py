import pytz
from pytz import timezone

def datetimefilter(value, format="%d/%m в %H:%M, %Y"):
    tz = pytz.timezone('Europe/Moscow') # timezone you want to convert to from UTC
    utc = pytz.timezone('UTC')  
    value = utc.localize(value, is_dst=None).astimezone(pytz.utc)
    local_dt = value.astimezone(tz)
    return local_dt.strftime(format)

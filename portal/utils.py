from datetime import datetime
from dateutil import tz

def indonesia_time(args, with_time=False):
    # Auto-detect zones:
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('Asia/Jakarta')
    wib = args.replace(tzinfo=from_zone)
    # Convert time zone
    wib = wib.astimezone(to_zone)
    if with_time:
        return f"{wib.strftime('%d-%B-%Y %H:%M')} WIB"
    return wib.strftime('%d-%B-%Y')
def safe_method_call(method):
    def wrapper(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except Exception as e:
            print(f"[SafeCall] Error in {self.__class__.__name__}.{method.__name__}: {e}")
    return wrapper

def format_time(minutes):
    """
    Format time values into hours/minutes.
    """
    if minutes < 60:
        return f"{minutes} min"
    hours = minutes // 60
    remaining_minutes = minutes % 60
    if remaining_minutes == 0:
        return f"{hours}h"
    else:
        return f"{hours}h {remaining_minutes} min"
    
def format_time_sec(seconds):
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining = seconds % 60
        return f"{minutes}m {remaining}s" if remaining else f"{minutes}min"
    else:
        hours = seconds // 3600
        return f"{hours}h"
    
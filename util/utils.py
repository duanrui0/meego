import functools
import time
from datetime import datetime


# 时间转换
def trans_unix_time(timestamp):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp / 1000)) if timestamp is not None else None


# 时间消耗统计
def time_cost(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        print(func.__name__ + " start time: %s " % datetime.now())
        result = func(*args, **kwargs)
        print(func.__name__ + " end time: %s " % datetime.now())
        print(func.__name__ + " elapsed time: %s " % round(time.time() - start_time, 4))
        return result
    return wrapper


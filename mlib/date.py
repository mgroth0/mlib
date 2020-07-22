from calendar import month_name, mdays

def months(): return [month_name[i] for i in range(1, 13)]
def non_leap_days_in_months(): return [mdays[i] for i in range(1, 13)]




from datetime import datetime

def now():
    # datetime object containing current date and time
    noww = datetime.now()

    # print("now =", now)
    # dd/mm/YY H:M:S
    dt_string = noww.strftime("%m/%d/%Y %H:%M:%S")
    # print("date and time =", dt_string)
    return dt_string

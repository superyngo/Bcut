import datetime

# Calculate needed dates as string or date
def _fn_calculate_closing_date(date:datetime.date) -> datetime.date:
    if 1 <= date.day <= 20:
        # 如果是1月，年份減1，月份變為12月
        if date.month == 1:
            adjusted_date = date.replace(year=date.year - 1, month=12, day=20)
        else:
            # 否則，月份減1
            adjusted_date = date.replace(month=date.month - 1, day=20)
    else:
        # 如果不在1到20日之間，則只更改日期為20
        adjusted_date = date.replace(day=20)
    return adjusted_date

def _fn_calculate_start_date(date:datetime.date) -> str:
    if 1 <= date.day <= 20:
        # 如果是1月，年份減1，月份變為12月
        if date.month == 1:
            result_date = date.replace(year=date.year - 1, month=12, day=21)
        else:
            # 否則，月份減1
            result_date = date.replace(month=date.month - 1, day=21)
    else:
        # 如果不在1到20日之間，則只更改日期為21
        result_date = date.replace(day=21)
    # 格式化日期為 "YYYY/MM/DD" 格式
    return result_date.strftime("%Y/%m/%d")

# Timestamp and needed date
DAT_TODAY:datetime = datetime.date.today()
STR_DATESTAMP:str = DAT_TODAY.strftime("%Y%m%d")
STR_FIRST_DAY_OF_THIS_YEAR:str = datetime.date(DAT_TODAY.year, 1, 1).strftime("%Y%m%d")
DAT_CLOSING_DATE:datetime = _fn_calculate_closing_date(DAT_TODAY)
STR_START_DATE:datetime = _fn_calculate_start_date(DAT_TODAY)
STR_THIS_MONTH_PREFIX:str = f"{DAT_CLOSING_DATE.year - 1911}{str(DAT_CLOSING_DATE.month).zfill(2)}"

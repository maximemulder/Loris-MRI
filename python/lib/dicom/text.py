from datetime import datetime, date

def write_value(value: str | int | float | None):
    if value == None:
        return ''

    return str(value)

def write_datetime(datetime: datetime):
    return datetime.strftime('%Y-%m-%d %H:%M:%S')

def write_date(date: date):
    return date.strftime('%Y-%m-%d')

def write_date_none(date: date | None):
    if date == None:
        return None

    return write_date(date)

def read_string(string: str):
    if string == '':
        return None

    return string

def read_date_none(string: str | None):
    if string == None:
        return None

    return datetime.strptime(string, '%Y-%m-%d').date()

def read_dicom_date(string: str | None):
    if string == None:
        return None

    return datetime.strptime(string, '%Y%m%d').date()

# TODO: Change read aproach: empty string by default, with nullable as an add-on

def read_required(text: str | None):
    if text == None:
        return ''
        raise Exception(f'Expected value string but found empty string.')

    return text

def read_int(text: str | None):
    if text == None:
        return None

    return int(text)

def read_float(text: str | None):
    if text == None:
        return None

    return float(text)

def null(text: str):
    if text == '':
        return None

    return text

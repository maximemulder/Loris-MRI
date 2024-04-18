def write_value(value: str | int | float | None):
    if value == None:
        return ''

    return str(value)

def read_string(string: str):
    if string == '':
        return None

    return string

def read_required(text: str | None):
    if text == None:
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

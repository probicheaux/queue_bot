def isint(in_string):
    try:
        int(in_string)
        return True
    except ValueError:
        return False

def isint(in_string):
    try:
        int(in_string)
        return True
    except ValueError:
        return False

class SmusError(Exception):
    def __init__(self, exception_message, user_message):
        self.user_message = user_message
        super(SmusError, self).__init__(exception_message)
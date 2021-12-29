def verify(args, params):
    for arg in args:
        if arg not in params:
            return arg
    return False
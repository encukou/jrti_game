def clamp(value, minimum=0, maximum=1):
    if value < minimum:
        return minimum
    if value > maximum:
        return maximum
    return value

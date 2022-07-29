
def containToRange(range: tuple[int, int], num: int) -> int:
    """ Checks if num is inside the range and returns the
    lowest possible number `x` where `num + x` is inside the range.

    Args:
        range (tuple):
            (lowerLimit, upperLimit): the range to check in.
            num: the number to check if x is in range.

    Returns:
        int: `x`
    """
    downLim =  range[0] - num
    upperLim = range[1] - num

    if (downLim > 0):
        return downLim
    elif (upperLim < 0):
        return upperLim
    else:
        return 0
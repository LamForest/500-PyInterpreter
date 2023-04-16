def are_you_rich(deposit):
    ret = None
    if deposit >= 1e5:
        ret = "rich"
    else:
        ret = "poor"
    return ret


kind_1 = are_you_rich(1e4)
kind_2 = are_you_rich(1e6)
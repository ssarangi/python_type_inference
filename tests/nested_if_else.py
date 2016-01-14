def main(a, b, c):
    d = 0
    if a > b:
        if b > c:
            c = b
            a = b
            d = a * c
        else:
            c = a * b
            a = c - b
            d = a - c
    else:
        d = b

    return d
from decimal import Decimal, ROUND_HALF_UP
def tl(x):
    q=Decimal(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    s=f"{q:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{s} TL"

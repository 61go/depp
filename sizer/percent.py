from backtrader.sizers import PercentSizer


# cerebro.addsizer(bt.sizers.FixedSize, stake=10)
class FullMoney(PercentSizer):
    params = (
        ('percents', 99),
    )

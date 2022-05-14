#!/usr/bin/env python3

from datetime import datetime
import backtrader as bt
from termcolor import colored
from config import DEVELOPMENT, COIN_TARGET, COIN_REFER, ENV, PRODUCTION, DEBUG
from utils import send_telegram_message


class StrategyBase(bt.Strategy):
    def __init__(self):
        self.order = None
        self.last_operation = "SELL"
        self.status = "DISCONNECTED"
        self.bar_executed = 0
        self.buy_price_close = None
        self.soft_sell = False
        self.hard_sell = False
        self.log("基本策略初始化完成")

    def reset_sell_indicators(self):
        self.soft_sell = False
        self.hard_sell = False
        self.buy_price_close = None

    def notify_data(self, data, status, *args, **kwargs):
        self.status = data._getstatusname(status)
        print(self.status)
        if status == data.LIVE:
            self.log("生产数据 - 交易已就绪")

    def short(self):
        if self.last_operation == "SELL":
            return

        if ENV == DEVELOPMENT:
            self.log("下卖单: $%.2f" % self.data0.close[0])
            return self.sell()

        cash, value = self.broker.get_wallet_balance(COIN_TARGET)
        amount = value*0.99
        self.log("下卖单: $%.2f. 数量 %.6f %s - $%.2f USDT" % (self.data0.close[0],
                                                                       amount, COIN_TARGET, value), True)
        return self.sell(size=amount)

    def long(self):
        if self.last_operation == "BUY":
            return

        self.log("下买单: $%.2f" % self.data0.close[0], True)
        self.buy_price_close = self.data0.close[0]
        price = self.data0.close[0]

        if ENV == DEVELOPMENT:
            return self.buy()

        cash, value = self.broker.get_wallet_balance(COIN_REFER)
        amount = (value / price) * 0.99  # Workaround to avoid precision issues
        self.log("下买单: $%.2f. 数量 %.6f %s. 余额 $%.2f USDT" % (self.data0.close[0],
                                                                              amount, COIN_TARGET, value), True)
        return self.buy(size=amount)

    def notify_order(self, order):
        if order.status in [order.Submitted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            self.log('订单提交成功！')
            self.order = order
            return
        if order.status in [order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            self.log('订单执行成功！')
            self.order = order
            return

        if order.status in [order.Expired]:
            self.log('买入-订单过期', True)

        elif order.status in [order.Completed]:
            if order.isbuy():
                self.last_operation = "BUY"
                self.log(
                    '执行买入:\n 价格: %.2f   成本: %.2f    手续费: %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm), True)
                if ENV == PRODUCTION:
                    print(order.__dict__)

            else:  # Sell
                self.last_operation = "SELL"
                self.reset_sell_indicators()
                self.log('执行卖出:\n 价格: %.2f  成本 : %.2f   手续费: %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm), True)

            # Sentinel to None: new orders allowed
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单被取消或被拒绝执行: 订单状态 %s - %s' % (order.Status[order.status],
                                                                         self.last_operation), True)

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        color = 'green'
        if trade.pnl < 0:
            color = 'red'

        self.log('本次操作收益结算：\n 毛利润 %.2f    净利润 %.2f' % (trade.pnl, trade.pnlcomm),  True, color)

    def log(self, txt, send_telegram=False, color=None):
        plain_txt = txt
        if not DEBUG:
            return

        value = datetime.now()
        if len(self) > 0:
            value = self.data0.datetime.datetime()

        if color:
            txt = colored(txt, color)

        print('[%s] %s' % (value.strftime("%d-%m-%y %H:%M"), txt))
        if send_telegram:
            send_telegram_message(plain_txt)

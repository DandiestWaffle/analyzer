'''
Created on Dec 18, 2011

@author: ppa
'''
import unittest
from datetime import datetime

from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import Session

from analyzer.backtest.trading_center import TradingCenter
from pyStock import Base
from pyStock.models.money import Currency, Money
from pyStock.models import (
    Stock,
    Tick,
    BuyOrder,
    CancelOrderStage,
    Account,
    Broker,
    Owner,
    Exchange,
)


# Connect to the database and create the schema within a transaction
engine = create_engine('sqlite://')
connection = engine.connect()
transaction = connection.begin()
Base.metadata.create_all(connection)


class testTradingCenter(unittest.TestCase):

    def setUp(self):
        self.trans = connection.begin()
        self.session = Session(connection)

        currency = Currency(name='Pesos', code='ARG')
        self.exchange = Exchange(name='Merval', code='MERV', currency=currency)
        self.owner = Owner(name='poor owner')
        self.broker = Broker(name='broker1')
        self.account = Account(owner=self.owner, broker=self.broker)
        self.account.deposit(Money(amount=10000, currency=currency))

    def tearDown(self):
        self.trans.rollback()
        self.session.close()

    def testGetCopyAccounts(self):
        tc=TradingCenter(self.session)
        tc.createAccountWithMetrix(100000, 0)
        tc.createAccountWithMetrix(200000, 0)

        accounts=tc.getCopyAccounts('.*')
        print([str(account) for account in accounts])
        self.assertEquals(2, len(accounts))

    def testGetCopyAccount(self):
        tc=TradingCenter(self.session)
        accountId1=tc.createAccountWithMetrix(100000, 0)

        account=tc.getCopyAccount(accountId1)
        self.assertEquals(100000, account.cash)

    def test_open_orders_by_order_id(self):
        stock=Stock(symbol='symbol', description='a stock', ISIN='US123456789', exchange=self.exchange)
        order1=BuyOrder(account=self.account, security=stock, price=13.2, share=10)
        order2=BuyOrder(account=self.account, security=stock, price=13.25, share=10)
        self.session.add(order1)
        self.session.add(order2)
        self.session.commit()

        tc=TradingCenter(self.session)
        order=tc.open_order_by_id(order1.id)
        self.assertEquals(order1, order)

        order=tc.open_order_by_id(100)
        self.assertEquals(None, order)

    def testGetOpenOrdersBySymbol(self):

        stock=Stock(symbol='symbol', description='a stock', ISIN='US123456789', exchange=self.exchange)
        order1=BuyOrder(account=self.account, security=stock, price=13.2, share=10)
        order2=BuyOrder(account=self.account, security=stock, price=13.25, share=10)
        self.session.add(order1)
        self.session.add(order2)
        self.session.commit()

        tc=TradingCenter(self.session)
        orders=tc.open_orders_by_symbol('symbol')
        self.assertEquals([order1, order2], list(orders))

    def testCancelOrder(self):

        stock=Stock(symbol='symbol', description='a stock', ISIN='US123456789', exchange=self.exchange)
        order1=BuyOrder(account=self.account, security=stock, price=13.2, share=10)
        order2=BuyOrder(account=self.account, security=stock, price=13.25, share=10)

        self.session.add(order1)
        self.session.add(order2)
        self.session.commit()

        tc=TradingCenter(self.session)

        order1.cancel()
        self.assertEquals([order2], tc.open_orders)
        self.assertEquals([order1], tc.closed_orders)
        self.assertEquals(CancelOrderStage, type(order1.current_stage))

        tc.cancelorder(order2)
        self.assertEquals({}, tc.open_orders())
        self.assertEquals([order1, order2], tc.closed_orders)

    def testCancelAllOpenOrders(self):
        security=Stock(symbol='symbol', description='a stock', ISIN='US123456789', exchange=self.exchange)
        order1=BuyOrder(account=self.account, security=security, price=13.2, share=10)
        order2=BuyOrder(account=self.account, security=security, price=13.25, share=10)

        self.session.add(order1)
        self.session.add(order2)
        self.session.commit()

        tc=TradingCenter(self.session)

        tc.cancel_all_open_orders()

        self.assertEquals([], tc.open_order())

    def testConsume(self):
        pass

    def testPostConsume(self):
        pass

    def testCreateAccountWithMetrix(self):
        pass
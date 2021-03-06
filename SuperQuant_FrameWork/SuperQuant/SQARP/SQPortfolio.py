# coding:utf-8

from functools import lru_cache

import pandas as pd

from SuperQuant.SQARP.SQAccount import SQ_Account
from SuperQuant.SQSetting.SQSetting import DATABASE
from SuperQuant.SQUtil.SQLogs import SQ_util_log_info
from SuperQuant.SQUtil.SQRandom import SQ_util_random_with_topic
from SuperQuant.SQSetting.SQParameter import MARKET_TYPE, RUNNING_ENVIRONMENT
# pylint: disable=old-style-class, too-few-public-methods


class SQ_Portfolio(SQ_Account):
    """SQ_Portfolio
    User-->Portfolio-->Account/Strategy

    ::::::::::::::::::::::::::::::::::::::::::::::::::
    ::        :: Portfolio 1 -- Account/Strategy 1  ::
    ::  USER  ::             -- Account/Strategy 2  ::
    ::        :: Portfolio 2 -- Account/Strategy 3  ::
    ::::::::::::::::::::::::::::::::::::::::::::::::::

    SuperQuant 多账户
    以及组合管理

    # 适用 回测/实盘

    # PORTFOLIO应当作为一个视图来处理,这个视图作为一个静态的观察点 可以去衡量风险 观察业绩等等
    @2018/02/26

    ::::::::::::::::::::::::::::::::::::::::::::::::
    ::        ::STRATEGY 1 -- ACCOUNT 1 --{P1,P3} ::
    ::  USER  ::STRATEGY 2 -- ACCOUNT 2 --{P1,P2} ::
    ::        ::STRATEGY 3 -- ACCOUNT 3 --{P2,P3} ::
    ::::::::::::::::::::::::::::::::::::::::::::::::


    PORTFOLIO

    在portfolio中,我们希望通过cookie来控制account_unit

    对于account的指标,要进行风险控制,组合成最优的投资组合的量

    用account的cookie来管理控制account

    portfolio里面的资产主要考虑的是 资金的分配

    @2018/05/16
    fix 通过 cookie 获取 account

    @royburns  1.根据指定的user_cookie创建user； 2.添加对应的测试代码； 3.添加注释
    2018/05/18

    @yutiansut
    修改init_assets ==> init_cash ,删除cash,history在初始的输入

    @2018/11/02

    """

    def __init__(self, user_cookie=None, portfolio_cookie=None, strategy_name=None, init_cash=100000000, sell_available=None, market_type=MARKET_TYPE.STOCK_CN,
                        running_environment=RUNNING_ENVIRONMENT.BACKETEST):
        self.user_cookie = user_cookie
        # self.portfolio_cookie = SQ_util_random_with_topic('Portfolio')
        self.portfolio_cookie = SQ_util_random_with_topic(
            'Portfolio') if portfolio_cookie is None else portfolio_cookie
        self.accounts = {}
        self.strategy_name = strategy_name
        # 和account一样的资产类
        self.init_cash = init_cash
        self.cash = [self.init_cash]
        # 可用资金
        self.sell_available = sell_available
        #self.history = []
        self.time_index = []
        self.commission_coeff = 0.005
        self.market_type = market_type
        self.running_environment = running_environment

        for cookie in self.accounts.keys():
            self.accounts[cookie] = SQ_Account(account_cookie=cookie)

    def __repr__(self):
        return '< SQ_Portfolio {} with {} Accounts >'.format(self.portfolio_cookie, len(self.accounts.keys()))

    @property
    def init_hold_table(self):
        return pd.concat([account.init_hold_with_account for account in list(self.accounts.values())])

    @property
    def init_hold(self):
        return self.init_hold_table.groupby('code').sum()

    @property
    def cash_available(self):
        return self.cash[-1]

    def get_portfolio(self):
        'return the accounts dict'
        return self.accounts

    def add_account(self, account):
        'portfolio add a account/stratetgy'
        if account.account_cookie not in self.accounts.keys():
            if self.cash_available > account.init_cash:
                account.portfolio_cookie = self.portfolio_cookie
                account.user_cookie = self.user_cookie
                self.cash.append(self.cash_available-account.init_cash)
                self.accounts[account.account_cookie] = account
        else:
            pass

    def new_account(self, account_cookie=None, init_cash=1000000, *args, **kwargs):
        """创建一个新的Account

        Keyword Arguments:
            account_cookie {[type]} -- [description] (default: {None})

        Returns:
            [type] -- [description]
        """

        if account_cookie is None:
            if self.cash_available > init_cash:

                temp = SQ_Account(portfolio_cookie=self.portfolio_cookie, init_cash=init_cash,
                                  user_cookie=self.user_cookie, *args, **kwargs)
                if temp.account_cookie not in self.accounts.keys():
                    self.accounts[temp.account_cookie] = temp
                    self.cash.append(self.cash_available-init_cash)
                    return temp

                else:
                    return self.new_account()
        else:
            if self.cash_available > init_cash:
                if account_cookie not in self.accounts.keys():
                    self.accounts[account_cookie] = SQ_Account(portfolio_cookie=self.portfolio_cookie, init_cash=init_cash,
                                                               user_cookie=self.user_cookie, account_cookie=account_cookie, *args, **kwargs)
                    self.cash.append(self.cash_available-init_cash)
                    return self.accounts[account_cookie]
                else:
                    return self.accounts[account_cookie]

    def get_account_by_cookie(self, cookie):
        '''
        'give the account_cookie and return the account/strategy back'
        :param cookie:
        :return: SQ_Account with cookie if in dict
                 None not in list
        '''
        try:
            return self.accounts[cookie]
        except:
            SQ_util_log_info('Can not find this account')
            return None

    def get_account(self, account):
        '''
        check the account whether in the protfolio dict or not
        :param account:  SQ_Account
        :return: SQ_Account if in dict
                 None not in list
        '''
        try:
            return self.accounts[account.account_cookie]
        except:
            SQ_util_log_info(
                'Can not find this account with cookies %s' % account.account_cookie)
            return None

    def cookie_mangement(self):
        pass

    @property
    def table(self):
        return pd.concat([acc.table for acc in self.accounts.values()], axis=1)

    def get_cash(self):
        """拿到整个portfolio的可用资金

        统计每一个时间点的时候的cash总和
        """

        pass

    def pull(self, account_cookie=None, collection=DATABASE.account):
        'pull from the databases'
        if account_cookie is None:
            for item in self.accounts.keys():
                try:
                    message = collection.find_one({'account_cookie': item})
                    SQ_util_log_info('{} sync successfully'.format(item))
                except Exception as e:
                    SQ_util_log_info(
                        '{} sync wrong \\\n wrong info {}'.format(item, e))
                self.accounts[item].from_message(message)

        else:
            try:
                message = collection.find_one(
                    {'account_cookie': account_cookie})
                SQ_util_log_info('{} sync successfully'.format(item))
            except Exception as e:
                SQ_util_log_info(
                    '{} sync wrong \\\n wrong info {}'.format(account_cookie, e))
            self.accounts[account_cookie].from_message(message)

    def push(self, account_cookie=None, collection=DATABASE.account):
        'push to databases'
        message = self.accounts[account_cookie].message
        if account_cookie is None:
            for item in self.accounts.keys():
                try:
                    message = collection.find_one_and_update(
                        {'account_cookie': item})
                    SQ_util_log_info('{} sync successfully'.format(item))
                except Exception as e:
                    SQ_util_log_info(
                        '{} sync wrong \\\n wrong info {}'.format(item, e))
                self.accounts[item].from_message(message)

        else:
            try:
                message = collection.find_one(
                    {'account_cookie': account_cookie})
                SQ_util_log_info('{} sync successfully'.format(item))
            except Exception as e:
                SQ_util_log_info(
                    '{} sync wrong \\\n wrong info {}'.format(account_cookie, e))
            self.accounts[account_cookie].from_message(message)

    @property
    def history(self):
        res = []
        ids = []
        for account in list(self.accounts.values()):
            res.append(account.history)
            ids.append(account.account_cookie)
        return res, ids

    @property
    def history_table(self):
        return pd.concat([account.history_table for account in list(self.accounts.values())])


class SQ_PortfolioView():
    """
    对于Portfolio而言,一切都是基于内部的account的信息的变更而变更的

    Portfolio不应该有过多可以修改的部分(作为一个view存在)
    """

    def __init__(self, account_list):
        """
                    ||portfolio||
        ||acc1_cookie--acc1||acc2-cookie--acc2||...||


        ||cash||assets||hold||history||trade_index||


        ||Risk_analysis||Performace_analysis||
        """
        self.account_cookie = SQ_util_random_with_topic('PVIEW', 3)
        self.account_list = dict(
            zip([account.account_cookie for account in account_list], account_list))
        self.portfolio_cookie = SQ_util_random_with_topic('Portfolio')
        self.user_cookie = None
        self.market_type = account_list[0].market_type

    def __repr__(self):
        return '< SQ_PortfolioVIEW {} with {} Accounts >'.format(self.account_cookie, len(self.accounts))

    @property
    def contained_cookie(self):
        """

        CHANGED in 1.0.38
        2018-05-23

        portfolio-view 含有的account_cookie使用contained_cookie来承载

        原先的account_cookie 使用 PVIEW_xxx 代替
        """
        return [account.account_cookie for account in self.accounts]

    @property
    def accounts(self):
        """
        return all accounts inside the portfolio view
        """
        return list(self.account_list.values())

    @property
    def start_date(self):
        return str(pd.to_datetime(pd.Series([account.start_date for account in self.accounts])).min())[0:10]

    @property
    def end_date(self):
        return str(pd.to_datetime(pd.Series([account.end_date for account in self.accounts])).max())[0:10]

    @property
    def code(self):
        return pd.concat([pd.Series(account.code) for account in self.accounts]).drop_duplicates().tolist()

    @property
    def init_cash(self):
        return sum([account.init_cash for account in self.accounts])

    @property
    def init_hold(self):
        return sum([account.init_hold for account in self.accounts])

    @property
    def init_assets(self):
        """初始化账户资产

        Returns:
            dict -- 2keys-cash,hold
        """

        return {
            'cash': self.init_cash,
            'hold': self.init_hold.to_dict()
        }

    @property
    def daily_cash(self):
        # res = pd.DataFrame(sum([account.daily_cash.set_index(
        #     'datetime').cash for account in self.accounts]))
        # res = res.assign(date=res.index)
        # res.date = res.date.apply(lambda x: str(x)[0:10])

        return pd.concat([item.daily_cash for item in self.accounts]).groupby(level=0).sum()\
            .assign(account_cookie=self.account_cookie).reset_index().set_index(['date', 'account_cookie'], drop=False)

    @property
    def daily_hold(self):
        return pd.concat([account.daily_hold.xs(account.account_cookie, level=1) for account in self.accounts])\
            .groupby('date').sum().assign(account_cookie=self.account_cookie)\
            .reset_index().set_index(['date', 'account_cookie'])

    @property
    def trade(self):
        return pd.concat([item.trade for item in self.accounts]).groupby(level=0).sum()\
            .assign(account_cookie=self.account_cookie).reset_index().set_index(['datetime', 'account_cookie'])

    @property
    def history_table(self):
        return pd.concat([item.history_table for item in self.accounts]).sort_index()

    @property
    def trade_day(self):
        return pd.concat([pd.Series(item.trade_day) for item in self.accounts]).drop_duplicates().sort_values().tolist()

    @property
    def trade_range(self):
        return pd.concat([pd.Series(item.trade_range) for item in self.accounts]).drop_duplicates().sort_values().tolist()


# coding:utf-8


import pandas as pd

from SuperQuant.SQARP.SQPortfolio import SQ_Portfolio
from SuperQuant.SQUtil.SQLogs import SQ_util_log_info
from SuperQuant.SQUtil.SQRandom import SQ_util_random_with_topic
from SuperQuant.SQSetting.SQSetting import SQ_Setting


class SQ_User():
    """SQ_User
    User-->Portfolio-->Account/Strategy

    :::::::::::::::::::::::::::::::::::::::::::::::::
    ::        :: Portfolio 1 -- Account/Strategy 1 ::
    ::  USER  ::             -- Account/Strategy 2 ::
    ::        :: Portfolio 2 -- Account/Strategy 3 ::
    :::::::::::::::::::::::::::::::::::::::::::::::::

    :: 需要增加对于SQ_USER的支持

    USER作为一个单位实体, 可以自由创建 组合Portfolio (需要被记录),修改 组合Portfolio

    @yutiansut
    2018/05/08

    @jerryw  添加注释，和 🛠todo list
    2018/05/16

    @royburns  1.根据指定的user_cookie创建user； 2.添加对应的测试代码； 3.添加注释
    2018/05/18
    """

    def __init__(self, user_cookie=None):
        '''
            随机初始化 user_cookie 的值
            Acc+4数字id+4位大小写随机
        '''
        self.setting = SQ_Setting()
        self.portfolio_list = {}

        self.user_cookie = SQ_util_random_with_topic(
            'USER') if user_cookie is None else user_cookie

    def __repr__(self):
        return '< SQ_USER {} with {} portfolio: {} >'.format(self.user_cookie, len(self.portfolio_list.keys()), self.portfolio_list)

    @property
    def table(self):
        return pd.concat([po.table for po in self.portfolio_list.values()], axis=1)

    def client(self):
        '''
        'user.client to connect database'
        :return: pymongo.MongoClient 数据库连接
        '''
        return self.setting.client

    def connect_database(self, ip='127.0.0.1', port=27017):
        '''
        'connect is also a way to change database from IP_A to IP_B
        :param ip: 连接mongodb ip
        :param port: 连接mongodb 端口
        :return: None
        '''
        self.setting.change(ip, port)

    def login(self, user_name, password):
        '''
        login to a database
        🛠todo： fix 返回 是否成功
        :param user_name: 连接 mongodb 的用户名
        :param password:  连接 mongodb 的密码
        :return: Boolean 是否成功连接
        '''
        if self.setting.login(user_name, password):
            SQ_util_log_info('SUCCESS')
            return True
        else:
            SQ_util_log_info('FAILD')
            return False

    def new_portfolio(self, portfolio_cookie=None):
        '''
            根据 self.user_cookie 创建一个 portfolio
        :return:
             如果存在 返回 新建的 SQ_Portfolio
             如果已经存在 不返回 None
        '''
        _portfolio = SQ_Portfolio(
            user_cookie=self.user_cookie, portfolio_cookie=portfolio_cookie)
        if _portfolio.portfolio_cookie not in self.portfolio_list.keys():
            self.portfolio_list[_portfolio.portfolio_cookie] = _portfolio
            return _portfolio
        else:
            print(" prortfolio with user_cookie ",
                  self.user_cookie, " already exist!!")

    def get_portfolio(self, portfolio):
        '''
        'get a portfolio'
        从 portfolio_list dict字典中 根据 portfolio key 获取
        :param portfolio: SQ_Portfolio类型
        :return: SQ_Portfolio类型
        '''
        # return self.portfolio_list[portfolio]
        # fix here use cookie as key to find value in dict
        return self.portfolio_list[portfolio.portfolio_cookie]

    def get_portfolio_by_cookie(self, portfolio_cookie):
        '''
        'get a portfolio'
        从 portfolio_list dict字典中 根据 portfolio key 获取
        :param portfolio: porfolio_cookie string
        :return: SQ_Portfolio类型
        '''
        return self.portfolio_list[portfolio_cookie]

    def generate_simpleaccount(self):
        """make a simple account with a easier way
        如果当前user中没有创建portfolio, 则创建一个portfolio,并用此portfolio创建一个account
        如果已有一个或多个portfolio,则使用第一个portfolio来创建一个account
        """
        if len(self.portfolio_list.keys()) < 1:
            po = self.new_portfolio()
        else:
            po = list(self.portfolio_list.values())[0]
        ac = po.new_account()
        return ac, po

    def register_account(self, account, portfolio_cookie=None):
        '''
        注册一个account到portfolio组合中
        account 也可以是一个策略类，实现其 on_bar 方法
        :param account: 被注册的account
        :return:
        '''
        # 查找 portfolio
        if len(self.portfolio_list.keys()) < 1:
            po = self.new_portfolio()
        elif portfolio_cookie is not None:
            po = self.portfolio_list[portfolio_cookie]
        else:
            po = list(self.portfolio_list.values())[0]
        # 把account 添加到 portfolio中去
        po.add_account(account)
        return (po, account)

    def save(self):
        """
        将SQ_USER的信息存入数据库
        """
        pass


if __name__ == '__main__':

    # 测试不对
    user = SQ_User(user_cookie='user_admin')
    folio = user.new_portfolio('folio_admin')
    ac1 = user.get_portfolio(folio).new_account('account_admin')

    print(user)
    print(user.get_portfolio(folio))
    print(user.get_portfolio(folio).get_account(ac1))


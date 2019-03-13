# coding:utf-8
#

from copy import deepcopy, copy

import pandas as pd

from SuperQuant.SQFetch.SQTdx import SQ_fetch_get_stock_realtime


class SQ_DataStruct_Stock_block():
    def __init__(self, DataFrame):
        self.data = DataFrame
        assert isinstance(DataFrame.index, pd.MultiIndex)
        self.index = self.data.index.remove_unused_levels()

    def __repr__(self):
        return '< SQ_DataStruct_Stock_Block >'

    def __call__(self):
        """调用直接返回内部的数据

        Returns:
            [type] -- [description]
        """

        return self.data

    def new(self, data):
        """通过data新建一个stock_block

        Arguments:
            data {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        temp = copy(self)
        temp.__init__(data)
        return temp

    @property
    def len(self):
        """返回DataStruct的长度

        Returns:
            [type] -- [description]
        """

        return len(self.data)

    @property
    def block_name(self):
        """返回所有的板块名

        Returns:
            [type] -- [description]
        """

        return self.index.levels[0].tolist()

    @property
    def code(self):
        """返回唯一的证券代码

        Returns:
            [type] -- [description]
        """

        return self.index.levels[1].tolist()

    @property
    def view_code(self):
        """按股票排列的查看blockname的视图

        Returns:
            [type] -- [description]
        """

        return self.data.groupby(level=1).apply(lambda x: [item for item in x.index.remove_unused_levels().levels[0]])

    @property
    def view_block(self):
        """按版块排列查看的code的视图

        Returns:
            [type] -- [description]
        """

        return self.data.groupby(level=0).apply(lambda x: [item for item in x.index.remove_unused_levels().levels[1]])

    def show(self):
        """展示DataStruct

        Returns:
            dataframe -- [description]
        """

        return self.data

    def get_code(self, code):
        """getcode 获取某一只股票的板块

        Arguments:
            code {str} -- 股票代码

        Returns:
            DataStruct -- [description]
        """
        # code= [code] if isinstance(code,str) else
        return self.new(self.data.loc[(slice(None), code), :])

    def get_block(self, block_name):
        """getblock 获取板块, block_name是list或者是单个str

        Arguments:
            block_name {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        # block_name = [block_name] if isinstance(
        #     block_name, str) else block_name
        # return SQ_DataStruct_Stock_block(self.data[self.data.blockname.apply(lambda x: x in block_name)])

        return self.new(self.data.loc[(block_name, slice(None)), :])

    def get_both_code(self, code):
        """get_both_code 获取几个股票相同的版块

        Arguments:
            code {[type]} -- [description]

        Returns:
            [type] -- [description]
        """

        return self.new(self.data.loc[(slice(None), code), :])

    def get_both_block(self, block_name):
        pass
    # def getdtype(self, dtype):
    #     """getdtype

    #     Arguments:
    #         dtype {str} -- gn-概念/dy-地域/fg-风格/zs-指数

    #     Returns:
    #         [type] -- [description]
    #     """

    #     return SQ_DataStruct_Stock_block(self.data[self.data['type'] == dtype])

    # def get_price(self, _block_name=None):
    #     """get_price

    #     Keyword Arguments:
    #         _block_name {[type]} -- [description] (default: {None})

    #     Returns:
    #         [type] -- [description]
    #     """

    #     if _block_name is not None:
    #         try:
    #             code = self.data[self.data['blockname']
    #                              == _block_name].code.unique().tolist()
    #             # try to get a datastruct package of lastest price
    #             return SQ_fetch_get_stock_realtime(code)

    #         except:
    #             return "Wrong Block Name! Please Check"
    #     else:
    #         code = self.data.code.unique().tolist()
    #         return SQ_fetch_get_stock_realtime(code)


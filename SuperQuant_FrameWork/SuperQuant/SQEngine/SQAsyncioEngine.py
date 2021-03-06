import asyncio
import datetime
import threading
import time
import traceback

import future

from SUPERQUANT.SQFetch.SQQuery_Async import SQ_fetch_stock_day


"""SuperQuant 异步引擎


"""


class SQAsync():
    def __init__(self):
        self.event_loop = asyncio.new_event_loop()
        self.elthread = threading.Thread(target=self.event_loop.run_forever)

        self.elthread.setDaemon(True)
        self.elthread.start()

    def run(self, func, callback, *args, **kwargs):
        # schedule a task

        return self.submit(func(*args, **kwargs)).add_done_callback(callback)

    def submit(self, coro):
        """

        future = asyncio.run_coroutine_threadsafe(coro, loop)

        Arguments:
            coro {[type]} -- [description]

        Returns:
            Future -- [description]
        """

        return asyncio.run_coroutine_threadsafe(coro, self.event_loop)
        #self.event_loop.call_soon_threadsafe()


def callback(result):
    r = result
    print(r.result())
    print(type(r))
    print(datetime.datetime.now()-time)
    return r


"""

run_until_complete 

"""


if __name__ == '__main__':
    time = datetime.datetime.now()
    SQE = SQAsync()

    print(datetime.datetime.now()-time)
    SQE.run(SQ_fetch_stock_day, callback,
            '000001', '1990-01-01', '2018-01-31')
    SQE.run(SQ_fetch_stock_day, callback,
            '000002', '1990-01-01', '2018-01-31')
    SQE.run(SQ_fetch_stock_day, callback,
            '000007', '1990-01-01', '2018-01-31')
    SQE.run(SQ_fetch_stock_day, callback,
            '000004', '1990-01-01', '2018-01-31')
    SQE.run(SQ_fetch_stock_day, callback,
            '000005', '1990-01-01', '2018-01-31')
    print(datetime.datetime.now()-time)
    # import SUPERQUANT as SQ
    # time=datetime.datetime.now()
    # r=SQ.SQ_fetch_stock_day('000001','1990-01-01', '2018-01-31')
    # print(len(r))
    # #print(datetime.datetime.now()-time)
    # r=SQ.SQ_fetch_stock_day('000002','1990-01-01', '2018-01-31')
    # print(len(r))
    # r=SQ.SQ_fetch_stock_day('000007','1990-01-01', '2018-01-31')
    # print(len(r))
    # r=SQ.SQ_fetch_stock_day('000004','1990-01-01', '2018-01-31')
    # print(len(r))
    # r=SQ.SQ_fetch_stock_day('000005','1990-01-01', '2018-01-31')
    # print(len(r))
    # print(datetime.datetime.now()-time)


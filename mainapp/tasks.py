from celery import shared_task
from stockproject.celery import app
from yahoo_fin.stock_info import *
from threading import Thread
import queue
from channels.layers import get_channel_layer
import asyncio
import simplejson as json
@shared_task(bind = True)
def update_stock(self, stockpickerr):
    data = {}
    available_stocks = tickers_nifty50()
    for i in stockpickerr:
        if i in available_stocks:
            pass
        else:
            stockpickerr.remove(i)
        
    n_threads = len(stockpickerr)
    thread_list = []
    que = queue.Queue()

    # for i in stockpickerr:
    #     details = get_quote_table(i)
    #     data.update({i: details})
    # details2 = get_quote_table("RELIANCE.NS")

    for i in range(n_threads):
        thread = Thread(target = lambda q, arg1: q.put({stockpickerr[i]: json.loads(json.dumps(get_quote_table(arg1), ignore_nan = True))}), args = (que, stockpickerr[i]))
        thread_list.append(thread)
        thread_list[i].start()

    for thread in thread_list:
        thread.join()

    while not que.empty():
        result = que.get()
        data.update(result)

    #send data to group

    # channel_layer = get_channel_layer()
    # loop = asyncio.new_event_loop()
    
    # asyncio.set_event_loop(loop)
 
    # loop.run_until_complete(channel_layer.group_send("stock_track",{
    #     'type' : 'send_stock_update',
    #     'message': data,
    # }))

       #send data to group

    channel_layer = get_channel_layer()

    async def send_data():
        await channel_layer.group_send("Stock_track",{
            'type' : 'send_stock_update',
            'message': data,
        })

    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_data())

    return 'Done'

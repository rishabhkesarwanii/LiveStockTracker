from threading import Thread
from django.http import HttpResponse
from django.shortcuts import render
from yahoo_fin.stock_info import *
import time
import queue
from asgiref.sync import sync_to_async

# Create your views here.

def stockPicker(request):
    stock_picker = tickers_nifty50()
    # print(stock_picker)
    return render(request, 'mainapp/stockpicker.html',{'stockpicker':stock_picker})

@sync_to_async
def checkAuthenticated(request):
    if not request.user.is_authenticated:
        return False
    else:
        return True

async def stockTracker(request):
    is_loginned = await checkAuthenticated(request)
    if not is_loginned:
        return HttpResponse("Login First")
    
    stockpickerr = request.GET.getlist('stockpicker')
    # for i in stockpickerr:
    #     print('AAAAAAAAAAAAAAAAAAAAAAAAAAA')
    #     print(i)
    # print(stockpickerr)
    data = {}
    available_stocks = tickers_nifty50()
    for i in stockpickerr:
        if i in available_stocks:
            pass
        else:
            return HttpResponse("Error")
        
    n_threads = len(stockpickerr)
    thread_list = []
    que = queue.Queue()

    start = time.time()
    # for i in stockpickerr:
    #     details = get_quote_table(i)
    #     data.update({i: details})
    # details2 = get_quote_table("RELIANCE.NS")

    for i in range(n_threads):
        thread = Thread(target = lambda q, arg1: q.put({stockpickerr[i]: get_quote_table(arg1)}), args = (que, stockpickerr[i]))
        thread_list.append(thread)
        thread_list[i].start()

    for thread in thread_list:
        thread.join()

    while not que.empty():
        result = que.get()
        data.update(result)


    end = time.time()
    time_taken = end - start
    print(time_taken)
    print(data)
    return render(request, 'mainapp/stocktracker.html',{'data': data, 'room_name': 'track'})


import threading
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from queue import Empty as QueueEmpty
from typing import Any, Callable, Optional
from ...utils.logger_module import logger 


LOCK = threading.Lock()

def create_lst_of(n:int, element={'index': None, 'driver': None, 'list': []}):
    return [element for _ in range(n)]

def split_list(input_list:list, num:int=1):
    # Create a list of empty lists
    result = [[] for _ in range(num)]
    # Iterate through the input list and distribute elements into sublists
    for i, val in enumerate(input_list):
        result[i % num].append(val)
    return result

def split_to_dict(source:Any, num:int=1) -> dict[int, Any]:
    def _list(_list, num:int=1)->dict[int, Any]:
        if len(_list) < num:
            num=len(_list)
        # Create a dictionary with empty lists for each key
        result = {i: [] for i in range(num)}
        # Iterate through the input list and distribute elements into the sublists
        for i, val in enumerate(_list):
            result[i % num].append(val)
        return result
    if isinstance(source, (list,tuple)):
        return _list(source, num)
    if isinstance(source, dict):
        return {k: dict(v) for k, v in _list(source.items(), num).items()}
    raise TypeError("source must be type list, tuple or dictionary")

def split_to_queue(source: Any) -> Queue:
    """Populate a Queue with items from source."""
    q = Queue()
    if isinstance(source, (list, tuple)):
        for item in source:
            q.put(item)
    elif isinstance(source, dict):
        for item in source.items():
            q.put(item)
    else:
        raise TypeError("source must be type list, tuple, or dictionary")
    return q

def worker(queue: Queue, call_def: Callable, args: tuple[Any], kwargs: dict, index: int):
    """Thread worker function to process items in the queue."""
    while not queue.empty():
        try:
            # item = queue.get_nowait()  # Non-blocking get
            # logger.info(f"{index}: Remaining items: {queue.qsize()}")
            # logger.info(f"{index}: Processing item: {item}")

            item = queue.get()  # Blocking get

            # Set up kwargs for the function call
            if isinstance(item, tuple):  # For dictionaries, item will be (key, value)
                kwargs.update({'source': {item[0]: item[1]}, 'index': index})
            else:
                kwargs.update({'source': [item], 'index': index})
            
            # Execute the provided function
            call_def(*args, **kwargs)
            queue.task_done()  # Ensure this item is marked as done
            logger.info(f"{index}: Remaining items: {queue.qsize()}")
            logger.info(f"{index}: Processing item: {item}")
        except QueueEmpty:
            logger.info("{index}: No remaining items.")
            break  # Exit if the queue is empty

def multithreading(call_def:Callable, source:Any=None, threads:int=1, args:Optional[tuple[Any]]=None, kwargs:Optional[dict]=None):
    if args is None: args = tuple()
    if kwargs is None: kwargs = {}
    with ThreadPoolExecutor(max_workers=threads) as executor:
        match source:
            case None:
                futures = [
                    executor.submit(call_def, *args, index=index, **kwargs)  
                    for index in range(threads)
                ]
            case list() | tuple() | dict():
                # for index in range(threads):
                #     executor.submit(worker, q, call_def, args, kwargs, index)
                # futures = [
                #     executor.submit(call_def, *args, source=splitted_source, index=index, **kwargs)  
                #     for index, splitted_source in split_to_dict(source, threads).items()
                # ]
                q = split_to_queue(source)
                futures = [
                    executor.submit(worker, q, call_def, args, kwargs, index)
                    for index in range(threads)
                ]
            case _:
                futures = [
                    executor.submit(call_def, *args, source=source, index=index, **kwargs) 
                    for index in range(threads)
                ] 
    for future in futures:
        future.result()

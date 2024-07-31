"""
Utility functions for parallel computing
"""
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import Callable, List, Type


def parallel_computation_in_batches_with_return(func: Callable, input_tables: List[list],
                                         executor_type: Type[
                                             concurrent.futures.Executor] = ThreadPoolExecutor,
                                         batch_size: int = 1, num_workers: int = 4, **kwargs):
    """
    Runs a function in parallel using batches of input data.

    :param func: Function to be called.
    :param input_tables: List of lists, tables of input data. The order of the arguments should be the same as the function.
    :param executor_type: Executor class, type of parallel execution (ThreadPoolExecutor or ProcessPoolExecutor).
    :param batch_size: Int, the size of the batch for each worker.
    :param num_workers: Int, the number of workers.
    :param kwargs: Additional keyword arguments to pass to the function.
    """
    results = []
    input_batches = split_into_batches(input_tables, batch_size=batch_size)
    with executor_type(max_workers=num_workers) as executor:
        futures = [executor.submit(run_func_in_batch_with_list_input_wrapper, func, input_batch, **kwargs)
                   for input_batch in input_batches]
        for future in concurrent.futures.as_completed(futures):
            try:
                results.extend(future.result())
            except Exception as e:
                print(f"Task generated an exception: {e}")

    return results


def split_into_batches(input_table: List[list], batch_size: int) -> List[List[list]]:
    """
    Splits multiple lists of data into batches of a specified size.

    :param input_table: List of lists, data to be split into batches.
    :param batch_size: Int, size of each batch.
    :return: List of batches.
    """
    num_items = len(input_table)
    if num_items < batch_size:
        return [input_table]

    return [input_table[i:i + batch_size] for i in range(0, num_items, batch_size)]


def run_func_in_batch_with_list_input_wrapper(func: Callable, args_list_in_batches: List[list], **kwargs):
    """
    Wrapper to call a function with arguments from a list of batches.

    :param func: Function to be called.
    :param args_list_in_batches: List of batches (list) of arguments to be passed to the function.
    :param kwargs: Additional keyword arguments to pass to the function.
    """
    results = []
    for args_list in args_list_in_batches:
        results.append(func(*args_list, **kwargs))

    return results


if __name__ == "__main__":
    # Example usage
    def add(a, b):
        return a + b

    input_data = [[1, 2], [3, 4], [5, 6], [7, 8]]
    results = parallel_computation_in_batches_with_return(func=add, input_tables=input_data, batch_size=4,num_workers=2)
    print(results)
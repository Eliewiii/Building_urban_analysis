"""

"""

import concurrent.futures


def append_1(list_to_append):
    list_to_append.append(1)


def run_func_in_parallel_with_concurrent(func, num_workers, arg_list):
    # with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(func, arg) for arg in arg_list]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()  # Ensure any exceptions are raised
            except Exception as e:
                print(f"Task generated an exception: {e}")


if __name__ == "__main__":
    in_list = [[] for element in range(10)]
    print(in_list)
    num_workers = 4  # Adjust this based on your system's capabilities

    run_func_in_parallel_with_concurrent(func=append_1,arg_list=in_list,num_workers=num_workers)
    print(in_list)

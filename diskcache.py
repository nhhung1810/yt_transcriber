import json
import os
from typing import Dict, List, Tuple

STORAGE_FILE = "disk_cache.json"


def load_cache_file():
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, "r") as f:
            return json.load(f)

    return {}


def save_cache_file(cache_data):
    with open(STORAGE_FILE, "w") as f:
        json.dump(cache_data, f)
        pass


# Structure of the cache file:
# {
#     "function_name": {"arg1_value": {"arg2_value": { '0_final_value' : "the actual result"}}},
# }
# As the result is stored in json format, every data must be serializable. Currently only support string data
# The order of argument will be sorted using the argument name.
# The final value will be stored in the key '0_final_value'.
# The leading '0_' is used to ensure that there is no clash with the kwargs list.


def recursive_cache_hit(
    cache_data: Dict[str, str], function_name: str, kw_list: List[Tuple[str, str]]
) -> str | None:
    cache_root = cache_data.get(function_name, None)
    if cache_root is None:
        return None

    # ascending sort
    kw_list = sorted(kw_list, key=lambda x: x[0])
    for kw in kw_list:
        cache_root = cache_root.get(kw[1], None)
        if cache_root == None:
            return None

    return cache_root.get("0_final_value", None)


def recursive_cache_write(
    cache_data: Dict[str, str],
    function_name: str,
    kw_list: List[Tuple[str, str]],
    value: str,
):
    if function_name not in cache_data:
        cache_data[function_name] = dict()
        pass

    cache_root = cache_data[function_name]

    kw_list = sorted(kw_list, key=lambda x: x[0])
    for kw in kw_list:
        if kw[1] not in cache_root:
            cache_root[kw[1]] = dict()
            pass

        cache_root = cache_root[kw[1]]
        pass

    cache_root["0_final_value"] = value
    pass


def cache_decorator(func):
    # To use the cache, function name and only keywords arguments will be considered.
    # Therefore, if there are any positional arguments, the cache will be omitted
    def wrapper(*args, **kwargs):
        cache_data = load_cache_file()
        if len(args) != 0:
            print("Function contain positional arguments. Cache will be omitted.")
            return func(*args, **kwargs)

        # Check if the function result is already cached
        cache_value = recursive_cache_hit(
            cache_data, func.__name__, list(kwargs.items())
        )
        if cache_value:
            return cache_value

        try:
            result = func(**kwargs)
            # Write cache
            recursive_cache_write(
                cache_data, func.__name__, list(kwargs.items()), result
            )
            # Save the result to cache file
            save_cache_file(cache_data)
            return result
        except Exception as e:
            print(e)
            print("Exception occurred. It's possible that the cache is not written.")
            return None

    return wrapper

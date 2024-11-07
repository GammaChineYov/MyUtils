from functools import wraps
import pickle
import os

def persistent_cache(cache_file):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 创建缓存文件路径
            cache_key = pickle.dumps((args, frozenset(kwargs.items())))  # 使用参数作为缓存键
            cache_path = f"{cache_file}.pkl"

            # 尝试读取缓存
            if os.path.exists(cache_path):
                with open(cache_path, 'rb') as f:
                    cache = pickle.load(f)
                if cache_key in cache:
                    print(f"加载缓存: {func.__name__}({args}, {kwargs})")
                    return cache[cache_key]

            # 调用原始函数并缓存结果
            result = func(*args, **kwargs)

            # 写入缓存
            with open(cache_path, 'ab+') as f:
                if os.path.getsize(cache_path) == 0:  # 创建空的字典用于缓存
                    cache = {}
                else:
                    f.seek(0)
                    cache = pickle.load(f)
                cache[cache_key] = result
                f.seek(0)
                pickle.dump(cache, f)

            return result
        return wrapper
    return decorator
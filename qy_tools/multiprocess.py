import os
import multiprocessing 
from tqdm import tqdm

def _process_wrapper(function, arg, error_files):
    """处理单个任务的包装函数，可以被pickle"""
    try:
        return function(arg)
    except Exception as e:
        error_files.append(arg)
        print(f"Error processing file: {arg}")
        return None

def multipool(function, args, processes=40):
    """多进程处理函数，简单记录出错的图片路径"""

    manager = multiprocessing.Manager()
    error_files = manager.list()  # 共享列表，用于进程间通信
    
    pool = multiprocessing.Pool(processes=processes)
    with tqdm(total=len(args)) as pbar:
        # 使用partial固定function和error_files参数
        from functools import partial
        wrapper = partial(_process_wrapper, function, error_files=error_files)
        
        for result in pool.imap_unordered(wrapper, args):
            pbar.update(1)
    pool.close()
    pool.join()
    
    if error_files:
        print(f"\nTotal {len(error_files)} files failed:")
        for f in error_files:
            print(f"  - {f}")

def multipool_path_args(image_paths,dir_list,join=True):
    
    """将图片路径和文件夹路径组合成多进程的参数
    Args:
        image_paths: 图片路径列表
        dir_list: 文件夹路径列表
        join: 是否将文件夹路径和图片路径组合
    Returns:
        args: 多进程参数列表
    """
    args = []
    for image_path in image_paths:
        arg = []
        for dir_item in dir_list:
            if join:
                arg.append(os.path.join(dir_item, image_path))
            else:
                if len(arg) == 0:
                    arg.append(image_path)
                arg.append(dir_item)
        args.append(tuple(arg))


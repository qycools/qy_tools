import os
import numpy as np
from PIL import Image
import multiprocessing
from tqdm import tqdm
import time
import torch
def process_image(path):
    """读取图片并返回RGB三个通道的像素值（flatten）"""
    img = Image.open(path).convert('RGB')  # 确保是RGB三通道
    img_np = np.array(img)
    R = img_np[:, :, 0].flatten()
    G = img_np[:, :, 1].flatten()
    B = img_np[:, :, 2].flatten()
    return R, G, B

def compute_rgb_stats_gpu(image_folder, device=None, batch_size=1):
    """GPU加速版本计算RGB均值和标准差
    
    Args:
        image_folder: 图片文件夹路径
        device: torch设备 (默认自动检测)
        batch_size: 批处理大小 (默认1)
    """
    if device is None:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # 获取所有图片路径
    image_paths = [os.path.join(image_folder, f) for f in os.listdir(image_folder)
                   if f.lower().endswith(('.png'))]
    
    # 预分配GPU内存
    R_all = torch.empty(0, dtype=torch.float32, device=device)
    G_all = torch.empty(0, dtype=torch.float32, device=device)
    B_all = torch.empty(0, dtype=torch.float32, device=device)
    
    # 分批处理避免内存溢出
    for i in tqdm(range(0, len(image_paths), batch_size)):
        batch_paths = image_paths[i:i+batch_size]
        batch_results = []
        
        # 处理当前批次
        for path in batch_paths:
            img = Image.open(path).convert('RGB')
            img_tensor = torch.from_numpy(np.array(img)).float().to(device)
            R, G, B = img_tensor[:, :, 0].flatten(), img_tensor[:, :, 1].flatten(), img_tensor[:, :, 2].flatten()
            batch_results.append((R, G, B))
        
        # 合并当前批次结果
        R_batch = torch.concatenate([res[0] for res in batch_results])
        G_batch = torch.concatenate([res[1] for res in batch_results])
        B_batch = torch.concatenate([res[2] for res in batch_results])
        
        # 更新总结果
        R_all = torch.concatenate([R_all, R_batch])
        G_all = torch.concatenate([G_all, G_batch])
        B_all = torch.concatenate([B_all, B_batch])
    
    # 计算均值和标准差 (保持精度)
    with torch.no_grad():
        R_mean, G_mean, B_mean = torch.mean(R_all), torch.mean(G_all), torch.mean(B_all)
        R_std, G_std, B_std = torch.std(R_all), torch.std(G_all), torch.std(B_all)
    
    # 打印结果
    print(f"R mean: {R_mean.cpu().numpy():.2f}, std: {R_std.cpu().numpy():.2f}")
    print(f"G mean: {G_mean.cpu().numpy():.2f}, std: {G_std.cpu().numpy():.2f}")
    print(f"B mean: {B_mean.cpu().numpy():.2f}, std: {B_std.cpu().numpy():.2f}")

def compute_rgb_stats(image_folder, num_processes=8):
    # 获取所有图片路径
    image_paths = [os.path.join(image_folder, f) for f in os.listdir(image_folder)
                   if f.lower().endswith(('.png'))]

    # 创建进程池并并行处理
    with multiprocessing.Pool(processes=num_processes) as pool:
        results = list(tqdm(pool.imap_unordered(process_image, image_paths), total=len(image_paths)))

    # 合并所有结果
    R_all = np.concatenate([res[0] for res in results])
    G_all = np.concatenate([res[1] for res in results])
    B_all = np.concatenate([res[2] for res in results])

    # 计算均值和标准差
    R_mean, G_mean, B_mean = np.mean(R_all), np.mean(G_all), np.mean(B_all)
    R_std, G_std, B_std = np.std(R_all), np.std(G_all), np.std(B_all)

    # 打印结果
    print(f"R mean: {R_mean:.2f}, std: {R_std:.2f}")
    print(f"G mean: {G_mean:.2f}, std: {G_std:.2f}")
    print(f"B mean: {B_mean:.2f}, std: {B_std:.2f}")

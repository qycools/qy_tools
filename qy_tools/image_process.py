import os
from PIL import Image
import numpy as np

binary_palette = [255,255,255,255,0,0,0,0,0]

def combine_images(image_paths:list, image_hw:tuple,output_path, grid_hw:tuple,blend_index=None,blend_alpha=0.25):
    """将多张图片合并为指定网格布局的图片
    
    Args:
        image_paths (list): 图片路径列表
        image_hw (tuple): 单张图片的(宽度,高度)元组，必须包含2个正整数
        output_path (str): 输出图片保存路径
        grid_hw (tuple): 网格布局的(行数,列数)元组，必须包含2个正整数
        blend_index (list, optional): 需要混合的图片索引列表，格式为[(源图1索引,源图2索引),...]
        blend_alpha (float, optional): 混合透明度(0-1之间)，默认0.25
        
    Returns:
        None: 直接保存合并后的图片到output_path
        
    Raises:
        TypeError: 当参数类型不符合要求时
        ValueError: 当参数值不符合要求时
    """
    # 参数类型检查
    if not isinstance(image_hw, tuple) or len(image_hw) != 2 or \
       not all(isinstance(x, int) and x > 0 for x in image_hw):
        raise TypeError("image_hw must be a tuple of 2 positive integers (width, height)")
        
    if not isinstance(grid_hw, tuple) or len(grid_hw) != 2 or \
       not all(isinstance(x, int) and x > 0 for x in grid_hw):
        raise TypeError("grid_hw must be a tuple of 2 positive integers (rows, cols)")
        
    if not isinstance(blend_alpha, (int, float)) or not 0 <= blend_alpha <= 1:
        raise ValueError("blend_alpha must be a float between 0 and 1")
    images = []

    for path in image_paths:
        img = Image.open(path)
        if img.mode == 'P':
            img = img.convert('RGB')
        images.append(img)
    
    width, height = image_hw

    height_num, width_num = grid_hw
    grid_width = width * width_num
    grid_height = height * height_num
    grid = Image.new('RGB', (grid_width, grid_height))

    if blend_index is None:

        blend_index=[]
        for i in range(height_num* width_num):
            blend_index.append((i,-1))

    for i in range(height_num* width_num):
        if i < len(blend_index):
            x = (i % width_num) * width
            y = (i // width_num) * height
            
                grid.paste(images[blend_index[i][0]], (x, y))
            else:
                blend_img = Image.blend(images[blend_index[i][0]], images[blend_index[i][1]], blend_alpha)
                grid.paste(blend_img, (x, y))

    grid.save(output_path)


def array2img(array, save_path,palette=binary_palette):
    img = Image.fromarray(array.astype(np.uint8),"P")
    img.putpalette(palette)
    img.save(save_path)

def crop_img(image_path,save_dir,crop_size=1024,stride=512):
    '''
    将图片裁剪成指定大小并保存到指定目录
    Args:
        image_path (str): 图片路径
        save_dir (str): 保存目录
        crop_size (int, optional): 裁剪区域大小. Defaults to 1024.
        stride (int, optional): 移动步长. Defaults to 512.
    '''
    baseneme = os.path.basename(image_path).split('.')[0]
    im = Image.open(image_path)
    width, height = im.size

    # 裁剪参数
    crop_size = 1024 # 裁剪区域大小为1024x1024
    stride = 512      # 移动步长为512像素

    # 计算x方向的起始位置列表
    x_starts = list(range(0, width - crop_size + 1, stride))
    if x_starts[-1] != width - crop_size:
        x_starts.append(width - crop_size)

    # 计算y方向的起始位置列表
    y_starts = list(range(0, height - crop_size + 1, stride))
    if y_starts[-1] != height - crop_size:
        y_starts.append(height - crop_size)


    # 遍历所有起始位置进行裁剪
    for top in y_starts:
        for left in x_starts:
            # 裁剪区域：左、上、右、下
            box = (left, top, left + crop_size, top + crop_size)
            patch = im.crop(box)
            output_path = os.path.join(save_dir, f"{baseneme}_{left}_{top}.png")
            patch.save(output_path)

def npy_to_rgb(input_path, output_path):
    """
    将.npy数组文件转换为RGB图像
    
    参数:
        input_path (str): 输入的.npy文件路径
        output_path (str): 输出的PNG图像文件路径
    
    功能:
        1. 加载.npy文件并验证其形状和数据类型
        2. 为数组中的每个唯一值生成随机RGB颜色
        3. 创建RGB图像并保存为PNG格式
    
    示例:
        >>> npy_to_rgb("input.npy", "output.png")
        Image saved to output.png

    """
    # 加载npy文件
    data = np.load(input_path)
    

    # 获取所有唯一值
    unique_values = np.unique(data)
    
    # 为每个唯一值生成随机RGB颜色
    color_map = {}
    for val in unique_values:
        color_map[val] = (random.randint(0, 255), 
                         random.randint(0, 255), 
                         random.randint(0, 255))
    
    # 创建RGB图像
    rgb_array = np.zeros((data.shape[0], data.shape[1], 3), dtype=np.uint8)
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            rgb_array[i,j] = color_map[data[i,j]]
    
    # 保存图像
    img = Image.fromarray(rgb_array)
    img.save(output_path)
    print(f"Image saved to {output_path}")

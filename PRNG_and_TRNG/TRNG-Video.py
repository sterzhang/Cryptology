import imageio
import numpy
import math
from itertools import chain
from moviepy.editor import *

# 图像数据存储格式
# image[y][x][rgb]
#    y: 行坐标
#    x: 列坐标
#    rgb: 颜色通道

numNeeded = 10000  # 所需随机数的数量
maxRange  = 256    # 数值范围的最大值

# 初始化变量
numPossibles = 0  # 可能的数值数量
schouldCont = True  # 控制循环是否继续的标志
frame = 0  # 当前处理的帧数
bitsRange = math.ceil(math.log(maxRange, 2))  # 计算所需位数
tmp = 0  # 临时变量，用于构建最终的数值
count = 0  # 计数器
sublist = []  # 存储单个位
tempSublist = []  # 存储临时子列表
outputList = []  # 输出的数值列表

# 从视频中截取帧
def frameCut():
  clip = VideoFileClip('example.mp4')  # 打开视频文件
  clip.save_frame('frame.png', t=frame)  # 保存当前帧为PNG图片

# 从帧中读取数值
numNeeded *= bitsRange

while(schouldCont):
  frameCut()
  image = imageio.imread('frame.png')  # 读取图片
  imgHigth, imgWidth, imgChannel = image.shape  # 获取图片尺寸和通道信息

  # 遍历整个帧，提取位值
  for i in range(0,imgHigth):
    for j in range(0,imgWidth):
      for k in range(0,imgChannel):
        # 只考虑特定范围内的像素值
        if(image[i][j][k] >= 2 and image[i][j][k] <= 253):
          sublist.append(image[i][j][k] & 0b1)  # 提取最低位
          numPossibles += 1
  frame += 1
  if(numPossibles >= numNeeded):
    schouldCont = False

# 计算正方形矩阵的大小
square = math.floor(math.sqrt(numNeeded))

# 将提取的位值填充到矩阵中
for i in range(0,square*square):
  tempSublist.append(sublist[i])

# 转置并重新排列矩阵
tempSublist = numpy.array(tempSublist).reshape(square, square)
transpose = tempSublist.T
tempSublist = transpose.tolist()
tempSublist = list(chain.from_iterable(tempSublist))

# 如果所需位数大于矩阵大小，则继续添加
if(square*square < numNeeded):
  for i in range(0, numNeeded - square*square):
    tempSublist.append(sublist[i+(square*square)])

x = 0
# 组合位值生成数值
while(count < numNeeded/bitsRange):
  for j in range(0, bitsRange):
    valTmp = tempSublist[x]
    tmp = tmp | (valTmp << j)
    x += 1
  outputList.append(tmp)
  tmp = 0
  count += 1

# 将生成的数值写入文件
output = open("output.txt", "w")
for element in outputList:
    output.write(str(element) + "\n")
output.close()

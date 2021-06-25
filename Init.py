import numpy as np
from collections import namedtuple
import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
from PIL import Image, ImageTk  # 导入PIL模块中的Image、ImageTk
from graphviz import Digraph
import json
import h5py as h5
from graphviz import Source
import cv2
# a label and all meta information
###label定义（表2）
Label = namedtuple('Label', [

    'name',  # The identifier of this label, e.g. 'car', 'person', ... .
    # We use them to uniquely name a class

    'id',  # An integer ID that is associated with this label.
    # The IDs are used to represent the label in ground truth images
    # An ID of -1 means that this label does not have an ID and thus
    # is ignored when creating ground truth images (e.g. license plate).
    # Do not modify these IDs, since exactly these IDs are expected by the
    # evaluation server.

    'trainId',  # Feel free to modify these IDs as suitable for your method. Then create
    # ground truth images with train IDs, using the tools provided in the
    # 'preparation' folder. However, make sure to validate or submit results
    # to our evaluation server using the regular IDs above!
    # For trainIds, multiple labels might have the same ID. Then, these labels
    # are mapped to the same class in the ground truth images. For the inverse
    # mapping, we use the label that is defined first in the list below.
    # For example, mapping all void-type classes to the same ID in training,
    # might make sense for some approaches.
    # Max value is 255!

    'category',  # The name of the category that this label belongs to

    'categoryId',  # The ID of this category. Used to create ground truth images
    # on category level.

    'hasInstances',  # Whether this label distinguishes between single instances or not

    'ignoreInEval',  # Whether pixels having this class as ground truth label are ignored
    # during evaluations or not

    'color',  # The color of this label
])

# --------------------------------------------------------------------------------
# A list of all labels
# --------------------------------------------------------------------------------

# Please adapt the train IDs as appropriate for your approach.
# Note that you might want to ignore labels with ID 255 during training.
# Further note that the current train IDs are only a suggestion. You can use whatever you like.
# Make sure to provide your results using the original IDs and not the training IDs.
# Note that many IDs are ignored in evaluation and thus you never need to predict these!

labels = [
    #       name                     id    trainId   category            catId     hasInstances   ignoreInEval   color
    Label('unlabeled', 0, 255, 'void', 0, False, True, (0, 0, 0)),
    Label('ego vehicle', 1, 255, 'void', 0, False, True, (0, 0, 1)),  #原本是000
    Label('rectification border', 2, 255, 'void', 0, False, True, (0, 0, 1)),#原本是000
    Label('out of roi', 3, 255, 'void', 0, False, True, (0, 0, 1)),#原本是000
    Label('static', 4, 255, 'void', 0, False, True, (0, 0, 1)),#原本是000
    Label('dynamic', 5, 255, 'void', 0, False, True, (111, 74, 0)),
    Label('ground', 6, 255, 'void', 0, False, True, (81, 0, 81)),
    Label('road', 7, 0, 'flat', 1, False, False, (128, 64, 128)),
    Label('sidewalk', 8, 1, 'flat', 1, False, False, (244, 35, 232)),
    Label('parking', 9, 255, 'flat', 1, False, True, (250, 170, 160)),
    Label('rail track', 10, 255, 'flat', 1, False, True, (230, 150, 140)),
    Label('building', 11, 2, 'construction', 2, False, False, (70, 70, 70)),
    Label('wall', 12, 3, 'construction', 2, False, False, (102, 102, 156)),
    Label('fence', 13, 4, 'construction', 2, False, False, (190, 153, 153)),
    Label('guard rail', 14, 255, 'construction', 2, False, True, (180, 165, 180)),
    Label('bridge', 15, 255, 'construction', 2, False, True, (150, 100, 100)),
    Label('tunnel', 16, 255, 'construction', 2, False, True, (150, 120, 90)),
    Label('pole', 17, 5, 'object', 3, False, False, (153, 153, 153)),
    Label('polegroup', 18, 255, 'object', 3, False, True, (0, 0, 1)), #原本是153, 153, 153
    Label('traffic light', 19, 6, 'object', 3, False, False, (250, 170, 30)),
    Label('traffic sign', 20, 7, 'object', 3, False, False, (220, 220, 0)),
    Label('vegetation', 21, 8, 'nature', 4, False, False, (107, 142, 35)),
    Label('terrain', 22, 9, 'nature', 4, False, False, (152, 251, 152)),
    Label('sky', 23, 10, 'sky', 5, False, False, (70, 130, 180)),
    Label('person', 24, 11, 'human', 6, True, False, (220, 20, 60)),
    Label('rider', 25, 12, 'human', 6, True, False, (255, 0, 0)),
    Label('car', 26, 13, 'vehicle', 7, True, False, (0, 0, 142)),
    Label('truck', 27, 14, 'vehicle', 7, True, False, (0, 0, 70)),
    Label('bus', 28, 15, 'vehicle', 7, True, False, (0, 60, 100)),
    Label('caravan', 29, 255, 'vehicle', 7, True, True, (0, 0, 90)),
    Label('trailer', 30, 255, 'vehicle', 7, True, True, (0, 0, 110)),
    Label('train', 31, 16, 'vehicle', 7, True, False, (0, 80, 100)),
    Label('motorcycle', 32, 17, 'vehicle', 7, True, False, (0, 0, 230)),
    Label('bicycle', 33, 18, 'vehicle', 7, True, False, (119, 11, 32)),
    Label('license plate', 34, -1, 'vehicle', 7, False, True, (0, 0, 1)), #原本是0, 0, 142
]

foregroundid = [17, 18, 19, 20, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34]
conid = [11, 12, 13, 14, 15, 16, 21, 23]
flatid = [6, 7, 8, 9, 10, 22]
noneid = [0, 1, 2, 3, 4, 5]



# 类编号-类名

# 建立颜色的索引和id的索引
color2label = {label.color: label for label in labels}
id2label = {label.id: label for label in labels}

# 输入原始图片地址，返回三个图片地址
file_name = []


ins_to_stuff = []
width =0
height=0
insid=[]


k = 2  # 默认k=3


if_open = 0  # 是否打开图片


rect = []  # 记录画板上的内容，其中rect0是底层图片


if_region = 1


rel_list_all = ["and", "belonging to", "made of", "at", "in", "from", "for", "to", "has", "covered in",
                "along","on", "with", "part of", "of", "against", "over", "in front of", "behind", "on back of",
                "under","between", "above", "near", "in the left of", "in the right of", "over", "parked on", "growing on","standing on",
                "attached to", "hanging from", "lying on", "flying in", "looking at", "holding", "laying on", "riding", "across", "walking on",
                "eating", "watching", "driving in", "sitting on", "carrying", "using", "covering", "playing", "painted on", "mounted on",
                "occluding", "occluded","completely in", "half of in", "access_in the left of", "access_in the right of","access_in the front of", "access_in the back of", "access_in the center of", "access_around",
                "ride on","in the front-left of", "in the front-right of","in the back-left of", "in the back-right of","access_between","access_in two side of"]

# 每个关系都有一个类型
rel_list_all_type = ["p", "p", "p", "p", "p", "p", "p", "p", "p", "p",
                     "p", "p", "p", "p", "p", "p", "s", "s", "s", "s",
                     "s", "s", "s", "s", "s", "s", "v", "a", "a", "a",
                     "v", "v", "a", "a", "v", "v", "a", "v", "a", "a",
                     "v", "v", "a", "a", "v", "v", "v", "v", "v", "v",
                     "o", "o", "a", "a", "l", "l", "l", "l", "l", "l",
                     "a", "s", "s", "s", "s","l","l"]

# 还有一个表格存放每一层对应的类型
rel_list_layer = [[], ["m"], ["p"], ["p"], [],
                  ["m"], ["s", "p", "v", "o"], ["s", "p", "v", "o", "a"], ["s", "p", "v", "o"], [],
                  ["m"], ["s", "p", "v", "o", "a"], ["l", "s"], ["s", "a", "o"], [],
                  ["m"], ["s", "p", "v", "o"], ["s", "a", "o"], ["s", "o","p"], [],
                  [], [], ["f"], ["f"], []]

# 先对表格进行一个分类
rel_p = []
for i in range(len(rel_list_all_type)):
    if rel_list_all_type[i] == 'p':
        rel_p.append([i, rel_list_all[i]])

rel_s = []
for i in range(len(rel_list_all_type)):
    if rel_list_all_type[i] == 's':
        rel_s.append([i, rel_list_all[i]])

rel_v = []
for i in range(len(rel_list_all_type)):
    if rel_list_all_type[i] == 'v':
        rel_v.append([i, rel_list_all[i]])

rel_o = []
for i in range(len(rel_list_all_type)):
    if rel_list_all_type[i] == 'o':
        rel_o.append([i, rel_list_all[i]])

rel_a = []
for i in range(len(rel_list_all_type)):
    if rel_list_all_type[i] == 'a':
        rel_a.append([i, rel_list_all[i]])

rel_l = []
for i in range(len(rel_list_all_type)):
    if rel_list_all_type[i] == 'l':
        rel_l.append([i, rel_list_all[i]])

rel_list_now_id = []


sub_rel_ob = [[-1, -1, -1]]
sub_rel_ob_attri=[[-1, -1, -1]] #记录三个属性变量


cs = 0
rect1 = []  # 起点集合
rect2 = []  # 终点集合
rect1_temp=[0,0]  #临时记录起点
rect2_temp=[0,0]  #临时记录终点
renum=0 #记录region个数
renum2=0 #记录点击了多少下region_enter
focus_region=-1

if_start_cluster = False
allcluster=[] #所有cluster的集合
select_cluster=[] #存放临时的cluster
cluster_num=0
cluster_list_index=0
direc_list_index=-1
annoedclu_index=0 #默认位置始终为停留的最新的位置
annoedclu_num=0

insid_cluster=[]
ins_to_stuff_cluster=[]

all_region_rel_list=[]
region_rel_list=[]

auto_num=0
auto_index=-1

recoid=-1

direc=[]

if_select_cluster=False
#global if_select_cluster

oripicnum=-1

m_a = []
m_a_a = []
new_m_a=[]
new_m_a_a=[]
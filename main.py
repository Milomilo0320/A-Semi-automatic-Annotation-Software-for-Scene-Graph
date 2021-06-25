####初始数据源
####
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
from Init import *
import copy
import shutil
import os
from tkinter import ttk

def three_pic(path):
    # path为原图地址，结构.../ori/aachen_000000_000019_leftImg8bit.png
    a = path.split('/')
    print(a)  # a是按/分开的数组[...][ori][aachen_000000_000019_leftImg8bit.png]
    mystr1 = '_'
    name = a[len(a) - 1].split('_')  # 最后一个单词aachen_000000_000019_leftImg8bit.png分开，取前三个
    mystr0 = '.'
    global file_name
    global oripicnum
    file_name = '_'.join([name[1], name[2], name[3]])#新建了文档，所以取第2~4个（标号1 2 3）
    #file_name = '_'.join([name[0], name[1], name[2]])
    print("file_name", file_name)
    print("name", name)
    oripicnum=name[0]
    ins_name = mystr1.join([name[1],name[2],name[3],name[4]]) #最后一个地址
    ori_name = a[len(a) - 1]
    del (name[-1])  # name剩下0 aachen  000000  000019
    #del (name[0])
    name.append("gtFine_color.png")
    stuff_name = mystr1.join([name[1],name[2],name[3],name[4]])
    mystr2 = '/'

    del (a[-1])
    del (a[-1])  # 删掉a最后两个元素
    # 补充文件夹和文件名字
    a.append("ins")
    a.append(ins_name)
    path_ins = mystr2.join(a)

    del (a[-1])
    del (a[-1])  # 删掉a最后两个元素
    # 补充文件夹和文件名字
    a.append("stuff")
    a.append(stuff_name)
    path_stuff = mystr2.join(a)

    del (a[-1])
    del (a[-1])  # 删掉a最后两个元素
    # 补充文件夹和文件名字
    a.append("ori")
    a.append(ori_name)
    path_ori = mystr2.join(a)

    return (path_ori, path_stuff, path_ins)

# 将实例图按像素扫描，如果是新出现的颜色，实例+1，并记录类别和层次
def encoding(stuff, ins):
    # stuff = Image.open(path_stuff)
    # ins = Image.open(path_ins)
    pix = ins.load()  # 实例图
    pix_stuff = stuff.load()  # 类型图
    # 理论上三个图片的大小应该是相同的
    global width,height
    width = ins.size[0]
    height = ins.size[1]
    insid = np.zeros((height, width))  # 存放像素实例id矩阵
    inslis = []  #
    stufflis = []  # 存放实例id对应的类别像素颜色
    ins_to_stuff = []  # 存放实例id-类别id（表1）
    zb = []  # 记录各个新实例开始的坐标

    #for i in range(width):  # 2048
    #    for j in range(height):  # 1024
    #        if(i)
    #print("pix[0, 0]",pix[0, 0]==(0,0,0))
    ins_color=[(220, 20, 60,255),(255, 0, 0,255),(0, 0, 142,255),(0, 0, 70,255),(0, 60, 100,255),(0, 0, 90,255),(0, 0, 110,255),(0, 80, 100,255),(0, 0, 230,255),(119, 11, 32,255),(0, 0, 1,255)]
    #print(pix_stuff[1590, 440] not in ins_color)
    #print(pix_stuff[1590, 440] != (0, 0, 0))
    #print(pix[1590, 440] == (0, 0, 0))
    #print(pix_stuff[1590, 440])

    for i in range(width):  # 2048
        for j in range(height):  # 1024
            # r,g,b=pix[i, j]
            if pix_stuff[i, j] != (0, 0, 0,255) and pix[i, j] == (0, 0, 0) and (pix_stuff[i, j] not in ins_color):
                #如果 类型不是空  并且  实例是黑色的  并且  类型不是车子和人
                pix[i, j]=pix_stuff[i, j]
            if (pix[i, j] not in inslis):  # 实例图中 如果是新出现的颜色(新的实例)
                inslis.append(pix[i, j])  # 实例颜色列表+1
                stufflis.append(pix_stuff[i, j])  # 每个实例对应类别颜色列表+1
                insid[j, i] = int(len(inslis) - 1)  # 实例id+1
                zb.append((i, j))
                new_stuff = [insid[j, i], color2label[pix_stuff[i, j][0:3]].id,i,j,i,j]  # 每个实例id,所属类别id  #顺便记录下每个坐标最左边和最上面的位置,2ll(这个肯定是不变的),3uu,4rr,5dd
                ins_to_stuff.append(new_stuff)
            else:
                insid[j, i] = inslis.index(pix[i, j])  # 如果是出现过的颜色，在像素上标注下实例id的颜色就好
                if j<ins_to_stuff[int(insid[j, i])][3]: #如果比最小的上界小
                    ins_to_stuff[int(insid[j, i])][3]=j
                if j > ins_to_stuff[int(insid[j, i])][5]:  # 如果比最大的下界下
                    ins_to_stuff[int(insid[j, i])][5] = j
                if i > ins_to_stuff[int(insid[j, i])][4]:  # 如果比最大的右界大(这里感觉还可以优化)
                    ins_to_stuff[int(insid[j, i])][4] = i

    return (insid, ins_to_stuff)  # insid存放像素实例id矩阵 ins_to_stuff存放实例id-类别id（表1）


# 对缩小后图像的像素可以查询在原始图像的位置
def q_ori(x, y):
    global k
    ori_x = int(k * x)
    ori_y = int(k * y)
    return (ori_x, ori_y)


# 对原始图像的每一个点可以查询id和label  总觉得这里xy的位置有点问题
def q_id(x, y):
    global insid
    return insid[y, x]


# 求label的编号
def q_label(x, y):
    global insid
    global ins_to_stuff
    return ins_to_stuff[int(insid[y, x])][1]


def q_layer(myid):  # 求某个实例id所在层 是id求层，不是类别求层！！！！
    labelid = ins_to_stuff[int(myid)][1]
    # q_label
    if labelid in foregroundid:
        layerid = 2
    if labelid in flatid:
        layerid = 3
    if labelid in conid:
        layerid = 4
    if labelid in noneid:
        layerid = -1
    return layerid

    # layerid=1 图像层
    # layerid=2 前景层
    # layerid=3 背景层之flat
    # layerid=4 背景层之con
    # layerid=5 场景层
    # layerid=-1 none 不知道咋分类


##透明化
def addTransparency(img, factor=0.7):
    img = img.convert('RGBA')
    img_blender = Image.new('RGBA', img.size, (0, 0, 0, 0))
    img = Image.blend(img_blender, img, factor)
    return img




###用new按键打开三个图片
def new_file():
    global if_open
    if if_open==1:
        return

    path = tk.filedialog.askopenfilename()  # 返回原始图片的文件名
    if path=="" : #如果没有成功打开
        return
    path_ori, path_stuff, path_ins = three_pic(path)

    ori = Image.open(path_ori)
    stuff = Image.open(path_stuff)
    ins = Image.open(path_ins)

    if_open = 1

    # 调整图片大小并记录比例
    global k
    # k = 2  # 缩放比例
    # im是大原图，im2是大实例图，im3是大类别图
    # imnew是小原图，imnew2是小实例图，imnew3是小类别图，img是小混合图

    global v2int,v22int
    v2int=1
    v22int = 1
    v.set(1)
    v22.set(1)

    global imnew, imnew2, imnew3, img, img_back #img_back为底层显示
    im = Image.open(path_ori)
    pix = im.load()  # 实例图
    width = im.size[0]
    height = im.size[1]
    imnew = Image.new('RGB', (width // k, height // k), "red")
    pixnew = imnew.load()  # 实例图

    im2 = Image.open(path_ins)  # 实例图
    pix2 = im2.load()  # 实例图
    width2 = im2.size[0]
    height2 = im2.size[1]
    imnew2 = Image.new('RGB', (width2 // k, height2 // k), "red")
    pixnew2 = imnew2.load()  # 实例图

    im3 = Image.open(path_stuff)  # 实例图
    pix3 = im3.load()  # 实例图
    width3 = im3.size[0]
    height3 = im3.size[1]
    imnew3 = Image.new('RGB', (width3 // k, height3 // k), "red")
    pixnew3 = imnew3.load()  # 实例图

    for x in range(width // k):  # 2048
        for y in range(height // k):  # 1024
            pixnew[x, y] = pix[x * k, y * k]

    for x in range(width2 // k):  # 2048
        for y in range(height2 // k):  # 1024
            pixnew2[x, y] = pix2[x * k, y * k]

    for x in range(width3 // k):  # 2048
        for y in range(height3 // k):  # 1024
            pixnew3[x, y] = pix3[x * k, y * k]

    img1 = imnew.convert('RGBA')
    img2 = imnew2.convert('RGBA')
    img = Image.blend(img1, img2, 0.3)
    img_back = Image.blend(img1, img2, 0.8)

    img.save('img.png')
    imnew.save('imnew.png')
    imnew2.save('imnew2.png')
    imnew3.save('imnew3.png')

    ###对图像信息进行编码
    global insid
    global ins_to_stuff
    insid, ins_to_stuff = encoding(stuff, ins)  # 对stuff和ins进行编码
    # 得到一个每个实例id的label记做ins_to_stuff和一个hxw的每个像素的实例id图
    ##每一个像素点包含：实例id和label和层次

    # 在image_box中显示图片
    # new_image=Image.open(path)#创建Label组件，通过Image=photo设置要展示的图片
    global rect
    new_photo = ImageTk.PhotoImage(img)  # 创建tkinter兼容的图片
    image_box.x = new_photo
    image_box['image'] = new_photo
    image_box.pack()
    # rect[0]=mycan.create_image(0,0,image= new_photo)  #这里添加的图片显示不出来？只能在外？
    # rect.append(mycan.create_image(0,0,image= new_photo))
    # mycan.create_image(0, 0, image=new_photo)
    # mycan.pack(side='left')

    # 测试部分
    # image_test = Image.open('white.png')  # 创建Label组件，通过Image=photo设置要展示的图片
    # image_photo_test = ImageTk.PhotoImage(image_test)  # 创建tkinter兼容的图片
    # rect.append(mycan.create_image(0, 0, image=image_photo_test,anchor='NW'))
    # mycan.itemconfigure(rect[0], image=image_photo_test)  #和图片内容没关系 应该是原本的。
    #
    # mycan.tag_raise(rect[1])
    # rect.append(mycan.create_rectangle(10,10,110,110,fill="yellow"))
    # mycan.tag_raise(rect[0]) #把rect里面的所有都raise一遍
    # mycan.delete(rect[0])

    # 把场景图显示在新窗口
    sg_image = Image.open('anewsg.gv.png')  # 创建Label组件，通过Image=photo设置要展示的图片
    sg_photo = ImageTk.PhotoImage(sg_image)  # 创建tkinter兼容的图片
    # 想让sg_box这个label直接显示在window2上
    sg_box.x = sg_photo
    sg_box['image'] = sg_photo
    sg_box.state = "on"
    sg_box.pack()  # 展示Label对象

    # new_photo2=ImageTk.PhotoImage(imnew2)#创建tkinter兼容的图片
    # image2_box.x = new_photo2
    # image2_box['image'] = new_photo2
    # image2_box.pack()

    # print(ins_to_stuff)
    global insid_cluster, ins_to_stuff_cluster
    insid_cluster = copy.deepcopy(insid)
    ins_to_stuff_cluster = copy.deepcopy(ins_to_stuff)

    #打开语对base
    #打开base  从base里读取语对信息
    if(os.path.exists("motif_attr.h5")==False):
        f = h5.File('motif_attr.h5', 'w')
        f.create_dataset('motif_attr', data=[])
        f.create_dataset('motif_attr_attr', data=[])

    motif_attr = h5.File("motif_attr.h5", 'r')
    global m_a,m_a_a
    m_a = motif_attr['motif_attr'][:].tolist()
    m_a_a = motif_attr['motif_attr_attr'][:].tolist()


###用open按键打开三个图片
def open_file():
    path = tk.filedialog.askopenfilename()  # 返回原石图片的文件名
    path_ori, path_stuff, path_ins = three_pic(path)
    ori = Image.open(path_ori)
    stuff = Image.open(path_stuff)
    ins = Image.open(path_ins)

    global if_open
    if_open = 1

    global v2int,v22int
    v2int=1
    v22int = 1
    v.set(1)
    v22.set(1)

    # 调整图片大小并记录比例
    global k
    # k = 2  # 缩放比例
    # im是大原图，im2是大实例图，im3是大类别图
    # imnew是小原图，imnew2是小实例图，imnew3是小类别图，img是小混合图
    global imnew, imnew2, imnew3, img
    im = Image.open(path_ori)
    pix = im.load()  # 实例图
    width = im.size[0]
    height = im.size[1]
    imnew = Image.new('RGB', (width // k, height // k), "red")
    pixnew = imnew.load()  # 实例图

    im2 = Image.open(path_ins)  # 实例图
    pix2 = im2.load()  # 实例图
    width2 = im2.size[0]
    height2 = im2.size[1]
    imnew2 = Image.new('RGB', (width2 // k, height2 // k), "red")
    pixnew2 = imnew2.load()  # 实例图

    im3 = Image.open(path_stuff)  # 实例图
    pix3 = im3.load()  # 实例图
    width3 = im3.size[0]
    height3 = im3.size[1]
    imnew3 = Image.new('RGB', (width3 // k, height3 // k), "red")
    pixnew3 = imnew3.load()  # 实例图

    for x in range(width // k):  # 2048
        for y in range(height // k):  # 1024
            pixnew[x, y] = pix[x * k, y * k]

    for x in range(width2 // k):  # 2048
        for y in range(height2 // k):  # 1024
            pixnew2[x, y] = pix2[x * k, y * k]

    for x in range(width3 // k):  # 2048
        for y in range(height3 // k):  # 1024
            pixnew3[x, y] = pix3[x * k, y * k]

    img1 = imnew.convert('RGBA')
    img2 = imnew2.convert('RGBA')
    img = Image.blend(img1, img2, 0.3)

    ###对图像信息进行编码
    global insid
    global ins_to_stuff
    insid, ins_to_stuff = encoding(stuff, ins)  # 对stuff和ins进行编码
    # 得到一个每个实例id的label记做ins_to_stuff和一个hxw的每个像素的实例id图
    ##每一个像素点包含：实例id和label和层次

    # 在image_box中显示图片
    # new_image=Image.open(path)#创建Label组件，通过Image=photo设置要展示的图片
    new_photo = ImageTk.PhotoImage(img)  # 创建tkinter兼容的图片
    image_box.x = new_photo
    image_box['image'] = new_photo
    image_box.pack()

    # 不应该是打开这张图，而应该是识别了相关信息然后直接生成场景图
    global file_name, sub_rel_ob
    # 把场景图显示在新窗口
    # sg_image = Image.open(''.join([file_name,'.gv.png']))  # 创建Label组件，通过Image=photo设置要展示的图片
    # sg_photo = ImageTk.PhotoImage(sg_image)  # 创建tkinter兼容的图片
    # 想让sg_box这个label直接显示在window2上
    # sg_box.x = sg_photo
    # sg_box['image'] = sg_photo
    # sg_box.state = "on"
    # sg_box.pack()  # 展示Label对象

    imdb = h5.File(''.join([file_name, '.h5']), 'r')
    # num_im, _, _, _ = imdb['images'].shape
    # imdb['images'].shape的值是(2, 3, 1024, 1024)，表示有2个图，3是常量表示3个通道，后面是图像大小
    # img_long_sizes = [512, 1024]
    sub_rel_ob = imdb['sub_rel_ob'][:].tolist()  # valid image indices
    print(type(sub_rel_ob))
    print(sub_rel_ob)
    show_me_sgimage()
    global anno_rel, anno_num

    anno_rel.delete(0)
    for i in sub_rel_ob:
        if i != [-1, -1, -1]:
            anno_num = anno_num + 1
            name_sub_str = id2label[int(ins_to_stuff[int(i[0])][1])].name
            name_rel_str = rel_list_all[int(i[1])]
            name_ob_str = id2label[int(ins_to_stuff[int(i[2])][1])].name
            a = [name_sub_str, name_rel_str, name_ob_str]
            b = "-"
            c = b.join(a)
            # 处理和删除显示的列表
            ###size()=1的时候，实际上是num=0，所以要判断选中的是修改还是添加
            # 不管是删除的还是新增的，都是删除索引，然后在索引位置添加新的内容。如果是新增的就num+1，如果是修改的就num不变
            anno_rel.insert("end", c)
    anno_rel.insert("end", "")


###save按键
def save_file():
    global sub_rel_ob, ins_to_stuff_cluster,ins_to_stuff,insid_cluster, insid,rect1,rect2,sub_rel_ob_attri,allcluster,direc
    #a = tk.filedialog.askopenfilename()  # 返回文件名 啥玩意儿 怎么会有这句话？？
    print("sub_rel_ob:")
    print(sub_rel_ob)
    print("ins_to_stuff:")
    print(ins_to_stuff)
    global file_name
    global oripicnum
    f = h5.File('D:\\h5_data\\' + oripicnum +'_'+''.join([file_name, '.h5']), 'w')
    f.create_dataset('sub_rel_ob', data=sub_rel_ob)
    f.create_dataset('sub_rel_ob_attri', data=sub_rel_ob_attri)
    f.create_dataset('ins_to_stuff', data=ins_to_stuff)
    f.create_dataset('ins_to_stuff_cluster', data=ins_to_stuff_cluster)
    f.create_dataset('insid', data=insid)
    f.create_dataset('insid_cluster', data=insid_cluster)
    f.create_dataset('rect1', data=rect1)
    f.create_dataset('rect2', data=rect2)
    a = [j for i in allcluster for j in i]
    len_a=[]
    for i in range(len(allcluster)):
        len_a.append(len(allcluster[i]))
    f.create_dataset('allcluster_num', data=len_a)
    f.create_dataset('allcluster', data=a)
    f.create_dataset('direc', data=direc)
    scene_graph_save = Digraph(comment='Scene Graph', format='png', engine='fdp')
    scene_graph_save = Source.from_file('alala.gv')
    scene_graph_save.render(''.join([file_name, '.gv']), view=False)
    scene_graph_save.render(''.join([file_name, '.gv']), format='png', view=False)
    #img_name = ''.join([file_name, '.h5'])
    #img_name_new = 'D:\\h5_data\\' + ''.join([file_name, '.h5'])
    #shutil.copyfile(img_name, "ttt.h5")

    fma = h5.File('..\\motif_attr.h5', 'w')
    global new_m_a,m_a,new_m_a_a,m_a_a
    #for i in new_m_a:
    #    m_a.append(i)
    out_m_a=new_m_a+m_a
    out_m_a_a = new_m_a_a + m_a_a
    fma.create_dataset('motif_attr', data=out_m_a)
    fma.create_dataset('motif_attr_attr', data=out_m_a_a)


###sgimage按键 生成场景图
###用del可以实时显示场景图！！
''' 这个功能用该已经没用了 把菜单栏相关按键也删除了
def sgimage_file():
    scene_graph = Digraph(comment='Scene Graph', format='png', engine='fdp')
    # scene_graph = Digraph("Digraph.gv")
    global sub_rel_ob, ins_to_stuff
    # 实验一下能不能弹出窗口
    # scene_graph.node("node1","my scene graph",color="#97816a", fillcolor="#f5d0e1", fontcolor="#fe8c82", shape="box", style="filled")
    # scene_graph.node("node2", "hhh", color="#97816a", fillcolor="#f5d0e1", fontcolor="#fe8c82", shape="box",style="filled")
    ########修改内容分界线

    mylis = []  # 记录已经生成的节点
    k = -1

    # for i in list(gt_rels): #每个i都是('6-head', 'of', '4-man')
    # xx=i[0].split("-")  #xx为(6,head)
    # yy=i[2].split("-")
    # 对于第一组关系
    for i in sub_rel_ob:  # 注意一下，subrelob最后一个始终为[-1,-1,-1],所以i要注意一下
        if i != [-1, -1, -1]:
            xx = (int(i[0]), id2label[
                ins_to_stuff[int(i[0])][1]].name)  # (实例id,类型名称)   int(i[0])是实例id  ins_to_stuff[int(i[0])][1]是类型Id
            yy = (int(i[2]), id2label[ins_to_stuff[int(i[2])][1]].name)  # (实例id,类型)

            if (xx[0] not in mylis):  # 看一下节点1有了没，如果没有则生成
                mylis.append(xx[0])
                point_name = xx[0]
                point_context = xx[1]
                scene_graph.node('%s%s' % ('gt_boxes', point_name), '%s%s%s' % (point_name, "-", point_context),
                                 color="#97816a", fillcolor="#f5d0e1", fontcolor="#fe8c82", shape="box", style="filled")

            k = k + 1  # 连接Ob和rel
            # 注意！！！因为编码的时候 关系lis是从1开始编号 所以这个地方value要-1！！！
            scene_graph.node('%s%s' % ('gt_rels', k), rel_list_all[int(i[1])], color="#97816a", fillcolor="#c9fcd3",
                             fontcolor="#47bba8", style="filled")
            # style="filled")
            scene_graph.edge('%s%s' % ('gt_boxes', xx[0]), '%s%s' % ('gt_rels', k), color="#97816a")
            if (yy[0] not in mylis):  # 看一下节点1有了没，如果没有则生成
                mylis.append(yy[0])
                point_name = yy[0]
                point_context = yy[1]
                scene_graph.node('%s%s' % ('gt_boxes', point_name), '%s%s%s' % (point_name, "-", point_context),
                                 color="#97816a", fillcolor="#f5d0e1", fontcolor="#fe8c82", shape="box", style="filled")
            scene_graph.edge('%s%s' % ('gt_rels', k), '%s%s' % ('gt_boxes', yy[0]), color="#97816a")

    ########修改内容分界线

    # del scene_graph.body[0]
    # scene_graph = Source.from_file('Digrap h.gv')
    # for i in scene_graph.body:
    #    print(i)
    ##保存
    scene_graph.render(view=False)
    # 把场景图显示在新窗口'''


def show_me_sgimage():
    scene_graph = Digraph(comment='Scene Graph', format='png', engine='fdp')
    # scene_graph = Digraph("Digraph.gv")
    global sub_rel_ob, ins_to_stuff
    # 实验一下能不能弹出窗口
    # scene_graph.node("node1","my scene graph",color="#97816a", fillcolor="#f5d0e1", fontcolor="#fe8c82", shape="box", style="filled")
    # scene_graph.node("node2", "hhh", color="#97816a", fillcolor="#f5d0e1", fontcolor="#fe8c82", shape="box",style="filled")
    ########修改内容分界线

    mylis = []  # 记录已经生成的节点
    k = -1

    # for i in list(gt_rels): #每个i都是('6-head', 'of', '4-man')
    # xx=i[0].split("-")  #xx为(6,head)
    # yy=i[2].split("-")
    # 对于第一组关系
    for i in sub_rel_ob:  # 注意一下，subrelob最后一个始终为[-1,-1,-1],所以i要注意一下
        if i != [-1, -1, -1]:
            xx = (int(i[0]), id2label[
                ins_to_stuff[int(i[0])][1]].name)  # (实例id,类型名称)   int(i[0])是实例id  ins_to_stuff[int(i[0])][1]是类型Id
            yy = (int(i[2]), id2label[ins_to_stuff[int(i[2])][1]].name)  # (实例id,类型)

            if (xx[0] not in mylis):  # 看一下节点1有了没，如果没有则生成
                mylis.append(xx[0])
                point_name = xx[0]
                point_context = xx[1]
                scene_graph.node('%s%s' % ('gt_boxes', point_name), '%s%s%s' % (point_name, "-", point_context),
                                 color="#000000", fillcolor="#f5d0e1", fontcolor="#000000", shape="box", style="filled")

            k = k + 1  # 连接Ob和rel
            # 注意！！！因为编码的时候 关系lis是从1开始编号 所以这个地方value要-1！！！
            scene_graph.node('%s%s' % ('gt_rels', k), rel_list_all[int(i[1])], color="#000000", fillcolor="#c9fcd3",
                             fontcolor="#000000", style="filled")
            # style="filled")
            scene_graph.edge('%s%s' % ('gt_boxes', xx[0]), '%s%s' % ('gt_rels', k), color="#000000")
            if (yy[0] not in mylis):  # 看一下节点1有了没，如果没有则生成
                mylis.append(yy[0])
                point_name = yy[0]
                point_context = yy[1]
                scene_graph.node('%s%s' % ('gt_boxes', point_name), '%s%s%s' % (point_name, "-", point_context),
                                 color="#000000", fillcolor="#f5d0e1", fontcolor="#000000", shape="box", style="filled")
            scene_graph.edge('%s%s' % ('gt_rels', k), '%s%s' % ('gt_boxes', yy[0]), color="#000000")

    ########修改内容分界线

    # del scene_graph.body[0]
    # scene_graph = Source.from_file('Digraph.gv')
    # for i in scene_graph.body:
    #    print(i)
    ##保存
    scene_graph.render("alala.gv", view=False)
    # 把场景图显示在新窗口

    #在这里把场景图大小替换

    sg_image = Image.open('alala.gv.png')  # 创建Label组件，通过Image=photo设置要展示的图片

    width = sg_image.size[0]
    height = sg_image.size[1]
    global w,h
    print("wh",width,height)
    if (width>(w-100)) or (height>(h-100)):
        k=max(width/(w-100),height/(h-100)) #k表示是几倍
        print("k",k)
        target_size=(int(width/k),int(height/k))
        print("ts", target_size)
        sg_image = sg_image.resize(target_size)
    #target_size = (500,500)
    #sg_image = sg_image.resize(target_size)

    sg_photo = ImageTk.PhotoImage(sg_image)  # 创建tkinter兼容的图片
    # 想让sg_box这个label直接显示在window2上
    sg_box.x = sg_photo
    sg_box['image'] = sg_photo
    sg_box.state = "on"
    sg_box.pack()  # 展示Label对象

def howto_help():
    window3 = tk.Toplevel()  # 显示场景图
    window3.title('How to label')
    window3.geometry('300x300')
    howto = tk.Label(window3,text='选择主语：鼠标左键\n\n选择宾语：shift+鼠标左键\n\n标注region：鼠标右键拖动')
    howto.pack()

def about_help():
    window4 = tk.Toplevel()  # 显示场景图
    window4.title('About us')
    window4.geometry('300x300')
    aboutus = tk.Label(window4, text="Emotion Computing Group\n\nXi’an Jiaotong University")
    aboutus.pack()





# global imnew,imnew2,imnew3,img
# play_func1-4分别表示4种显示模式
def play_func1():
    if if_open==0 :
        return
    global v2int
    v2int = 1
    color_for_subnob(sub_id, ob_id)
    #new_photo = ImageTk.PhotoImage(img)  # 创建tkinter兼容的图片
    #image_box.x = new_photo
    #image_box['image'] = new_photo
    #image_box.pack()

    global v22int
    if v22int == 1:
        play_func12()
    if v22int == 2:
        play_func22()
    if v22int == 3:
        play_func32()


def play_func2():
    if if_open==0 :
        return
    global v2int
    v2int = 2
    color_for_subnob(sub_id, ob_id)
    #new_photo = ImageTk.PhotoImage(imnew)  # 创建tkinter兼容的图片
    #image_box.x = new_photo
    #image_box['image'] = new_photo
    #image_box.pack()

    global v22int
    if v22int == 1:
        play_func12()
    if v22int == 2:
        play_func22()
    if v22int == 3:
        play_func32()


def play_func3():
    if if_open==0 :
        return
    global v2int
    v2int = 3
    color_for_subnob(sub_id, ob_id)
    #new_photo = ImageTk.PhotoImage(imnew2)  # 创建tkinter兼容的图片
    #image_box.x = new_photo
    #image_box['image'] = new_photo
    #image_box.pack()

    global v22int
    if v22int == 1:
        play_func12()
    if v22int == 2:
        play_func22()
    if v22int == 3:
        play_func32()


def play_func4():
    if if_open==0 :
        return
    global v2int
    v2int = 4
    color_for_subnob(sub_id, ob_id)
    #new_photo = ImageTk.PhotoImage(imnew3)  # 创建tkinter兼容的图片
    #image_box.x = new_photo
    #image_box['image'] = new_photo
    #image_box.pack()

    global v22int
    if v22int == 1:
        play_func12()
    if v22int == 2:
        play_func22()
    if v22int == 3:
        play_func32()




def play_func12():
    if if_open==0 :
        return
    global v22int
    v22int = 1
    global rect1, rect2,renum
    global v2int
    if v2int == 1:
        image = cv2.imread('img.png')
    if v2int == 2:
        image = cv2.imread('imnew.png')
    if v2int == 3:
        image = cv2.imread('imnew2.png')
    if v2int == 4:
        image = cv2.imread('imnew3.png')

    global focus_region
    if rect1!=[] and rect2!=[] :
        cv2.rectangle(image, (rect1[int(focus_region)][0], rect1[int(focus_region)][1]),
                      (rect2[int(focus_region)][0], rect2[int(focus_region)][1]), (0, 0, 255), 2)
    cv2.imwrite('mymytest.png', image)
    new = Image.open('mymytest.png')
    new_photo = ImageTk.PhotoImage(new)  # 创建tkinter兼容的图片
    image_box.x = new_photo
    image_box['image'] = new_photo
    image_box.pack()


def play_func22():
    if if_open==0 :
        return
    global v22int
    v22int = 2
    global rect1, rect2,renum
    global v2int
    if v2int == 1:
        image = cv2.imread('img.png')
    if v2int == 2:
        image = cv2.imread('imnew.png')
    if v2int == 3:
        image = cv2.imread('imnew2.png')
    if v2int == 4:
        image = cv2.imread('imnew3.png')

    for i in range(renum):
        cv2.rectangle(image, (rect1[i][0], rect1[i][1]), (rect2[i][0], rect2[i][1]), (0, 0, 255), 2)
    cv2.imwrite('mymytest.png', image)
    new = Image.open('mymytest.png')
    new_photo = ImageTk.PhotoImage(new)  # 创建tkinter兼容的图片
    image_box.x = new_photo
    image_box['image'] = new_photo
    image_box.pack()



def play_func32():
    if if_open==0 :
        return
    global v22int
    v22int = 3

    global v2int
    if v2int == 1:
        image = cv2.imread('img.png')
    if v2int == 2:
        image = cv2.imread('imnew.png')
    if v2int == 3:
        image = cv2.imread('imnew2.png')
    if v2int == 4:
        image = cv2.imread('imnew3.png')

    cv2.imwrite('mymytest.png', image)
    new = Image.open('mymytest.png')
    new_photo = ImageTk.PhotoImage(new)  # 创建tkinter兼容的图片
    image_box.x = new_photo
    image_box['image'] = new_photo
    image_box.pack()


def small_label(self):
    print(rel_list_all)


def q_dpic2(opic,idnum,mycolor): #生成一个叠加图,0表示红色,1表示蓝色,2表示黄色
    #功能：在原始图片opic上，把id所在图层变成原图，然后把id以外的dpic_mini变成opic，最后返回融合的图片
    global insid,width,height,imnew,imnew2,imnew3,img,insid_cluster
    if mycolor==0:
        dpic_mini = Image.new('RGBA', (width // k, height // k), "red")
    if mycolor==1:
        dpic_mini = Image.new('RGBA', (width // k, height // k), "blue")
    if mycolor==2:
        dpic_mini = Image.new('RGBA', (width // k, height // k), "yellow")
    pixdpic_mini = dpic_mini.load()  #叠加层像素pixdpic_mini
    opic_rgba = opic.convert('RGBA')  # opic的RGAB版本
    pixopic = opic_rgba.load()  # oopic的像素
    imnew_rgba=imnew.convert('RGBA')  # 原图的RGAB版本
    piximnew = imnew_rgba.load()  # 原图的像素
    for x in range(width // k):  # 2048
        for y in range(height // k):  # 1024
            if insid_cluster[y* k,x* k]!=idnum:  #叠加层本来是全红色，如果是id以外的部分
                pixdpic_mini[x,y]=pixopic[x, y]
            else:
                pixopic[x, y] = piximnew[x, y]
    bl_img = Image.blend(opic_rgba, dpic_mini, 0.4)
    return bl_img


def color_for_subnob(sub_id,ob_id):
    if v2int == 1:
        myimg = img
    if v2int == 2:
        myimg = imnew
    if v2int == 3:
        myimg = imnew2
    if v2int == 4:
        myimg = imnew3
    sub_img = q_dpic2(myimg, sub_id, 0)  # 生成一个叠加图,0表示红色,1表示蓝色, 并缩小
    new_photo = ImageTk.PhotoImage(sub_img)  # 创建tkinter兼容的图片
    if ob_id !=-1: #等于-1的时候表示没有,不
        sub_img2 = q_dpic2(sub_img, ob_id, 1)  # 生成一个叠加图,0表示红色,1表示蓝色, 并缩小
        # 使得主语所在像素高亮
        # 实验部分 显示读取图像
        # img1 = img.convert('RGBA')
        #    sub_img = Image.blend(img, sub_dpic, 0.3)
        new_photo = ImageTk.PhotoImage(sub_img2)  # 创建tkinter兼容的图片
    image_box.x = new_photo
    image_box['image'] = new_photo
    image_box.pack()


# 选择sub主语
def select_sub(event):
    if if_open==0 :
        return
    # print("现在的位置是图片中的：", event.x, event.y)
    x, y = q_ori(event.x, event.y)
    # print("现在的位置是原始图片中的：",x, y)
    # print("实例id是：",q_id(x,y))
    # print("label id是：",q_label(x,y))
    global ob_id, rel_id, sub_id, name_ob_str, name_sub_str, name_rel_str, name_rel
    #print("x",x,"y",y)
    sub_id = q_id(x, y)
    name_sub.set(str(int(sub_id))+":"+str(id2label[q_label(x, y)].name))  # 选择一个新的主语时候，宾语和关系要跳没
    name_ob.set("There is ob")
    name_rel.set("There is rel")
    name_sub_str = id2label[q_label(x, y)].name
    name_ob_str = "There is ob"
    name_rel_str = "NONE"
    ob_id = -1
    rel_id = -1

    global imnew, imnew2, imnew3, img,sub_img,select_cluster
    global if_select_cluster
    if_select_cluster=False

    if v2int == 1:
        myimg = img
    if v2int == 2:
        myimg = imnew
    if v2int == 3:
        myimg = imnew2
    if v2int == 4:
        myimg = imnew3

    sub_img=q_dpic2(myimg,sub_id,0) #生成一个叠加图,0表示红色,1表示蓝色, 并缩小
    new_photo = ImageTk.PhotoImage(sub_img)  # 创建tkinter兼容的图片
    image_box.x = new_photo
    image_box['image'] = new_photo
    image_box.pack()

    if if_start_cluster == True: #如果此时是正在标注过程，则存储下subid 并且在cluster_list里显示
        select_cluster.append(sub_id)
        c = [str(int(sub_id)), "-", name_sub_str]
        mm = ''.join(c)
        cluster_list.insert("end", mm)

    f_text.set(" ")
    b_text.set(" ")
    l_text.set(" ")
    r_text.set(" ")


# 选择sub主语
def select_direc(event):
    if if_open==0 :
        return
    # print("现在的位置是图片中的：", event.x, event.y)
    x, y = q_ori(event.x, event.y)
    # print("现在的位置是原始图片中的：",x, y)
    # print("实例id是：",q_id(x,y))
    # print("label id是：",q_label(x,y))
    global ob_id, rel_id, sub_id, name_ob_str, name_sub_str, name_rel_str, name_rel
    sub_id = q_id(x, y)
    name_sub.set(str(int(sub_id))+":"+str(id2label[q_label(x, y)].name))  # 选择一个新的主语时候，宾语和关系要跳没
    name_ob.set("There is ob")
    name_rel.set("There is rel")
    name_sub_str = id2label[q_label(x, y)].name
    name_ob_str = "There is ob"
    name_rel_str = "NONE"
    ob_id = -1
    rel_id = -1

    global imnew, imnew2, imnew3, img,sub_img,select_cluster

    if v2int == 1:
        myimg = img
    if v2int == 2:
        myimg = imnew
    if v2int == 3:
        myimg = imnew2
    if v2int == 4:
        myimg = imnew3

    sub_img=q_dpic2(myimg,sub_id,2) #生成一个叠加图,0表示红色,1表示蓝色,2表示黄色 并缩小
    new_photo = ImageTk.PhotoImage(sub_img)  # 创建tkinter兼容的图片
    image_box.x = new_photo
    image_box['image'] = new_photo
    image_box.pack()


    #direc_set.insert("end","Forward")#插入朝前
    #direc_set.insert("forward", "Backward")  # 插入朝后
    #direc_set.insert("forward", "Leftward")  # 插入朝左
    #direc_set.insert("forward", "Righttward")  # 插入朝右
    f_text.set("  ↑  ")
    b_text.set("  ↓  ")
    l_text.set("  ←  ")
    r_text.set("  →  ")





# 求a层和b层之间的关系
def q_rel_list_now(a, b):
    # 如果是11对应00=0 12对应01=1
    #     21对应10=5
    rel_list_now = []
    global rel_list_now_id
    rel_list_now_id = []  # 定位显示的关系在关系列表里的id
    rel_list_now_type = rel_list_layer[(a - 1) * 5 + (b - 1)]  # 举个例子，比如rel_list_now_type=["s","p","v","o"]
    '''原来的方法
    for i in range(len(rel_list_all_type)):  #i=1~61
        if rel_list_all_type[i] in rel_list_now_type: #当列表里第i个的类型在rel_list_now_type中，则提取她。
            rel_list_now.append(rel_list_all[i])'''
    # 新方法
    for i in rel_list_now_type:
        if i == "s":
            rel_list_now.append("----Spatial----")
            rel_list_now_id.append(-1)
            for j in rel_s:
                rel_list_now.append(j[1])
                rel_list_now_id.append(j[0])
        if i == "p":
            rel_list_now.append("----Preposition----")
            rel_list_now_id.append(-1)
            for j in rel_p:
                rel_list_now.append(j[1])
                rel_list_now_id.append(j[0])
        if i == "v":
            rel_list_now.append("----Verb----")
            rel_list_now_id.append(-1)
            for j in rel_v:
                rel_list_now.append(j[1])
                rel_list_now_id.append(j[0])
        if i == "a":
            rel_list_now.append("----Area----")
            rel_list_now_id.append(-1)
            for j in rel_a:
                rel_list_now.append(j[1])
                rel_list_now_id.append(j[0])
        if i == "o":
            rel_list_now.append("----Occlusion----")
            rel_list_now_id.append(-1)
            for j in rel_o:
                rel_list_now.append(j[1])
                rel_list_now_id.append(j[0])
        if i == "l":
            rel_list_now.append("----Link----")
            rel_list_now_id.append(-1)
            for j in rel_l:
                rel_list_now.append(j[1])
                rel_list_now_id.append(j[0])
    return rel_list_now


# 弹出sub_id和ob_id的关系
def popup_rel(sub_id, ob_id):
    rel_list_now = q_rel_list_now(q_layer(sub_id), q_layer(ob_id))
    now_rel.delete(0, "end")
    for i in rel_list_now:
        now_rel.insert("end", i)


# 选择ob宾语
def select_ob(event):
    if if_open==0 :
        return
    global ob_id, sub_id, rel_id, name_ob_str, name_rel_str, name_rel, name_ob
    if sub_id != -1:  # 宾语必须在主语选择后才能选择
        # print("现在的位置是图片中的：", event.x, event.y)
        x, y = q_ori(event.x, event.y)
        # print("现在的位置是原始图片中的：",x, y)
        # print("实例id是：",q_id(x,y))
        # print("label id是：",q_label(x,y))
        ob_id = q_id(x, y)
        name_ob.set(str(int(ob_id))+":"+str(id2label[q_label(x, y)].name))
        name_ob_str = id2label[q_label(x, y)].name
        name_rel.set("There is rel")
        name_rel_str = "NONE"
        rel_id = -1
        popup_rel(sub_id, ob_id)  # 选择宾语后自动弹出关系

        global imnew, imnew2, imnew3, img, sub_img

        sub_img2 = q_dpic2(sub_img, ob_id, 1)  # 生成一个叠加图,0表示红色,1表示蓝色, 并缩小
        # 使得主语所在像素高亮
        # 实验部分 显示读取图像
        # img1 = img.convert('RGBA')
        #    sub_img = Image.blend(img, sub_dpic, 0.3)
        new_photo = ImageTk.PhotoImage(sub_img2)  # 创建tkinter兼容的图片
        image_box.x = new_photo
        image_box['image'] = new_photo
        image_box.pack()


# 确定按键
def certainrel(event):
    if if_open==0 :
        return
    global sub_rel_ob,sub_rel_ob_attri
    global ob_id, sub_id, rel_id, sub_rel_ob
    global name_ob_str, name_sub_str, name_rel_str, name_sub, name_ob, name_rel
    a = [name_sub_str, name_rel_str, name_ob_str]
    b = "-"
    c = str(int(sub_id))+":"+name_sub_str+"  ---"+name_rel_str+"---  "+str(int(ob_id))+":"+name_ob_str
    # 处理和删除显示的列表
    ###size()=1的时候，实际上是num=0，所以要判断选中的是修改还是添加
    global anno_num, anno_index,auto_index
    global region_rel_list,recoid
    newattri1,newattri2,newattri3=attri_attach(sub_id,ob_id)
    global if_select_cluster

    if if_select_cluster==True:#如果是批量的
            #看看普通的是怎么增加的
        anno_rel.delete(int(anno_index)) #删除最后一个，然后在最后添加一串
        del sub_rel_ob[int(anno_index)]  # 删除最后的[-1,-1,-1]
        del sub_rel_ob_attri[int(anno_index)]
        for i in allcluster[annoedclu_index]:
            c2 = str(int(i)) + ":" + name_sub_str + "  ---" + name_rel_str + "---  " + str(
                int(ob_id)) + ":" + name_ob_str
            anno_rel.insert("end", c2)
            # 记录在数组里，不管是删除的还是新增的，都是删除索引，然后在索引位置添加新的内容。如果是新增的就num+1，如果是修改的就num不变
            # print("删除并添加：",int(anno_index))
            sub_rel_ob.append([int(i), rel_id, ob_id])
            newattri12, newattri22, newattri32 = attri_attach(int(i), ob_id)
            sub_rel_ob_attri.append([newattri12, newattri22, newattri32])
            anno_num = anno_num + 1
        anno_rel.insert("end", "")
        bt_text.set("Enter")
        dele_text.set("       ")
        sub_rel_ob.append([-1, -1, -1])
        sub_rel_ob_attri.append([-1, -1, -1])
        anno_index = anno_num  # index始终指向最后一个
        anno_rel.activate(anno_index)
        # 确认后这些都要跳没
        name_sub.set("There is sub")
        name_rel.set("There is rel")
        name_ob.set("There is ob")
        name_sub_str = "NONE"
        name_rel_str = "NONE"
        name_ob_str = "NONE"
        if_select_cluster =False
        f_text.set(" ")
        b_text.set(" ")
        l_text.set(" ")
        r_text.set(" ")

    else:

        if anno_index == -1 and auto_index != -1: #修改的是auto_list
            '''如果选中的是auto列表按了确认键后把auto列表里的东西（subrelob）：
            1.保存在后台数据库列表里
            2.显示在已标注list里
            3.更新在autolist里（删除这一项在auto_rel和region_rel_list）
            4.subrelob文本清空 新的指标指着anno的新建这层'''
        # 功能1
            sub_rel_ob.insert(int(anno_num), [sub_id, rel_id, ob_id])
            sub_rel_ob_attri.insert(int(anno_num), [newattri1,newattri2,newattri3])
        # 功能2
            anno_rel.insert(int(anno_num), c)
            anno_num = anno_num + 1
        #anno_rel.insert("end", "")
            bt_text.set("Enter")
            dele_text.set("       ")
        #功能3
        # 找一下关于autorel显示相关的内容：和region_rel_list有关.那么要同时删除autorel和region_rel_list
        #为什么要同时删除而不是删除其中一个，因为文本显示和region_rel_list有关。
            del region_rel_list[int(auto_index)]
            auto_rel.delete(int(auto_index))
        # 功能4
            anno_index = anno_num  # index始终指向最后一个
            auto_index = -1
            anno_rel.activate(anno_index)
        # 确认后这些都要跳没
            name_sub.set("There is sub")
            name_rel.set("There is rel")
            name_ob.set("There is ob")
            name_sub_str = "NONE"
            name_rel_str = "NONE"
            name_ob_str = "NONE"
        #show_me_sgimage()

        else: #修改的不是auto_list
            # 不管是删除的还是新增的，都是删除索引，然后在索引位置添加新的内容。如果是新增的就num+1，如果是修改的就num不变
            anno_rel.delete(int(anno_index))
            anno_rel.insert(int(anno_index), c)
            # 记录在数组里，不管是删除的还是新增的，都是删除索引，然后在索引位置添加新的内容。如果是新增的就num+1，如果是修改的就num不变
            # print("删除并添加：",int(anno_index))
            del sub_rel_ob[int(anno_index)]
            del sub_rel_ob_attri[int(anno_index)]
            sub_rel_ob.insert(int(anno_index), [sub_id, rel_id, ob_id])
            sub_rel_ob_attri.insert(int(anno_index), [newattri1, newattri2, newattri3])
            if anno_index == anno_num:  # 新增的
                # num=1:111//000/,index=0表示修改，index=1表示新增,num=2:111//222//000
                anno_num = anno_num + 1
                anno_rel.insert("end", "")
                bt_text.set("Enter")
                dele_text.set("       ")
                sub_rel_ob.append([-1, -1, -1])
                sub_rel_ob_attri.append([-1, -1, -1])
            anno_index = anno_num  # index始终指向最后一个
            anno_rel.activate(anno_index)
            # 确认后这些都要跳没
            name_sub.set("There is sub")
            name_rel.set("There is rel")
            name_ob.set("There is ob")
            name_sub_str = "NONE"
            name_rel_str = "NONE"
            name_ob_str = "NONE"
    show_me_sgimage()
    print(sub_rel_ob)
    print(sub_rel_ob_attri)
    reco_rel.delete(0, "end")
    recoid = -1

    #添加功能：颜色显示全部弹没(然后把删除按键也添加一个这个功能)



# 选择可选关系
def select_rel(event):
    if if_open==0 :
        return
    global name_rel_str, rel_id  # 关系名字
    # name_rel.set(rel_list_now[now_rel.curselection()[0]])
    # name_rel_str = rel_list_now[now_rel.curselection()[0]]
    if (now_rel.curselection() != ()):
        if (rel_list_now_id[int(now_rel.curselection()[0])] != -1):  # 如果选中的不是分割线了话（分割线的rel_list_now_id=-1）
            # 为啥点别的时候 这个会出错？
            value = now_rel.get(now_rel.curselection())
            name_rel.set(value)
            name_rel_str = value
            rel_id = rel_list_now_id[int(now_rel.curselection()[0])]  # 不等于-1的时候才可以记录relid~~

def select_direc_list(event):
    if if_open==0 :
        return
    global name_rel_str, rel_id,direc_list_index  # 关系名字
    # name_rel.set(rel_list_now[now_rel.curselection()[0]])
    # name_rel_str = rel_list_now[now_rel.curselection()[0]]
    if (direc_list.curselection() != ()):
        direc_list_index = int(direc_list.curselection()[0])

        global imnew, imnew2, imnew3, img, sub_img
        if v2int == 1:
            myimg = img
        if v2int == 2:
            myimg = imnew
        if v2int == 3:
            myimg = imnew2
        if v2int == 4:
            myimg = imnew3

        sub_img = q_dpic2(myimg, direc[direc_list_index][0], 2)  # 生成一个叠加图,0表示红色,1表示蓝色,2表示黄色 并缩小
        new_photo = ImageTk.PhotoImage(sub_img)  # 创建tkinter兼容的图片
        image_box.x = new_photo
        image_box['image'] = new_photo
        image_box.pack()


# 选中已有关系的时候
def select_anno_rel(event):
    if if_open==0 :
        return
    # print(anno_rel.curselection())  #为什么有时候选择已选关系会出错？
    if (anno_rel.curselection() != ()):  # 如果不等于空了话，则执行后续

        num = int(anno_rel.curselection()[0])  # 选择的是第几条已有关系
        # sub_rel_ob[num][0] #sub的id
        # sub_rel_ob[num][1] #rel的id
        # sub_rel_ob[num][2] #ob的id
        global ins_to_stuff  # 实例id-所属类别id
        global ob_id, rel_id, sub_id, name_ob_str, name_sub_str, name_rel_str
        # 判断一下是修改还是增加
        global anno_num, anno_index,auto_index
        anno_index = num
        auto_index=-1 #把auto的归-1
        if anno_index == anno_num:  # 如果索引指着最后一个 则是新增  num=1:111//000/,index=0表示修改，index=1表示新增
            # 新增的情况
            sub_id = -1
            rel_id = -1
            ob_id = -1
            name_sub.set("There is sub")
            name_rel.set("There is rel")
            name_ob.set("There is ob")
            name_sub_str = "NONE"
            name_rel_str = "NONE"
            name_ob_str = "NONE"
            bt_text.set("Enter")
            dele_text.set("       ")

            #下面是修改的 目的是把之前选中的清空
            global imnew, imnew2, imnew3, img
            if v2int == 1:
                image = img
            if v2int == 2:
                image = imnew
            if v2int == 3:
                image = imnew2
            if v2int == 4:
                image = imnew3

            new_photo = ImageTk.PhotoImage(image)  # 创建tkinter兼容的图片
            image_box.x = new_photo
            image_box['image'] = new_photo
            image_box.pack()

        else:  # 修改的情况
            # ins_to_stuff[sub_id][1] #type的id
            sub_id = int(sub_rel_ob[num][0])
            rel_id = int(sub_rel_ob[num][1])
            ob_id = int(sub_rel_ob[num][2])

            # 更新融合的实例的情况
            global ins_to_stuff_cluster
            inslen = len(ins_to_stuff_cluster)
            if sub_id >= inslen:  # 说明是融合的内容
                subid = int(allcluster[int(int(sub_id) - inslen)][0])  # 某一个融合的第一个实例的id
            else:
                subid = sub_id
            if ob_id >= inslen:  # 说明是融合的内容
                obid = int(allcluster[int(int(ob_id) - inslen)][0])  # 某一个融合的第一个实例的id
            else:
                obid = ob_id

            name_sub.set(str(int(sub_id))+":"+str(id2label[int(ins_to_stuff[subid][1])].name))  # 选择一个新的主语时候，宾语和关系要跳没
            name_sub_str = id2label[int(ins_to_stuff[subid][1])].name
            name_ob.set(str(int(ob_id))+":"+str(id2label[int(ins_to_stuff[obid][1])].name))  # 选择一个新的主语时候，宾语和关系要跳没
            name_ob_str = id2label[int(ins_to_stuff[obid][1])].name

            name_rel.set(rel_list_all[rel_id])  # 选择一个新的主语时候，宾语和关系要跳没
            name_rel_str = rel_list_all[rel_id]
            bt_text.set("Change")
            dele_text.set("Delete")

            ###下面是复制粘贴的
            color_for_subnob(sub_id,ob_id)
            popup_rel(subid, obid)

def select_reco_rel(event):
    if if_open==0 :
        return
    # print(anno_rel.curselection())  #为什么有时候选择已选关系会出错？
    if (reco_rel.curselection() != ()):  # 如果不等于空了话，则执行后续


        rel_id = recoid

        if rel_id==-1:
            name_rel.set("NONE")  # 选择一个新的主语时候，宾语和关系要跳没
            name_rel_str = "NONE"
        else:
            name_rel.set(rel_list_all[rel_id])  # 选择一个新的主语时候，宾语和关系要跳没
            name_rel_str = rel_list_all[rel_id]


def select_auto_rel(event):
    if if_open==0 :
        return
    # print(anno_rel.curselection())  #为什么有时候选择已选关系会出错？
    if (auto_rel.curselection() != ()):  # 如果不等于空了话，则执行后续

        num = int(auto_rel.curselection()[0])  # 选择的是第几条已有关系
        # sub_rel_ob[num][0] #sub的id
        # sub_rel_ob[num][1] #rel的id
        # sub_rel_ob[num][2] #ob的id
        global ins_to_stuff  # 实例id-所属类别id
        global ob_id, rel_id, sub_id, name_ob_str, name_sub_str, name_rel_str
        # 判断一下是修改还是增加
        global auto_num, auto_index,region_rel_list,anno_index
        auto_index = num
        anno_index=-1
        sub_id = int(region_rel_list[num][0])
        rel_id = int(region_rel_list[num][5])
        ob_id = int(region_rel_list[num][2])

        #更新融合的实例的情况
        global ins_to_stuff_cluster
        inslen = len(ins_to_stuff_cluster)
        if sub_id >= inslen:  # 说明是融合的内容
            subid = int(allcluster[int(int(sub_id) - inslen)][0])  # 某一个融合的第一个实例的id
        else:
            subid = sub_id
        if ob_id >= inslen:  # 说明是融合的内容
            obid = int(allcluster[int(int(ob_id) - inslen)][0])  # 某一个融合的第一个实例的id
        else:
            obid = ob_id

        name_sub.set(str(int(sub_id))+":"+str(id2label[int(ins_to_stuff[subid][1])].name))  # 选择一个新的主语时候，宾语和关系要跳没
        name_sub_str = id2label[int(ins_to_stuff[subid][1])].name
        name_ob.set(str(int(ob_id))+":"+str(id2label[int(ins_to_stuff[obid][1])].name))  # 选择一个新的主语时候，宾语和关系要跳没
        name_ob_str = id2label[int(ins_to_stuff[obid][1])].name

        if rel_id==-1:
            name_rel.set("NONE")  # 选择一个新的主语时候，宾语和关系要跳没
            name_rel_str = "NONE"
        else:
            name_rel.set(rel_list_all[rel_id])  # 选择一个新的主语时候，宾语和关系要跳没
            name_rel_str = rel_list_all[rel_id]
        bt_text.set("修改")
        dele_text.set("删除")

            ###下面是复制粘贴的
        color_for_subnob(sub_id,ob_id)
        popup_rel(subid, obid)

        global m_a,m_a_a
        if len(m_a)<20:
            print("数量不够")
        else:
            print(m_a,m_a_a,[int(ins_to_stuff[subid][1]),int(ins_to_stuff[obid][1])],1) #以Init为准
            Recommend(m_a, m_a_a, [int(ins_to_stuff[subid][1]),int(ins_to_stuff[obid][1])], 1)



# 删除关系
def delerel(event):
    if if_open==0 :
        return
    global sub_rel_ob
    global anno_num, anno_index
    global ob_id, rel_id, sub_id, name_ob_str, name_sub_str, name_rel_str
    if anno_index != anno_num:  # 如果索引指着最后一个则不能删除
        anno_num = anno_num - 1
        anno_rel.delete(anno_index)
        # print("删除了：", int(anno_index))
        del sub_rel_ob[int(anno_index)]
        del sub_rel_ob_attri[int(anno_index)]
        anno_index = anno_num  # 指向新的
        anno_rel.activate(anno_index)
        sub_id = -1
        rel_id = -1
        ob_id = -1
        name_sub.set("There is sub")
        name_rel.set("There is rel")
        name_ob.set("There is ob")
        name_sub_str = "NONE"
        name_rel_str = "NONE"
        name_ob_str = "NONE"
        bt_text.set("Enter")
        dele_text.set("       ")
        show_me_sgimage()


def to_anno(event):
    global bt_anno, if_region
    if if_region == 0:
        bt_anno.set("开始标注")
        if_region = 1
    else:
        bt_anno.set("停止标注")
        if_region = 0
        start_to()



'''
def start_to(event):
    # print("现在的位置是图片中的：", event.x, event.y)
    x, y = q_ori(event.x, event.y)
    global rect1, rect2
    global cs  # 记录点击次数，双数时候标注数据
    cs = cs + 1
    # print("现在的位置是原始图片中的：",x, y)
    # print("实例id是：",q_id(x,y))
    # print("label id是：",q_label(x,y))
    global v2int
    if v2int == 1:
        image = cv2.imread('img.png')
    if v2int == 2:
        image = cv2.imread('imnew.png')
    if v2int == 3:
        image = cv2.imread('imnew2.png')
    if v2int == 4:
        image = cv2.imread('imnew3.png')

    if cs % 2 == 1:  # 单数
        rect1.append([event.x, event.y])

    if cs % 2 == 0:  # 双数
        rect2.append([event.x, event.y])
        cv2.rectangle(image, (rect1[int(cs / 2) - 1][0], rect1[int(cs / 2) - 1][1]),
                      (rect2[int(cs / 2) - 1][0], rect2[int(cs / 2) - 1][1]), (0, 0, 255), 2)

        cv2.imwrite('mymytest.png', image)
        new = Image.open('mymytest.png')
        new_photo = ImageTk.PhotoImage(new)  # 创建tkinter兼容的图片
        image_box.x = new_photo
        image_box['image'] = new_photo
        image_box.pack()
        # c=["region-",int(cs/2)-1,",(",rect1[int(cs/2)-1][0],",",rect1[int(cs/2)-1][1],"),(",rect2[int(cs/2)-1][0],",",rect2[int(cs/2)-1][1],")"]
        # mm=''.join(c)
        region_list.insert("end", int(cs / 2) - 1)
        # print(c)
    # print(mm)
    # print(type(mm))'''

def start_to1(event):
    # print("现在的位置是图片中的：", event.x, event.y)
    #x, y = q_ori(event.x, event.y)
    if if_open==0 :
        return
    global rect1_temp
    rect1_temp[0]=event.x
    rect1_temp[1]=event.y
    bt_region.set("确认region")

def start_to2(event):
    # print("现在的位置是图片中的：", event.x, event.y)
    #x, y = q_ori(event.x, event.y)
    if if_open==0 :
        return
    global rect1_temp
    # print("现在的位置是原始图片中的：",x, y)
    # print("实例id是：",q_id(x,y))
    # print("label id是：",q_label(x,y))
    global v2int
    if v2int == 1:
        image = cv2.imread('img.png')
    if v2int == 2:
        image = cv2.imread('imnew.png')
    if v2int == 3:
        image = cv2.imread('imnew2.png')
    if v2int == 4:
        image = cv2.imread('imnew3.png')

    cv2.rectangle(image, (rect1_temp[0], rect1_temp[1]),
                      (event.x, event.y), (0, 127, 255), 2)

    cv2.imwrite('mymytest.png', image)
    new = Image.open('mymytest.png')
    new_photo = ImageTk.PhotoImage(new)  # 创建tkinter兼容的图片
    image_box.x = new_photo
    image_box['image'] = new_photo
    image_box.pack()
        # c=["region-",int(cs/2)-1,",(",rect1[int(cs/2)-1][0],",",rect1[int(cs/2)-1][1],"),(",rect2[int(cs/2)-1][0],",",rect2[int(cs/2)-1][1],")"]
        # mm=''.join(c)
    #region_list.insert("end", int(cs / 2) - 1)
        # print(c)
    # print(mm)
    # print(type(mm))


def start_to3(event):
    # print("现在的位置是图片中的：", event.x, event.y)
    #x, y = q_ori(event.x, event.y)
    if if_open==0 :
        return
    global rect2_temp
    rect2_temp[0]=event.x
    rect2_temp[1]=event.y

def to_region_enter(event):
    # print("现在的位置是图片中的：", event.x, event.y)
    if if_open==0 :
        return
    global rect1_temp,rect2_temp,renum,renum2
    #x, y = q_ori(event.x, event.y)
    global rect1, rect2
    rect1.append([rect1_temp[0], rect1_temp[1]])
    rect2.append([rect2_temp[0], rect2_temp[1]])
    renum=renum+1
    renum2 = renum2 + 1
    c=["region-",str(int(renum2)),",(",str(rect1_temp[0]),",",str(rect1_temp[1]),"),(",str(rect2_temp[0]),",",str(rect2_temp[1]),")"]
    mm=''.join(c)
    region_list.insert("end", mm)
    bt_region.set("You haven't select a region")

    global v2int
    if v2int == 1:
        image = cv2.imread('img.png')
    if v2int == 2:
        image = cv2.imread('imnew.png')
    if v2int == 3:
        image = cv2.imread('imnew2.png')
    if v2int == 4:
        image = cv2.imread('imnew3.png')

    cv2.rectangle(image, (rect1_temp[0], rect1_temp[1]),
                  (rect2_temp[0], rect2_temp[1]), (0, 0, 255), 2)
    cv2.imwrite('mymytest.png', image)
    new = Image.open('mymytest.png')
    new_photo = ImageTk.PhotoImage(new)  # 创建tkinter兼容的图片
    image_box.x = new_photo
    image_box['image'] = new_photo
    image_box.pack()

    rect1_temp=[0,0]
    rect2_temp = [0, 0]


'''def select_region():
    global v22int
    if (region_list.curselection()!=()):
        if(v22int==1):
            num=int(region_list.curselection()[0])
            global v2int,cs
            if v2int==1 :
                image = cv2.imread('img.png')
            if v2int==2 :
                image = cv2.imread('imnew.png')
            if v2int==3 :
                image = cv2.imread('imnew2.png')
            if v2int==4 :
                image = cv2.imread('imnew3.png')

            if cs%2==1:   #单数则清空已经选了的
                cs=cs-1
            else:   #双数
                cv2.rectangle(image,(rect1[num][0],rect1[num][1]),(rect2[num][0],rect2[num][1]),(0,0,255),2)
                cv2.imwrite('mymytest.png',image)
                new = Image.open('mymytest.png')
                new_photo = ImageTk.PhotoImage(new)  # 创建tkinter兼容的图片
                image_box.x = new_photo
                image_box['image'] = new_photo
                image_box.pack()'''

def select_region(event):
    if if_open==0 :
        return
    global v22int,v22
    global renum, renum2
    global rect1, rect2
    if (region_list.curselection()!=()):
        num=int(region_list.curselection()[0]) #选中的是第几个
        global focus_region
        focus_region=num
        #不管选中第几个，都把group2改成1
        v22int=1
        v22.set(1)
        global v2int,cs
        if v2int==1 :
            image = cv2.imread('img.png')
        if v2int==2 :
            image = cv2.imread('imnew.png')
        if v2int==3 :
            image = cv2.imread('imnew2.png')
        if v2int==4 :
            image = cv2.imread('imnew3.png')

        cv2.rectangle(image,(rect1[num][0],rect1[num][1]),(rect2[num][0],rect2[num][1]),(0,255,255),2)
        cv2.imwrite('mymytest.png',image)
        new = Image.open('mymytest.png')
        new_photo = ImageTk.PhotoImage(new)  # 创建tkinter兼容的图片
        image_box.x = new_photo
        image_box['image'] = new_photo
        image_box.pack()

def to_region_del(event):
    if if_open==0 :
        return
    global v22int, v22
    global renum, renum2
    global rect1, rect2
    if (region_list.curselection() != ()):
        num = int(region_list.curselection()[0])  # 选中的是第几个
        # 不管选中第几个，都把group2改成1
        v22int = 1
        v22.set(1)
        global v2int, cs
        if v2int == 1:
            image = cv2.imread('img.png')
        if v2int == 2:
            image = cv2.imread('imnew.png')
        if v2int == 3:
            image = cv2.imread('imnew2.png')
        if v2int == 4:
            image = cv2.imread('imnew3.png')

        cv2.imwrite('mymytest.png', image)
        new = Image.open('mymytest.png')
        new_photo = ImageTk.PhotoImage(new)  # 创建tkinter兼容的图片
        image_box.x = new_photo
        image_box['image'] = new_photo
        image_box.pack()

        del rect1[num]
        del rect2[num]
        renum=renum-1
        region_list.delete(num)

def to_cluster_enter(event):
    global if_start_cluster,select_cluster,allcluster,annoedclu_num,annoedclu_index
    if (if_start_cluster == True):
        bt_cluster.set("Start to annotate cluster")
        if_start_cluster = False
        if annoedclu_index==annoedclu_num: #如果是新的cluster
            annoedclu_num=annoedclu_num+1
            allcluster.append(select_cluster)
            name_sub_str = id2label[int(ins_to_stuff[int(select_cluster[0])][1])].name
            c = ["Cluster NO.",str(int(annoedclu_num)), "- ", name_sub_str, " Class"]
            mm = ''.join(c)
            annoedclu.insert(annoedclu_num-1, mm)
        else:
            del allcluster[int(annoedclu_index)]
            allcluster.insert(int(annoedclu_index),select_cluster)
            name_sub_str = id2label[int(ins_to_stuff[int(select_cluster[0])][1])].name
            c = ["第", str(int(annoedclu_num)), "组cluster- ", name_sub_str, " 类"]
            mm = ''.join(c)
            annoedclu.delete(int(annoedclu_index))
            annoedclu.insert(int(annoedclu_index), mm)

        select_cluster=[]
        cluster_list.delete(0, "end")
        annoedclu_index=annoedclu_num


    else:
        bt_cluster.set("停止标注cluster")
        if_start_cluster = True

def select_cluster_list(event):
    if if_open==0 :
        return

    if (cluster_list.curselection() != ()):  # 如果不等于空了话，则执行后续
        num = int(cluster_list.curselection()[0])  # 选择的是第几条已有关系
        # sub_rel_ob[num][0] #sub的id
        # sub_rel_ob[num][1] #rel的id
        # sub_rel_ob[num][2] #ob的id
        global ins_to_stuff  # 实例id-所属类别id
        #global ob_id, rel_id, sub_id, name_ob_str, name_sub_str, name_rel_str
        # 判断一下是修改还是增加
        global select_cluster,cluster_list_index
        #global anno_num, anno_index
        cluster_list_index = num

        #bt_text.set("修改")
        #dele_text.set("删除")

# 删除关系
def deleclu(event):
    if if_open==0 :
        return
    global cluster_list_index,select_cluster
    del select_cluster[int(cluster_list_index)]
    cluster_list.delete(int(cluster_list_index))

def select_annoedclu(event):
    if if_open==0 :
        return
    if (annoedclu.curselection() != ()):  # 如果不等于空了话，则执行后续
        num = int(annoedclu.curselection()[0])  # 选择的是第几条已有关系
        # sub_rel_ob[num][0] #sub的id
        # sub_rel_ob[num][1] #rel的id
        # sub_rel_ob[num][2] #ob的id
        global ins_to_stuff  # 实例id-所属类别id
        #global ob_id, rel_id, sub_id, name_ob_str, name_sub_str, name_rel_str
        # 判断一下是修改还是增加
        global select_cluster,annoedclu_index
        global if_select_cluster
        global sub_id,name_sub_str
        #global anno_num, anno_index
        annoedclu_index = num #0 1

        if annoedclu_index == annoedclu_num : #说明选中了空白的
            select_cluster = []
            f_text.set(" ")
            b_text.set(" ")
            l_text.set(" ")
            r_text.set(" ")
            if_select_cluster=False
        else :
            select_cluster=allcluster[num]
            sub_id = int(select_cluster[0])
            sub_id = int(select_cluster[0])
            name_sub_str = id2label[int(ins_to_stuff[int(select_cluster[0])][1])].name

            # 显示主语
            name_sub_str = id2label[int(ins_to_stuff[int(select_cluster[0])][1])].name
            c = ["第", str(int(annoedclu_num)), "组cluster- ", name_sub_str, " 类"]
            mm = ''.join(c)
            name_sub.set(mm)
            if_select_cluster = True

            #批量方向标注开启
            f_text.set("  ↑  ")
            b_text.set("  ↓  ")
            l_text.set("  ←  ")
            r_text.set("  →  ")

            #批量关系标注开启


        cluster_list.delete(0,"end")
        for i in select_cluster: #在左侧列表中显示每一个内容
            name_sub_str = id2label[int(ins_to_stuff[int(i)][1])].name
            c = [str(int(i)), "-", name_sub_str]
            mm = ''.join(c)
            cluster_list.insert("end", mm)

def deleannoedclu(event):
    if if_open==0 :
        return
    global cluster_list_index,select_cluster,annoedclu_num,allcluster,annoedclu_index
    del allcluster[int(annoedclu_index)]
    annoedclu_num=annoedclu_num-1
    annoedclu.delete(int(annoedclu_index))
    annoedclu_index=annoedclu_num
    cluster_list.delete(0,"end")
    global if_select_cluster
    if_select_cluster=False
    f_text.set(" ")
    b_text.set(" ")
    l_text.set(" ")
    r_text.set(" ")


    #print("annoedclu_num:", annoedclu_num)
    #print("allcluster:", allcluster)

def to_auto(event):
    #先把Insid里面的东西融合
    global insid_cluster,ins_to_stuff_cluster,ins_to_stuff
    insid_cluster=copy.deepcopy(insid)
    ins_to_stuff_cluster = copy.deepcopy(ins_to_stuff)
    #inslis_cluster=[]

    inslen=len(ins_to_stuff_cluster) #是标准的长度，1-n共计n个

    for i in range(len(ins_to_stuff_cluster)): #i为0~insid的数量-1
        #对于每一个实例，判断一下有没有在聚类里。如果有，就改变他们的实例id：ins_to_stuff_cluster[i][0]。如果没有，实例编号不变。
        for j in range(len(allcluster)):
            if int(ins_to_stuff_cluster[i][0]) in allcluster[j]:
                ins_to_stuff_cluster[i][0]=inslen+j
                break

    for i in range(width):  # 2048
        for j in range(height):  # 1024
            insid_cluster[j, i]=int(ins_to_stuff_cluster[int(insid[j,i])][0])
    global region_rel_list
    region_rel_list = []
    auto_rel.delete(0, "end")
    global focus_region
    permu(int(focus_region))

    #print(ins_to_stuff)

    #排列组合

'''
def gzpd(subid,subkind,obid,obkind):
    if subkind in flatid:
    if 
'''
def inter_coor(aa,bb,cc,dd,ee,ff,gg,hh): #求两个矩阵相交的坐标和相交类型
    if aa<=ee and bb<=ff:
        if cc>=ee and cc<=gg and dd>=ff and dd<=hh:
            return([ee,ff],[cc,dd],1)
        if cc>=gg and dd>=ff and dd<=hh:
            return([ee,ff],[gg,dd],2)
        if cc>=ee and cc<=gg and dd>=hh:
            return([ee,ff],[cc,hh],3)
        if cc>=gg and dd>=hh:
            return([ee,ff],[gg,hh],4)
    if aa>=ee and aa<=gg and bb<=ff:
        if cc>=ee and cc<=gg and dd>=ff and dd<=hh:
            return([aa,ff],[cc,dd],5)
        if cc>=gg and dd>=ff and dd<=hh:
            return([aa,ff],[gg,dd],6)
        if cc>=ee and cc<=gg and dd>=hh:
            return([aa,ff],[cc,hh],7)
        if cc>=gg and dd>=hh:
            return([aa,ff],[gg,hh],8)
    if aa<=ee and bb>=ff and bb<=hh:
        if cc>=ee and cc<=gg and dd>=ff and dd<=hh:
            return([ee,bb],[cc,dd],9)
        if cc>=gg and dd>=ff and dd<=hh:
            return([ee,bb],[gg,dd],10)
        if cc>=ee and cc<=gg and dd>=hh:
            return([ee,bb],[cc,hh],11)
        if cc>=gg and dd>=hh:
            return([ee,bb],[gg,hh],12)
    if aa>=ee and aa<=gg and bb>=ff and bb<=hh:
        if cc>=ee and cc<=gg and dd>=ff and dd<=hh:
            return([aa,bb],[cc,dd],13)
        if cc>=gg and dd>=ff and dd<=hh:
            return([aa,bb],[gg,dd],14)
        if cc>=ee and cc<=gg and dd>=hh:
            return([aa,bb],[cc,hh],15)
        if cc>=gg and dd>=hh:
            return([aa,bb],[gg,hh],16)
    else:
        return([0,0],[0,0],0)


def rule_flat_to_flat(subid_old,subkind,obid_old,obkind,x1,y1,x2,y2):
    #先判断是否存在关系(对于群 因为和别的关系一样，所以认为选其中一个即可（还可以减少计算）)
    global ins_to_stuff_cluster
    inslen = len(ins_to_stuff_cluster)
    if subid_old >= inslen:  # 说明是融合的内容
        subid = int(allcluster[int(int(subid_old) - inslen)][0])  # 某一个融合的第一个实例的id
    else:
        subid = subid_old
    if obid_old >= inslen:  # 说明是融合的内容
        obid = int(allcluster[int(int(obid_old) - inslen)][0])  # 某一个融合的第一个实例的id
    else:
        obid = obid_old

    aa=ins_to_stuff[int(subid)][2]
    bb=ins_to_stuff[int(subid)][3]
    cc=ins_to_stuff[int(subid)][4]
    dd=ins_to_stuff[int(subid)][5]
    ee=ins_to_stuff[int(obid)][2]
    ff=ins_to_stuff[int(obid)][3]
    gg=ins_to_stuff[int(obid)][4]
    hh=ins_to_stuff[int(obid)][5]
    [inter_aa,inter_bb],[inter_cc,inter_dd],inter_type=inter_coor(aa,bb,cc,dd,ee,ff,gg,hh)
    if inter_type==0: #如果主语和宾语不相交，认为不存在关系
        #print("主语和宾语不相交")
        return(False,-1)
    else:
        [inter_ee,inter_ff],[inter_gg,inter_hh],inter_type2=inter_coor(inter_aa,inter_bb,inter_cc,inter_dd,x1,y1,x2,y2)
        if inter_type2==0: #如果相交区域和region不相交，认为不存在关系
            #print("相交区域和region不相交")
            return (False, -1)
        else: #主语宾语相交区域和region也相交
            for i in range(inter_ee, inter_gg):
                for j in range(inter_ff, inter_hh):
                    if((insid_cluster[j,i]==subid and insid_cluster[j+1,i]==obid) or (insid_cluster[j,i]==subid and insid_cluster[j,i+1]==obid) or
                        (insid_cluster[j, i] == obid and insid_cluster[j + 1, i] == subid) or (insid_cluster[j, i] == obid and insid_cluster[j, i + 1] == subid)):
                        if inter_type in [1,3,9,11]:#主语在右边（框2在左边）
                            return (True,55)
                        if inter_type in [6,8,14,16]:#主语在左边（框2在右边）
                            return (True,54)
                        if inter_type in [12,15]:#主语在上边（框2在下边）
                            return (True,56)
                        if inter_type in [2,5]:#主语在下边（框2在上边）
                            return (True,57)
                        if inter_type in [4,7,10]:#主语在中间（框2在周围边）
                            return (True,58)
                        if inter_type in [13]: #主语在周围边（框2在中间）
                            return (True,59)
            return(False,-1)#区域相交但是没有连接

def rule_flat_to_ob(subid_old, subkind, obid_old, obkind, x1, y1, x2, y2): #subid是物体的，obid是flat的
    global ins_to_stuff_cluster
    print("原本的subid", subid_old)
    print("原本的obid", obid_old)
    inslen=len(ins_to_stuff_cluster)
    if subid_old >= inslen:  # 说明是融合的内容
        subid = int(allcluster[int(int(subid_old) - inslen)][0]) # 某一个融合的第一个实例的id
    else:
        subid = subid_old

    if obid_old >= inslen:  # 说明是融合的内容
        obid = int(allcluster[int(int(obid_old) - inslen)][0]) # 某一个融合的第一个实例的id
    else:
        obid = obid_old
    print("新的subid", subid)
    print("新的obid", obid)
    aa = ins_to_stuff[int(subid)][2]
    bb = ins_to_stuff[int(subid)][3]
    cc = ins_to_stuff[int(subid)][4]
    dd = ins_to_stuff[int(subid)][5]
    ee = ins_to_stuff[int(obid)][2]
    ff = ins_to_stuff[int(obid)][3]
    gg = ins_to_stuff[int(obid)][4]
    hh = ins_to_stuff[int(obid)][5]
    #if_rel = False
    [inter_aa, inter_bb], [inter_cc, inter_dd], inter_type = inter_coor(aa, bb, cc, dd, ee, ff, gg, hh)
    num=0
    if inter_type == 0:  # 如果主语和宾语不相交，认为不存在关系。
        # print("主语和宾语不相交")
        return (False, -1)
    else:    #这里有个细节处理 对比flat_to_flat少了一个和region的相交，因为一般认为region已经和ob相交了
             # 并且不需要考虑矩形相交但是没有相交的情况，实在不行计数0就行
        #print("inter:",inter_aa, inter_cc,int(inter_bb+(inter_dd-inter_bb)/3*2), inter_dd)
        #if (subid == 2 and obid == 9):
        #    print(insid_cluster[inter_aa:inter_cc,int(inter_bb+(inter_dd-inter_bb)/3*2):inter_dd])
        #不是相交的1/3 而是Ob的1/3！
        #for i in range(inter_aa, inter_cc):
        #    for j in range(int(inter_bb+(inter_dd-inter_bb)/3*2), inter_dd): #取底部1/3
        for i in range(aa, cc):
            for j in range(int(bb+(dd-bb)/3*2), dd): #取底部1/3
                if (insid_cluster[j, i] == subid and insid_cluster[j + 1, i]==obid):   #如果相连了话 记录为1
                    num=num+1
                    #if_rel=True
                    break
        return(True,num)

def rule_ob_to_ob(subid, subkind, obid, obkind,num_one,num_two): #不用xy了 直接用两个global和num_two
    global region_rel_list
    #在region_rel_list_matrix的第0列找subid，并且在第4列找sub_flat
    #在region_rel_list_matrix的第0列找obbid，并且在第4列找ob_flat
    #如果两个都没有flat或者有一个没有flat 认为不存在关系。
    #否则 如果两个都有flat  在region_rel_list_matrix的第0列找sub_flat且在第2列找ob_flat，或者在第2列找sub_flat且在第0列找ob_flat
    #如果存在关系 则返回true-near 否则返回false--1
    obflatid=-1
    subflatid = -1
    #print("one",num_one)
    #print("two", num_two)
    for i in range(num_one,num_two):
        if region_rel_list[i][0] == obid and region_rel_list[i][4] == 1:
            obflatid = region_rel_list[i][2]
        if region_rel_list[i][0] == subid and region_rel_list[i][4] == 1:
            subflatid = region_rel_list[i][2]
    #print("subflatid", subflatid)
    #print("obflatid", obflatid)
    if obflatid==-1 or subflatid==-1:
        return(False,-1)
    else:
        #print("两个都存在平台")
        if obflatid==subflatid:
            return (True, 23)
        else:
            for i in range(num_one):#这里要改 要改成从总的里面找，而不是只从rel里面找
                if ((region_rel_list[i][0] == obflatid and region_rel_list[i][2] == subflatid) or (region_rel_list[i][0] == subflatid and region_rel_list[i][2] == obflatid)):
                    if region_rel_list[i][4]==0:
                        return(False,-1)
                    else:
                        return(True,23)
                else:
                    return (False, -1)

def ifexist(subid,obid): #判断主语和宾语的关系是否存在与已有列表
    for i in sub_rel_ob:
        if(i[0]==subid and i[2]==obid):
            return True
    return False

def attri_attach(subid_old,obid_old): #判断boundingbox接触性
    #ifattach=False
    global ins_to_stuff_cluster
    inslen = len(ins_to_stuff_cluster)
    if subid_old >= inslen:  # 说明是融合的内容
        subid = int(allcluster[int(int(subid_old) - inslen)][0])  # 某一个融合的第一个实例的id
        aa = ins_to_stuff[int(subid)][2]
        bb = ins_to_stuff[int(subid)][3]
        cc = ins_to_stuff[int(subid)][4]
        dd = ins_to_stuff[int(subid)][5]
        for i in range(1,len(allcluster[int(int(subid_old) - inslen)])): #除了第一个 后面的以此和第一个进行比较 选一个最小的
            if ins_to_stuff[int(i)][2]<aa:
                aa=ins_to_stuff[int(i)][2]
            if ins_to_stuff[int(i)][3]<bb:
                bb=ins_to_stuff[int(i)][3]
            if ins_to_stuff[int(i)][4]>cc:
                cc=ins_to_stuff[int(i)][4]
            if ins_to_stuff[int(i)][5]>dd:
                dd=ins_to_stuff[int(i)][5]
    else:
        subid = subid_old
        aa = ins_to_stuff[int(subid)][2]
        bb = ins_to_stuff[int(subid)][3]
        cc = ins_to_stuff[int(subid)][4]
        dd = ins_to_stuff[int(subid)][5]
    if obid_old >= inslen:  # 说明是融合的内容
        obid = int(allcluster[int(int(obid_old) - inslen)][0])  # 某一个融合的第一个实例的id
        ee = ins_to_stuff[int(obid)][2]
        ff = ins_to_stuff[int(obid)][3]
        gg = ins_to_stuff[int(obid)][4]
        hh = ins_to_stuff[int(obid)][5]
        for i in range(1, len(allcluster[int(int(obid_old) - inslen)])):  # 除了第一个 后面的以此和第一个进行比较 选一个最小的
            if ins_to_stuff[int(i)][2] < ee:
                ee = ins_to_stuff[int(i)][2]
            if ins_to_stuff[int(i)][3] < ff:
                ff = ins_to_stuff[int(i)][3]
            if ins_to_stuff[int(i)][4] > gg:
                gg = ins_to_stuff[int(i)][4]
            if ins_to_stuff[int(i)][5] > hh:
                hh = ins_to_stuff[int(i)][5]
    else:
        obid = obid_old
        ee = ins_to_stuff[int(obid)][2]
        ff = ins_to_stuff[int(obid)][3]
        gg = ins_to_stuff[int(obid)][4]
        hh = ins_to_stuff[int(obid)][5]
    [inter_aa, inter_bb], [inter_cc, inter_dd], inter_type = inter_coor(aa, bb, cc, dd, ee, ff, gg, hh)
    if inter_type == 0:  # 如果主语和宾语不相交，认为不存在关系
        ifattach=False
        if aa<=ee and cc<=ee: #aa在ee左边  这里的判断 and连接的两句 其中一句是废话。。算了不管了
            ifloca = 2
        if aa>=gg and cc>=gg:
            ifloca= 3
        if bb<=ff and dd<=ff:
            ifloca = 0
        if bb>=hh and dd>=hh:
            ifloca = 1
        # print("主语和宾语不相交")
        #return (False, -1)
    else:
        ifattach = True
        if inter_type in [1, 3, 9, 11]:  # 主语在右边（框2在左边）
            ifloca= 3
        if inter_type in [6, 8, 14, 16]:  # 主语在左边（框2在右边）
            ifloca = 2
        if inter_type in [12, 15]:  # 主语在上边（框2在下边）
            ifloca = 0
        if inter_type in [2, 5]:  # 主语在下边（框2在上边）
            ifloca = 1
        if inter_type in [4, 7, 10]:  # 主语在中间（框2在周围边）
            ifloca = 4
        if inter_type in [13]:  # 主语在周围边（框2在中间）
            ifloca = 4
    if abs((cc-aa)-(gg-ee))/(cc-aa)<(1/5) and abs((dd-bb)-(hh-ff))/(dd-bb)<(1/5):
        ifequ=True
    else:
        ifequ = False
    return (ifattach,ifequ,ifloca)


def permu(rei): #对第rei个region中涉及的元素进行排列组合  #这个编号是0~n-1
    #如果默认为-1，则自动标注整幅图
    if rei==-1:
        #10,10,   2048 1024
        x1=10
        y1=10
        x2=2040
        y2=1020
    #获取第rei个region的信息，包括起点和终点
    else:
        print(rect1)
        print(rect2)
        qd=rect1[rei]  #起点坐标和终点坐标
        zd=rect2[rei]
        x1,y1=q_ori(qd[0],qd[1])  #1结尾是起点，2结尾是终点
        x2,y2=q_ori(zd[0], zd[1])
    print(x1, x2, y1, y2)
    if x1>x2:
        x1,x2=x2,x1
    if y1 > y2:
        y1, y2 = y2, y1
    #获取第rei个region中的实例信息
    #print(x1,x2,y1,y2)
    #print(insid_cluster[y1:(y2 + 1),x1:(x2 + 1)])
    unique_data =np.unique(insid_cluster[y1:(y2 + 1),x1:(x2 + 1)]) #所有实例信息
    print(unique_data)
    aa=[jj for ii in allcluster for jj in ii]

    #按照 路面、物体的顺序排序
    new_uni_flat=[]
    new_uni_ob = []
    inslen=len(ins_to_stuff_cluster)
    for i in unique_data: #对unique进行排序，使得路面>物体，这样可以优先处理#1.路面和路面 2.路面和物体 3.物体和物体。
        if i>=inslen: #说明是融合的内容
            kind=ins_to_stuff_cluster[int(allcluster[int(int(i)-inslen)][0])][1]  #某一个融合的第一个实例的id
        else:
            kind=int(ins_to_stuff_cluster[int(i)][1])
        print("实例",i,"的类型是：",kind,id2label[int(kind)].name)

        if kind in flatid:
            new_uni_flat.append([i,kind])
            #print("属于flat")
        elif kind in noneid:
            print("属于未标注")
        else:
            new_uni_ob.append([i,kind])
            #print("不属于flat")
        #这样new_uni是[[实例id，类型]并且flat始终排列在前]
    print("ins to stuff clu",ins_to_stuff_cluster)
    print("flat:",new_uni_flat,"  ob:",new_uni_ob)

    global region_rel_list
    region_rel_list = []
    #flat和flat
    for i in range(len(new_uni_flat)): #宾语
        for j in range(i+1,len(new_uni_flat)):  # 主语
            #以后再添加判断是否标注，先默认全部没标注
            #print(j,i)
            #print("主语：",new_uni_flat[j][0],"-",id2label[int(new_uni_flat[j][1])].name,"  宾语：", new_uni_flat[i][0],"-",id2label[int(new_uni_flat[i][1])].name)
            #print(new_uni_flat[j][0], new_uni_flat[j][1], new_uni_flat[i][0], new_uni_flat[i][1],x1,y1,x2,y2)
            if ifexist(new_uni_flat[j][0],new_uni_flat[i][0])==False:
                rule_if_rel,rule_rel=rule_flat_to_flat(new_uni_flat[j][0], new_uni_flat[j][1], new_uni_flat[i][0], new_uni_flat[i][1],x1,y1,x2,y2)
            #rule_if_rel是是否存在关系 rule_rel是关系类型
                region_rel_list.append([new_uni_flat[j][0],new_uni_flat[j][1],new_uni_flat[i][0],new_uni_flat[i][1],rule_if_rel,rule_rel])
    #print(region_rel_list) 实验用的

    # flat和object
    #这个地方 可以变通一下，让ob和每一个flat都去试一下
    num_one = len(region_rel_list)  # 记录一下前面的数据大小
    for j in range(len(new_uni_ob)):  # 主语
        num_max_ob_to_flat = -1
        index_max_ob_to_flat = -1
        numob =0
        for i in range(len(new_uni_flat)):  # 宾语

            #判断是否为标注过的，如果没有，则numob=numob+1.判断是否有一方在cluster中，因为后面已经有cluster了，如果没有，则加1.
            if (ifexist(new_uni_ob[j][0], new_uni_flat[i][0]) == False) and (new_uni_ob[j][0] not in aa):
                numob = numob + 1 #记录的是这个ob中没有被删除
                print(j,i)
                print("主语：",new_uni_ob[j][0],"-",id2label[int(new_uni_ob[j][1])].name,"  宾语：", new_uni_flat[i][0],"-",id2label[int(new_uni_flat[i][1])].name)
            # print(new_uni_flat[j][0], new_uni_flat[j][1], new_uni_flat[i][0], new_uni_flat[i][1],x1,y1,x2,y2)
                rule_if_rel, rule_rel = rule_flat_to_ob(new_uni_ob[j][0], new_uni_ob[j][1], new_uni_flat[i][0],
                                                      new_uni_flat[i][1], x1, y1, x2, y2) #这次返回的 第一个是否连通 第二个是连通的个数
            # rule_if_rel是第一个是否连通 rule_rel是连通的个数
                if num_max_ob_to_flat < rule_rel: #直接记录下对每个ob来说最可能所处的flat
                    num_max_ob_to_flat=rule_rel
                    index_max_ob_to_flat = numob
                region_rel_list.append(
                    [new_uni_ob[j][0], new_uni_ob[j][1], new_uni_flat[i][0], new_uni_flat[i][1], rule_if_rel, rule_rel])
        #然后在这个位置 对前面处理过的关于主语ob  j  的flat再处理一遍
        numlist=len(region_rel_list)
        #print("对于主语",new_uni_ob[j][0],"修改前的regionlist",region_rel_list)
        if num_max_ob_to_flat==0:#全部都是false 没有在地面上
            for i in range(numlist - 1, numlist - numob - 1, -1):
                region_rel_list[i][4] = False
                region_rel_list[i][5] = -1
        else:
            for i in range(numlist-1,numlist-numob-1,-1):
                if i!=(numlist-numob+index_max_ob_to_flat-1):
                    region_rel_list[i][4] = False
                    region_rel_list[i][5] = -1
                else:
                    region_rel_list[i][5] = 4
        #print("对于主语", new_uni_ob[j][0], "修改后的regionlist", region_rel_list)
    print(region_rel_list)


    #object和object
    num_two = len(region_rel_list) #记录一下前面的数据大小
    global region_rel_list_matrix
    for i in range(len(new_uni_ob)):  # 宾语
        for j in range(i + 1, len(new_uni_ob)):  # 主语
            # 以后再添加判断是否标注，先默认全部没标注
            # gzpd(new_uni[j][0],new_uni[j][1],new_uni[i][0],new_uni[j][1]) #参数分别是：主语实例id 主语类型id 宾语实例id 宾语类型id
            if (ifexist(new_uni_ob[j][0], new_uni_ob[i][0]) == False) and (new_uni_ob[j][0] not in aa) and (new_uni_ob[i][0] not in aa):
                print("主语：", new_uni_ob[j][0], "-", id2label[int(new_uni_ob[j][1])].name, "  宾语：",
                        new_uni_ob[i][0], "-", id2label[int(new_uni_ob[i][1])].name)
                rule_if_rel, rule_rel = rule_ob_to_ob(new_uni_ob[j][0], new_uni_ob[j][1], new_uni_ob[i][0],new_uni_ob[i][1],num_one,num_two) #不用xy了
                region_rel_list.append([new_uni_ob[j][0], new_uni_ob[j][1], new_uni_ob[i][0], new_uni_ob[i][1], rule_if_rel, rule_rel])

    print(region_rel_list)
    #解码数据并输出到list中
    for i in range(len(region_rel_list)):
        if region_rel_list[i][4]==False:
            c=[str(int(region_rel_list[i][0])),":",id2label[int(region_rel_list[i][1])].name,"  ---          ---  ", str(int(region_rel_list[i][2])),":",id2label[int(region_rel_list[i][3])].name]
        else:
            c=[str(int(region_rel_list[i][0])),":",id2label[int(region_rel_list[i][1])].name,"  ---",rel_list_all[int(region_rel_list[i][5])],"---  ", str(int(region_rel_list[i][2])),":",id2label[int(region_rel_list[i][3])].name]
        auto_rel.insert("end",''.join(c))


def Recommend(sub_rel_ob,sub_rel_ob_attri,user, K):
    records=[]
    inslen = len(ins_to_stuff_cluster)
    for i in range(len(sub_rel_ob)):
        subkind, relkind, obidkind=int(sub_rel_ob[i][0]),int(sub_rel_ob[i][1]),int(sub_rel_ob[i][2])
        attri1, attri2, attri3=int(sub_rel_ob_attri[i][0]),int(sub_rel_ob_attri[i][1]),int(sub_rel_ob_attri[i][2])

        #if subid>=inslen: #说明是融合的内容
        #    subkind=ins_to_stuff_cluster[int(allcluster[int(int(subid)-inslen)][0])][1]  #某一个融合的第一个实例的id
        #else:
        #    subkind=int(ins_to_stuff_cluster[int(subid)][1])
        #print("实例",subid,"的类型是：",subkind,id2label[int(subkind)].name)
    #    if obid>=inslen: #说明是融合的内容
    #        obkind=ins_to_stuff_cluster[int(allcluster[int(int(obid)-inslen)][0])][1]  #某一个融合的第一个实例的id
    #    else:
    #        obkind=int(ins_to_stuff_cluster[int(obid)][1])
        #print("实例",subid,"的类型是：",obkind,id2label[int(obkind)].name)
    #    records.append([''.join([str(subkind),'-',str(obkind)]),str(rel),''.join([str(attri1),str(attri2),str(attri3)])])
    #print(records)

        records.append([''.join([str(subkind),'-',str(obkind)]),str(relkind),''.join([str(attri1),str(attri2),str(attri3)])])
        #print("制作records", subid, "的类型是：", obkind, id2label[int(obkind)].name)

    user_tags = dict()  # 语对打过标签的次数
    tag_items = dict()  # 关系被打过标签的次数，代表关系流行度
    for user, item, tag in records:
        user_tags.setdefault(user, dict())
        user_tags[user].setdefault(tag, 0)
        user_tags[user][tag] += 1
        tag_items.setdefault(tag, dict())
        tag_items[tag].setdefault(item, 0)
        tag_items[tag][item] += 1
        print(user, item, tag)
    print("语对打过标签的次数: ", user_tags)
    print("关系打过标签的次数: ", tag_items)

    recommend_items = dict()
    for tag, wut in user_tags[user].items():
        for item, wti in tag_items[tag].items():
            if item not in recommend_items:
                recommend_items[item] = wut * wti  # 计算用户对物品兴趣度
            else:
                recommend_items[item] += wut * wti

    rec = sorted(recommend_items.items(), key=lambda x: x[1], reverse=True)  # 将推荐歌曲按兴趣度排名
    print("语对对关系兴趣度: ", rec)
    reco_rel.delete(0, "end")
    #for i in rel_list_now:
    reco_rel.insert("end", rel_list_all[int(rec[0][0])])
    global recoid
    recoid = int(rec[0][0])

    #music = []
    #print(type(music))
    '''
    for i in range(K):
        music.append(rec[i][0])
        music = "/".join(music)
        print("为用户推荐歌曲: ", music)'''
    #return music

def to_reco(event):
    Recommend(sub_rel_ob,sub_rel_ob_attri,'car-car', 1)

def to_ts(event): #调试 输出重要数据
    print("file_name:",file_name)
    print("sub_rel_ob:", sub_rel_ob)
    print("sub_rel_ob_attri:", sub_rel_ob_attri)
    print("focus_region:", focus_region)
    print("allcluster:", allcluster)
    print("cluster_num:", cluster_num)
    print("cluster_list_index:",cluster_list_index)
    print("annoedclu_index:", annoedclu_index)
    print("auto_index:", auto_index)
    print("sub_id:", sub_id)
    print("ob_id:", ob_id)
    print("rel_id:",rel_id)
    print("direc:", direc)

def to_lx(event): #调试 输出重要数据
    print("file_name:",file_name)
    print("sub_rel_ob:", sub_rel_ob)
    print("sub_rel_ob_attri:", sub_rel_ob_attri)
    print("focus_region:", focus_region)
    print("allcluster:", allcluster)
    print("cluster_num:", cluster_num)
    print("cluster_list_index:",cluster_list_index)
    print("annoedclu_index:", annoedclu_index)
    print("auto_index:", auto_index)
    print("sub_id:", sub_id)
    print("ob_id:", ob_id)
    print("rel_id:",rel_id)
    print("direc:", direc)

def to_direc_f(event):#
    global sub_id,direc
    global if_select_cluster
    if if_select_cluster==True:
        for i in allcluster[annoedclu_index]:
            direc.append([int(i), 1])
            c = "↑     " + str(int(i)) + ":" + id2label[int(ins_to_stuff[int(i)][1])].name
            direc_list.insert("end", c)
    else:
        direc.append([sub_id,1])
        c = "↑     "+str(sub_id)+":"+id2label[int(ins_to_stuff[int(sub_id)][1])].name
        direc_list.insert("end",c)
    f_text.set(" ")
    b_text.set(" ")
    l_text.set(" ")
    r_text.set(" ")
    global name_sub_str,name_rel_str,name_ob_str
    name_sub.set("There is sub")
    name_rel.set("There is rel")
    name_ob.set("There is ob")
    name_sub_str = "NONE"
    name_rel_str = "NONE"
    name_ob_str = "NONE"
    if_select_cluster =False

def to_direc_b(event):#
    global sub_id,direc

    global if_select_cluster
    if if_select_cluster == True:
        for i in allcluster[annoedclu_index]:
            direc.append([int(i), 2])
            c = "↓     " + str(int(i)) + ":" + id2label[int(ins_to_stuff[int(i)][1])].name
            direc_list.insert("end", c)
    else:
        direc.append([sub_id, 2])
        c = "↓     " + str(sub_id) + ":" + id2label[int(ins_to_stuff[int(sub_id)][1])].name
        direc_list.insert("end", c)

    f_text.set(" ")
    b_text.set(" ")
    l_text.set(" ")
    r_text.set(" ")
    global name_sub_str,name_rel_str,name_ob_str
    name_sub.set("There is sub")
    name_rel.set("There is rel")
    name_ob.set("There is ob")
    name_sub_str = "NONE"
    name_rel_str = "NONE"
    name_ob_str = "NONE"
    if_select_cluster = False

def to_direc_l(event):#
    global sub_id,direc

    global if_select_cluster
    if if_select_cluster == True:
        for i in allcluster[annoedclu_index]:
            direc.append([int(i), 3])
            c = "←     " + str(int(i)) + ":" + id2label[int(ins_to_stuff[int(i)][1])].name
            direc_list.insert("end", c)
    else:
        direc.append([sub_id, 3])
        c = "←     " + str(sub_id) + ":" + id2label[int(ins_to_stuff[int(sub_id)][1])].name
        direc_list.insert("end", c)

    f_text.set(" ")
    b_text.set(" ")
    l_text.set(" ")
    r_text.set(" ")
    global name_sub_str,name_rel_str,name_ob_str
    name_sub.set("There is sub")
    name_rel.set("There is rel")
    name_ob.set("There is ob")
    name_sub_str = "NONE"
    name_rel_str = "NONE"
    name_ob_str = "NONE"
    if_select_cluster = False

def to_direc_r(event):#
    global sub_id,direc

    global if_select_cluster
    if if_select_cluster == True:
        for i in allcluster[annoedclu_index]:
            direc.append([int(i), 4])
            c = "→     " + str(int(i)) + ":" + id2label[int(ins_to_stuff[int(i)][1])].name
            direc_list.insert("end", c)
    else:
        direc.append([sub_id, 4])
        c = "→     " + str(sub_id) + ":" + id2label[int(ins_to_stuff[int(sub_id)][1])].name
        direc_list.insert("end", c)

    f_text.set(" ")
    b_text.set(" ")
    l_text.set(" ")
    r_text.set(" ")
    global name_sub_str,name_rel_str,name_ob_str
    name_sub.set("There is sub")
    name_rel.set("There is rel")
    name_ob.set("There is ob")
    name_sub_str = "NONE"
    name_rel_str = "NONE"
    name_ob_str = "NONE"
    if_select_cluster = False

def to_direc_dele(event):
    global direc,direc_list_index
    if direc_list_index!=-1:
        del direc[int(direc_list_index)]
        direc_list.delete(int(direc_list_index))
        direc_list_index=-1

window = tk.Tk()
window.title('GeneAnnotator')
w, h = window.maxsize()
window.minsize(1300, 750)
window.state("zoomed")

window2 = tk.Toplevel(bg='white')  # 显示场景图
window2.title('Real time Scene Graph')
window2.geometry('1300x600')

#tkinter.messagebox.showinfo('提示','人生苦短\n我')

########菜单部分
menubar = tk.Menu(window)  # menu属于窗口window
filemenu = tk.Menu(menubar, tearoff=0)  # 第一个filemenu属于menubar
helpmenu = tk.Menu(menubar, tearoff=0)  # 第2个filemenu属于menubar

###场景图初始相关
scene_graph = Digraph(comment='Scene Graph', format='png', engine='fdp')  # 先初始化一个场景图
scene_graph.render("anewsg.gv", view=False)  # 把文件保存成"anewsg.gv"和"anewsg.png"
mylis = []  # 记录已经生成的节点


menubar.add_cascade(label='File', menu=filemenu)
menubar.add_cascade(label='Help', menu=helpmenu)
# filemenu.add_command(label='New', command=lambda: new_file(image_box))  # 打开一张图
filemenu.add_command(label='New', command=new_file)  # 打开一张图
#filemenu.add_command(label='Open', command=open_file)  # 打开一个场景图标注 这个暂时被屏蔽了后续要添加
filemenu.add_command(label='Save', command=save_file)  # 保存成场景图标注 这个暂时被屏蔽了后续要添加
#filemenu.add_command(label='SGImage', command=sgimage_file)  # 场景图可视化
helpmenu.add_command(label='How to label...', command=howto_help)  # 如何使用
helpmenu.add_command(label='About us...', command=about_help)  # 如何使用
window.config(menu=menubar)
###########################

########GUI部分image_frm和sg_frm，分别有image_box和sg_box
# mycan = tk.Canvas(window)
image_frm = tk.Frame(window)
image_frm.place(relx=0, rely=0, anchor='nw')
# sg_frm = tk.Frame(window)
# sg_frm.pack(side='right')

image_image = Image.open('white.png')  # 创建Label组件，通过Image=photo设置要展示的图片
image_photo = ImageTk.PhotoImage(image_image)  # 创建tkinter兼容的图片

###从后面开始这一段 以后要注释

image_box = tk.Label(image_frm)  # 创建Label组件对象
image_box.x = image_photo
image_box['image'] = image_photo
image_box.state = "on"
image_box.pack()  # 展示Label对象
#
# rect.append(mycan.create_image(0,0,image= image_photo))  #这里添加的图片是没问题的

# image_test = Image.open('white.png')  # 创建Label组件，通过Image=photo设置要展示的图片
# image_photo_test = ImageTk.PhotoImage(image_test)  # 创建tkinter兼容的图片
# rect.append(mycan.create_image(0, 0, image=image_photo_test))  # 这里添加的图片是没问题的
# mycan.itemconfigure(rect[0],image=image_photo_test)


# mycan.create_rectangle(50,50,200,200,fill="red") #起始坐标和终止坐标


# rect.append(mycan.create_rectangle(10,10,110,110,fill="yellow"))
# mycan.tag_raise(rect[0]) #把rect里面的所有都raise一遍
# mycan.delete(rect[0])
# mycan.pack(side='left')


sg_box = tk.Label(window2)  # 创建Label组件对象

'''把这段挪到new按钮里面
sg_image = Image.open('anewsg.png')  # 创建Label组件，通过Image=photo设置要展示的图片
sg_photo = ImageTk.PhotoImage(sg_image)  # 创建tkinter兼容的图片
#想让sg_box这个label直接显示在window2上
sg_box = tk.Label(window2)  # 创建Label组件对象
sg_box.x = sg_photo
sg_box['image'] = sg_photo
sg_box.state = "on"
sg_box.pack()#展示Label对象
'''

bt_region = tk.StringVar()
bt_region.set("You haven\'t select a region")
region_enter = ttk.Button(window, textvariable=bt_region,width = 25)  # 确定关系键
region_enter.place(x=35, y=666, anchor='nw')

bt_region2 = tk.StringVar()
bt_region2.set("Delete this region")
region_del = ttk.Button(window, textvariable=bt_region2,width = 25)  # 确定关系键
region_del.place(x=35, y=706, anchor='nw')

group2 = ttk.LabelFrame(window, text='Region Display Mode')
group2.place(x=35, y=550, anchor='nw')


v22 = tk.IntVar()
v22.set(1)
v22int = 1

play12 = tk.Radiobutton(group2, text="One", variable=v22, value=1, command=play_func12,width=22,anchor='w')
play22 = tk.Radiobutton(group2, text="All", variable=v22, value=2, command=play_func22,width=22,anchor='w')
play32 = tk.Radiobutton(group2, text="None", variable=v22, value=3, command=play_func32,width=22,anchor='w')
play12.pack(anchor='w')
play22.pack(anchor='w')
play32.pack(anchor='w')

group = ttk.LabelFrame(window, text='Image Display Mode',width=100)
group.place(x=1100, y=10, anchor='nw')

v = tk.IntVar()
v.set(1)
v2int = 1

play1 = tk.Radiobutton(group, text="Original-Semantic Image", variable=v, value=1, command=play_func1,width=22,anchor='w')
play2 = tk.Radiobutton(group, text="Original Image", variable=v, value=2, command=play_func2,width=22,anchor='w')
play3 = tk.Radiobutton(group, text="Instance Image", variable=v, value=3, command=play_func3,width=22,anchor='w')
play4 = tk.Radiobutton(group, text="Semantic Image", variable=v, value=4, command=play_func4,width=22,anchor='w')
play1.pack(anchor='w')
play2.pack(anchor='w')
play3.pack(anchor='w')
play4.pack(anchor='w')



region_frm=tk.Frame(window,width=60, height=100)
region_scrollbar = ttk.Scrollbar(region_frm, orient="vertical")
region_list = tk.Listbox(region_frm, width=35, height=10, yscrollcommand=region_scrollbar.set)
region_scrollbar.config(command=region_list.yview)
region_scrollbar.pack(side="right", fill="y")
region_list.pack(side="left",fill="both", expand=True)
region_frm.place(x=250,y=550,anchor='nw')
#region_list = tk.Listbox(window)
#region_list.place(x=200,y=550,anchor='nw')

anno_rel_frm=tk.Frame(window,width=100, height=100)
anno_rel_scrollbar = ttk.Scrollbar(anno_rel_frm, orient="vertical")
anno_rel = tk.Listbox(anno_rel_frm, width=60, height=8, yscrollcommand=anno_rel_scrollbar.set)
anno_rel_scrollbar.config(command=anno_rel.yview)
anno_rel_scrollbar.pack(side="right", fill="y")
anno_rel.pack(side="left",fill="both", expand=True)
anno_rel_frm.place(x=580,y=550,anchor='nw')

anno_rel.insert("end", "")
anno_index = 0  # 创建一个索引，表示当前确认键要插入的位置
anno_num = 0  # 统计已经标记的个数

name_sub = tk.StringVar()
name_rel = tk.StringVar()
name_ob = tk.StringVar()
name_sub.set("There is subject")
name_rel.set("There is relationship")
name_ob.set("There is object")
name_sub_str = "NONE"
name_rel_str = "NONE"
name_ob_str = "NONE"
sub_id = -1
ob_id = -1
rel_id = -1

sub = tk.Label(window, width=25, height=2, textvariable=name_sub,relief='ridge')  # 当前主谓宾的label
rel = tk.Label(window, width=25, height=2, textvariable=name_rel,relief='ridge')
ob = tk.Label(window, width=25, height=2, textvariable=name_ob,relief='ridge')
sub.place(x=1100, y=150)
rel.place(x=1100, y=200)
ob.place(x=1100, y=250)
# rel_frm.pack()


bt_text = tk.StringVar()  # 按键的名字
bt_text.set("Enter")
certain = ttk.Button(window, textvariable=bt_text,width=25)  # 确定关系键
certain.place(x=1100, y=305)
dele_text = tk.StringVar()  # 按键的名字
dele_text.set("Delete this relationship")
#dele = ttk.Button(window, textvariable=dele_text)  # 删除键
dele = ttk.Button(window, text='Delete this relationship',width=60)
dele.place(x=580,y=706,anchor='nw')

now_rel_frm=tk.Frame(window,width=60, height=150)
now_rel_scrollbar = tk.Scrollbar(now_rel_frm, orient="vertical")
now_rel = tk.Listbox(now_rel_frm, width=26, height=34, yscrollcommand=now_rel_scrollbar.set)
now_rel_scrollbar.config(command=now_rel.yview)
now_rel_scrollbar.pack(side="right", fill="y")
now_rel.pack(side="left",fill="both", expand=True)
now_rel_frm.place(x=1100,y=350,anchor='nw')


reco_rel_frm=tk.Frame(window,width=60, height=100)
reco_rel_scrollbar = tk.Scrollbar(reco_rel_frm, orient="vertical")
reco_rel = tk.Listbox(reco_rel_frm, width=26, height=34, yscrollcommand=reco_rel_scrollbar.set)
reco_rel_scrollbar.config(command=reco_rel.yview)
reco_rel_scrollbar.pack(side="right", fill="y")
reco_rel.pack(side="left",fill="both", expand=True)
reco_rel_frm.place(x=1340,y=350,anchor='nw')

# = tk.Listbox(window, width=23, height=5)
#direc_set.place(x=1500,y=350,anchor='nw')

#direc_certain = tk.Button(window, text="确定方向")  # 确定关系键
#direc_certain.place(x=1700,y=350,anchor='nw')

f_text = tk.StringVar()  # 按键的名字
f_text.set(" ")
direc_f=ttk.Button(window, textvariable=f_text)
direc_f.place(x=1630,y=350,anchor='nw')

b_text = tk.StringVar()  # 按键的名字
b_text.set(" ")
direc_b=ttk.Button(window, textvariable=b_text)
direc_b.place(x=1630,y=420,anchor='nw')

l_text = tk.StringVar()  # 按键的名字
l_text.set(" ")
direc_l=ttk.Button(window, textvariable=l_text)
direc_l.place(x=1565,y=385,anchor='nw')

r_text = tk.StringVar()  # 按键的名字
r_text.set(" ")
direc_r=ttk.Button(window, textvariable=r_text)
direc_r.place(x=1695,y=385,anchor='nw')

direc_list_frm=tk.Frame(window,width=60, height=100)
direc_list_scrollbar = tk.Scrollbar(direc_list_frm, orient="vertical")
direc_list = tk.Listbox(direc_list_frm, width=26, height=15, yscrollcommand=direc_list_scrollbar.set)
direc_list_scrollbar.config(command=direc_list.yview)
direc_list_scrollbar.pack(side="right", fill="y")
direc_list.pack(side="left",fill="both", expand=True)
direc_list_frm.place(x=1580,y=480,anchor='nw')

direc_dele = ttk.Button(window, text="Delete this orientation",width=27)  # 确定关系键
direc_dele.place(x=1580,y=780,anchor='nw')

auto = ttk.Button(window, text="Start to Auto-Annotation",width=60)  # 确定关系键
auto.place(x=1340, y=16)

#reco = tk.Button(window, text="推荐")  # 确定关系键
#reco.place(x=1300, y=300)

auto_rel_frm=tk.Frame(window,width=100, height=400)
auto_rel_scrollbar = tk.Scrollbar(auto_rel_frm, orient="vertical")
auto_rel = tk.Listbox(auto_rel_frm, width=61, height=15, yscrollcommand=auto_rel_scrollbar.set)
auto_rel_scrollbar.config(command=auto_rel.yview)
auto_rel_scrollbar.pack(side="right", fill="y")
auto_rel.pack(side="left",fill="both", expand=True)
auto_rel_frm.place(x=1340,y=52,anchor='nw')

bt_cluster = tk.StringVar()
bt_cluster.set("Start to annotate cluster")
cluster_enter = ttk.Button(window, textvariable=bt_cluster,width =30)  # 确定关系键
cluster_enter.place(x=35, y=940, anchor='nw')

cluster_frm=tk.Frame(window,width=60, height=100)
cluster_scrollbar = tk.Scrollbar(cluster_frm, orient="vertical")
cluster_list = tk.Listbox(cluster_frm, width=66, height=8, yscrollcommand=cluster_scrollbar.set)
cluster_scrollbar.config(command=cluster_list.yview)
cluster_scrollbar.pack(side="right", fill="y")
cluster_list.pack(side="left",fill="both", expand=True)
cluster_frm.place(x=35,y=780,anchor='nw')

bt_cluster_dele = tk.StringVar()
bt_cluster_dele.set("Delete this instance")
cluster_dele = ttk.Button(window, textvariable=bt_cluster_dele,width = 30)  # 确定关系键
cluster_dele.place(x=290, y=940, anchor='nw')


annoedclu_frm=tk.Frame(window,width=100, height=100)
annoedclu_scrollbar = tk.Scrollbar(annoedclu_frm, orient="vertical")
annoedclu = tk.Listbox(annoedclu_frm, width=60, height=8, yscrollcommand=annoedclu_scrollbar.set)
annoedclu_scrollbar.config(command=annoedclu.yview)
annoedclu_scrollbar.pack(side="right", fill="y")
annoedclu.pack(side="left",fill="both", expand=True)
annoedclu_frm.place(x=580,y=780,anchor='nw')
annoedclu.insert("end", "")

bt_annoedclu_dele = tk.StringVar()
bt_annoedclu_dele.set("Delete this cluster")
annoedclu_dele = ttk.Button(window, textvariable=bt_annoedclu_dele,width=60)  # 确定关系键
annoedclu_dele.place(x=580,y=940, anchor='nw')

ts = ttk.Button(window, text="Print information",width=27)  # 确定关系键
ts.place(x=1580,y=840, anchor='nw')

#lx = tk.Button(window, text="连续in front")  # 确定关系键
#lx.place(x=1400,y=850, anchor='nw')



'''
##当鼠标移动到一个像素上并点击，所有实例id变色(暂时不处理，变成在图层下方显示当前的层次)
for i in range(width//k):
    for y in range(height//k):
        pixnew[x,y]=pix[x*k,y*k]
##根据层次弹出可选关系
###将选择的关系和主谓语进行编码
###对层次信息进行编码'''





# sg_box.bind("<Enter>", small_label)
image_box.bind("<Button-1>", select_sub)       #选择主语
image_box.bind("<Shift-Button-1>", select_ob)  #选择宾语
#image_box.bind("<Shift-Button-3>", start_to) #选择框
image_box.bind("<ButtonPress-3>", start_to1) #记录开始点
image_box.bind("<B3-Motion>", start_to2) #根据开始点和移动点随时绘制
image_box.bind("<ButtonRelease-3>", start_to3) #记录结束点
image_box.bind("<Control-Button-1>", select_direc) #标注方向

region_list.bind("<<ListboxSelect>>", select_region) #这句话的意思是选中的时候执行
#当选中一个框的时候 记录选中的id
region_enter.bind("<Button-1>", to_region_enter) #确认一个框
region_del.bind("<Button-1>", to_region_del) #删除一个框

certain.bind("<Button-1>", certainrel)
dele.bind("<Button-1>", delerel)
now_rel.bind("<<ListboxSelect>>", select_rel)  # 这句话的意思是选中的时候执行
anno_rel.bind("<<ListboxSelect>>", select_anno_rel)  # 这句话的意思是选中已有关系的时候

cluster_enter.bind("<Button-1>", to_cluster_enter)
cluster_list.bind("<<ListboxSelect>>", select_cluster_list)  # 这句话的意思是选中已有cluster实例（主要用于删除和显示是哪一个）
cluster_dele.bind("<Button-1>", deleclu)
annoedclu.bind("<<ListboxSelect>>", select_annoedclu)  # 这句话的意思是选中已有cluster实例（主要用于删除和显示是哪一个）
annoedclu_dele.bind("<Button-1>", deleannoedclu)

auto.bind("<Button-1>", to_auto)
auto_rel.bind("<<ListboxSelect>>", select_auto_rel)  # 这句话的意思是选中已有关系的时候
#reco.bind("<Button-1>", to_reco)

reco_rel.bind("<<ListboxSelect>>", select_reco_rel)

direc_f.bind("<Button-1>", to_direc_f)
direc_b.bind("<Button-1>", to_direc_b)
direc_r.bind("<Button-1>", to_direc_r)
direc_l.bind("<Button-1>", to_direc_l)

direc_dele.bind("<Button-1>", to_direc_dele)
direc_list.bind("<<ListboxSelect>>", select_direc_list)  # 这句话的意思是选中已有cluster实例（主要用于删除和显示是哪一个）


ts.bind("<Button-1>", to_ts)#调试 输出当前重要数据
#lx.bind("<Button-1>", to_lx)#调试 输出当前重要数据
# name_rel.set(now_rel.curselection("active"))

############################

window.mainloop()


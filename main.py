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
    a = path.split('/')
    
    global file_name
    #global oripicnum
    file_name = a[len(a) - 1]
    #file_name = '_'.join([name[0], name[1], name[2]])
    
    ins_name = file_name #最后一个地址
    ori_name = file_name
    stuff_name = file_name
    
    path_ins = ".\\ins\\"+file_name
    path_ori = ".\\ori\\"+file_name 
    path_stuff = ".\\stuff\\"+file_name
    

    return (path_ori, path_stuff, path_ins)



def encoding(stuff, ins):

    pix = ins.load()
    pix_stuff = stuff.load()

    global width,height
    width = ins.size[0]
    height = ins.size[1]
    insid = np.zeros((height, width))
    inslis = []  #
    stufflis = []  #
    ins_to_stuff = []  #
    zb = []  #

    ins_color=[(220, 20, 60,255),(255, 0, 0,255),(0, 0, 142,255),(0, 0, 70,255),(0, 60, 100,255),(0, 0, 90,255),(0, 0, 110,255),(0, 80, 100,255),(0, 0, 230,255),(119, 11, 32,255),(0, 0, 1,255)]


    for i in range(width):  # 2048
        for j in range(height):  # 1024

            if pix_stuff[i, j] != (0, 0, 0,255) and pix[i, j] == (0, 0, 0) and (pix_stuff[i, j] not in ins_color):

                pix[i, j]=pix_stuff[i, j]
            if (pix[i, j] not in inslis):
                inslis.append(pix[i, j])
                stufflis.append(pix_stuff[i, j])
                insid[j, i] = int(len(inslis) - 1)
                zb.append((i, j))
                new_stuff = [insid[j, i], color2label[pix_stuff[i, j][0:3]].id,i,j,i,j]
                ins_to_stuff.append(new_stuff)
            else:
                insid[j, i] = inslis.index(pix[i, j])
                if j<ins_to_stuff[int(insid[j, i])][3]:
                    ins_to_stuff[int(insid[j, i])][3]=j
                if j > ins_to_stuff[int(insid[j, i])][5]:
                    ins_to_stuff[int(insid[j, i])][5] = j
                if i > ins_to_stuff[int(insid[j, i])][4]:
                    ins_to_stuff[int(insid[j, i])][4] = i

    return (insid, ins_to_stuff)


def q_ori(x, y):
    global k
    ori_x = int(k * x)
    ori_y = int(k * y)
    return (ori_x, ori_y)


def q_id(x, y):
    global insid
    return insid[y, x]



def q_label(x, y):
    global insid
    global ins_to_stuff
    return ins_to_stuff[int(insid[y, x])][1]


def q_layer(myid):
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




def addTransparency(img, factor=0.7):
    img = img.convert('RGBA')
    img_blender = Image.new('RGBA', img.size, (0, 0, 0, 0))
    img = Image.blend(img_blender, img, factor)
    return img



def new_file():
    global if_open
    if if_open==1:
        return

    path = tk.filedialog.askopenfilename()
    if path=="" :
        return
    path_ori, path_stuff, path_ins = three_pic(path)

    ori = Image.open(path_ori)
    stuff = Image.open(path_stuff)
    ins = Image.open(path_ins)

    if_open = 1

    global k


    annoedclu.insert("end", "(Create a new cluster)")
    anno_rel.insert("end", "(Create a new relationship)")
    reco_rel.insert("end", "----Recommended----")

    global v2int,v22int
    v2int=1
    v22int = 1
    v.set(1)
    v22.set(1)

    global imnew, imnew2, imnew3, img, img_back
    im = Image.open(path_ori)
    pix = im.load()  #
    width = im.size[0]
    height = im.size[1]
    imnew = Image.new('RGB', (width // k, height // k), "red")
    pixnew = imnew.load()  #

    im2 = Image.open(path_ins)  #
    pix2 = im2.load()  #
    width2 = im2.size[0]
    height2 = im2.size[1]
    imnew2 = Image.new('RGB', (width2 // k, height2 // k), "red")
    pixnew2 = imnew2.load()  #

    im3 = Image.open(path_stuff)  #
    pix3 = im3.load()  #
    width3 = im3.size[0]
    height3 = im3.size[1]
    imnew3 = Image.new('RGB', (width3 // k, height3 // k), "red")
    pixnew3 = imnew3.load()  #

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
    insid, ins_to_stuff = encoding(stuff, ins)


    global rect
    new_photo = ImageTk.PhotoImage(img)
    image_box.x = new_photo
    image_box['image'] = new_photo
    image_box.pack()

    sg_image = Image.open('anewsg.gv.png')
    sg_photo = ImageTk.PhotoImage(sg_image)

    sg_box.x = sg_photo
    sg_box['image'] = sg_photo
    sg_box.state = "on"
    sg_box.pack()



    global insid_cluster, ins_to_stuff_cluster
    insid_cluster = copy.deepcopy(insid)
    ins_to_stuff_cluster = copy.deepcopy(ins_to_stuff)

    if(os.path.exists("motif_attr.h5")==False):
        f = h5.File('motif_attr.h5', 'w')
        f.create_dataset('motif_attr', data=[])
        f.create_dataset('motif_attr_attr', data=[])

    motif_attr = h5.File("motif_attr.h5", 'r')
    global m_a,m_a_a
    m_a = motif_attr['motif_attr'][:].tolist()
    m_a_a = motif_attr['motif_attr_attr'][:].tolist()


def open_file():
    global if_open
    if if_open==1:
        return

    path = tk.filedialog.askopenfilename()
    if path=="" :
        return

    path_ori, path_stuff, path_ins = open_three_pic(path)
    #print(path_ori, path_stuff, path_ins)

    ori = Image.open(path_ori)
    stuff = Image.open(path_stuff)
    ins = Image.open(path_ins)

    if_open = 1

    global k

    op_h5file = h5.File(path, 'r')
    global allcluster,allcluster_num,direc,rect2,rect1,sub_rel_ob,sub_rel_ob_attri
    allcluster = op_h5file['allcluster'][:].tolist()
    allcluster_num = op_h5file['allcluster_num'][:].tolist()
    direc = op_h5file['direc'][:].tolist()
    rect2 = op_h5file['rect2'][:].tolist()
    rect1 = op_h5file['rect1'][:].tolist()
    sub_rel_ob = op_h5file['sub_rel_ob'][:].tolist()
    sub_rel_ob_attri = op_h5file['sub_rel_ob_attri'][:].tolist()

    global renum,renum2
    for i in range(len(rect1)):
        renum = renum + 1
        renum2 = renum2 + 1
        c = ["region-", str(i+1), ",(", str(rect1[i][0]), ",", str(rect1[i][1]), "),(", str(rect2[i][0]),
             ",", str(rect2[i][1]), ")"]
        mm = ''.join(c)
        region_list.insert("end", mm)
        bt_region.set("Enter a region")



    annoedclu.insert("end", "(Create a new cluster)")
    anno_rel.insert("end", "(Create a new relationship)")
    reco_rel.insert("end", "----Recommended----")

    global v2int,v22int
    v2int=1
    v22int = 1
    v.set(1)
    v22.set(1)

    global imnew, imnew2, imnew3, img, img_back
    im = Image.open(path_ori)
    pix = im.load()  #
    width = im.size[0]
    height = im.size[1]
    imnew = Image.new('RGB', (width // k, height // k), "red")
    pixnew = imnew.load()  #

    im2 = Image.open(path_ins)  #
    pix2 = im2.load()  #
    width2 = im2.size[0]
    height2 = im2.size[1]
    imnew2 = Image.new('RGB', (width2 // k, height2 // k), "red")
    pixnew2 = imnew2.load()  #

    im3 = Image.open(path_stuff)  #
    pix3 = im3.load()  #
    width3 = im3.size[0]
    height3 = im3.size[1]
    imnew3 = Image.new('RGB', (width3 // k, height3 // k), "red")
    pixnew3 = imnew3.load()  #

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

    global insid
    global ins_to_stuff
    insid, ins_to_stuff = encoding(stuff, ins)
    global rect
    new_photo = ImageTk.PhotoImage(img)
    image_box.x = new_photo
    image_box['image'] = new_photo
    image_box.pack()

    sg_image = Image.open('anewsg.gv.png')
    sg_photo = ImageTk.PhotoImage(sg_image)
    sg_box.x = sg_photo
    sg_box['image'] = sg_photo
    sg_box.state = "on"
    sg_box.pack()

    #
    global insid_cluster, ins_to_stuff_cluster
    insid_cluster = copy.deepcopy(insid)
    ins_to_stuff_cluster = copy.deepcopy(ins_to_stuff)


    if(os.path.exists("motif_attr.h5")==False):
        f = h5.File('motif_attr.h5', 'w')
        f.create_dataset('motif_attr', data=[])
        f.create_dataset('motif_attr_attr', data=[])

    motif_attr = h5.File("motif_attr.h5", 'r')
    global m_a,m_a_a
    m_a = motif_attr['motif_attr'][:].tolist()
    m_a_a = motif_attr['motif_attr_attr'][:].tolist()


def save_file():
    global sub_rel_ob, ins_to_stuff_cluster,ins_to_stuff,insid_cluster, insid,rect1,rect2,sub_rel_ob_attri,allcluster,direc

    #print("sub_rel_ob:")
    #print(sub_rel_ob)
    #print("ins_to_stuff:")
    #print(ins_to_stuff)
    global file_name
    global oripicnum
    f = h5.File('.\\' + ''.join([file_name.split('.')[0], '.h5']), 'w')
    f.create_dataset('sub_rel_ob', data=sub_rel_ob)
    f.create_dataset('sub_rel_ob_attri', data=sub_rel_ob_attri)
    f.create_dataset('ins_to_stuff', data=ins_to_stuff)
    f.create_dataset('ins_to_stuff_cluster', data=ins_to_stuff_cluster)
    f.create_dataset('insid', data=insid)
    f.create_dataset('insid_cluster', data=insid_cluster)
    f.create_dataset('rect1', data=rect1)
    f.create_dataset('rect2', data=rect2)
    a = [j for i in allcluster for j in i]
    len_a = []
    for i in range(len(allcluster)):
        len_a.append(len(allcluster[i]))
    f.create_dataset('allcluster_num', data=len_a)
    f.create_dataset('allcluster', data=a)
    f.create_dataset('direc', data=direc)
    scene_graph_save = Digraph(comment='Scene Graph', format='png', engine='fdp')
    scene_graph_save = Source.from_file('alala.gv')
    scene_graph_save.render(''.join([file_name, '.gv']), view=False)
    scene_graph_save.render(''.join([file_name, '.gv']), format='png', view=False)

    fma = h5.File('.\\motif_attr.h5', 'w')
    global new_m_a, m_a, new_m_a_a, m_a_a

    out_m_a= new_m_a+m_a
    out_m_a_a = new_m_a_a + m_a_a
    fma.create_dataset('motif_attr', data=out_m_a)
    fma.create_dataset('motif_attr_attr', data=out_m_a_a)




def show_me_sgimage():
    scene_graph = Digraph(comment='Scene Graph', format='png', engine='fdp')

    global sub_rel_ob, ins_to_stuff


    mylis = []
    k = -1

    for i in sub_rel_ob:
        if i != [-1, -1, -1]:
            xx = (int(i[0]), id2label[
                ins_to_stuff[int(i[0])][1]].name)
            yy = (int(i[2]), id2label[ins_to_stuff[int(i[2])][1]].name)

            if (xx[0] not in mylis):
                mylis.append(xx[0])
                point_name = xx[0]
                point_context = xx[1]
                scene_graph.node('%s%s' % ('gt_boxes', point_name), '%s%s%s' % (point_name, "-", point_context),
                                 color="#000000", fillcolor="#f5d0e1", fontcolor="#000000", shape="box", style="filled")

            k = k + 1

            scene_graph.node('%s%s' % ('gt_rels', k), rel_list_all[int(i[1])], color="#000000", fillcolor="#c9fcd3",
                             fontcolor="#000000", style="filled")

            scene_graph.edge('%s%s' % ('gt_boxes', xx[0]), '%s%s' % ('gt_rels', k), color="#000000")
            if (yy[0] not in mylis):  # 看一下节点1有了没，如果没有则生成
                mylis.append(yy[0])
                point_name = yy[0]
                point_context = yy[1]
                scene_graph.node('%s%s' % ('gt_boxes', point_name), '%s%s%s' % (point_name, "-", point_context),
                                 color="#000000", fillcolor="#f5d0e1", fontcolor="#000000", shape="box", style="filled")
            scene_graph.edge('%s%s' % ('gt_rels', k), '%s%s' % ('gt_boxes', yy[0]), color="#000000")

    scene_graph.render("alala.gv", view=False)


    sg_image = Image.open('alala.gv.png')

    width = sg_image.size[0]
    height = sg_image.size[1]
    global w,h
    #print("wh",width,height)
    if (width>(w-100)) or (height>(h-100)):
        k=max(width/(w-100),height/(h-100))
        #print("k",k)
        target_size=(int(width/k),int(height/k))
        #print("ts", target_size)
        sg_image = sg_image.resize(target_size)


    sg_photo = ImageTk.PhotoImage(sg_image)

    sg_box.x = sg_photo
    sg_box['image'] = sg_photo
    sg_box.state = "on"
    sg_box.pack()

def howto_help():
    window3 = tk.Toplevel()
    window3.title('How to Annotate')
    window3.geometry('800x300')
    howto = tk.Label(window3,text='Select subject : Leftmouse click\n\n Select object : Shift + Leftmouse click\n\n Select the appropriate relationship and click "Enter" to confirm \n\nSelect region : Leftmouse dragging \n\nAnnotate the attribute : Ctrl + Leftmouse click You can watch the demo video.')
    howto.pack()

def about_help():
    window4 = tk.Toplevel()
    window4.title('About us')
    window4.geometry('700x300')
    aboutus = tk.Label(window4,text="Our github:")
    em = tk.Text(window4,width=90,height=1)
    em.insert('end', "https://github.com/Milomilo0320/A-Semi-automatic-Annotation-Software-for-Scene-Graph")
    em.config(state='disabled')
    aboutus.pack()
    em.pack()
    aboutus2 = tk.Label(window4,text="\n Email:zxzhang970320@163.com")
    aboutus2.pack()





def play_func1():
    if if_open==0 :
        return
    global v2int
    v2int = 1
    color_for_subnob(sub_id, ob_id)


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
                      (rect2[int(focus_region)][0], rect2[int(focus_region)][1]), (0, 255, 255), 2)
    cv2.imwrite('mymytest.png', image)
    new = Image.open('mymytest.png')
    new_photo = ImageTk.PhotoImage(new)
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
        cv2.rectangle(image, (rect1[i][0], rect1[i][1]), (rect2[i][0], rect2[i][1]), (0, 255, 255), 2)
    cv2.imwrite('mymytest.png', image)
    new = Image.open('mymytest.png')
    new_photo = ImageTk.PhotoImage(new)
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
    new_photo = ImageTk.PhotoImage(new)
    image_box.x = new_photo
    image_box['image'] = new_photo
    image_box.pack()


def small_label(self):
    #print(rel_list_all)
    pass


def q_dpic2(opic,idnum,mycolor):

    global insid,width,height,imnew,imnew2,imnew3,img,insid_cluster
    if mycolor==0:
        dpic_mini = Image.new('RGBA', (width // k, height // k), "red")
    if mycolor==1:
        dpic_mini = Image.new('RGBA', (width // k, height // k), "blue")
    if mycolor==2:
        dpic_mini = Image.new('RGBA', (width // k, height // k), "yellow")
    pixdpic_mini = dpic_mini.load()
    opic_rgba = opic.convert('RGBA')
    pixopic = opic_rgba.load()
    imnew_rgba=imnew.convert('RGBA')  #
    piximnew = imnew_rgba.load()  #
    for x in range(width // k):  # 2048
        for y in range(height // k):  # 1024
            if insid_cluster[y* k,x* k]!=idnum:  #
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
    sub_img = q_dpic2(myimg, sub_id, 0)  #
    new_photo = ImageTk.PhotoImage(sub_img)  #
    if ob_id !=-1:
        sub_img2 = q_dpic2(sub_img, ob_id, 1)

        new_photo = ImageTk.PhotoImage(sub_img2)
    image_box.x = new_photo
    image_box['image'] = new_photo
    image_box.pack()


#
def select_sub(event):
    if if_open==0 :
        return

    x, y = q_ori(event.x, event.y)

    global ob_id, rel_id, sub_id, name_ob_str, name_sub_str, name_rel_str, name_rel

    sub_id = q_id(x, y)
    name_sub.set(str(int(sub_id))+":"+str(id2label[q_label(x, y)].name))
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

    sub_img=q_dpic2(myimg,sub_id,0)
    new_photo = ImageTk.PhotoImage(sub_img)
    image_box.x = new_photo
    image_box['image'] = new_photo
    image_box.pack()

    if if_start_cluster == True:
        select_cluster.append(sub_id)
        c = [str(int(sub_id)), "-", name_sub_str]
        mm = ''.join(c)
        cluster_list.insert("end", mm)

    f_text.set(" ")
    b_text.set(" ")
    l_text.set(" ")
    r_text.set(" ")


def select_direc(event):
    if if_open==0 :
        return

    x, y = q_ori(event.x, event.y)

    global ob_id, rel_id, sub_id, name_ob_str, name_sub_str, name_rel_str, name_rel
    sub_id = q_id(x, y)
    name_sub.set(str(int(sub_id))+":"+str(id2label[q_label(x, y)].name))
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

    sub_img=q_dpic2(myimg,sub_id,2)
    new_photo = ImageTk.PhotoImage(sub_img)
    image_box.x = new_photo
    image_box['image'] = new_photo
    image_box.pack()


    f_text.set("  ↑  ")
    b_text.set("  ↓  ")
    l_text.set("  ←  ")
    r_text.set("  →  ")





def q_rel_list_now(a, b):
    rel_list_now = []
    global rel_list_now_id
    rel_list_now_id = []
    rel_list_now_type = rel_list_layer[(a - 1) * 5 + (b - 1)]

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


def popup_rel(sub_id, ob_id):
    rel_list_now = q_rel_list_now(q_layer(sub_id), q_layer(ob_id))
    now_rel.delete(0, "end")
    for i in rel_list_now:
        now_rel.insert("end", i)


def select_ob(event):
    if if_open==0 :
        return
    global ob_id, sub_id, rel_id, name_ob_str, name_rel_str, name_rel, name_ob
    if sub_id != -1:
        x, y = q_ori(event.x, event.y)
        ob_id = q_id(x, y)
        name_ob.set(str(int(ob_id))+":"+str(id2label[q_label(x, y)].name))
        name_ob_str = id2label[q_label(x, y)].name
        name_rel.set("There is rel")
        name_rel_str = "NONE"
        rel_id = -1
        popup_rel(sub_id, ob_id)
        Recommend(m_a, m_a_a, ''.join([str(int(ins_to_stuff[int(sub_id)][1])), '-', str(int(ins_to_stuff[int(ob_id)][1]))]), 5)

        global imnew, imnew2, imnew3, img, sub_img

        sub_img2 = q_dpic2(sub_img, ob_id, 1)
        new_photo = ImageTk.PhotoImage(sub_img2)
        image_box.x = new_photo
        image_box['image'] = new_photo
        image_box.pack()



def certainrel(event):
    if if_open==0 :
        return
    global sub_rel_ob,sub_rel_ob_attri
    global ob_id, sub_id, rel_id, sub_rel_ob
    global name_ob_str, name_sub_str, name_rel_str, name_sub, name_ob, name_rel
    a = [name_sub_str, name_rel_str, name_ob_str]
    b = "-"
    c = str(int(sub_id))+":"+name_sub_str+"  ---"+name_rel_str+"---  "+str(int(ob_id))+":"+name_ob_str

    global anno_num, anno_index,auto_index
    global region_rel_list,recoid
    newattri1,newattri2,newattri3=attri_attach(sub_id,ob_id)
    global if_select_cluster

    if if_select_cluster==True:

        anno_rel.delete(int(anno_index))
        del sub_rel_ob[int(anno_index)]
        del sub_rel_ob_attri[int(anno_index)]
        for i in allcluster[annoedclu_index]:
            c2 = str(int(i)) + ":" + name_sub_str + "  ---" + name_rel_str + "---  " + str(
                int(ob_id)) + ":" + name_ob_str
            anno_rel.insert("end", c2)

            sub_rel_ob.append([int(i), rel_id, ob_id])
            newattri12, newattri22, newattri32 = attri_attach(int(i), ob_id)
            sub_rel_ob_attri.append([newattri12, newattri22, newattri32])
            anno_num = anno_num + 1
        anno_rel.insert("end", "(Create a new relationship)")
        bt_text.set("Enter")
        dele_text.set("       ")
        sub_rel_ob.append([-1, -1, -1])
        sub_rel_ob_attri.append([-1, -1, -1])
        anno_index = anno_num
        anno_rel.activate(anno_index)
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

        if anno_index == -1 and auto_index != -1:

            sub_rel_ob.insert(int(anno_num), [sub_id, rel_id, ob_id])
            sub_rel_ob_attri.insert(int(anno_num), [newattri1,newattri2,newattri3])
            anno_rel.insert(int(anno_num), c)
            anno_num = anno_num + 1
            bt_text.set("Enter")
            dele_text.set("       ")

            del region_rel_list[int(auto_index)]
            auto_rel.delete(int(auto_index))

            anno_index = anno_num
            auto_index = -1
            anno_rel.activate(anno_index)
            name_sub.set("There is sub")
            name_rel.set("There is rel")
            name_ob.set("There is ob")
            name_sub_str = "NONE"
            name_rel_str = "NONE"
            name_ob_str = "NONE"


        else:

            anno_rel.delete(int(anno_index))
            anno_rel.insert(int(anno_index), c)

            del sub_rel_ob[int(anno_index)]
            del sub_rel_ob_attri[int(anno_index)]
            sub_rel_ob.insert(int(anno_index), [sub_id, rel_id, ob_id])
            sub_rel_ob_attri.insert(int(anno_index), [newattri1, newattri2, newattri3])
            if anno_index == anno_num:
                anno_num = anno_num + 1
                anno_rel.insert("end", "(Create a new relationship)")
                bt_text.set("Enter")
                dele_text.set("       ")
                sub_rel_ob.append([-1, -1, -1])
                sub_rel_ob_attri.append([-1, -1, -1])
            anno_index = anno_num
            anno_rel.activate(anno_index)

            name_sub.set("There is sub")
            name_rel.set("There is rel")
            name_ob.set("There is ob")
            name_sub_str = "NONE"
            name_rel_str = "NONE"
            name_ob_str = "NONE"
    show_me_sgimage()
    #print(sub_rel_ob)
    #print(sub_rel_ob_attri)
    reco_rel.delete(0, "end")
    recoid = []

def select_rel(event):
    if if_open==0 :
        return
    global name_rel_str, rel_id

    if (now_rel.curselection() != ()):
        if (rel_list_now_id[int(now_rel.curselection()[0])] != -1):

            value = now_rel.get(now_rel.curselection())
            name_rel.set(value)
            name_rel_str = value
            rel_id = rel_list_now_id[int(now_rel.curselection()[0])]

def select_direc_list(event):
    if if_open==0 :
        return
    global name_rel_str, rel_id,direc_list_index

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

        sub_img = q_dpic2(myimg, direc[direc_list_index][0], 2)
        new_photo = ImageTk.PhotoImage(sub_img)
        image_box.x = new_photo
        image_box['image'] = new_photo
        image_box.pack()


def select_anno_rel(event):
    if if_open==0 :
        return

    if (anno_rel.curselection() != ()):

        num = int(anno_rel.curselection()[0])

        global ins_to_stuff
        global ob_id, rel_id, sub_id, name_ob_str, name_sub_str, name_rel_str

        global anno_num, anno_index,auto_index
        anno_index = num
        auto_index=-1
        if anno_index == anno_num:
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

            global imnew, imnew2, imnew3, img
            if v2int == 1:
                image = img
            if v2int == 2:
                image = imnew
            if v2int == 3:
                image = imnew2
            if v2int == 4:
                image = imnew3

            new_photo = ImageTk.PhotoImage(image)
            image_box.x = new_photo
            image_box['image'] = new_photo
            image_box.pack()

        else:
            sub_id = int(sub_rel_ob[num][0])
            rel_id = int(sub_rel_ob[num][1])
            ob_id = int(sub_rel_ob[num][2])


            global ins_to_stuff_cluster
            inslen = len(ins_to_stuff_cluster)
            if sub_id >= inslen:
                subid = int(allcluster[int(int(sub_id) - inslen)][0])
            else:
                subid = sub_id
            if ob_id >= inslen:
                obid = int(allcluster[int(int(ob_id) - inslen)][0])
            else:
                obid = ob_id

            name_sub.set(str(int(sub_id))+":"+str(id2label[int(ins_to_stuff[subid][1])].name))
            name_sub_str = id2label[int(ins_to_stuff[subid][1])].name
            name_ob.set(str(int(ob_id))+":"+str(id2label[int(ins_to_stuff[obid][1])].name))
            name_ob_str = id2label[int(ins_to_stuff[obid][1])].name

            name_rel.set(rel_list_all[rel_id])
            name_rel_str = rel_list_all[rel_id]
            bt_text.set("Update")
            dele_text.set("Delete")

            color_for_subnob(sub_id,ob_id)
            popup_rel(subid, obid)

def select_reco_rel(event):
    if if_open==0 :
        return

    if (reco_rel.curselection() != ()):

        global rel_id,name_rel_str
        num = int(reco_rel.curselection()[0])
        rel_id = recoid[num-1]
        #print("rel_id",rel_id)

        if rel_id==-1:
            name_rel.set("NONE")
            name_rel_str = "NONE"
        else:
            name_rel.set(rel_list_all[rel_id])
            name_rel_str = rel_list_all[rel_id]


def select_auto_rel(event):
    if if_open==0 :
        return

    if (auto_rel.curselection() != ()):

        num = int(auto_rel.curselection()[0])

        global ins_to_stuff
        global ob_id, rel_id, sub_id, name_ob_str, name_sub_str, name_rel_str

        global auto_num, auto_index,region_rel_list,anno_index
        auto_index = num
        anno_index=-1
        sub_id = int(region_rel_list[num][0])
        rel_id = int(region_rel_list[num][5])
        ob_id = int(region_rel_list[num][2])


        global ins_to_stuff_cluster
        inslen = len(ins_to_stuff_cluster)
        if sub_id >= inslen:
            subid = int(allcluster[int(int(sub_id) - inslen)][0])
        else:
            subid = sub_id
        if ob_id >= inslen:
            obid = int(allcluster[int(int(ob_id) - inslen)][0])
        else:
            obid = ob_id

        name_sub.set(str(int(sub_id))+":"+str(id2label[int(ins_to_stuff[subid][1])].name))
        name_sub_str = id2label[int(ins_to_stuff[subid][1])].name
        name_ob.set(str(int(ob_id))+":"+str(id2label[int(ins_to_stuff[obid][1])].name))
        name_ob_str = id2label[int(ins_to_stuff[obid][1])].name

        if rel_id==-1:
            name_rel.set("NONE")
            name_rel_str = "NONE"
        else:
            name_rel.set(rel_list_all[rel_id])
            name_rel_str = rel_list_all[rel_id]
        bt_text.set("Update")
        dele_text.set("Delete")

        color_for_subnob(sub_id,ob_id)
        popup_rel(subid, obid)

        global m_a,m_a_a
        if len(m_a)<20:
            #print("数量不够")
            pass
        else:
            #print('reccc',[int(ins_to_stuff[subid][1]),int(ins_to_stuff[obid][1])],1)
            Recommend(m_a, m_a_a, ''.join([str(int(ins_to_stuff[subid][1])),'-',str(int(ins_to_stuff[obid][1]))]), 5)



def delerel(event):
    if if_open==0 :
        return
    global sub_rel_ob
    global anno_num, anno_index
    global ob_id, rel_id, sub_id, name_ob_str, name_sub_str, name_rel_str
    if anno_index != anno_num:
        anno_num = anno_num - 1
        anno_rel.delete(anno_index)
        del sub_rel_ob[int(anno_index)]
        del sub_rel_ob_attri[int(anno_index)]
        anno_index = anno_num
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
        bt_anno.set("Start to annotation")
        if_region = 1
    else:
        bt_anno.set("End to annotation")
        if_region = 0
        start_to()


def start_to1(event):

    if if_open==0 :
        return
    global rect1_temp
    rect1_temp[0]=event.x
    rect1_temp[1]=event.y
    bt_region.set("Enter a region")

def start_to2(event):

    if if_open==0 :
        return
    global rect1_temp

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
    new_photo = ImageTk.PhotoImage(new)
    image_box.x = new_photo
    image_box['image'] = new_photo
    image_box.pack()


def start_to3(event):

    if if_open==0 :
        return
    global rect2_temp
    rect2_temp[0]=event.x
    rect2_temp[1]=event.y

def to_region_enter(event):
    if if_open==0 :
        return
    global rect1_temp,rect2_temp,renum,renum2

    global rect1, rect2
    rect1.append([rect1_temp[0], rect1_temp[1]])
    rect2.append([rect2_temp[0], rect2_temp[1]])
    renum=renum+1
    renum2 = renum2 + 1
    c=["region-",str(int(renum2)),",(",str(rect1_temp[0]),",",str(rect1_temp[1]),"),(",str(rect2_temp[0]),",",str(rect2_temp[1]),")"]
    mm=''.join(c)
    region_list.insert("end", mm)
    bt_region.set("Enter a region")

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
                  (rect2_temp[0], rect2_temp[1]), (0, 255, 255), 2)
    cv2.imwrite('mymytest.png', image)
    new = Image.open('mymytest.png')
    new_photo = ImageTk.PhotoImage(new)
    image_box.x = new_photo
    image_box['image'] = new_photo
    image_box.pack()

    rect1_temp=[0,0]
    rect2_temp = [0, 0]


def select_region(event):
    if if_open==0 :
        return
    global v22int,v22
    global renum, renum2
    global rect1, rect2
    if (region_list.curselection()!=()):
        num=int(region_list.curselection()[0])
        global focus_region
        focus_region=num
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
        new_photo = ImageTk.PhotoImage(new)
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
        num = int(region_list.curselection()[0])
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
        new_photo = ImageTk.PhotoImage(new)
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
        if annoedclu_index==annoedclu_num:
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
            c = ["Cluster NO.", str(int(annoedclu_num)), "- ", name_sub_str, " Class"]
            mm = ''.join(c)
            annoedclu.delete(int(annoedclu_index))
            annoedclu.insert(int(annoedclu_index), mm)

        select_cluster=[]
        cluster_list.delete(0, "end")
        annoedclu_index=annoedclu_num


    else:
        bt_cluster.set("Stop to annotate cluster")
        if_start_cluster = True

def select_cluster_list(event):
    if if_open==0 :
        return

    if (cluster_list.curselection() != ()):
        num = int(cluster_list.curselection()[0])

        global ins_to_stuff

        global select_cluster,cluster_list_index

        cluster_list_index = num

def deleclu(event):
    if if_open==0 :
        return
    global cluster_list_index,select_cluster
    del select_cluster[int(cluster_list_index)]
    cluster_list.delete(int(cluster_list_index))

def select_annoedclu(event):
    if if_open==0 :
        return
    if (annoedclu.curselection() != ()):
        num = int(annoedclu.curselection()[0])

        global ins_to_stuff

        global select_cluster,annoedclu_index
        global if_select_cluster
        global sub_id,name_sub_str
        annoedclu_index = num #0 1

        if annoedclu_index == annoedclu_num :
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


            name_sub_str = id2label[int(ins_to_stuff[int(select_cluster[0])][1])].name
            c = ["Cluster NO.", str(int(annoedclu_num)), "- ", name_sub_str, " Class"]
            mm = ''.join(c)
            name_sub.set(mm)
            if_select_cluster = True

            f_text.set("  ↑  ")
            b_text.set("  ↓  ")
            l_text.set("  ←  ")
            r_text.set("  →  ")



        cluster_list.delete(0,"end")
        for i in select_cluster:
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



def to_auto(event):
    global insid_cluster,ins_to_stuff_cluster,ins_to_stuff
    insid_cluster=copy.deepcopy(insid)
    ins_to_stuff_cluster = copy.deepcopy(ins_to_stuff)
    #inslis_cluster=[]

    inslen=len(ins_to_stuff_cluster)

    for i in range(len(ins_to_stuff_cluster)):
        #print(len(allcluster))
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

def inter_coor(aa,bb,cc,dd,ee,ff,gg,hh):
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
    global ins_to_stuff_cluster
    inslen = len(ins_to_stuff_cluster)
    if subid_old >= inslen:
        subid = int(allcluster[int(int(subid_old) - inslen)][0])
    else:
        subid = subid_old
    if obid_old >= inslen:
        obid = int(allcluster[int(int(obid_old) - inslen)][0])
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
    if inter_type==0:
        return(False,-1)
    else:
        [inter_ee,inter_ff],[inter_gg,inter_hh],inter_type2=inter_coor(inter_aa,inter_bb,inter_cc,inter_dd,x1,y1,x2,y2)
        if inter_type2==0:

            return (False, -1)
        else:
            for i in range(inter_ee, inter_gg):
                for j in range(inter_ff, inter_hh):
                    if((insid_cluster[j,i]==subid and insid_cluster[j+1,i]==obid) or (insid_cluster[j,i]==subid and insid_cluster[j,i+1]==obid) or
                        (insid_cluster[j, i] == obid and insid_cluster[j + 1, i] == subid) or (insid_cluster[j, i] == obid and insid_cluster[j, i + 1] == subid)):

                        if inter_type in [1,3,9,11]:
                            return (True,38)
                        if inter_type in [6,8,14,16]:
                            return (True,39)
                        if inter_type in [12,15]:
                            return (True,41)
                        if inter_type in [2,5]:
                            return (True,40)
                        if inter_type in [4,7,10]:
                            return (True,43)
                        if inter_type in [13]:
                            return (True,42)
            return(False,-1)

def rule_flat_to_ob(subid_old, subkind, obid_old, obkind, x1, y1, x2, y2):
    global ins_to_stuff_cluster
    inslen=len(ins_to_stuff_cluster)
    if subid_old >= inslen:
        subid = int(allcluster[int(int(subid_old) - inslen)][0])
    else:
        subid = subid_old

    if obid_old >= inslen:
        obid = int(allcluster[int(int(obid_old) - inslen)][0])
    else:
        obid = obid_old
    aa = ins_to_stuff[int(subid)][2]
    bb = ins_to_stuff[int(subid)][3]
    cc = ins_to_stuff[int(subid)][4]
    dd = ins_to_stuff[int(subid)][5]
    ee = ins_to_stuff[int(obid)][2]
    ff = ins_to_stuff[int(obid)][3]
    gg = ins_to_stuff[int(obid)][4]
    hh = ins_to_stuff[int(obid)][5]

    [inter_aa, inter_bb], [inter_cc, inter_dd], inter_type = inter_coor(aa, bb, cc, dd, ee, ff, gg, hh)
    num=0
    if inter_type == 0:

        return (False, -1)
    else:

        for i in range(aa, cc):
            for j in range(int(bb+(dd-bb)/3*2), dd):
                if (insid_cluster[j, i] == subid and insid_cluster[j + 1, i]==obid):
                    num=num+1

                    break

        return(True,num)

def rule_ob_to_ob(subid, subkind, obid, obkind,num_one,num_two):
    global region_rel_list

    obflatid=-1
    subflatid = -1

    for i in range(num_one,num_two):
        if region_rel_list[i][0] == obid and region_rel_list[i][4] == 1:
            obflatid = region_rel_list[i][2]
        if region_rel_list[i][0] == subid and region_rel_list[i][4] == 1:
            subflatid = region_rel_list[i][2]

    if obflatid==-1 or subflatid==-1:
        return(False,-1)
    else:

        if obflatid==subflatid:
            return (True, 17)
        else:
            for i in range(num_one):
                if ((region_rel_list[i][0] == obflatid and region_rel_list[i][2] == subflatid) or (region_rel_list[i][0] == subflatid and region_rel_list[i][2] == obflatid)):
                    if region_rel_list[i][4]==0:
                        return(False,-1)
                    else:
                        return(True,17)
                else:
                    return (False, -1)

def ifexist(subid,obid):
    for i in sub_rel_ob:
        if(i[0]==subid and i[2]==obid):
            return True
    return False

def attri_attach(subid_old,obid_old):
    global ins_to_stuff_cluster
    inslen = len(ins_to_stuff_cluster)
    if subid_old >= inslen:
        subid = int(allcluster[int(int(subid_old) - inslen)][0])
        aa = ins_to_stuff[int(subid)][2]
        bb = ins_to_stuff[int(subid)][3]
        cc = ins_to_stuff[int(subid)][4]
        dd = ins_to_stuff[int(subid)][5]
        for i in range(1,len(allcluster[int(int(subid_old) - inslen)])):
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
    if obid_old >= inslen:
        obid = int(allcluster[int(int(obid_old) - inslen)][0])
        ee = ins_to_stuff[int(obid)][2]
        ff = ins_to_stuff[int(obid)][3]
        gg = ins_to_stuff[int(obid)][4]
        hh = ins_to_stuff[int(obid)][5]
        for i in range(1, len(allcluster[int(int(obid_old) - inslen)])):
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
    if inter_type == 0:
        ifattach=False
        if aa<=ee and cc<=ee:
            ifloca = 2
        if aa>=gg and cc>=gg:
            ifloca= 3
        if bb<=ff and dd<=ff:
            ifloca = 0
        if bb>=hh and dd>=hh:
            ifloca = 1

    else:
        ifattach = True
        if inter_type in [1, 3, 9, 11]:
            ifloca= 3
        if inter_type in [6, 8, 14, 16]:
            ifloca = 2
        if inter_type in [12, 15]:
            ifloca = 0
        if inter_type in [2, 5]:
            ifloca = 1
        if inter_type in [4, 7, 10]:
            ifloca = 4
        if inter_type in [13]:
            ifloca = 4
    if abs((cc-aa)-(gg-ee))/(cc-aa)<(1/5) and abs((dd-bb)-(hh-ff))/(dd-bb)<(1/5):
        ifequ=True
    else:
        ifequ = False
    return (ifattach,ifequ,ifloca)


def permu(rei):

    if rei==-1:

        x1=10
        y1=10
        x2=2040
        y2=1020

    else:
        #print(rect1)
        #print(rect2)
        qd=rect1[rei]
        zd=rect2[rei]
        x1,y1=q_ori(qd[0],qd[1])
        x2,y2=q_ori(zd[0], zd[1])
    #print(x1, x2, y1, y2)
    if x1>x2:
        x1,x2=x2,x1
    if y1 > y2:
        y1, y2 = y2, y1

    unique_data =np.unique(insid_cluster[y1:(y2 + 1),x1:(x2 + 1)])
    #print(unique_data)
    aa=[jj for ii in allcluster for jj in ii]

    new_uni_flat=[]
    new_uni_ob = []
    inslen=len(ins_to_stuff_cluster)
    for i in unique_data:
        if i>=inslen:
            kind=ins_to_stuff_cluster[int(allcluster[int(int(i)-inslen)][0])][1]
        else:
            kind=int(ins_to_stuff_cluster[int(i)][1])

        if kind in flatid:
            new_uni_flat.append([i,kind])
        elif kind in noneid:
            pass
        else:
            new_uni_ob.append([i,kind])

    #print("ins to stuff clu",ins_to_stuff_cluster)
    #print("flat:",new_uni_flat,"  ob:",new_uni_ob)

    global region_rel_list
    region_rel_list = []
    for i in range(len(new_uni_flat)):
        for j in range(i+1,len(new_uni_flat)):

            if ifexist(new_uni_flat[j][0],new_uni_flat[i][0])==False:
                rule_if_rel,rule_rel=rule_flat_to_flat(new_uni_flat[j][0], new_uni_flat[j][1], new_uni_flat[i][0], new_uni_flat[i][1],x1,y1,x2,y2)
                region_rel_list.append([new_uni_flat[j][0],new_uni_flat[j][1],new_uni_flat[i][0],new_uni_flat[i][1],rule_if_rel,rule_rel])

    num_one = len(region_rel_list)
    for j in range(len(new_uni_ob)):
        num_max_ob_to_flat = -1
        index_max_ob_to_flat = -1
        numob =0
        for i in range(len(new_uni_flat)):
            if (ifexist(new_uni_ob[j][0], new_uni_flat[i][0]) == False) and (new_uni_ob[j][0] not in aa):
                numob = numob + 1
                rule_if_rel, rule_rel = rule_flat_to_ob(new_uni_ob[j][0], new_uni_ob[j][1], new_uni_flat[i][0],
                                                      new_uni_flat[i][1], x1, y1, x2, y2)
                if num_max_ob_to_flat < rule_rel:
                    num_max_ob_to_flat=rule_rel
                    index_max_ob_to_flat = numob
                region_rel_list.append(
                    [new_uni_ob[j][0], new_uni_ob[j][1], new_uni_flat[i][0], new_uni_flat[i][1], rule_if_rel, rule_rel])
        numlist=len(region_rel_list)
        if num_max_ob_to_flat==0:
            for i in range(numlist - 1, numlist - numob - 1, -1):
                region_rel_list[i][4] = False
                region_rel_list[i][5] = -1
        else:
            for i in range(numlist-1,numlist-numob-1,-1):
                if i!=(numlist-numob+index_max_ob_to_flat-1):
                    region_rel_list[i][4] = False
                    region_rel_list[i][5] = -1
                else:
                    region_rel_list[i][5] = 2
    #print(region_rel_list)

    num_two = len(region_rel_list)
    global region_rel_list_matrix
    for i in range(len(new_uni_ob)):
        for j in range(i + 1, len(new_uni_ob)):
            if (ifexist(new_uni_ob[j][0], new_uni_ob[i][0]) == False) and (new_uni_ob[j][0] not in aa) and (new_uni_ob[i][0] not in aa):
                rule_if_rel, rule_rel = rule_ob_to_ob(new_uni_ob[j][0], new_uni_ob[j][1], new_uni_ob[i][0],new_uni_ob[i][1],num_one,num_two) #不用xy了
                region_rel_list.append([new_uni_ob[j][0], new_uni_ob[j][1], new_uni_ob[i][0], new_uni_ob[i][1], rule_if_rel, rule_rel])

    #print(region_rel_list)

    for i in range(len(region_rel_list)):
        if region_rel_list[i][4]==False:
            pass
            c=[str(int(region_rel_list[i][0])),":",id2label[int(region_rel_list[i][1])].name,"  ---          ---  ", str(int(region_rel_list[i][2])),":",id2label[int(region_rel_list[i][3])].name]
        else:

            c=[str(int(region_rel_list[i][0])),":",id2label[int(region_rel_list[i][1])].name,"  ---",rel_list_all[int(region_rel_list[i][5])],"---  ", str(int(region_rel_list[i][2])),":",id2label[int(region_rel_list[i][3])].name]
        auto_rel.insert("end",''.join(c))


def Recommend(sub_rel_ob,sub_rel_ob_attri,user2, K):
    records=[]
    records2=[]
    inslen = len(ins_to_stuff_cluster)
    for i in range(len(sub_rel_ob)):
        subkind, relkind, obkind=int(sub_rel_ob[i][0]),int(sub_rel_ob[i][1]),int(sub_rel_ob[i][2])
        attri1, attri2, attri3=int(sub_rel_ob_attri[i][0]),int(sub_rel_ob_attri[i][1]),int(sub_rel_ob_attri[i][2])

        records.append([''.join([str(subkind),'-',str(obkind)]),str(relkind),''.join([str(subkind),str(obkind),str(attri1),str(attri2),str(attri3)])])
        records2.append(str(subkind)+'-'+str(obkind))
    user_tags = dict()
    tag_items = dict()
    for user, item, tag in records:
        user_tags.setdefault(user, dict())
        user_tags[user].setdefault(tag, 0)
        user_tags[user][tag] += 1
        tag_items.setdefault(tag, dict())
        tag_items[tag].setdefault(item, 0)
        tag_items[tag][item] += 1
        #print(user, item, tag)

    recommend_items = dict()
    global recoid
    recoid=[]
    if user2 in records2:
        for tag, wut in user_tags[user2].items():
            for item, wti in tag_items[tag].items():
                if item not in recommend_items:
                    recommend_items[item] = wut * wti
                else:
                    recommend_items[item] += wut * wti

        rec = sorted(recommend_items.items(), key=lambda x: x[1], reverse=True)
        reco_rel.delete(0, "end")
        reco_rel.insert("end", "----Recommended----")
        for i in range(K):
            if i<len(rec):
                reco_rel.insert("end", rel_list_all[int(rec[i][0])])
                recoid.append(int(rec[i][0]))
    else:
        reco_rel.delete(0, "end")
        reco_rel.insert("end", "----Recommended----")
        recoid.append(-1)


def to_reco(event):
    Recommend(sub_rel_ob,sub_rel_ob_attri,'car-car', 1)

def to_ts(event):
    print("file_name:",file_name)
    #print("sub_rel_ob:", sub_rel_ob)
    #print("sub_rel_ob_attri:", sub_rel_ob_attri)
    #print("focus_region:", focus_region)
    #print("allcluster:", allcluster)
    #print("cluster_num:", cluster_num)
    #print("cluster_list_index:",cluster_list_index)
    #print("annoedclu_index:", annoedclu_index)
    #print("auto_index:", auto_index)
    #print("sub_id:", sub_id)
    #print("ob_id:", ob_id)
    #print("rel_id:",rel_id)
    #print("direc:", direc)

def to_lx(event):
    print("file_name:",file_name)
    #print("sub_rel_ob:", sub_rel_ob)
    #print("sub_rel_ob_attri:", sub_rel_ob_attri)
    #print("focus_region:", focus_region)
    #print("allcluster:", allcluster)
    #print("cluster_num:", cluster_num)
    #print("cluster_list_index:",cluster_list_index)
    #print("annoedclu_index:", annoedclu_index)
    #print("auto_index:", auto_index)
    #print("sub_id:", sub_id)
    #print("ob_id:", ob_id)
    #print("rel_id:",rel_id)
    #print("direc:", direc)

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
        c = "↑     "+str(int(sub_id))+":"+id2label[int(ins_to_stuff[int(sub_id)][1])].name
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
        direc.append([int(sub_id), 2])
        c = "↓     " + str(int(sub_id)) + ":" + id2label[int(ins_to_stuff[int(sub_id)][1])].name
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
        direc.append([int(sub_id), 3])
        c = "←     " + str(int(sub_id)) + ":" + id2label[int(ins_to_stuff[int(sub_id)][1])].name
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
        direc.append([int(sub_id), 4])
        c = "→     " + str(int(sub_id)) + ":" + id2label[int(ins_to_stuff[int(sub_id)][1])].name
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



###########################
########GUI Design

window = tk.Tk()
window.title('GeneAnnotator')
w, h = window.maxsize()
window.minsize(1300, 750)
window.state("zoomed")

window2 = tk.Toplevel(bg='white')
window2.title('Real time Scene Graph')
window2.geometry('1300x600')

menubar = tk.Menu(window)
filemenu = tk.Menu(menubar, tearoff=0)
helpmenu = tk.Menu(menubar, tearoff=0)

scene_graph = Digraph(comment='Scene Graph', format='png', engine='fdp')
scene_graph.render("anewsg.gv", view=False)
mylis = []


menubar.add_cascade(label='File', menu=filemenu)
menubar.add_cascade(label='Help', menu=helpmenu)
filemenu.add_command(label='New', command=new_file)
#filemenu.add_command(label='Open', command=open_file)   # todo
filemenu.add_command(label='Save', command=save_file)
helpmenu.add_command(label='How to annotate...', command=howto_help)
helpmenu.add_command(label='About us...', command=about_help)
window.config(menu=menubar)


image_frm = tk.Frame(window)
image_frm.place(relx=0, rely=0, anchor='nw')


image_image = Image.open('white.png')
image_photo = ImageTk.PhotoImage(image_image)


image_box = tk.Label(image_frm)
image_box.x = image_photo
image_box['image'] = image_photo
image_box.state = "on"
image_box.pack()


sg_box = tk.Label(window2,bg='white')


bt_region = tk.StringVar()
bt_region.set("Enter a region")
region_enter = ttk.Button(window, textvariable=bt_region,width = 25)
region_enter.place(x=35, y=666, anchor='nw')

bt_region2 = tk.StringVar()
bt_region2.set("Delete this region")
region_del = ttk.Button(window, textvariable=bt_region2,width = 25)
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


anno_rel_frm=tk.Frame(window,width=100, height=100)
anno_rel_scrollbar = ttk.Scrollbar(anno_rel_frm, orient="vertical")
anno_rel = tk.Listbox(anno_rel_frm, width=60, height=8, yscrollcommand=anno_rel_scrollbar.set)
anno_rel_scrollbar.config(command=anno_rel.yview)
anno_rel_scrollbar.pack(side="right", fill="y")
anno_rel.pack(side="left",fill="both", expand=True)
anno_rel_frm.place(x=580,y=550,anchor='nw')

anno_index = 0
anno_num = 0

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

sub = tk.Label(window, width=25, height=2, textvariable=name_sub,relief='ridge')
rel = tk.Label(window, width=25, height=2, textvariable=name_rel,relief='ridge')
ob = tk.Label(window, width=25, height=2, textvariable=name_ob,relief='ridge')
sub.place(x=1100, y=150)
rel.place(x=1100, y=200)
ob.place(x=1100, y=250)


bt_text = tk.StringVar()
bt_text.set("Enter")
certain = ttk.Button(window, textvariable=bt_text,width=25)
certain.place(x=1100, y=305)
dele_text = tk.StringVar()
dele_text.set("Delete this relationship")
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


f_text = tk.StringVar()
f_text.set(" ")
direc_f=ttk.Button(window, textvariable=f_text)
direc_f.place(x=1630,y=350,anchor='nw')

b_text = tk.StringVar()
b_text.set(" ")
direc_b=ttk.Button(window, textvariable=b_text)
direc_b.place(x=1630,y=420,anchor='nw')

l_text = tk.StringVar()
l_text.set(" ")
direc_l=ttk.Button(window, textvariable=l_text)
direc_l.place(x=1565,y=385,anchor='nw')

r_text = tk.StringVar()
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

direc_dele = ttk.Button(window, text="Delete this orientation",width=27)
direc_dele.place(x=1580,y=780,anchor='nw')

auto = ttk.Button(window, text="Select a region and CLICK HERE to Auto-Annotation",width=60)
auto.place(x=1340, y=16)


auto_rel_frm=tk.Frame(window,width=100, height=400)
auto_rel_scrollbar = tk.Scrollbar(auto_rel_frm, orient="vertical")
auto_rel = tk.Listbox(auto_rel_frm, width=61, height=15, yscrollcommand=auto_rel_scrollbar.set)
auto_rel_scrollbar.config(command=auto_rel.yview)
auto_rel_scrollbar.pack(side="right", fill="y")
auto_rel.pack(side="left",fill="both", expand=True)
auto_rel_frm.place(x=1340,y=52,anchor='nw')

bt_cluster = tk.StringVar()
bt_cluster.set("Start to annotate cluster")
cluster_enter = ttk.Button(window, textvariable=bt_cluster,width =30)
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
cluster_dele = ttk.Button(window, textvariable=bt_cluster_dele,width = 30)
cluster_dele.place(x=290, y=940, anchor='nw')


annoedclu_frm=tk.Frame(window,width=100, height=100)
annoedclu_scrollbar = tk.Scrollbar(annoedclu_frm, orient="vertical")
annoedclu = tk.Listbox(annoedclu_frm, width=60, height=8, yscrollcommand=annoedclu_scrollbar.set)
annoedclu_scrollbar.config(command=annoedclu.yview)
annoedclu_scrollbar.pack(side="right", fill="y")
annoedclu.pack(side="left",fill="both", expand=True)
annoedclu_frm.place(x=580,y=780,anchor='nw')

bt_annoedclu_dele = tk.StringVar()
bt_annoedclu_dele.set("Delete this cluster")
annoedclu_dele = ttk.Button(window, textvariable=bt_annoedclu_dele,width=60)
annoedclu_dele.place(x=580,y=940, anchor='nw')

ts = ttk.Button(window, text="Print information",width=27)
ts.place(x=1580,y=840, anchor='nw')



image_box.bind("<Button-1>", select_sub)
image_box.bind("<Shift-Button-1>", select_ob)
image_box.bind("<ButtonPress-3>", start_to1)
image_box.bind("<B3-Motion>", start_to2)
image_box.bind("<ButtonRelease-3>", start_to3)
image_box.bind("<Control-Button-1>", select_direc)

region_list.bind("<<ListboxSelect>>", select_region)
region_enter.bind("<Button-1>", to_region_enter)
region_del.bind("<Button-1>", to_region_del)

certain.bind("<Button-1>", certainrel)
dele.bind("<Button-1>", delerel)
now_rel.bind("<<ListboxSelect>>", select_rel)
anno_rel.bind("<<ListboxSelect>>", select_anno_rel)

cluster_enter.bind("<Button-1>", to_cluster_enter)
cluster_list.bind("<<ListboxSelect>>", select_cluster_list)
cluster_dele.bind("<Button-1>", deleclu)
annoedclu.bind("<<ListboxSelect>>", select_annoedclu)
annoedclu_dele.bind("<Button-1>", deleannoedclu)

auto.bind("<Button-1>", to_auto)
auto_rel.bind("<<ListboxSelect>>", select_auto_rel)


reco_rel.bind("<<ListboxSelect>>", select_reco_rel)

direc_f.bind("<Button-1>", to_direc_f)
direc_b.bind("<Button-1>", to_direc_b)
direc_r.bind("<Button-1>", to_direc_r)
direc_l.bind("<Button-1>", to_direc_l)

direc_dele.bind("<Button-1>", to_direc_dele)
direc_list.bind("<<ListboxSelect>>", select_direc_list)


ts.bind("<Button-1>", to_ts)#Print information

############################

window.mainloop()


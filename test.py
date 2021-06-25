import h5py as h5

imdb = h5.File("hamburg_000000_071675.h5", 'r')
sub_rel_ob = imdb['sub_rel_ob'][:].tolist()  # valid image indices
ins_to_stuff=imdb['ins_to_stuff'][:].tolist()

#print(sub_rel_ob)
print(ins_to_stuff)



'''
f = h5.File(''.join([file_name, '.h5']), 'w')
    f.create_dataset('sub_rel_ob', data=sub_rel_ob)
    f.create_dataset('sub_rel_ob_attri', data=sub_rel_ob_attri)
    f.create_dataset('ins_to_stuff', data=ins_to_stuff)
    f.create_dataset('ins_to_stuff_cluster', data=ins_to_stuff_cluster)
    f.create_dataset('insid', data=insid)
    f.create_dataset('insid_cluster', data=insid_cluster)
    f.create_dataset('rect1', data=rect1)
    f.create_dataset('rect2', data=rect2)
'''
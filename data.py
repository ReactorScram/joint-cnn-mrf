from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from scipy.io import loadmat
from scipy import misc
import numpy as np

"""
This script generate the x_train, x_test, y_train, y_test for the further process from the FLIC dataset.

x_train, x_test is [, 360, 240, 3], type = uint8, value is from 0 to 255 (unnormalized)

y_train, y_test is [, 90, 60, 11], type = uint16, you should divide it by 256 before any use

There're 3987 for training and 1016 for testing
"""

def downsample_cube(myarr,factor,ignoredim=0):
    """
    Downsample a 3D array by averaging over *factor* pixels on the last two
    axes.
    """
    if ignoredim > 0:
        myarr = myarr.swapaxes(0,ignoredim)
    zs,ys,xs = myarr.shape
    crarr = myarr[:,:ys-(ys % int(factor)),:xs-(xs % int(factor))]
    dsarr = np.mean(np.concatenate([[crarr[:,i::factor,j::factor]
        for i in range(factor)]
        for j in range(factor)]), axis=0)
    if ignoredim > 0: dsarr = dsarr.swapaxes(0,ignoredim)
    return dsarr


data_FLIC = loadmat('data_FLIC.mat')
data_FLIC = data_FLIC['examples'][0]
joint_ids = ['lsho', 'lelb', 'lwri', 'rsho', 'relb', 'rwri', 'lhip', 'rhip', 'nose']  # , 'leye', 'reye',
dict = {'lsho':0, 'lelb':1, 'lwri':2, 'rsho':3, 'relb':4, 'rwri':5, 'lhip':6,
                 'lkne':7, 'lank':8, 'rhip':9, 'rkne':10, 'rank':11, 'leye':12, 'reye':13,
                 'lear':14, 'rear':15, 'nose':16, 'msho':17, 'mhip':18, 'mear':19, 'mtorso':20,
                 'mluarm':21, 'mruarm':22, 'mllarm':23, 'mrlarm':24, 'mluleg':25, 'mruleg':26,
                'mllleg':27, 'mrlleg':28}
is_train = [data_FLIC[i][7][0, 0] for i in range(len(data_FLIC))]
is_train = np.array(is_train)
train_index = list(np.where(is_train == 1))[0]
test_index = list(np.array(np.where(is_train == 0)))[0]
print(len(train_index), len(test_index))
coefs = np.array([[1, 8, 28, 56, 70, 56, 28, 8, 1]], dtype=np.uint16)  # 1 / 256 *
kernel = coefs.T @ coefs
temp = np.int((len(kernel)-1) / 2)
print(temp)
pad = 5  # use padding to avoid the exceeding of the boundary

### This part is for x_train
x_train = []
for i in range(len(train_index)):
    img = misc.imread('./images_FLIC/' + data_FLIC[i][3][0])
    img = downsample_cube(img, 2, ignoredim=2)  # the third dim

    img = img.astype(np.uint8)
    img = img.swapaxes(0, 1)
    # img = img / 255

    x_train.append(img)
x_train = np.array(x_train)

### This part is for x_test
x_test = []
for i in range(len(test_index)):
    img = misc.imread('./images_FLIC/' + data_FLIC[i][3][0])
    img = downsample_cube(img, 2, ignoredim=2)  # the third dim

    img = img.astype(np.uint8)
    img = img.swapaxes(0, 1)
    # img = img / 255
    x_test.append(img)
x_test = np.array(x_test)

print(x_train.shape, x_test.shape)
print(type(x_train), type(x_test))
np.save('x_train_flic', x_train)
np.save('x_test_flic', x_test)

### This part is for y_train
# i = 0
x_train_hmap = []
for i in range(len(train_index)):
    hmap = []
    for joint in joint_ids:
        print(joint)
        id = dict[joint]
        coords = data_FLIC[i][2][:, id] / 8  # divided by 8
        coords[0] = np.int(coords[0])
        coords[1] = np.int(coords[1])
        if coords[0]>90:
            coords[0] = 90
        if coords[0]<0:
            coords[0] = 0
        if coords[1]>60:
            coords[1] = 60
        if coords[1]<0:
            coords[1] = 0

        heat_map = np.zeros([90, 60], dtype=np.uint16)  # 90 by 60
        heat_map = np.lib.pad(heat_map, ((pad,pad), (pad,pad)), 'constant', constant_values=0)
        # print(heat_map.shape)
        # print(data_FLIC[i][2][:, id])
        print(i, joint)
        coords = coords + pad
        print(coords)
        heat_map[np.int(coords[0] - temp):np.int(coords[0] + temp + 1),
            np.int(coords[1] - temp):np.int(coords[1] + temp + 1)] = kernel
        # a = heat_map[327-4:327+4+1, 213-4:213+4+1]
        heat_map = heat_map[pad:pad+90, pad:pad+60]
        print(heat_map.shape)
        hmap.append(heat_map)
    hmap = np.array(hmap)
    hmap = hmap.swapaxes(0, 1)
    hmap = hmap.swapaxes(1, 2)
    print(hmap.shape)

    x_train_hmap.append(hmap)
x_train_hmap = np.array(x_train_hmap)
print(x_train_hmap.shape)
np.save('y_train_flic', x_train_hmap)


### This part is for y_test
x_test_hmap = []
for i in range(len(test_index)):
    hmap = []
    for joint in joint_ids:
        print(joint)
        id = dict[joint]
        coords = data_FLIC[i][2][:, id] / 8  # divided by 8
        coords[0] = np.int(coords[0])
        coords[1] = np.int(coords[1])
        if coords[0]>90:
            coords[0] = 90
        if coords[0]<0:
            coords[0] = 0
        if coords[1]>60:
            coords[1] = 60
        if coords[1]<0:
            coords[1] = 0
        print(coords)
        heat_map = np.zeros([90, 60], dtype=np.uint16)  # 90 by 60
        heat_map = np.lib.pad(heat_map, ((pad,pad), (pad,pad)), 'constant', constant_values=0)
        # print(heat_map.shape)
        # print(data_FLIC[i][2][:, id])
        # print(i, joint)
        coords = coords + pad
        heat_map[np.int(coords[0] - temp):np.int(coords[0] + temp + 1),
            np.int(coords[1] - temp):np.int(coords[1] + temp + 1)] = kernel
        # a = heat_map[327-4:327+4+1, 213-4:213+4+1]
        heat_map = heat_map[pad:pad+90, pad:pad+60]
        print(heat_map.shape)
        hmap.append(heat_map)
    hmap = np.array(hmap)
    hmap = hmap.swapaxes(0, 1)
    hmap = hmap.swapaxes(1, 2)
    print(hmap.shape)

    x_test_hmap.append(hmap)
x_test_hmap = np.array(x_test_hmap)
print(x_test_hmap.shape)
np.save('y_test_flic', x_test_hmap)

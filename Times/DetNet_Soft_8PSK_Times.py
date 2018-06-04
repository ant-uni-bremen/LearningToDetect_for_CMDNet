#!/usr/bin/env python
import tensorflow as tf
import numpy as np
import time as tm
import math
import sys
import pickle as pkl


def find_nearest_mpsk_np(value):
    min_dist = 999
    ret_Val = 0
    dist = np.square(value - 1)
    if dist < min_dist:
        min_dist=dist
        ret_Val = 1
    
    dist = np.square(value  - 1.0/np.sqrt(2))
    if dist < min_dist:
        min_dist=dist
        ret_Val = 1.0/np.sqrt(2)
    
    dist = np.square(value - 0)
    if dist < min_dist:
        min_dist=dist
        ret_Val = 0
    
    dist = np.square(value + 1.0/np.sqrt(2))
    if dist < min_dist:
        min_dist=dist
        ret_Val = -1.0/np.sqrt(2)
    
    dist = np.square(value + 1.0)
    if dist < min_dist:
        min_dist=dist
        ret_Val = -1
    return ret_Val

def find_nearest(values):
    values = values + 3
    values = values/2
    values = tf.clip_by_value(values,0,3)
    values = tf.round(values)
    values = values * 2
    values = values - 3
    return values

"""Data generation for train and test phases
In this example, both functions are the same.
This duplication is in order to easily allow testing cases where the test is over different distributions of data than in the training phase.
e.g. training over gaussian i.i.d. channels and testing over a specific constant channel.
currently both test and train are over i.i.d gaussian channel.
"""




def validate4(y, SNR, H, K, N):
    final_probs_sqrt2 = np.zeros((K))
    final_probs_one = np.zeros((K))
    final_probs_minus_one = np.zeros((K))
    final_probs_minus_sqrt2 = np.zeros((K))
    final_probs_zero     = np.zeros((K))
    sum_plus_sqrt2  = 0
    sum_plus = 0
    sum_minus = 0
    sum_minus_sqrt2 = 0
    sum_zero = 0
    
    all_pos = np.array(np.meshgrid([1, -1, 0,-1/np.sqrt(2),1/np.sqrt(2)],[1, -1, 0,-1/np.sqrt(2),1/np.sqrt(2)],[1, -1, 0,-1/np.sqrt(2),1/np.sqrt(2)],[1, -1, 0,-1/np.sqrt(2),1/np.sqrt(2)],
                                    [1, -1, 0,-1/np.sqrt(2),1/np.sqrt(2)],[1, -1, 0,-1/np.sqrt(2),1/np.sqrt(2)],[1, -1, 0,-1/np.sqrt(2),1/np.sqrt(2)],[1, -1, 0,-1/np.sqrt(2),1/np.sqrt(2)])).T.reshape(-1,2*4)
    for i in range(len(all_pos)):
        x= all_pos[i]
        tmp_snr = (H.T.dot(H)).trace()/ K
        H_tmp = H / np.sqrt(tmp_snr) * np.sqrt(SNR)
        y_temp = x.dot(H_tmp)

        prob = np.exp(-0.5 * (np.sum(np.power(y_temp[jj] - y[jj], 2) for jj in range(N))))

        for ii in range(K):
            if x[ii] == 1/np.sqrt(2):
                final_probs_sqrt2[ii] = final_probs_sqrt2[ii] + ((1.0 / np.power(2, K)) * prob)
                sum_plus_sqrt2 = sum_plus_sqrt2 + 1
            if x[ii] == 1:
                final_probs_one[ii] = final_probs_one[ii] + ((1.0 / np.power(2, K)) * prob)
                sum_plus = sum_plus + 1
            if x[ii] == -1:
                final_probs_minus_one[ii] = final_probs_minus_one[ii] + ((1.0 / np.power(2, K)) * prob)
                sum_minus = sum_minus + 1
            if x[ii] == -1/np.sqrt(2):
                final_probs_minus_sqrt2[ii] = final_probs_minus_sqrt2[ii] + ((1.0 / np.power(2, K)) * prob)
                sum_minus_sqrt2 = sum_minus_sqrt2 + 1
            if x[ii] == 0:
                final_probs_zero[ii] = final_probs_zero[ii] + ((1.0 / np.power(2, K)) * prob)
                sum_zero = sum_zero + 1                
    for ii in range(K):
        norm = final_probs_one[ii] + final_probs_minus_one[ii] + final_probs_minus_sqrt2[ii] + final_probs_sqrt2[ii] + final_probs_zero[ii]
        final_probs_one[ii] = final_probs_one[ii] / norm
        final_probs_minus_one[ii] = final_probs_minus_one[ii] / norm
        final_probs_minus_sqrt2[ii] = final_probs_minus_sqrt2[ii]/norm
        final_probs_sqrt2[ii] = final_probs_sqrt2[ii]/norm       
        final_probs_zero[ii] = final_probs_zero[ii]/norm
    # if(any(0.8>ff>0.2  for ff in final_probs_one)):
    #    print(Real_X)
    #	print(final_probs_one)
    #	print(final_probs_minus_one)
    return final_probs_one, final_probs_minus_one,final_probs_minus_sqrt2,final_probs_sqrt2 , final_probs_zero

def validate3(y, SNR, H, K, N):
    final_probs_sqrt2 = np.zeros((K))
    final_probs_one = np.zeros((K))
    final_probs_minus_one = np.zeros((K))
    final_probs_minus_sqrt2 = np.zeros((K))
    final_probs_zero     = np.zeros((K))
    sum_plus_sqrt2  = 0
    sum_plus = 0
    sum_minus = 0
    sum_minus_sqrt2 = 0
    sum_zero = 0
    
    all_pos = np.array(np.meshgrid([1, -1, 0,-1/np.sqrt(2),1/np.sqrt(2)],[1, -1, 0,-1/np.sqrt(2),1/np.sqrt(2)],[1, -1, 0,-1/np.sqrt(2),1/np.sqrt(2)],
                                    [1, -1, 0,-1/np.sqrt(2),1/np.sqrt(2)],[1, -1, 0,-1/np.sqrt(2),1/np.sqrt(2)],[1, -1, 0,-1/np.sqrt(2),1/np.sqrt(2)])).T.reshape(-1,2*3)
    for i in range(len(all_pos)):
        x= all_pos[i]
        tmp_snr = (H.T.dot(H)).trace()/ K
        H_tmp = H / np.sqrt(tmp_snr) * np.sqrt(SNR)
        y_temp = x.dot(H_tmp)

        prob = np.exp(-0.5 * (np.sum(np.power(y_temp[jj] - y[jj], 2) for jj in range(N))))

        for ii in range(K):
            if x[ii] == 1/np.sqrt(2):
                final_probs_sqrt2[ii] = final_probs_sqrt2[ii] + ((1.0 / np.power(2, K)) * prob)
                sum_plus_sqrt2 = sum_plus_sqrt2 + 1
            if x[ii] == 1:
                final_probs_one[ii] = final_probs_one[ii] + ((1.0 / np.power(2, K)) * prob)
                sum_plus = sum_plus + 1
            if x[ii] == -1:
                final_probs_minus_one[ii] = final_probs_minus_one[ii] + ((1.0 / np.power(2, K)) * prob)
                sum_minus = sum_minus + 1
            if x[ii] == -1/np.sqrt(2):
                final_probs_minus_sqrt2[ii] = final_probs_minus_sqrt2[ii] + ((1.0 / np.power(2, K)) * prob)
                sum_minus_sqrt2 = sum_minus_sqrt2 + 1
            if x[ii] == 0:
                final_probs_zero[ii] = final_probs_zero[ii] + ((1.0 / np.power(2, K)) * prob)
                sum_zero = sum_zero + 1                
    for ii in range(K):
        norm = final_probs_one[ii] + final_probs_minus_one[ii] + final_probs_minus_sqrt2[ii] + final_probs_sqrt2[ii] + final_probs_zero[ii]
        final_probs_one[ii] = final_probs_one[ii] / norm
        final_probs_minus_one[ii] = final_probs_minus_one[ii] / norm
        final_probs_minus_sqrt2[ii] = final_probs_minus_sqrt2[ii]/norm
        final_probs_sqrt2[ii] = final_probs_sqrt2[ii]/norm       
        final_probs_zero[ii] = final_probs_zero[ii]/norm

    return final_probs_one, final_probs_minus_one,final_probs_minus_sqrt2,final_probs_sqrt2 , final_probs_zero





###start here
"""
Parameters
K - size of x
N - size of y
snrdb_low - the lower bound of noise db used during training
snr_high - the higher bound of noise db used during training
L - number of layers in DetNet
v_size = size of auxiliary variable at each layer
hl_size - size of hidden layer at each DetNet layer (the dimention the layers input are increased to
startingLearningRate - the initial step size of the gradient descent algorithm
decay_factor & decay_step_size - each decay_step_size steps the learning rate decay by decay_factor
train_iter - number of train iterations
train_batch_size - batch size during training phase
test_iter - number of test iterations
test_batch_size  - batch size during testing phase
LOG_LOSS - equal 1 if loss of each layer should be sumed in proportion to the layer depth, otherwise all losses have the same weight 
res_alpha- the proportion of the previuos layer output to be added to the current layers output (view ResNet article)
snrdb_low_test & snrdb_high_test & num_snr - when testing, num_snr different SNR values will be tested, uniformly spread between snrdb_low_test and snrdb_high_test 
"""
sess = tf.InteractiveSession()

#parameters
K = 4
N = 8
M = 7

snrdb_low = 18.0
snrdb_high = 25.0
snr_low = 10.0 ** (snrdb_low/10.0)
snr_high = 10.0 ** (snrdb_high/10.0)
L=30
v_size = 4*(2*K)
hl_size = 12*(2*K)
startingLearningRate1 = 0.0005
startingLearningRate2 = 0.0005
decay_factor1 = 0.97
decay_factor2 = 0.97
decay_step_size1 = 1000
decay_step_size2 = 1000
train_iter = 8
train_iter_no_noise = 10
n0 = 0.5

train_batch_size = 50

test_iter= 4
test_batch_size = 3

LOG_LOSS = 1
res_alpha=0.9
num_snr = 6
snrdb_low_test=19.0
snrdb_high_test=24.0
symbols = np.array([-1,-1.0/np.sqrt(2),0,1.0/np.sqrt(2),1])

print('8PSK soft TIMES with validation') #changed 24.2
print(K)
print(N)
print(snrdb_low)
print(snrdb_high)
print(snr_low)
print(snr_high)
print(L)
print(v_size)
print(hl_size)
print(startingLearningRate1)
print(startingLearningRate2)
print(decay_factor1)
print(decay_factor2)
print(decay_step_size1)
print(decay_step_size2)
print(train_iter)
print(train_batch_size)
print('test_iter')
print(test_iter)
print('test_batch_size')
print(test_batch_size)
print(res_alpha)
print(num_snr)
print(snrdb_low_test)
print(snrdb_high_test)

"""Data generation for train and test phases
In this example, both functions are the same.
This duplication is in order to easily allow testing cases where the test is over different distributions of data than in the training phase.
e.g. training over gaussian i.i.d. channels and testing over a specific constant channel.

currently both test and train are over i.i.d gaussian channel.
"""

def generate_data_sd(B,K,N,snr_low,snr_high):
    x_bit = np.random.randint(2, size=(B, 3 * K))
    x_r = np.zeros((B, K))
    x_i = np.zeros((B, K))
    x_ind = np.zeros((B, 8*K))
    for i in range(B):
        for ii in range(K):
            sym = x_bit[i, 3 * ii:3 * ii + 3]
            if sym[0] == 0 and sym[1] == 0 and sym[2] == 0:
                x_r[i, ii] = -1.0/np.sqrt(2)
                x_i[i, ii] = -1.0/np.sqrt(2)
                x_ind[i,0+ii*8] = 1
            if sym[0] == 0 and sym[1] == 0 and sym[2] == 1:
                x_r[i, ii] = -1
                x_i[i, ii] = 0
                x_ind[i,1+ii*8] = 1
            if sym[0] == 0 and sym[1] == 1 and sym[2] == 1:
                x_r[i, ii] = -1.0/np.sqrt(2)
                x_i[i, ii] = 1.0/np.sqrt(2)
                x_ind[i,2+ii*8] = 1
            if sym[0] == 0 and sym[1] == 1 and sym[2] == 0:
                x_r[i, ii] = 0
                x_i[i, ii] = 1
                x_ind[i,3+ii*8] = 1
            if sym[0] == 1 and sym[1] == 1 and sym[2] == 0:
                x_r[i, ii] = 1.0/np.sqrt(2)
                x_i[i, ii] = 1.0/np.sqrt(2)
                x_ind[i,4+ii*8] = 1
            if sym[0] == 1 and sym[1] == 1 and sym[2] == 1:
                x_r[i, ii] = 1
                x_i[i, ii] = 0
                x_ind[i,5+ii*8] = 1
            if sym[0] == 1 and sym[1] == 0 and sym[2] == 1:
                x_r[i, ii] = 1.0/np.sqrt(2)
                x_i[i, ii] = -1.0/np.sqrt(2)
                x_ind[i,6+ii*8] = 1
            if sym[0] == 1 and sym[1] == 0 and sym[2] == 0:
                x_r[i, ii] = 0
                x_i[i, ii] = -1
                x_ind[i,7+ii*8] = 1

    x_ = np.concatenate((x_r, x_i), axis=1)

    H_R = np.random.randn(B, K, N)
    H_I = np.random.randn(B, K, N)
    H_ = np.zeros([B, 2 * K, 2 * N])

    y_ = np.zeros([B, 2 * N])

    w_R = np.random.randn(B, N)
    w_I = np.random.randn(B, N)
    w = np.concatenate((w_R, w_I), axis=1)

    Hy_ = x_ * 0
    HH_ = np.zeros([B, 2 * K, 2 * K])
    SNR_ = np.zeros([B])
    for i in range(B):
        # print i
        SNR = np.random.uniform(low=snr_low, high=snr_high)
        H = np.concatenate((np.concatenate((H_R[i, :, :], -1 * H_I[i, :, :]), axis=1),
                            np.concatenate((H_I[i, :, :], H_R[i, :, :]), axis=1)), axis=0)
        tmp_snr = (H.T.dot(H)).trace() / (2 * K)
        H = H / np.sqrt(tmp_snr) * np.sqrt(SNR)
        H_[i, :, :] = H
        y_[i,:] = x_[i,:].dot(H) + w[i,:]
        Hy_[i, :] = H.dot(y_[i, :])
        HH_[i, :, :] = H.dot(H.T)
        SNR_[i] = SNR
    return y_,H_,Hy_,HH_,x_,SNR_, H_R, H_I, x_r, x_i, w_R, w_I,x_ind

def generate_data(B,K,N,snr_low,snr_high):
    x_bit = np.random.randint(2, size=(B, 3 * K))
    x_r = np.zeros((B, K))
    x_i = np.zeros((B, K))
    x_ind = np.zeros([B,K,8])
    for i in range(B):
        for ii in range(K):
            sym = x_bit[i, 3 * ii:3 * ii + 3]
            if sym[0] == 0 and sym[1] == 0 and sym[2] == 0:
                x_r[i, ii] = -1.0/np.sqrt(2)
                x_i[i, ii] = -1.0/np.sqrt(2)
                x_ind[i,ii,0] = 1
            if sym[0] == 0 and sym[1] == 0 and sym[2] == 1:
                x_r[i, ii] = -1
                x_i[i, ii] = 0
                x_ind[i,ii,1] = 1
            if sym[0] == 0 and sym[1] == 1 and sym[2] == 1:
                x_r[i, ii] = -1.0/np.sqrt(2)
                x_i[i, ii] = 1.0/np.sqrt(2)
                x_ind[i,ii,2] = 1
            if sym[0] == 0 and sym[1] == 1 and sym[2] == 0:
                x_r[i, ii] = 0
                x_i[i, ii] = 1
                x_ind[i,ii,3] = 1
            if sym[0] == 1 and sym[1] == 1 and sym[2] == 0:
                x_r[i, ii] = 1.0/np.sqrt(2)
                x_i[i, ii] = 1.0/np.sqrt(2)
                x_ind[i,ii,4] = 1
            if sym[0] == 1 and sym[1] == 1 and sym[2] == 1:
                x_r[i, ii] = 1
                x_i[i, ii] = 0
                x_ind[i,ii,5] = 1
            if sym[0] == 1 and sym[1] == 0 and sym[2] == 1:
                x_r[i, ii] = 1.0/np.sqrt(2)
                x_i[i, ii] = -1.0/np.sqrt(2)
                x_ind[i,ii,6] = 1
            if sym[0] == 1 and sym[1] == 0 and sym[2] == 0:
                x_r[i, ii] = 0
                x_i[i, ii] = -1
                x_ind[i,ii,7] = 1

    x_ = np.concatenate((x_r, x_i), axis=1)
                     

    H_R = np.random.randn(B, N, K)
    H_I = np.random.randn(B, N, K)
    H_ = np.zeros([B, 2 * N, 2 * K])

    y_ = np.zeros([B, 2 * N])

    w_R = np.random.randn(B, N)
    w_I = np.random.randn(B, N)
    w = np.concatenate((w_R, w_I), axis=1)

    Hy_ = x_ * 0
    HH_ = np.zeros([B, 2 * K, 2 * K])
    SNR_ = np.zeros([B])
    for i in range(B):
        # print i
        SNR = np.random.uniform(low=snr_low, high=snr_high)
        H = np.concatenate((np.concatenate((H_R[i, :, :], -1 * H_I[i, :, :]), axis=1),
                            np.concatenate((H_I[i, :, :], H_R[i, :, :]), axis=1)), axis=0)
        tmp_snr = (H.T.dot(H)).trace() / (2 * K)
        H = H / np.sqrt(tmp_snr) * np.sqrt(SNR)
        H_[i, :, :] = H
        y_[i, :] = H.dot(x_[i, :])   +w[i,:]
        Hy_[i, :] = H.T.dot(y_[i, :])
        HH_[i, :, :] = H.T.dot(H_[i, :, :])
        SNR_[i] = SNR
    return y_,H_,Hy_,HH_,x_,SNR_,x_ind

def generate_data_no_noise(B,K,N,snr_low,snr_high):
    x_bit = np.random.randint(2, size=(B, 3 * K))
    x_r = np.zeros((B, K))
    x_i = np.zeros((B, K))
    x_ind = np.zeros([B,K,8])
    for i in range(B):
        for ii in range(K):
            sym = x_bit[i, 3 * ii:3 * ii + 3]
            if sym[0] == 0 and sym[1] == 0 and sym[2] == 0:
                x_r[i, ii] = -1.0/np.sqrt(2)
                x_i[i, ii] = -1.0/np.sqrt(2)
                x_ind[i,ii,0] = 1
            if sym[0] == 0 and sym[1] == 0 and sym[2] == 1:
                x_r[i, ii] = -1
                x_i[i, ii] = 0
                x_ind[i,ii,1] = 1
            if sym[0] == 0 and sym[1] == 1 and sym[2] == 1:
                x_r[i, ii] = -1.0/np.sqrt(2)
                x_i[i, ii] = 1.0/np.sqrt(2)
                x_ind[i,ii,2] = 1
            if sym[0] == 0 and sym[1] == 1 and sym[2] == 0:
                x_r[i, ii] = 0
                x_i[i, ii] = 1
                x_ind[i,ii,3] = 1
            if sym[0] == 1 and sym[1] == 1 and sym[2] == 0:
                x_r[i, ii] = 1.0/np.sqrt(2)
                x_i[i, ii] = 1.0/np.sqrt(2)
                x_ind[i,ii,4] = 1
            if sym[0] == 1 and sym[1] == 1 and sym[2] == 1:
                x_r[i, ii] = 1
                x_i[i, ii] = 0
                x_ind[i,ii,5] = 1
            if sym[0] == 1 and sym[1] == 0 and sym[2] == 1:
                x_r[i, ii] = 1.0/np.sqrt(2)
                x_i[i, ii] = -1.0/np.sqrt(2)
                x_ind[i,ii,6] = 1
            if sym[0] == 1 and sym[1] == 0 and sym[2] == 0:
                x_r[i, ii] = 0
                x_i[i, ii] = -1
                x_ind[i,ii,7] = 1

    x_ = np.concatenate((x_r, x_i), axis=1)

    H_R = np.random.randn(B, N, K)
    H_I = np.random.randn(B, N, K)
    H_ = np.zeros([B, 2 * N, 2 * K])

    y_ = np.zeros([B, 2 * N])

    w_R = np.random.randn(B, N)
    w_I = np.random.randn(B, N)
    w = np.concatenate((w_R, w_I), axis=1)

    Hy_ = x_ * 0
    HH_ = np.zeros([B, 2 * K, 2 * K])
    SNR_ = np.zeros([B])
    for i in range(B):
        # print i
        SNR = np.random.uniform(low=snr_low, high=snr_high)
        H = np.concatenate((np.concatenate((H_R[i, :, :], -1 * H_I[i, :, :]), axis=1),
                            np.concatenate((H_I[i, :, :], H_R[i, :, :]), axis=1)), axis=0)
        tmp_snr = (H.T.dot(H)).trace() / (2 * K)
        H = H / np.sqrt(tmp_snr) * np.sqrt(SNR)
        H_[i, :, :] = H
        y_[i, :] = H.dot(x_[i, :]) #  +w[i,:]
        Hy_[i, :] = H.T.dot(y_[i, :])
        HH_[i, :, :] = H.T.dot(H_[i, :, :])
        SNR_[i] = SNR
    return y_,H_,Hy_,HH_,x_,SNR_,x_ind


def affine_layer(x,input_size,output_size,Layer_num):
    W = tf.Variable(tf.random_normal([input_size, output_size], stddev=0.01))
    w = tf.Variable(tf.random_normal([1, output_size], stddev=0.01))
    y = tf.matmul(x, W)+w
    return y,W,w

def relu_layer(x,input_size,output_size,Layer_num):
    y,W,w = affine_layer(x,input_size,output_size,Layer_num)
    y= tf.nn.relu(y)
    return y,W,w

def sign_layer(x,input_size,output_size,Layer_num):
    #y = piecewise_linear_soft_sign(affine_layer(x,input_size,output_size,Layer_num))
    y,W,w= affine_layer(x,input_size,output_size,Layer_num)
    return y,W,w

#tensorflow placeholders, the input given to the model in order to train and test the network
HY = tf.placeholder(tf.float32,shape=[None,2*K])
X = tf.placeholder(tf.float32,shape=[None,2*K])
X_IND = tf.placeholder(tf.float32,shape=[None,K,8])
HH = tf.placeholder(tf.float32,shape=[None, 2*K , 2*K])

batch_size = tf.shape(HY)[0]
X_LS = tf.matmul(tf.expand_dims(HY,1),tf.matrix_inverse(HH))
X_LS= tf.squeeze(X_LS,1)
loss_LS = tf.reduce_mean(tf.square(X - X_LS))
xLS_real = find_nearest(X_LS)[:,0:K]
xLS_imag = find_nearest(X_LS)[:,K:2*K]
x_real = X[:,0:K]
x_imag = X[:,K:2*K]

ber_LS =  tf.reduce_mean(tf.cast(tf.logical_or(tf.not_equal(x_real,xLS_real) , tf.not_equal(x_imag,xLS_imag)), tf.float32))


S1=[]
S1.append(tf.zeros([batch_size,2*K]))
S2=[]
S2.append(tf.zeros([batch_size,8*K]))
S4 = []
S4.append(tf.zeros([batch_size,K,5,2]))
V=[]
V.append(tf.zeros([batch_size,v_size]))
LOSS=[]
LOSS.append(tf.zeros([]))
BER=[]
BER.append(tf.zeros([]))
delta = tf.Variable(tf.zeros(L*2,1))
Z1 = []
ZZ1 = []
W11 = []
w11 = []
W22 = []
w22 = []
W33 = []
w33 = []
Z1_1 = []
temp1 = []
Z = []
first = []
second = []
#The architecture of DetNet
for i in range(1,L):
    print('i')
    print(i)
    temp11 = tf.matmul(tf.expand_dims(S1[-1],1),HH)
    temp1.append(tf.squeeze(temp11,1))
    first.append(delta[(i-1) * 2]*HY)
    second.append(delta[(i-1) * 2 + 1]*temp1[-1])
    Z1.append(S1[-1] - (delta[(i-1) * 2]*HY) + (delta[(i-1) * 2 + 1]*temp1[-1]))
    Z.append(tf.concat([Z1[-1], V[-1]], 1))
    ZZ,Wtemp,wtemp = relu_layer(Z[-1],(2*K) + v_size , hl_size,'relu'+str(i))
    
    W11.append(Wtemp)
    w11.append(wtemp)
    ZZ1.append((ZZ))
    
    S2_temp,W22_temp,w22_temp = sign_layer(ZZ , hl_size , 8*K,'sign'+str(i))
    
    S2.append(S2_temp)
    W22.append(W22_temp)
    w22.append(w22_temp)
    
    S2[i]=(1-res_alpha)*S2[i]+res_alpha*S2[i-1]
    S2[i] =    tf.clip_by_value(S2[i],0,1)

    V_temp ,  W33_temp , w33_temp = affine_layer(ZZ , hl_size , v_size,'aff'+str(i))
    
    V.append(V_temp)
    W33.append(W33_temp)
    w33.append(w33_temp)
    
    V[i]=(1-res_alpha)*V[i]+res_alpha*V[i-1] 
    
    S3 = tf.reshape(S2[i],[batch_size,K,8])

    temp_0 = S3[:,:,0]
    temp_1 = S3[:,:,1]
    temp_2 = S3[:,:,2]
    temp_3 = S3[:,:,3]
    temp_4 = S3[:,:,4]
    temp_5 = S3[:,:,5]
    temp_6 = S3[:,:,6]
    temp_7 = S3[:,:,7]
   

    S1_real = (-1/tf.sqrt(2.0))*temp_0  +\
              (-1)*temp_1 + \
              (-1 / tf.sqrt(2.0))*temp_2 +\
                0 * temp_3 + \
              (1.0 / np.sqrt(2.0)) * temp_4 +\
              1 * temp_5 + \
              (1.0 / np.sqrt(2.0)) * temp_6 + \
              0 * temp_7

    S1_im = (-1 / tf.sqrt(2.0)) * temp_0 + \
              (0) * temp_1 + \
              (1 / tf.sqrt(2.0)) * temp_2 + \
              1 * temp_3 + \
              (1 / tf.sqrt(2.0)) * temp_4 + \
              0 * temp_5 + \
              (-1 / tf.sqrt(2.0)) * temp_6 + \
               (-1) * temp_7
               
    S1.append(tf.concat([S1_real, S1_im], 1))
    
    S4_temp =  tf.zeros([batch_size,K, 5, 2])  

    temp_0 = tf.expand_dims(temp_0,2)
    temp_1 = tf.expand_dims(temp_1,2)
    temp_2 = tf.expand_dims(temp_2,2)
    temp_3 = tf.expand_dims(temp_3,2)
    temp_4 = tf.expand_dims(temp_4,2)
    temp_5 = tf.expand_dims(temp_5,2)
    temp_6 = tf.expand_dims(temp_6,2)
    temp_7 = tf.expand_dims(temp_7,2)

    #                        -1       -1/sqrt(2)      0             1/sqrt(2)       1
    S4_temp1 = tf.concat([temp_1 , temp_0 + temp_2 , temp_3 + temp_7 , temp_4 + temp_6 , temp_5],2)
    S4_temp2 = tf.concat([temp_7 , temp_0 + temp_6 , temp_1 + temp_5 , temp_2 + temp_4 , temp_3],2)
    S4_temp1 = tf.expand_dims(S4_temp1,3)
    S4_temp2 = tf.expand_dims(S4_temp2,3)
    

    S4_temp3 = tf.concat([S4_temp1,S4_temp2],3)

    
    S4.append(S4_temp3)
    X_IND_reshaped = tf.reshape(X_IND,[batch_size,8*K])
    if LOG_LOSS == 1:
        LOSS.append(np.log(i)*tf.reduce_mean(tf.reduce_mean(tf.square(X_IND_reshaped - S2[-1]),1)))#/tf.reduce_mean(tf.square(X - X_LS),1)))
    else:
        LOSS.append(tf.reduce_mean(tf.reduce_mean(tf.square(X_IND_reshaped - S2[-1]),1)))#/tf.reduce_mean(tf.square(X - X_LS),1)))
    BER.append(tf.reduce_mean(tf.cast(tf.not_equal(X_IND, tf.round(S3)), tf.float32)))
Max_Val = tf.reduce_max(S3,axis=2, keep_dims=True)
Greater = tf.greater_equal(S3,Max_Val)
BER2 = tf.round(tf.cast(Greater,tf.float32))
#BER2 = tf.round(S3) 
BER3 = tf.not_equal(BER2, X_IND)
BER4 = tf.reduce_sum(tf.cast(BER3,tf.float32),2)
BER5 = tf.cast(tf.greater(BER4,0),tf.float32)
SER =  tf.reduce_mean(BER5)     

TOTAL_LOSS=tf.add_n(LOSS)


global_step1 = tf.Variable(0, trainable=False)
learning_rate1 = tf.train.exponential_decay(startingLearningRate1, global_step1, decay_step_size1, decay_factor1, staircase=True)
train_step1 = tf.train.AdamOptimizer(learning_rate1).minimize(TOTAL_LOSS)

global_step2 = tf.Variable(0, trainable=False)
learning_rate2 = tf.train.exponential_decay(startingLearningRate2, global_step2, decay_step_size2, decay_factor2, staircase=True)
train_step2 = tf.train.AdamOptimizer(learning_rate2).minimize(TOTAL_LOSS)

init_op=tf.initialize_all_variables()

sess.run(init_op)
for i in range(train_iter_no_noise): #num of train iter
    batch_Y, batch_H, batch_HY, batch_HH, batch_X , SNR1, x_ind= generate_data_no_noise(train_batch_size,K,N,snr_low,snr_high)
    train_step1.run(feed_dict={HY: batch_HY, HH: batch_HH, X: batch_X ,X_IND: x_ind})
    if i % 100== 0 :
        sys.stderr.write(str(i)+' ')
        batch_Y, batch_H, batch_HY, batch_HH, batch_X ,SNR1,x_ind= generate_data_no_noise(train_batch_size,K,N,snr_low,snr_high)
        results = sess.run([loss_LS,LOSS[L-1],ber_LS,SER], {HY: batch_HY, HH: batch_HH, X: batch_X,X_IND: x_ind})
        #print('x_ind')
        #print(x_ind)
        #print('S3')
        #print(sess.run(S3[-1], {HY: batch_HY, HH: batch_HH, X: batch_X,X_IND: x_ind}))
        #print('BER4')
        #print(sess.run(BER4, {HY: batch_HY, HH: batch_HH, X: batch_X,X_IND: x_ind}))
        #print('SER')
        #print(sess.run(SER, {HY: batch_HY, HH: batch_HH, X: batch_X,X_IND: x_ind}))
        print_string = [i]+results
        print ' '.join('%s' % x for x in print_string)

for i in range(train_iter): #num of train iter
    batch_Y, batch_H, batch_HY, batch_HH, batch_X , SNR1,x_ind= generate_data(train_batch_size,K,N,snr_low,snr_high)
    train_step2.run(feed_dict={HY: batch_HY, HH: batch_HH, X: batch_X,X_IND: x_ind})
    if i % 100 == 0 :
	sys.stderr.write(str(i)+ ' ')
        batch_Y, batch_H, batch_HY, batch_HH, batch_X ,SNR1,x_ind= generate_data(train_batch_size,K,N,snr_low,snr_high)
        results = sess.run([loss_LS,LOSS[L-1],ber_LS,SER], {HY: batch_HY, HH: batch_HH, X: batch_X,X_IND: x_ind})
        print_string = [i]+results
        print ' '.join('%s' % x for x in print_string)
        
#start np times
W1 = sess.run(W11)
w1 = sess.run(w11)
W2 = sess.run(W22)
w2 = sess.run(w22)
W3 = sess.run(W33)
w3 = sess.run(w33)
delta_comp = sess.run(delta)


tic = tm.time()

tmp_times_np = np.zeros((test_iter,1)) 

for i_iter in range(test_iter):
    batch_Y, batch_H, batch_HY, batch_HH, batch_X ,SNR1,x_ind= generate_data(test_batch_size,K,N,snr_low,snr_high)
    batch_size = np.shape(batch_HY)[0]
    S1_comp=[]
    S1_comp.append(np.zeros([batch_size,2*K]))
    S2_comp=[]
    S2_comp.append(np.zeros([batch_size,8*K]))
    S4_comp = []
    S4_comp.append(np.zeros([batch_size,K, 4, 2]))
    V_comp=[]
    V_comp.append(np.zeros([batch_size,v_size]))
    LOSS_comp=[]
    LOSS_comp.append(np.zeros([]))
    BER_comp=[]
    BER_comp.append(np.zeros([]))
    
    

    
    X_LS_comp = np.matmul(np.expand_dims(batch_HY,1),np.linalg.inv(batch_HH))
    X_LS_comp= np.squeeze(X_LS_comp,1)
    loss_LS_comp = np.mean(np.square(batch_X - X_LS_comp))

    ber_LS_comp = np.mean(np.not_equal(batch_X,np.sign(X_LS_comp)).astype(np.float32))
    tic = tm.time()

    for i in range(0,L-1):

        temp1_comp = np.matmul(np.expand_dims(S1_comp[i], 1), batch_HH)
        temp1_comp = np.squeeze(temp1_comp, 1)

        Z1_comp = S1_comp[-1] -  delta_comp[(i) * 2]*batch_HY + delta_comp[(i) * 2 + 1]*temp1_comp

        Z_comp = np.concatenate((Z1_comp, V_comp[-1]), 1)
        #print('Z tf')
        #print(np.array(sess.run(Z[i], {HY: batch_HY, HH: batch_HH, X: batch_X, X_IND:x_ind})))
        #print('Z_comp')
        #print(Z_comp)
        y_temp = np.matmul(Z_comp, W1[i]) + w1[i]
        ZZ_comp = np.maximum(0 , y_temp)

        y_temp = np.matmul(ZZ_comp , W2[i]) + w2[i]

        S2_comp.append(y_temp)

        S2_comp[i+1] = (1-res_alpha)*S2_comp[i+1]+res_alpha*S2_comp[i]
        S2_comp[i+1] = np.clip(S2_comp[i+1], 0, 1)

        y_temp = np.matmul(ZZ_comp, W3[i]) + w3[i]
        
        V_comp.append(y_temp)
        V_comp[i+1] = (1 - res_alpha) * V_comp[i+1] + res_alpha * V_comp[i]

        S3_comp = np.reshape(S2_comp[i+1],[batch_size,K,8])
        

        temp_0_comp = S3_comp[:,:,0]
        temp_1_comp = S3_comp[:,:,1]
        temp_2_comp = S3_comp[:,:,2]
        temp_3_comp = S3_comp[:,:,3]
        temp_4_comp = S3_comp[:,:,4]
        temp_5_comp = S3_comp[:,:,5]
        temp_6_comp = S3_comp[:,:,6]
        temp_7_comp = S3_comp[:,:,7]
   

        S1_real_comp = (-1/np.sqrt(2.0))*temp_0_comp  +\
              (-1)*temp_1_comp + \
              (-1 / np.sqrt(2.0))*temp_2_comp +\
                0 * temp_3_comp + \
              (1.0 / np.sqrt(2.0)) * temp_4_comp +\
              1 * temp_5_comp + \
              (1.0 / np.sqrt(2.0)) * temp_6_comp + \
              0 * temp_7_comp

        S1_im_comp = (-1 / np.sqrt(2.0)) * temp_0_comp + \
              (0) * temp_1_comp + \
              (1 / np.sqrt(2.0)) * temp_2_comp + \
              1 * temp_3_comp + \
              (1 / np.sqrt(2.0)) * temp_4_comp + \
              0 * temp_5_comp + \
              (-1 / np.sqrt(2.0)) * temp_6_comp + \
               (-1) * temp_7_comp
               
        S1_comp.append(np.concatenate([S1_real_comp, S1_im_comp], 1))
    
        S4_temp_comp =  np.zeros([batch_size,K, 5, 2])  

        temp_0_comp = np.expand_dims(temp_0_comp,2)
        temp_1_comp = np.expand_dims(temp_1_comp,2)
        temp_2_comp = np.expand_dims(temp_2_comp,2)
        temp_3_comp = np.expand_dims(temp_3_comp,2)
        temp_4_comp = np.expand_dims(temp_4_comp,2)
        temp_5_comp = np.expand_dims(temp_5_comp,2)
        temp_6_comp = np.expand_dims(temp_6_comp,2)
        temp_7_comp = np.expand_dims(temp_7_comp,2)

    #                        -1       -1/sqrt(2)      0             1/sqrt(2)       1
        S4_temp1_comp = np.concatenate([temp_1_comp , temp_0_comp + temp_2_comp , temp_3_comp + temp_7_comp , temp_4_comp + temp_6_comp , temp_5_comp],2)
        S4_temp2_comp = np.concatenate([temp_7_comp , temp_0_comp + temp_6_comp , temp_1_comp + temp_5_comp , temp_2_comp + temp_4_comp , temp_3_comp],2)
        S4_temp1_comp = np.expand_dims(S4_temp1_comp,3)
        S4_temp2_comp = np.expand_dims(S4_temp2_comp,3)

        S4_temp3_comp = np.concatenate([S4_temp1_comp,S4_temp2_comp],3)
    
        S4_comp.append(S4_temp3_comp)
        X_IND_reshaped_comp = np.reshape(x_ind,[batch_size,8*K])
        LOSS_comp.append(np.log(i)*np.mean(np.mean(np.square(X_IND_reshaped_comp - S2_comp[-1]),1)))
        BER_comp.append(np.mean(np.not_equal(batch_X,np.sign(S1_comp[-1])).astype(np.float32)))

    toc = tm.time()
    tmp_times_np[i_iter] =   (toc-tic)


Max_Val_comp = np.amax(S3_comp,axis=2,keepdims =True)
Greater_comp = np.greater_equal(S3_comp,Max_Val_comp)
BER2_comp = np.round(Greater_comp.astype(np.float32))
x_ind_reshaped = np.reshape(x_ind,[batch_size,K,8])
BER3_comp = np.not_equal(BER2_comp, x_ind_reshaped)
BER4_comp = np.sum(BER3_comp.astype(np.float32),2)
BER5_comp = np.greater(BER4_comp.astype(np.float32),0)
SER_comp =  np.mean(BER5_comp)    

np_time = np.mean(tmp_times_np)/test_batch_size
print('np_time_final')
print(np_time)         



def Choose_best(M,temp_dist,temp_codes,dist_add,BestAll):
    dist_zip_code = zip(temp_dist, temp_codes)
    dist_zip_code.sort()
    codes = [x for _, x in dist_zip_code]

    dist_zip_dist_add = zip(temp_dist, dist_add)
    dist_zip_dist_add.sort()
    added = [x for _, x in dist_zip_dist_add]
    temp_dist.sort()

    if len(codes) > np.minimum(M, len(codes)):
        BestAll.append(codes[np.minimum(M,len(codes)):-1])


    return temp_dist[0:np.minimum(M,len(temp_dist))] , codes[0:np.minimum(M,len(codes))] , added[0:np.minimum(M,len(codes))],BestAll

def SD(L,z,symbols,K,M):

    e = np.zeros((M,2*K))

    e[:,:] = z.dot(np.linalg.pinv(L))
    u = np.zeros((len(symbols),2*K))
    BestM = []
    BestMDists = []
    BestAll = []
    #print('e is:')
    #print(e)
    for k in reversed(range(2*K)):


        temp_dist = []
        dist_add = []
        temp_codes = BestM
        new_temp_codes = []
        for i in range(len(BestM)):
 
            for t in range(len(symbols)):

                u[t,k] = symbols[t]
                a_temp = (e[i,k] - u[t,k])/L[k,k]
                dist_add.append(a_temp)

                temp_dist.append(BestMDists[i] + np.power(a_temp,2))
                new_temp_codes.append(temp_codes[i]+[symbols[t]])

        if len(BestM) == 0:
            for t in range(len(symbols)):
                new_temp_codes.append([symbols[t]])
                temp_b = np.power((e[0,k]- symbols[t])/L[k,k],2)
                dist_add.append(temp_b)
                temp_dist.append(temp_b)


        BestMDists,BestM,dist_add,BestAll = Choose_best(M,temp_dist,new_temp_codes,dist_add,BestAll)
        for i in range(len(BestM)):
            for j in range(k-1):
                e[i,j] = e[i,j]-dist_add[i]*L[k,j]

    return BestM,BestAll



sd_times = np.zeros((num_snr,1))

print('K')
print(K)
print('N')
print(N)
print('M')
print(M)
print('test_iter')
print(test_iter)

snrdb_list = np.linspace(snrdb_low_test,snrdb_high_test,num_snr)
snr_list = 10.0 ** (snrdb_list/10.0)
basic_dist = np.zeros((num_snr,2*K))
ext_dist = np.zeros((num_snr,2*K))
new_dist = np.zeros((num_snr,2*K))
new_ext_dist = np.zeros((num_snr,2*K))
bers_basic = np.zeros((num_snr))

for j in range(num_snr):
    print(j)
    sys.stderr.write(str(j)+ 'snr ')

    total_wrong_basic = 0.0
    batch_Y, batch_H, batch_HY, batch_HH, batch_X, SNR1, H_R, H_I, x_R, x_I, w_R, w_I,x_ind= generate_data_sd(test_iter, K, N, snr_list[j], snr_list[j])

    basic_dist_temp = np.zeros((2*K))
    ext_dist_temp = np.zeros((2*K))
    new_dist_temp = np.zeros((2*K))
    new_ext_dist_temp = np.zeros((2*K))
    
    sd_times_temp = np.zeros((test_iter,1))
    #print(batch_Y)
    for jj in range(test_iter):
        if jj%10 == 0:
            print(jj)
            sys.stderr.write(str(jj)+ ' ')
        basic_prob_one = np.zeros((2*K))
        basic_prob_minus_one = np.zeros((2*K))
        basic_prob_sqrt2 = np.zeros((2*K))
        basic_prob_minus_sqrt2 = np.zeros((2*K))
        basic_prob_zeros = np.zeros((2*K))
        
        ext_prob_one = np.zeros((2*K))
        ext_prob_minus_one = np.zeros((2*K))
        ext_prob_sqrt2  = np.zeros((2*K))
        ext_prob_minus_sqrt2  = np.zeros((2*K))
        ext_prob_zeros = np.zeros((2*K))

        new_prob_one = np.zeros((2*K))
        new_prob_minus_one = np.zeros((2*K))
        new_prob_sqrt2 = np.zeros((2*K))
        new_prob_minus_sqrt2  = np.zeros((2*K))
        new_prob_zeros = np.zeros((2*K))

        
        new_ext_prob_one = np.zeros((2*K))
        new_ext_prob_minus_one = np.zeros((2*K))
        new_ext_prob_sqrt2  = np.zeros((2*K))
        new_ext_prob_minus_sqrt2  = np.zeros((2*K))
        new_ext_prob_zeros = np.zeros((2*K))


        H = batch_H[jj]
        tic = tm.time()

        U, s, V = np.linalg.svd(H, full_matrices=0)

        S = np.diag(s)

        Vinv = np.linalg.pinv(V)
        H1 = U.dot(S)

        q_t, r_t = np.linalg.qr(np.transpose(H1))
        q = np.transpose(q_t)
        r = np.transpose(r_t)
        y = batch_Y

        pos = np.diag(np.sign(np.diag(r)))
        final_H = r.dot(pos)
        
        y = batch_Y[jj]
        a1 = q.dot(V)
        aa1 = y.dot(np.linalg.pinv(q.dot(V)))
        final_y = y.dot(np.linalg.pinv(q.dot(V))).dot(pos)


        BestM ,BestAll= SD(final_H, final_y, symbols, K, M)

        BestM =  np.flip(BestM,1)
        BestAllTemp = []
        for i in range(len(BestAll)):
            for ii in range(len(BestAll[i])):
                BestAllTemp.append(np.flip(BestAll[i][ii],0))
        BestAll = BestAllTemp
        toc = tm.time()
        sd_times_temp[jj] =sd_times_temp[jj] +toc-tic
        final_guess= BestM[0]

        #print(np.sum(np.not_equal(batch_X[jj],final_guess)))
        total_wrong_basic = total_wrong_basic + np.sum(np.not_equal(batch_X[jj],final_guess))
        
        for i in range(2*K):
            #print(np.sum(np.equal([a[i] for a in BestM],1))*1.00/M)
            
            basic_prob_one[i] = np.sum(np.equal([a[i] for a in BestM],1))*1.00/M
            basic_prob_minus_one[i] = np.sum(np.equal([a[i] for a in BestM],-1))*1.00/M
            basic_prob_sqrt2[i] = np.sum(np.equal([a[i] for a in BestM],1.0/np.sqrt(2)))*1.00/M
            basic_prob_minus_sqrt2[i] = np.sum(np.equal([a[i] for a in BestM],-1.0/np.sqrt(2)))*1.00/M
            basic_prob_zeros[i] = np.sum(np.equal([a[i] for a in BestM],0))*1.00/M

        for i in range(len(BestM)):
            BestAll.append(BestM[i])
        #for the solutions in the extended version, if solution is shorter than K, extend it to a full using the LS soluiton
        LS_solution = np.zeros((2*K))
        for ii in range(2*K):
            LS_solution[ii] = find_nearest_mpsk_np((batch_Y[jj]).dot(batch_H[jj].T).dot(np.linalg.inv((batch_H[jj]).dot(batch_H[jj].T)))[ii])
        #print('LS_solution')
        #print(LS_solution)
        for i in range(len(BestAll)):
            for ii in range(2*K):
                if len(BestAll[i])<=ii:
                    BestAll[i] = np.append(BestAll[i],LS_solution[ii])


        for i in range(2*K):
            #print(np.sum(np.equal([a[i] for a in BestM],1))*1.00/M)
            ext_prob_one[i] = np.sum(np.equal([a[i] for a in BestAll],1))*1.00/(len(BestAll))
            ext_prob_minus_one[i] =  np.sum(np.equal([a[i] for a in BestAll],-1))*1.00/(len(BestAll))
            ext_prob_sqrt2[i] =  np.sum(np.equal([a[i] for a in BestAll],1.0/np.sqrt(2)))*1.00/(len(BestAll))
            ext_prob_minus_sqrt2[i] =  np.sum(np.equal([a[i] for a in BestAll],-1.0/np.sqrt(2)))*1.00/(len(BestAll))
            ext_prob_zeros[i] =  np.sum(np.equal([a[i] for a in BestAll],0))*1.00/(len(BestAll))
        #new calculation M candidates

        exp_dists_basic = np.zeros((M))
        for i in range(M):
            exp_dists_basic[i] = np.exp(-1*np.sum(np.square(y-BestM[i].dot(H))))
        sum_dists_new = np.sum(exp_dists_basic)

        for i in range(2*K):
            temp_sum_one = 0
            temp_sum_minus_one = 0
            temp_sum_sqrt2 = 0
            temp_sum_minus_sqrt2 = 0
            temp_sum_zero = 0
            for ii in range(M):
                if BestM[ii][i] == 1:
                    temp_sum_one = temp_sum_one + np.exp(-1*np.sum(np.square(y-BestM[ii].dot(H))))
                if BestM[ii][i] == -1:
                    temp_sum_minus_one = temp_sum_minus_one + np.exp(-1*np.sum(np.square(y-BestM[ii].dot(H))))
                if BestM[ii][i] == 1.0/np.sqrt(2):
                    temp_sum_sqrt2 = temp_sum_sqrt2 + np.exp(-1*np.sum(np.square(y-BestM[ii].dot(H))))
                if BestM[ii][i] == -1.0/np.sqrt(2):
                    temp_sum_minus_sqrt2 = temp_sum_minus_sqrt2 + np.exp(-1*np.sum(np.square(y-BestM[ii].dot(H))))
                if BestM[ii][i] == 0:
                    temp_sum_zero = temp_sum_zero + np.exp(-1*np.sum(np.square(y-BestM[ii].dot(H))))
            new_prob_one[i] = temp_sum_one/sum_dists_new
            new_prob_minus_one[i] = temp_sum_minus_one/sum_dists_new
            new_prob_sqrt2[i] = temp_sum_sqrt2/sum_dists_new
            new_prob_minus_sqrt2[i] = temp_sum_minus_sqrt2/sum_dists_new
            new_prob_zeros[i] = temp_sum_zero/sum_dists_new
        

        #new calculation all candidates
        tic =tm.time()
        exp_dists_all = np.zeros(len(BestAll))
        for i in range(len(BestAll)):
            exp_dists_all[i] = np.exp(-1 * np.sum(np.square(y - BestAll[i].dot(H))))
        sum_dists_new_all = np.sum(exp_dists_all)

        for i in range(2*K):
            temp_sum_one = 0
            temp_sum_minus_one = 0
            temp_sum_sqrt2 = 0
            temp_sum_minus_sqrt2 = 0
            temp_sum_zero = 0
            for ii in range(len(BestAll)):
                if BestAll[ii][i] == 1:
                    temp_sum_one = temp_sum_one + np.exp(-1*np.sum(np.square(y-BestAll[ii].dot(H))))
                if BestAll[ii][i] == -1:
                    temp_sum_minus_one = temp_sum_minus_one + np.exp(-1*np.sum(np.square(y-BestAll[ii].dot(H))))
                if BestAll[ii][i] == 1.0/np.sqrt(2):
                    temp_sum_sqrt2 = temp_sum_sqrt2 + np.exp(-1*np.sum(np.square(y-BestAll[ii].dot(H))))
                if BestAll[ii][i] == -1.0/np.sqrt(2):
                    temp_sum_minus_sqrt2 = temp_sum_minus_sqrt2 + np.exp(-1*np.sum(np.square(y-BestAll[ii].dot(H))))
                if BestAll[ii][i] == 0:
                    temp_sum_zero = temp_sum_zero + np.exp(-1*np.sum(np.square(y-BestAll[ii].dot(H))))
            new_ext_prob_one[i] = temp_sum_one/sum_dists_new_all
            new_ext_prob_minus_one[i] = temp_sum_minus_one/sum_dists_new_all
            new_ext_prob_sqrt2[i] = temp_sum_sqrt2/sum_dists_new_all
            new_ext_prob_minus_sqrt2[i] = temp_sum_minus_sqrt2/sum_dists_new_all
            new_ext_prob_zeros[i] = temp_sum_zero/sum_dists_new_all
        toc =tm.time()
        sd_times_temp[jj] =sd_times_temp[jj] +toc-tic
        if K==4:
            real_prob_one, real_prob_min_one ,real_prob_min_sqrt2,real_prob_sqrt2,real_prob_zero = validate4(batch_Y[jj], SNR1[jj], batch_H[jj], 2*K, 2*N)
        if K==3:
            real_prob_one, real_prob_min_one ,real_prob_min_sqrt2,real_prob_sqrt2,real_prob_zero = validate3(batch_Y[jj], SNR1[jj], batch_H[jj], 2*K, 2*N)
            
        basic_dist_temp =   basic_dist_temp   + np.absolute(basic_prob_one   - real_prob_one)  + np.absolute(basic_prob_minus_one   - real_prob_min_one) + np.absolute(basic_prob_minus_sqrt2   - real_prob_min_sqrt2) + np.absolute(basic_prob_sqrt2   - real_prob_sqrt2) + np.absolute(basic_prob_zeros   - real_prob_zero)
        ext_dist_temp =     ext_dist_temp     + np.absolute(ext_prob_one     - real_prob_one)  + np.absolute(ext_prob_minus_one     - real_prob_min_one) + np.absolute(ext_prob_minus_sqrt2     - real_prob_min_sqrt2) + np.absolute(ext_prob_sqrt2     - real_prob_sqrt2) + np.absolute(ext_prob_zeros     - real_prob_zero)
        new_dist_temp =     new_dist_temp     + np.absolute(new_prob_one     - real_prob_one)  + np.absolute(new_prob_minus_one     - real_prob_min_one) + np.absolute(new_prob_minus_sqrt2     - real_prob_min_sqrt2) + np.absolute(new_prob_sqrt2     - real_prob_sqrt2) + np.absolute(new_prob_zeros     - real_prob_zero) 
        new_ext_dist_temp = new_ext_dist_temp + np.absolute(new_ext_prob_one - real_prob_one)  + np.absolute(new_ext_prob_minus_one - real_prob_min_one) + np.absolute(new_ext_prob_minus_sqrt2 - real_prob_min_sqrt2) + np.absolute(new_ext_prob_sqrt2 - real_prob_sqrt2) + np.absolute(new_ext_prob_zeros - real_prob_zero)
    sd_times[j] = np.mean(sd_times_temp)

    bers_basic[j] = total_wrong_basic/(2*K*test_iter)
    basic_dist[j] = basic_dist_temp/test_iter
    ext_dist[j] = ext_dist_temp/test_iter
    new_dist[j] = new_dist_temp/test_iter
    new_ext_dist[j] = new_ext_dist_temp/test_iter

print('bers_basic')
print(bers_basic)
#print('basic_dist')
#print(basic_dist)
#print('ext_dist')
#print(ext_dist)
#print('new_dist')
#print(new_dist)
print('new_ext_dist')
print(new_ext_dist)
print('sd_times')
print(sd_times)
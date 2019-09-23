'''
compute the 3-d convolution
'''

import numpy as np
import pandas as pd
import binascii
import convert  #从convert.py文件中import一些必要函数

#对有符号16进制数 进行 进一步处理 #https://stackoverflow.com/questions/24563786/conversion-from-hex-to-signed-dec-in-python/32276534
def s16(value):
    return -(value & 0x80) | (value & 0x7f)  #用于处理8bits
def s16_bias(value):
    return -(value & 0x8000) | (value & 0x7fff) #用于处理16bits

'''
the information of all layers should first be read and saved in the lists
Cause the space, comments, '\n', all these have been recorded in contents list. We should do more to this lists to make sure that the information in the list is useful.
不管是读ifmap，weights，bias都通过这个文件读，并且同时要标注读文件多少行的内容
'''
def load_file(file, line_start, line_end):
    a_flag = 0                                   #用于标记读的行数，最开始都是0
    contents = []
    label_list = []
    #firstly, read layers information from the existed file
    with open(file, 'r') as file_to_read:
        while a_flag <= line_end:
            if a_flag >= line_start:
                line = file_to_read.readline()       #read one line, and store as a list
                if not line:
                    break
                line = line.strip('\n')              #remove the '\n' in the end
                line = line.strip(' ')               #remove the ' ' in the end
                line = line.split(' ')               #convert the line string in the list into the different strings, based on the character:' 'space
                label_list = [s16(int(i,16)) for i in line]  #convert the string type to int type
                '''
                for i in line:
                    #print(int(i,16))
                    #print(s16(int(i,16)))
                    f = open('file_1.txt', 'a')  # 若是'wb'就表示写二进制文件  #https://www.cnblogs.com/programer-xinmu78/p/10661170.html
                    f.write(str(int(i,16))+" ")         #16进制转化成10进制
                    f.write(str(s16(int(i,16))) + "\n") #有符号16进制转化成10进制
                    f.close()
                '''
                contents = contents + label_list     #注意这个写法
            else:
                file_to_read.readline()
            a_flag+=1
    file_to_read.close()
    return contents
  
def load_bias_file(file):
    contents = []
    label_list = []
    flag = 0  
    #firstly, read layers information from the existed file
    with open(file, 'r') as file_to_read:
        while 1:
            line = file_to_read.readline()       #read one line, and store as a list
            if not line:
                break
            line = line.strip('\n')              #remove the '\n' in the end
            line = line.strip(' ')               #remove the ' ' in the end
            #这一块数据处理也是一个难点啊
            line = line.split(' ')               #convert the line string in the list into the different strings, based on the character:' 'space
            line = line[::-1]                    #取一遍倒续
            for i in line:
                if flag == 0:
                    str1 = i
                    flag = flag + 1
                else:
                    str2 = i
                    flag = 0
                    str = str2 + str1            #这里应该是str1+str2，还是str2+str1 ? 因为取了倒续，所以是2+1
                    #print(str)
                    parameter = s16_bias(int(str, 16))
                    #print(parameter)
                    contents.append(parameter)
    return contents
    
def max(a,b):
    if a>b:
        return a
    else:
        return b
        
def max_4(a1,a2,a3,a4):
    t1 = max(a1, a2)
    t2 = max(a3, a4)
    t = max(t1, t2)
    return t

def bias_load():
    file = '/mnt/hgfs/Python Programming/FuWeiBei/数字AI赛道测试样例2/data_bias.txt'   #注意这个路径，随着改变
    bias = load_bias_file(file)
    return bias

'''
按照kernel的循环来计算，先从文件中取出一个kernel
在这个kernel下，循环一遍ifmap，得到一个ofmap
'''	
def main():
    ofmap = []
    file_list = ['/mnt/hgfs/Python Programming/FuWeiBei/数字AI赛道测试样例2/ifmap.txt', '/mnt/hgfs/Python Programming/FuWeiBei/数字AI赛道测试样例2/kernel.txt', '/mnt/hgfs/Python Programming/FuWeiBei/数字AI赛道测试样例2/data_bias.txt']
    ifm_flag = 34                      #在列上滑动时，需要的基数
    ofm_flag = 32*2                    #做Max_pooling时的基数 stride=2
    bias_count = 0
    pooling_out = []
    relu_out = []
    f = open('ofmap.txt', 'w')  # 若是'wb'就表示写二进制文件  #https://www.cnblogs.com/programer-xinmu78/p/10661170.html
    f_pooling = open('pooling.txt', 'w')
    f_relu = open('relu.txt','w')
    f_truncation = open('truncation.txt','w')
    
    bias = bias_load()                 #加载bias
    #print(len(bias))
    
    for w in range(128):
        #一个kernel的计算
        file = file_list[1]                        #kernel
        weights = load_file(file,0+w*9,8+w*9)      #9*64 elements
        #print(weights)
       
        file = file_list[0]                        #ifmap
        '''convolution 计算'''
        ofmap = []            #这个需要在这里进行赋初值，不然不同kernel的结果会被磊到一个列表中
        #输出output feature map的一个层，即完成一个kernel的完整计算。ofmap的数据排列，就是第一行第一个数据，第一行第二个......第32行第32个
        for i in range(32):                #在列上滑动 stride=1。列上滑动，可不止只加32,乘以一个基数
            for j in range(32):            #在行上滑动
                ifmap_0 = load_file(file, 0+i*ifm_flag+j, 2+i*ifm_flag+j)
                ifmap_1 = load_file(file, 0+34+i*ifm_flag+j, 2+34+i*ifm_flag+j)
                ifmap_2 = load_file(file, 0+68+i*ifm_flag+j, 2+68+i*ifm_flag+j)
                ifmap = ifmap_0 + ifmap_1 + ifmap_2  #三个列表合成一个列表，得到一个9*9的感知区域
                #print(ifmap)
                partial_sum = 0            #初始部分和为0
                for ii in range(len(weights)):    #计算一个3*3的矩阵计算
                    #print(partial_sum)
                    partial_sum = partial_sum + weights[ii] * ifmap[ii]  #得到一个ofmap中的元素
                ofmap.append(partial_sum)
                #print(ofmap)
        '''add bias'''
        for i in range(len(ofmap)):
            ofmap[i] = ofmap[i]+bias[bias_count];        
        #print(len(ofmap))
        f.write(str(ofmap)+"\n") #写卷积输出结果
        '''Max pooling'''
        pooling_out = []
        for i in range(16):                    #在列上滑动
            for j in range(16):                #在行上滑动
                pooling = max_4(ofmap[0+j*2+i*ofm_flag], ofmap[1+j*2+i*ofm_flag], ofmap[0+32+j*2+i*ofm_flag], ofmap[1+32+j*2+i*ofm_flag])
                pooling_out.append(pooling)
        f_pooling.write(str(pooling_out)+"\n")
        '''ReLU'''
        relu_out = []
        for i in range(len(pooling_out)):
            relu = max(0, pooling_out[i])
            relu_out.append(relu)
        f_relu.write(str(relu_out)+"\n")
        '''truncation'''
        truncate = []
        for i in range(len(relu_out)):
            #t = bin(relu_out[i])                   #https://jingyan.baidu.com/article/11c17a2cfb80d6f446e39d8a.html
            t_4 = relu_out[i] & 0b1000              #https://developer.aliyun.com/ask/121319?spm=a2c6h.13159736s
            #舍弃低4位
            t_truncate = relu_out[i] >> 4           #https://blog.csdn.net/zichehanTZ/article/details/81809176
            #得到中间的8位   #这里应该是得到中间的7位，因为结果是有符号数，必须有一位用于存符号，又都是正数，所以直接取七位
            #t_truncate = t_truncate & 0b11111111   #https://stackoverflow.com/questions/46202913/python-cut-a-x-bit-binary-number-to-a-byte-8bit/46202957
            #得到中间八位
            if t_truncate >= 0b1111111:             #进行饱和操作
                t_carry = 0b1111111
            else:
                if t_4 == 0:  #不进位
                    t_carry = t_truncate & 0b1111111 #取低7位
                else:         #进位
                    t_truncate = t_truncate + 1
                    t_carry = t_truncate & 0b1111111 #取低7位
            t_16 = hex(t_carry)                     #https://blog.csdn.net/mouday/article/details/83445028
            truncate.append(t_16)
        f_truncation.write(str(truncate)+"\n")
        '''bias'''
        bias_count = bias_count + 1  #要开始进行下一个kernel的计算了，bias标注也要更新
    
    f.close()
    f_pooling.close()
    f_relu.close()
    f_truncation.close()
       
'''
execution lines
'''
#数据格式转化
convert.main_initial()    #这个必须最开始执行
convert.main_ifmap()
convert.main_kernel()
#主函数执行
main()
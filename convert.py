'''作用：
1 拆分原始文件，分别存为ifmap kernel bias文件
2 给Ifmap加padding
3 转化weights的排列方式
'''
#主要用于给ifmap加padding
#并且转化weights的摆放方式
def load_file(file, line_start, line_end):
    a_flag = 0                                   #用于标记读的行数，最开始都是0
    contents = ""
    label_list = []
    #firstly, read layers information from the existed file
    with open(file, 'r') as file_to_read:
        while a_flag <= line_end:
            if a_flag >= line_start:
                line = file_to_read.readline()       #read one line, and store as a list
                contents= contents + line
            else:
                file_to_read.readline()
            a_flag+=1
    return contents
    
#add 64 zeros
def zero():
    a = "00 "
    b = ""
    for i in range(64):
        b = b + a
    return b

#给ifmap加padding    
def main_ifmap():
    file_list = ['/mnt/hgfs/Python Programming/FuWeiBei/数字AI赛道测试样例2/data_ifm.txt', '/mnt/hgfs/Python Programming/FuWeiBei/数字AI赛道测试样例2/data_kernel.txt', '/mnt/hgfs/Python Programming/FuWeiBei/数字AI赛道测试样例2/data_bias.txt']
    file = file_list[0]
    #for i in range(64):
    #    zero.append(00)
    #print(len(zero))
    zero_64 = zero()
    f = open('ifmap.txt', 'w')  # 若是'wb'就表示写二进制文件  #https://www.cnblogs.com/programer-xinmu78/p/10661170.html
    for i in range(35):
        f.write(zero_64 + "\n")
    ifmap_flag = 32
    for i in range(32):
        line_start = 0+ifmap_flag * i    #这里用i乘以一个基数，表示向前
        line_end = 31+ifmap_flag * i
        ifmap = load_file(file, line_start, line_end)
        f.write(ifmap)
        f.write(zero_64 + "\n")
        f.write(zero_64 + "\n")
    for i in range(32):
        f.write(zero_64 + "\n")
    f.write(zero_64)
    f.close()
        
#改变kernel的排列方式
def main_kernel():
    file = '/mnt/hgfs/Python Programming/FuWeiBei/数字AI赛道测试样例2/data_kernel.txt'
    f = open('kernel.txt', 'w') #用于存排列之后的kernel的数据
    for i in range(64):         #共64个kernels
        for j in range(9):      #取一个kernel
            kernel = load_file(file, i+64*j, i+64*j) #每次只取一行
            f.write(kernel)
    for i in range(64):         #共64个kernels
        for j in range(9):      #取一个kernel
            kernel = load_file(file, 9*64+i+64*j, 9*64+i+64*j) #每次只取一行
            f.write(kernel)
    f.close()

#把最初的文件，先分摊给三个文件，ifmap.txt，kernel.txt，bias.txt
def main_initial():
    file_list = ['/mnt/hgfs/Python Programming/FuWeiBei/数字AI赛道测试样例2/输入数据+参数+偏置.txt']
    file = file_list[0]
    f_ifmap = open('data_ifm.txt', 'w')
    f_kernel = open('data_kernel.txt', 'w')
    f_bias = open('data_bias.txt', 'w')
    str1='load ifm data\n'
    str2='load weights data\n'
    str3='load const data\n'

    with open(file, 'r') as file_to_read:
        while 1:
            line = file_to_read.readline()
            if not line:
                break
            if str1 == line:
                while 1:
                    line = file_to_read.readline()
                    if line == str2:
                        break
                    line=line[6:]
                    f_ifmap.write(line)
            if line == str2:
                i=0
                while 1:
                    line = file_to_read.readline()
                    if line == str3:
                        break
                    line=line[6:]
                    if i <= 1150:            #这个if else是用于去掉最后一行的\n。之所以ifmap不需要，是因为匹配之前写的ifmap代码
                        f_kernel.write(line)
                        i=i+1
                    else:
                        line=line.strip('\n')
                        f_kernel.write(line)
            if line == str3:
                i=0
                while 1:
                    line = file_to_read.readline()
                    if not line:
                        break
                    line=line[6:]
                    if i <= 2:
                        f_bias.write(line)
                        i=i+1
                    else:
                        line=line.strip('\n')
                        f_bias.write(line)
            break
            
    f_ifmap.close()
    f_kernel.close()
    f_bias.close()

#这些语句在main.py中被执行
'''
main_initial()    #这个必须最开始执行
main_ifmap()
main_kernel()
#main_bias()'''
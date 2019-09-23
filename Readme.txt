可直接运行main.py
使用命令：python3 main.py

txt文件中都是数据
其中ofmap.txt pooling.txt relu.txt truncation.txt等文件，都是算法中，各阶段输出的中间值
数据都是按照层来存储的。即ofmap有128个通道，即128层，一层有32*32的数据，这32*32的数据是存在一起的，按照先x再y的方式

convert.py是用于数据格式处理
将“输入数据+参数+偏置.txt”文件，转化成我们需要的文件。最终在main.py中被用到的是data_bias.txt ifmap.txt kernel.txt
data_ifmap.txt data_kernel.txt是输出的中间文件。
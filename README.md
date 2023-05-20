# 动手制作一台计算机

![image](https://github.com/bitetata/make_a_computer/blob/master/gif/computer1.gif)

### 本项目中的文件是《动手制作一台计算机》的演示文件。在动手制作计算机电路的环节，我们使用logisim仿真软件来制作计算机。主要的文件简介如下：
* “logisim-generic-2.7.1.jar”是logisim软件的jar包，需要安装java5以上的环境才可运行
* “computer1.circ”是第五章“制作一个最简单能够运转的计算机”的仿真电路文件
* “computer2.circ”是第五章“制作一个能做加法运算的计算机”的仿真电路文件
* “computer3.circ”是第五章“制作一个能带有内存的计算机”的仿真电路文件（注意：为了能够容纳更多的ROM指令，ROM地址输入端使用8位，而不是书中的4位）
* “computer4.circ”是第五章“制作一个支持条件跳转的计算机”的仿真电路文件（注意：为了能够容纳更多的ROM指令，ROM地址输入端使用8位，而不是书中的4位）
* “computer4汇编器.py”是为最终计算机电路“computer4.circ”编写的一个“汇编器”。它能够把汇编指令编译成ROM指令
* “computer4测试代码.txt”是书中fabonacci数列的汇编代码实现。由于这个计算机电路的数据位只有4位，所以只能计算前几个数列，超过7个就会溢出。
* “computer4生成的ROM代码.txt”是使用“computer4汇编器.py”编译“computer4测试代码.txt”生成的ROM指令文件。“computer4生成的ROM代码.txt”可以在logisim软件中被直接加载到ROM里
* “fabonacci的python代码.py”是书中fabonacci的python版本代码

### 最后注意的一点是，由于书中的演示的集成电路和logisim软件中自带的集成电路有点区别，所以logisim里面的电路连接方式和书中相比会有一点区别。比如比较器的输出端不同、内存的输入输出端不同，但多数的电路连接方式都是相同的。
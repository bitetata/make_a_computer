# _*_ coding: utf-8 _*_
from Tkinter import *
from ScrolledText import *
import tkMessageBox
from tkFileDialog import *
import fileinput
import re
import math

t1=[]
root=None

raBits = 8						#ROM地址输入端的位数
raMask = pow(2, raBits) - 1		#raBits转换成mask。比如raBits=8，那么raMask=二进制的11111111
rdBits = 4						#ROM地址输入端的位数
rdMask = pow(2, rdBits) - 1		#rdBits转换成mask。比如rdBits=4，那么rdMask=二进制的1111
otBits = raBits + rdBits		#其它控制指令是从ROM输出端的第otBits位开始


def genMoveCode(arg1, arg2, startAddr):
	"""
	地址1：把“内存地址”传送到总线
	地址2：内存的CP_A由低电平变成高电平，选择“内存地址”
	地址3：把“数字”传送到总线
	地址4：内存的CP_W由低电平变成高电平，“数字”就会被保存到“内存地址”中。
	"""
	print("move", arg1, arg2, startAddr)
	return [
		(startAddr+1)&raMask | ((arg1&rdMask)<<raBits) | (1<<otBits),
		(startAddr+2)&raMask | ((arg1&rdMask)<<raBits) | (1<<otBits) | (1<<(otBits+6)),
		(startAddr+3)&raMask | ((arg2&rdMask)<<raBits) | (1<<otBits),
		(startAddr+4)&raMask | ((arg2&rdMask)<<raBits) | (1<<otBits) | (1<<(otBits+7)),
	]

def genAddCode(arg1, arg2, arg3, startAddr):
	"""
	地址1：把“内存地址2”传送到总线
	地址2：内存的CP_A由0变1，选择“内存地址”
	地址3：内存的En变成1，内存输出数据到总线
	地址4：加法器的CP1由0变1，总线数据被传送到加法器的寄存器1里
	地址5：把“内存地址3”传送到总线
	地址6：内存的CP_A由0变1，选择“内存地址”
	地址7：内存的En变成1，内存输出数据到总线
	地址8：加法器的CP2由0变1，总线数据被传送到加法器的寄存器2里
	地址9：把“内存地址1”传送到总线
	地址10：内存的CP_A由0变1，选择“内存地址”
	地址11：加法器的En变成1，计算结果传送到总线上
	地址12：内存的CP_W由0变1，把总线数据保存到内存中
	"""
	print("add", arg1, arg2, arg3, startAddr)
	return [
		(startAddr+1)&raMask | ((arg2&rdMask)<<raBits) | (1<<otBits),
		(startAddr+2)&raMask | ((arg2&rdMask)<<raBits) | (1<<otBits) | (1<<(otBits+6)),
		(startAddr+3)&raMask | (1<<(otBits+5)),
		(startAddr+4)&raMask | (1<<(otBits+5)) | (1<<(otBits+3)),
		(startAddr+5)&raMask | ((arg3&rdMask)<<raBits) | (1<<otBits),
		(startAddr+6)&raMask | ((arg3&rdMask)<<raBits) | (1<<otBits) | (1<<(otBits+6)),
		(startAddr+7)&raMask | (1<<(otBits+5)),
		(startAddr+8)&raMask | (1<<(otBits+5)) | (1<<(otBits+4)),
		(startAddr+9)&raMask | ((arg1&rdMask)<<raBits) | (1<<otBits),
		(startAddr+10)&raMask | ((arg1&rdMask)<<raBits) | (1<<otBits) | (1<<(otBits+6)),
		(startAddr+11)&raMask | (1<<(otBits+2)),
		(startAddr+12)&raMask | (1<<(otBits+2)) | (1<<(otBits+7)),
	]

def genJumpCode(arg1, startAddr):
	"""
	直接把“指令地址”设置到ROM的D4~D1位里
	"""
	print("jump", arg1, startAddr)
	return [
		arg1,
	]

def genJumpIfCode(arg1, arg2, arg3, startAddr):
	"""
	地址1：把“内存地址1”传送到总线
	地址2：内存的CP_A由0变1，选择“内存地址”
	地址3：内存的En变成1，内存输出数据到总线
	地址4：比较器的CP1由0变1，总线数据被传送到比较器的寄存器1里
	地址5：把“内存地址2”传送到总线
	地址6：内存的CP_A由0变1，选择“内存地址”
	地址7：内存的En变成1，内存输出数据到总线
	地址8：比较器的CP2由0变1，总线数据被传送到比较器的寄存器2里
	地址9：D19和D20都设置1，比较器生效
	地址10：本条指令的D4~D1被设置成“当前地址+2”，即下下条指令地址
	地址11：本条指令的D4~D1被设置成“指令地址”
	"""
	print("jumpif", arg1, arg2, arg3, startAddr)
	return [
		(startAddr+1)&raMask | ((arg2&rdMask)<<raBits) | (1<<otBits),
		(startAddr+2)&raMask | ((arg2&rdMask)<<raBits) | (1<<otBits) | (1<<(otBits+6)),
		(startAddr+3)&raMask | (1<<(otBits+5)),
		(startAddr+4)&raMask | (1<<(otBits+5)) | (1<<(otBits+9)),
		(startAddr+5)&raMask | ((arg3&rdMask)<<raBits) | (1<<otBits),
		(startAddr+6)&raMask | ((arg3&rdMask)<<raBits) | (1<<otBits) | (1<<(otBits+6)),
		(startAddr+7)&raMask | (1<<(otBits+5)),
		(startAddr+8)&raMask | (1<<(otBits+5)) | (1<<(otBits+8)),
		(startAddr+9)&raMask | (1<<(otBits+10)) | (1<<(otBits+11)),
		(startAddr+11)&raMask,
		arg1,
	]

def genOutCode(arg1, startAddr):
	"""
	地址1：把“内存地址”传送到总线
	地址2：内存的CP_A由低电平变成高电平，选择“内存地址”
	地址3：把“数字”传送到总线
	地址4：ROM的D10由0变成1，总线数据显示到“7段发光二极管”上
	"""
	print("out", arg1, startAddr)
	return [
		(startAddr+1)&raMask | ((arg1&rdMask)<<raBits) | (1<<otBits),
		(startAddr+2)&raMask | ((arg1&rdMask)<<raBits) | (1<<otBits) | (1<<(otBits+6)),
		(startAddr+3)&raMask | (1<<(otBits+5)),
		(startAddr+4)&raMask | (1<<(otBits+5)) | (1<<(otBits+1)),
	]

#compile
def compileOneLine(text, startAddr):
	m = re.match(r'^[ \t]*mov[ \t]+\[(\d+)\][ \t]*,[ \t]*(\d+)[ \t]*$', text)
	if m:
		arg1 = int(m.groups()[0])
		arg2 = int(m.groups()[1])
		return genMoveCode(arg1, arg2, startAddr)
	m = re.match(r'^[ \t]*add[ \t]+\[(\d+)\][ \t]*,[ \t]+\[(\d+)\][ \t]*,[ \t]+\[(\d+)\][ \t]*$', text)
	if m:
		arg1 = int(m.groups()[0])
		arg2 = int(m.groups()[1])
		arg3 = int(m.groups()[2])
		return genAddCode(arg1, arg2, arg3, startAddr)
	m = re.match(r'^[ \t]*jump[ \t]+(\w+)[ \t]*$', text)
	if m:
		arg1 = m.groups()[0]
		return genJumpCode(arg1, startAddr)
	m = re.match(r'^[ \t]*jumpif[ \t]+(\w+)[ \t]*,[ \t]+\[(\d+)\][ \t]*,[ \t]+\[(\d+)\][ \t]*$', text)
	if m:
		arg1 = m.groups()[0]
		arg2 = int(m.groups()[1])
		arg3 = int(m.groups()[2])
		return genJumpIfCode(arg1, arg2, arg3, startAddr)
	m = re.match(r'^[ \t]*out[ \t]+\[(\d+)\][ \t]*$', text)
	if m:
		arg1 = int(m.groups()[0])
		return genOutCode(arg1, startAddr)


def complieCode(text):
	labelAddrMap = {}
	binCodeList = []
	lineNumber = 0
	for line in text.split("\n"):
		lineNumber = lineNumber + 1
		line = line.strip().lower()
		if len(line) <= 0:
			continue
		m = re.match(r'^[ \t]*(\w+):[ \t]*$', line)
		if m:
			arg1 = m.groups()[0]
			labelAddrMap[arg1] = len(binCodeList)
		else:
			oneCodes = compileOneLine(line, len(binCodeList))
			if oneCodes != None:
				binCodeList.extend(oneCodes)
			else:
				tkMessageBox.showinfo('语法错误', "Line " + str(lineNumber) + ":\n" + line)
				return
	#把label修正成ROM地址
	print(labelAddrMap)
	for i in xrange(0,len(binCodeList)):
		if not isinstance(binCodeList[i], int):
			if labelAddrMap.has_key(binCodeList[i]):
				binCodeList[i] = labelAddrMap[binCodeList[i]] & raMask
			else:
				tkMessageBox.showinfo('语法错误', "Unknown label:\n" + binCodeList[i])
				return
	print(binCodeList)
	return binCodeList


def die():
	sys.exit(0)


class editor:
	def __init__(self,rt):
		if rt==None:
			self.t=Tk()
		else:
			self.t=Toplevel(rt)
		self.t.title("汇编器")#("汇编器 %d"%len(t1))
		self.t.geometry("550x600")  
		self.bar=Menu(rt)
		
		self.filem=Menu(self.bar, tearoff=0)
		self.filem.add_command(label="打开",command=self.openfile)
		#self.filem.add_command(label="新建",command=neweditor)
		self.filem.add_command(label="保存",command=self.savefile)
		#self.filem.add_command(label="关闭",command=self.close)
		self.filem.add_separator()
		self.filem.add_command(label="退出",command=die)
		
		self.compilem=Menu(self.bar, tearoff=0)
		self.compilem.add_command(label="编译生成Bin文件",command=self.compile)

		self.bar.add_cascade(label="文件",menu=self.filem)
		self.bar.add_cascade(label="编译",menu=self.compilem)
		self.t.config(menu=self.bar)
		
		self.f=Frame(self.t,width=512)
		self.f.pack(expand=1,fill=BOTH)
		
		self.st=ScrolledText(self.f,background="white", font=('courier', 20, 'normal'))
		self.st.pack(side=LEFT,fill=BOTH,expand=1)
	
	def close(self):
		self.t.destroy()
	
	def openfile(self):
		p1=END
		oname=askopenfilename(filetypes=[("Python file","*.txt")])
		if oname:
			for line in fileinput.input(oname):
				self.st.insert(p1,line)
			self.t.title(oname)
	
	def savefile(self):
		sname=asksaveasfilename(filetypes=[("Python file","*.txt")])
		if sname:
			ofp=open(sname,"w")
			ofp.write(self.st.get(1.0,END))
			ofp.flush()
			ofp.close()
			self.t.title(sname)

	def saveHexfile(self, data):
		sname=asksaveasfilename(filetypes=[("Python file","*.txt")])
		if sname:
			ofp=open(sname,"wb")
			ofp.write(data)
			ofp.flush()
			ofp.close()
			self.t.title(sname)

	def compile(self):
		binCodeList = complieCode(self.st.get(1.0,END))
		if binCodeList != None:
			dataList = ["v2.0 raw"]
			lineCount = (len(binCodeList)+15) / 16
			for x in xrange(0,lineCount):
				lineDataList = []
				for y in xrange(16*x, 16*(x+1)):
					if y >= len(binCodeList):
						break
					lineDataList.append("%X" % binCodeList[y])
				dataList.append(' '.join(lineDataList))
			data = '\n'.join(dataList)
			self.saveHexfile(data)
	
def neweditor():
	global root
	t1.append(editor(root))


if __name__=="__main__":
	root=None
	t1.append(editor(root))
	root=t1[0].t
	root.mainloop()

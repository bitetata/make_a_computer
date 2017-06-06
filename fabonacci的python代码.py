var0 = 1
var1 = 1
var2 = 0
var3 = 1
var4 = 10
while True:
	var0 = var0 + var1
	var1 = var0 + var1
	var2 = var2 + var3
	if var2 >= var4:
		break
print(var1)
from sympy import *

f = open("text1.txt").read()
l = len(f)
d = divisors(l)
#print(l)
print (d)
#for s in divisors(l)
valor_inicial = 2
valor_final = 1000

rango_seleccionado = [x for x in d if valor_inicial <= x <= valor_final]

print(rango_seleccionado)

"""for i in range(0,l):

    if i % 197 == 0:
        print(f[i], end="\n")  
    else:
        print (f[i])

x = 0
for i in range(0,l):
    print(f[x], end= '')
    x = x+197
"""


for j in range (0,len(rango_seleccionado)):
    print("\n")
    x = 0
    for i in range(0,1000):   
        print(f[x], end= '')
        x = x+rango_seleccionado[j]
    
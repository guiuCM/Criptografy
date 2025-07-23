from sympy import Matrix
#from intertools import *
import numpy as np

texto = open("text2.txt").read()
l = len(texto)
print(l)

from collections import defaultdict
#import re

# Función para dividir el texto en trigramas
def generar_trigramas(texto):
    #palabras = re.findall(r'\b\w+\b', texto.lower())  # Divide el texto en palabras
    trigramas = []
    for i in range(0,l-2):
        trigramas.append((texto[i], texto[i + 1], texto[i + 2]))
    return trigramas

# Genera trigramas
trigramas = generar_trigramas(texto)

# Cuenta la frecuencia de los trigramas
frecuencia_trigramas = defaultdict(int)
for trigrama in trigramas:
    frecuencia_trigramas[trigrama] += 1

# Encuentra los tres trigramas más frecuentes
trigramas_mas_frecuentes = sorted(frecuencia_trigramas.items(), key=lambda x: x[1], reverse=True)[:3]

m_en = np.array([[11, 17, 6],[3, 18, 18],[9, 7, 3]])
m_freq = np.array([[19, 7, 4],[0, 13, 3],[8, 13, 6]])
""""
# Imprime los tres trigramas más frecuentes
x = 0
y = 0
for trigrama, frecuencia in trigramas_mas_frecuentes:
    m1[x][y] = ord(trigrama[0])-65  #es la A en ASCII (0x65 0 101)
    m1[x][y+1] = ord(trigrama[1])-65
    m1[x][y+2] = ord(trigrama[2])-65
    print(trigrama, frecuencia)
    x = x+1
    """

#print(m1)
print('\n')
#permutations=(['THE','AND','THA', 'ENT', 'ING', 'ION', 'TIO', 'FOR', 'NDE'], 3)
#print (permutations)
print('\n')
m_freq_inv = Matrix(m_freq).inv_mod(26)
#print(m_freq_inv)

h_trans = np.dot(m_freq_inv, m_en)
h_trans_mod26 = h_trans % 26
H = np.transpose(h_trans_mod26)
H = Matrix(H).inv_mod(26)
print("La matriu clau es: ")
print (H)
print("\n")
#print(trigramas[0])

mf = np.array([[1],[1],[1]])

espai = 0
for i in range(0, 1000,3): #multiplicar nomes trigrames
    mf[0][0] = ord(texto[i])-65  #es la A en ASCII (0x65 0 101)
    mf[1][0] = ord(texto[i+1])-65
    mf[2][0] = ord(texto[i+2])-65
    
    """
    mf[1][0] = ord(texto[i+3])-65  #es la A en ASCII (0x65 0 101)
    mf[1][1] = ord(texto[i+4])-65
    mf[1][2] = ord(texto[i+5])-65

    mf[2][0] = ord(texto[i+6])-65  #es la A en ASCII (0x65 0 101)
    mf[2][1] = ord(texto[i+7])-65
    mf[2][2] = ord(texto[i+8])-65
    """
    
    #print (mf)

    rf = H * mf
    #print(rf)
    #rf = Matrix(rf).inv_mod(26)
    rf2 = np.array(rf  % 26)
    #print("\n")
    #print(rf2)
    #print("\n")


    
    for x in range(0, 3):
        print( chr((rf2[x][0]+65)), end= '')
        espai += 1
        if espai == 10:
            print("\n")


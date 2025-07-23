import sympy as sp

# Definir una matriz como símbolos
A =sp.Matrix([
    [19, 7, 4],
    [0, 13, 3],
    [19, 7, 0]
])

A_inv = A.inv()

# Imprimir la matriz inversa
print("Matriz Original:")
print(A)
print("\nMatriz Inversa:")
print(A_inv)

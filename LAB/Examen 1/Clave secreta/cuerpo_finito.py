class G_F:
    
    # Genera un cuerpo finito usando como polinomio irreducible el dado
    # representado como un entero. Por defecto toma el polinomio del AES.
    # Los elementos del cuerpo los representaremos por enteros 0<= n <= 255.
    

    def __init__(self, Polinomio_Irreducible = 0x11B):
    
    
    # Entrada: un entero que representa el polinomio para construir el cuerpo
    # Tabla_EXP y Tabla_LOG dos tablas, la primera tal que en la posicion
    # i-esima tenga valor a=g**i y la segunda tal que en la posicion a-esima
    # tenga el valor i tal que a=g**i. (g generador del cuerpo finito
    # representado por el menor entero entre 0 y 255.)

        self.Polinomio_Irreducible = Polinomio_Irreducible
        self.Tabla_EXP, self.Tabla_LOG = self.generar_tablas()
        #self.Tamaño_Cuerpo = 256  # El cuerpo tiene 256 elementos (valores de 0 a 255)

    def generar_tablas(self):
        # Crear listas vacías para Tabla_EXP y Tabla_LOG
        Tabla_EXP = [0] * 256    #0-255
        Tabla_LOG = [0] * 256    #0-255

        # Inicializar valores iniciales
        valor = 1
        for i in range(256 - 1):
            Tabla_EXP[i] = valor
            Tabla_LOG[valor] = i
            valor = (valor * 2) % 256
            if valor >= 256:
                valor ^= self.Polinomio_Irreducible  #mod (0x11B)

        # La última entrada de Tabla_EXP
        Tabla_EXP[256 - 1] = Tabla_EXP[0]

        return Tabla_EXP, Tabla_LOG



    def xTimes(self, n):
    
    # Entrada: un elemento del cuerpo representado por un entero entre 0 y 255
    # Salida: un elemento del cuerpo representado por un entero entre 0 y 255
    # que es el producto en el cuerpo de 'n' y 0x02 (el polinomio X).


        #Multiplicar 'n' por el polinomio X (0x02) en el cuerpo finito
        resultado = n << 1  # Desplazamiento a la izquierda es equivalente a multiplicar por 2
        if resultado >= 256:
            resultado ^= self.Polinomio_Irreducible  #mod (0x11B)
        return resultado

    #def Producto_lento(self, a, b):
        

    def producto(self, a, b):
    
    # Entrada: dos elementos del cuerpo representados por enteros entre 0 y 255
    # Salida: un elemento del cuerpo representado por un entero entre 0 y 255
    # que es el producto en el cuerpo de la entrada.
    # Atencion: Se valorara la eficiencia. No es lo mismo calcularlo
    # usando la definicion en terminos de polinomios o calcular
    # usando las tablas Tabla_EXP y Tabla_LOG.
        
        # Se tiene que usar las tablas
        if a == 0 or b == 0:
            return 0    # Caso base, multiplicar per 0
        else:
            log_a = self.Tabla_LOG[a]
            log_b = self.Tabla_LOG[b]
            log_result = (log_a + log_b) % 255  # Suma en el cuerpo finito
            result = self.Tabla_EXP[log_result] 
            return result
            #no s'ha de fer modul?


    def inverso(self, n):
    
    # Entrada: un elementos del cuerpo representado por un entero entre 0 y 255
    # Salida: 0 si la entrada es 0,
    # el inverso multiplicativo de n representado por un entero entre
    # 1 y 255 si n <> 0.
    # Atencion: Se valorara la eficiencia.

        # Usar las tablas
        if n == 0:
            return 0  # El inverso de 0 es 0 en cualquier cuerpo finito
        else:
            log_n = self.Tabla_LOG[n]
            log_inverso = 255 - log_n  # Resta en el cuerpo finito
            inverso = self.Tabla_EXP[log_inverso]
            return inverso
        


cf = G_F()
n = 150
n1 = 50
n2 = 100

r = cf.xTimes(n)
r1 = cf.producto(n1,n2)
r2 = cf.inverso(n)

print(r)
print('\n')
print(r1)
print('\n')
print(r2)
print('\n')
print(cf.Tabla_EXP)


# import hashlib
# myhash = hashlib.sha512("mmm")
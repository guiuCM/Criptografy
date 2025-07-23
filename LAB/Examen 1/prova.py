import os
import random

import AES # Fichero AES.py con vuestras clases implementadas

Polinonios_Irreducibles=[0x11b, 0x11d, 0x1f5, 0x1f9]

for polinomio in Polinonios_Irreducibles:
    print(hex(polinomio))
    for len_key in [16,24,32][:]:
        key = os.urandom(len_key)
        fichero = 'wells_the_time_machine.txt' # Fichero cualquiera a cifrar/descifrar
        aes_alumno = AES.AES(key, polinomio)

        aes_alumno.encrypt_file(fichero)
        aes_alumno.decrypt_file(fichero+'.enc')

        comando = f'diff {fichero} {fichero}.enc.dec'
        print('Coincide descifrado y original '+fichero, os.system(comando))
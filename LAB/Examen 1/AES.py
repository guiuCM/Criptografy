import numpy as np
import os

class G_F:
    
    # Genera un cuerpo finito usando como polinomio irreducible el dado
    # representado como un entero. Por defecto toma el polinomio del AES.
    # Los elementos del cuerpo los representaremos por enteros 0<= n <= 255.

    def __init__(self, Polinomio_Irreducible = 0x11B):
       
        self.Polinomio_Irreducible = Polinomio_Irreducible
        exp, log = self.generar_tabla()
        self.Tabla_EXP = exp
        self.Tabla_LOG = log

    def xTimes(self, n):
       
        if n < 128:
            return n << 1
        else:
            res = n << 1
            return res ^ self.Polinomio_Irreducible

    def producto_lento(self, a, b):
        if a == 0 or b == 0:
            return 0

        res = 0
        for i in range(8):
            if b & 1:
                res ^= a
            b >>= 1
            a = self.xTimes(a)

        return res
    
    def elevar_lento(self, a, b):

        res = 1
        for _ in range(b):
            res = self.producto_lento(res, a)

        return res
    
    def elevar(self, a, b):
        
        res = 1
        for _ in range(b):
            res = self.producto(res, a)

        return res

    def matrix_multiplication(self, A, B):

        result = np.zeros(A.shape[0], dtype=int)

        for i in range(A.shape[0]):
            for j in range(A.shape[1]):
                result[i] ^= self.producto(A[i,j], B[j])

        return result

    
    def generar_tabla(self):

        for i in range(2,256):
            exp = np.zeros(256, dtype=np.int32)
            log = np.zeros(256, dtype=np.int32)
            for j in range(256):
                exp[j] = self.elevar_lento(i,j)
                log[exp[j]] = j
            if len(set(exp))==255:
                return np.append(exp,exp[1:256]), log    


    def producto(self, a, b):
        
        if a==0 or b==0:
            return 0

        return self.Tabla_EXP[(self.Tabla_LOG[a]+self.Tabla_LOG[b])]
    
    def inverso(self, n):

        if n==0:
            return 0

        return self.Tabla_EXP[255-self.Tabla_LOG[n]]



###############################################################################################################################################
###############################################################################################################################################



class AES:

    # Documento de referencia:
    # Federal Information Processing Standards Publication (FIPS) 197: Advanced Encryption
    # Standard (AES) https://doi.org/10.6028/NIST.FIPS.197-upd1
    # El nombre de los métodos, tablas, etc son los mismos (salvo capitalización)
    # que los empleados en el FIPS 197

    def __init__(self, key, Polinomio_Irreducible = 0x11B):

        self.Polinomio_Irreducible = Polinomio_Irreducible
        self.Gf = G_F(Polinomio_Irreducible)
        Sbox, ISbox = self.TableSubBytes()
        self.SBox = Sbox
        self.InvSBox = ISbox
        self.Rcon = self.ConstructRcon()
        self.InvMixMatrix = np.array([[0x0e,0x0b,0x0d,0x09],
                                      [0x09,0x0e,0x0b,0x0d],
                                      [0x0d,0x09,0x0e,0x0b],
                                      [0x0b,0x0d,0x09,0x0e]])
        self.Mix = np.array([[0x02,0x03,0x01,0x01],
                        [0x01,0x02,0x03,0x01],
                        [0x01,0x01,0x02,0x03],
                        [0x03,0x01,0x01,0x02]])
        nr, expanded_key = self.KeyExpansion(list(key))
        self.Nr = nr
        self.Expanded_KEY = expanded_key
    
    def ConstructRcon(self):
        result = np.zeros(10, dtype=int)
        result[0] = 0x01
        for i in range (1,10):
            result[i] = self.Gf.xTimes(result[i-1])
        return result

    def TableSubBytes(self):

        def bits_to_byte(bits):
            return int(''.join(map(str,bits)), 2)

        def sum_bits(vec):
            aux = bits_to_byte(vec)            
            return aux ^ 0x63

        result = np.zeros(256, dtype=int)
        i_result = np.zeros(256, dtype=int)
        get_bits = lambda byte: [int(bit) for bit in f"{byte:08b}"]
        Affine = np.array([[1,1,1,1,1,0,0,0],
                           [0,1,1,1,1,1,0,0],
                           [0,0,1,1,1,1,1,0],
                           [0,0,0,1,1,1,1,1],
                           [1,0,0,0,1,1,1,1],
                           [1,1,0,0,0,1,1,1],
                           [1,1,1,0,0,0,1,1],
                           [1,1,1,1,0,0,0,1]])
        
        for value in range(256):
                inv = self.Gf.inverso(value)
                b_inv = get_bits(inv)
                vec = np.array(b_inv)
                aux = self.Gf.matrix_multiplication(Affine,vec)
                sum_b = sum_bits(aux)
                result[value] = sum_b
                i_result[sum_b] = value
        
        return result, i_result


    def SubBytes(self, State):

        
        result = np.array([[self.SBox[State[0][0]],self.SBox[State[0][1]],self.SBox[State[0][2]],self.SBox[State[0][3]]],
                           [self.SBox[State[1][0]],self.SBox[State[1][1]],self.SBox[State[1][2]],self.SBox[State[1][3]]],
                           [self.SBox[State[2][0]],self.SBox[State[2][1]],self.SBox[State[2][2]],self.SBox[State[2][3]]],
                           [self.SBox[State[3][0]],self.SBox[State[3][1]],self.SBox[State[3][2]],self.SBox[State[3][3]]]])

        return result

    def InvSubBytes(self, State):

        result = np.array([[self.InvSBox[State[0][0]],self.InvSBox[State[0][1]],self.InvSBox[State[0][2]],self.InvSBox[State[0][3]]],
                           [self.InvSBox[State[1][0]],self.InvSBox[State[1][1]],self.InvSBox[State[1][2]],self.InvSBox[State[1][3]]],
                           [self.InvSBox[State[2][0]],self.InvSBox[State[2][1]],self.InvSBox[State[2][2]],self.InvSBox[State[2][3]]],
                           [self.InvSBox[State[3][0]],self.InvSBox[State[3][1]],self.InvSBox[State[3][2]],self.InvSBox[State[3][3]]]])

        return result

    def ShiftRows(self, State):
        
        return np.array([ State[0],
                [State[1][1],State[1][2],State[1][3],State[1][0]],
                [State[2][2],State[2][3],State[2][0],State[2][1]],
                [State[3][3],State[3][0],State[3][1],State[3][2]]
               ])

    def InvShiftRows(self, State):
        
        return np.array([ State[0],
                [State[1][3],State[1][0],State[1][1],State[1][2]],
                [State[2][2],State[2][3],State[2][0],State[2][1]],
                [State[3][1],State[3][2],State[3][3],State[3][0]]
               ])

    def MixColumns(self, State):

        result = np.zeros((4,4), dtype=int)
    
        for col in range(4):
            result[0][col] = self.Gf.producto(0x02, State[0][col]) ^ self.Gf.producto(0x03, State[1][col]) ^ State[2][col] ^ State[3][col]
            result[1][col] = State[0][col] ^ self.Gf.producto(0x02, State[1][col]) ^ self.Gf.producto(0x03, State[2][col]) ^ State[3][col]
            result[2][col] = State[0][col] ^ State[1][col] ^ self.Gf.producto(0x02, State[2][col]) ^ self.Gf.producto(0x03, State[3][col])
            result[3][col] = self.Gf.producto(0x03, State[0][col]) ^ State[1][col] ^ State[2][col] ^ self.Gf.producto(0x02, State[3][col])
        
        return result

    def InvMixColumns(self, State):

        result = np.zeros((4,4), dtype=int)
    
        for col in range(4):
            result[0][col] = self.Gf.producto(0x0e, State[0][col]) ^ self.Gf.producto(0x0b, State[1][col]) ^ self.Gf.producto(0x0d, State[2][col]) ^ self.Gf.producto(0x09, State[3][col])
            result[1][col] = self.Gf.producto(0x09, State[0][col]) ^ self.Gf.producto(0x0e, State[1][col]) ^ self.Gf.producto(0x0b, State[2][col]) ^ self.Gf.producto(0x0d, State[3][col])
            result[2][col] = self.Gf.producto(0x0d, State[0][col]) ^ self.Gf.producto(0x09, State[1][col]) ^ self.Gf.producto(0x0e, State[2][col]) ^ self.Gf.producto(0x0b, State[3][col])
            result[3][col] = self.Gf.producto(0x0b, State[0][col]) ^ self.Gf.producto(0x0d, State[1][col]) ^ self.Gf.producto(0x09, State[2][col]) ^ self.Gf.producto(0x0e, State[3][col])
        
        return result

    def AddRoundKey(self, State, roundKey):

        result = np.array([[State[0][0] ^ roundKey[0][0],State[0][1] ^ roundKey[1][0],State[0][2] ^ roundKey[2][0],State[0][3] ^ roundKey[3][0]],
                           [State[1][0] ^ roundKey[0][1],State[1][1] ^ roundKey[1][1],State[1][2] ^ roundKey[2][1],State[1][3] ^ roundKey[3][1]],
                           [State[2][0] ^ roundKey[0][2],State[2][1] ^ roundKey[1][2],State[2][2] ^ roundKey[2][2],State[2][3] ^ roundKey[3][2]],
                           [State[3][0] ^ roundKey[0][3],State[3][1] ^ roundKey[1][3],State[3][2] ^ roundKey[2][3],State[3][3] ^ roundKey[3][3]]])

        return result
    
    def SubWord(self, pos):
        
        return self.SBox[pos]

    def KeyExpansion(self, key):

        Nk = len(key) // 4
        Nb = 4
        Nr = 10 if Nk == 4 else 12 if Nk == 6 else 14

        expanded_key = [0] * (Nb * (Nr + 1))

        for i in range(Nk):
            word = key[4 * i : 4 * (i + 1)]
            expanded_key[i] = word
        
        for i in range(Nk, Nb * (Nr + 1)):
            temp = list(expanded_key[i - 1])

            if i % Nk == 0:
                temp = [temp[1], temp[2], temp[3], temp[0]]
                for j in range(4):
                    temp[j] = self.SubWord(temp[j])
                temp[0] ^= self.Rcon[i // Nk - 1]

            elif Nk > 6 and i % Nk == 4:
                for j in range(4):
                    temp[j] = self.SubWord(temp[j])

            for j in range(4):
                temp[j] ^= expanded_key[i - Nk][j]

            expanded_key[i] = temp

        return Nr, expanded_key


    def Cipher(self, State, Nr, Expanded_KEY):

        State = self.AddRoundKey(State, Expanded_KEY[0:4])
    
        for round in range(1, Nr):
            State = self.SubBytes(State)
            State = self.ShiftRows(State)
            State = self.MixColumns(State)
            State = self.AddRoundKey(State, Expanded_KEY[round*4:(round*4)+4])

        State = self.SubBytes(State)
        State = self.ShiftRows(State)
        State = self.AddRoundKey(State, Expanded_KEY[Nr*4:(Nr*4)+4])
        
        return State


    def InvCipher(self, State, Nr, Expanded_KEY):

        State = self.AddRoundKey(State, Expanded_KEY[Nr*4:(Nr*4)+4])
    
        for round in range(Nr-1, 0,-1):
            State = self.InvShiftRows(State)
            State = self.InvSubBytes(State)
            State = self.AddRoundKey(State, Expanded_KEY[round*4:(round*4)+4])
            State = self.InvMixColumns(State)
          
        State = self.InvShiftRows(State)
        State = self.InvSubBytes(State)
        State = self.AddRoundKey(State, Expanded_KEY[0:4])
        
        return State

    def encrypt_file(self, fichero):

        mult = True
        iv = os.urandom(16)
        input_file = fichero
        output_file = input_file + '.enc'

        with open(input_file, 'rb') as f_in, open(output_file, 'wb') as f_out:
            f_out.write(iv)
            previous_block = np.array(list(iv)).reshape(4, 4).transpose()

            while True:
                block = f_in.read(16)

                if not block:
                    break

                if len(block) < 16:
                    mult = False
                    padding_length = 16 - len(block)
                    block += bytes([padding_length] * padding_length)

                block_array = np.array(list(block)).reshape(4, 4).transpose()
                block_array = np.bitwise_xor(block_array,previous_block)
                
                encrypted_block = self.Cipher(block_array, self.Nr, self.Expanded_KEY)
                previous_block = encrypted_block
                encrypted_block = encrypted_block.transpose().flatten()
                byte_arr = list(encrypted_block)
                some_bytes = bytes(bytearray(byte_arr))

                f_out.write(some_bytes)
            
            if mult:
                padding_length = 16
                block = bytes([padding_length] * padding_length)
                block_array = np.array(list(block)).reshape(4, 4).transpose()
                block_array = np.bitwise_xor(block_array,previous_block)             
                encrypted_block = self.Cipher(block_array, self.Nr, self.Expanded_KEY)
                encrypted_block = encrypted_block.transpose().flatten()
                byte_arr = list(encrypted_block)
                some_bytes = bytes(bytearray(byte_arr))
                f_out.write(some_bytes)


    def decrypt_file(self, fichero):

        encrypted_file = fichero
        output_file = encrypted_file + '.dec'

        with open(encrypted_file, 'rb') as f_enc, open(output_file, 'wb') as f_out:
            iv = f_enc.read(16)
            previous_block = np.array(list(iv)).reshape(4, 4).transpose()
            
            while True:
                encrypted_block = f_enc.read(16)

                if not encrypted_block:
                    break
                
                block_array = np.array(list(encrypted_block)).reshape(4, 4).transpose()
                decrypted_block = self.InvCipher(block_array, self.Nr, self.Expanded_KEY)

                decrypted_block = np.bitwise_xor(decrypted_block,previous_block)
                decrypted_block = decrypted_block.transpose().flatten()
                byte_arr = list(decrypted_block)
                some_bytes = bytes(bytearray(byte_arr))
                f_out.write(some_bytes)

                previous_block = block_array

        with open(output_file, 'r+b') as f_out:
            f_out.seek(-1, 2)
            last_byte = f_out.read(1)

            if not last_byte:
                return

            bytes_to_remove = ord(last_byte)
            f_out.seek(-bytes_to_remove, 1)

            new_file_size = f_out.tell()
            f_out.truncate(new_file_size)


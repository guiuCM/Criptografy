import hashlib
import math
import sympy
import random
from random import randint



class rsa_key:
    def __init__(self,bits_modulo=2048,e=2**16+1):
        # genera una clave RSA (de 2048 bits y exponente p´ublico 2**16+1 por defecto)

        self.publicExponent = e
        self.primeP = sympy.randprime(pow(2, (bits_modulo - 1)), pow(2, bits_modulo))
        self.primeQ = sympy.randprime(pow(2, (bits_modulo - 1)), pow(2, bits_modulo))

        while not(self.are_coprime_with_third()) and (self.primeP == self.primeQ):
            self.primeP = sympy.randprime(pow(2, (bits_modulo - 1)), pow(2, bits_modulo))
            self.primeQ = sympy.randprime(pow(2, (bits_modulo - 1)), pow(2, bits_modulo))

        self.privateExponent = sympy.mod_inverse(self.publicExponent, (self.primeP - 1) * (self.primeQ - 1))
        self.modulus = self.primeP * self.primeQ
        self.privateExponentModulusPhiP = self.privateExponent % (self.primeP - 1)
        self.privateExponentModulusPhiQ = self.privateExponent % (self.primeQ - 1)
        self.inverseQModulusP = sympy.mod_inverse(self.primeQ, self.primeP)
    
    def are_coprime_with_third(self):
        return math.gcd(self.publicExponent, self.primeP) == 1 and math.gcd(self.publicExponent, self.primeQ) == 1


    def sign(self,message):
    # Salida: un entero que es la firma de "message" hecha con la clave RSA usando el TCR

        c1 = pow(message, self.privateExponentModulusPhiP, self.primeP)
        c2 = pow(message, self.privateExponentModulusPhiQ, self.primeQ)

        return (c1 * self.inverseQModulusP * self.primeQ + 
                c2 * (1 - self.inverseQModulusP * self.primeQ)) % self.modulus

    def sign_slow(self,message):
    # Salida: un entero que es la firma de "message" hecha con la clave RSA sin usar el TCR

        return pow(message, self.privateExponent, self.modulus)
    


class rsa_public_key:
    def __init__(self, rsa_key):
    # genera la clave p´ublica RSA asociada a la clave RSA "rsa_key"

        self.publicExponent = rsa_key.publicExponent
        self.modulus = rsa_key.modulus

    def verify(self, message, signature):
    # Salida: el booleano True si "signature" se corresponde con la
    # firma de "message" hecha con la clave RSA asociada a la clave
    # p´ublica RSA;
    # el booleano False en cualquier otro caso.

        return pow(signature, self.publicExponent, self.modulus) == message
    


class transaction:
    def __init__(self, message, RSAkey):
    # genera una transaccion firmando "message" con la clave "RSAkey"

        self.public_key = rsa_public_key(RSAkey)
        self.message = message
        self.signature = RSAkey.sign(message)

    def verify(self):
    # Salida: el booleano True si "signature" se corresponde con la
    # firma de "message" hecha con la clave RSA asociada a la clave
    # p´ublica RSA;
    # el booleano False en cualquier otro caso.

        return self.public_key.verify(self.message, self.signature)
    


class block:
    def __init__(self):
    # crea un bloque (no necesariamente v´alido)

        self.block_hash = None
        self.previous_block_hash = None
        self.transaction = None
        self.seed = None

    def genesis(self,transaction):
    # genera el primer bloque de una cadena con la transacci´on "transaction"
    # que se caracteriza por:
    # - previous_block_hash=0
    # - ser v´alido

        self.previous_block_hash = 0
        self.transaction = transaction
        self.seed_and_hash()
        return self
    
    def is_genesis(self):
        return self.previous_block_hash == 0 and self.verify_block()

    def seed_and_hash(self, invalid = False):
        prev_block_string = str(self.previous_block_hash)
        prev_block_string = prev_block_string + str(self.transaction.public_key.publicExponent)
        prev_block_string = prev_block_string + str(self.transaction.public_key.modulus)
        prev_block_string = prev_block_string + str(self.transaction.message)
        prev_block_string = prev_block_string + str(self.transaction.signature)

        if invalid:
            while True:
                self.seed = randint(0, 2 ** 256)
                aux = prev_block_string + str(self.seed)
                h = int(hashlib.sha256(aux.encode()).hexdigest(), 16)
                if h >= 2 ** (256 - 16):
                    break

        else:
            while True:
                self.seed = randint(0, 2 ** 256)
                aux = prev_block_string + str(self.seed)
                h = int(hashlib.sha256(aux.encode()).hexdigest(), 16)
                if h < 2 ** (256 - 16):
                    break

        self.block_hash = h

    def next_block(self, transaction):
    # genera un bloque v´alido seguiente al actual con la transacci´on "transaction"

        n_block = block()
        n_block.transaction = transaction
        n_block.previous_block_hash = self.block_hash
        n_block.seed_and_hash()
        return n_block

    def next_invalid_block(self, transaction):
        n_block = block()
        n_block.transaction = transaction
        n_block.previous_block_hash = self.block_hash
        n_block.seed_and_hash(invalid=True)
        return n_block

    def verify_block(self):
    # Verifica si un bloque es v´alido:
    # -Comprueba que el hash del bloque anterior cumple las condiciones exigidas
    # -Comprueba que la transacci´on del bloque es v´alida
    # -Comprueba que el hash del bloque cumple las condiciones exigidas
    # Salida: el booleano True si todas las comprobaciones son correctas;
    # el booleano False en cualquier otro caso.

        prev_hash_ver = self.previous_block_hash < 2 ** (256 - 16)
        transaction_ver = self.transaction.verify()
        hash_ver = self.block_hash < 2 ** (256 - 16)
        hash_ver_2 = self.verify_hash()
        return prev_hash_ver and transaction_ver and hash_ver and hash_ver_2
    
    def verify_hash(self):
        prev_block_string = str(self.previous_block_hash)
        prev_block_string = prev_block_string + str(self.transaction.public_key.publicExponent)
        prev_block_string = prev_block_string + str(self.transaction.public_key.modulus)
        prev_block_string = prev_block_string + str(self.transaction.message)
        prev_block_string = prev_block_string + str(self.transaction.signature)
        prev_block_string = prev_block_string + str(self.seed)
        h = int(hashlib.sha256(prev_block_string.encode()).hexdigest(), 16)
        return h == self.block_hash



class block_chain:
    def __init__(self,transaction):
    # genera una cadena de bloques que es una lista de bloques,
    # el primer bloque es un bloque "genesis" generado amb la transacci´o "transaction"
    
        self.list_of_blocks = [block().genesis(transaction)]

    def add_block(self,transaction):
    # a~nade a la cadena un nuevo bloque v´alido generado con la transacci´on "transaction"

        n_block = self.list_of_blocks[-1].next_block(transaction)
        self.list_of_blocks.append(n_block)
        return self
    
    def add_invalid_block(self, transaction):
        n_block = self.list_of_blocks[-1].next_invalid_block(transaction)
        self.list_of_blocks.append(n_block)
        return self


    def verify(self):
    # verifica si la cadena de bloques es v´alida:
    # - Comprueba que todos los bloques son v´alidos
    # - Comprueba que el primer bloque es un bloque "genesis"
    # - Comprueba que para cada bloque de la cadena el siguiente es correcto
    # Salida: el booleano True si todas las comprobaciones son correctas;
    # en cualquier otro caso, el booleano False y un entero
    # correspondiente al ´ultimo bloque v´alido

        if not self.list_of_blocks[0].is_genesis():
            return False, -1

        for idx, current_block in enumerate(self.list_of_blocks[1:], 1):
            if current_block.previous_block_hash != self.list_of_blocks[idx - 1].block_hash:
                return False, idx - 1

            if not current_block.verify_block():
                return False, idx - 1
        return True, len(self.list_of_blocks) - 1
     
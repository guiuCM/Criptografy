import hashlib
import AES

mensaje = "tu_mensaje"
hash_sha512 = hashlib.sha512(mensaje.encode()).hexdigest()

print(hash_sha512)
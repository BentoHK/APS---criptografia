import pika
import threading
import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

# Função para criptografar uma mensagem
def encrypt(message, key):
    cipher = AES.new(key, AES.MODE_CBC)  
    ct_bytes = cipher.encrypt(pad(message.encode(), AES.block_size))  
    iv = base64.b64encode(cipher.iv).decode('utf-8')  
    ct = base64.b64encode(ct_bytes).decode('utf-8')  
    return iv, ct  

# Função para descriptografar uma mensagem
def decrypt(iv, ct, key):
    iv = base64.b64decode(iv) 
    ct = base64.b64decode(ct) 
    cipher = AES.new(key, AES.MODE_CBC, iv) 
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt.decode('utf-8')

print("\nDigite (sair) para encerrar o código")

# Função para receber mensagens da fila
def receber_mensagens(canal, key):
    while True:
        method_frame, header_frame, body = canal.basic_get(queue='Cliente1', auto_ack=True)
        if method_frame:
            print(f"Mensagem criptografada recebida: {body.decode('utf-8')}")
            iv, ct = body.decode('utf-8').split(':')
            try:
                mensagem_decryptada = decrypt(iv, ct, key)
                print(f"\nUsuário 2: {mensagem_decryptada}")
            except Exception as e:
                print(f"Erro ao descriptografar a mensagem: {e}")
        time.sleep(0.5) 

# Conexão com RabbitMQ
conexao = pika.BlockingConnection(pika.ConnectionParameters(
    host='15.228.248.2',
    port=5672,
    virtual_host='Host-MHPG',
    credentials=pika.PlainCredentials('Admin', '1234')
))
canal = conexao.channel()  # Cria um canal de comunicação


key_input = input("Digite uma chave de 16 bytes: ")
key_input = key_input[:16].ljust(16)
key = key_input.encode('utf-8') 

# Inicia a thread para receber mensagens
threading.Thread(target=receber_mensagens, args=(canal, key), daemon=True).start()

# Loop para enviar mensagens
while True:
    mensagem = input("")
    if mensagem.lower() == 'sair':
        break 

    iv, ct = encrypt(mensagem, key)
    body = f"{iv}:{ct}" 

    canal.basic_publish(
        exchange='Unip-aps-cc2p2',
        routing_key='Cliente2',
        body=body,
        properties=pika.BasicProperties(delivery_mode=2) 
    )
    print(f"Mensagem criptografada enviada: {iv + ct}")

conexao.close() 

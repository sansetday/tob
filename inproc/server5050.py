import socket


sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind (('localhost',5050))
client = [] # Массив где храним адреса клиентов
print ('Start Server')
while 1 :
    data, addres = sock.recvfrom(1024)
    print (addres[0], addres[1])
    if addres not in client:
        client.append(addres)# Если такова клиента нету , то добавить
    for clients in client :
        if clients == addres:
            continue # Не отправлять данные клиенту который их прислал
        sock.sendto(data,clients)
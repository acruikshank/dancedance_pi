import serial
import sys
import time
import atexit
import socket
from multiprocessing import Process, Queue

HOST = '192.168.0.10'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

def send_to_teensy(q, id, i):
    while True:
        try:
          with serial.Serial('/dev/serial/by-id/usb-Teensyduino_USB_Serial_' + id + '-if00', 115200, timeout=1) as conn:
              conn.write(bytearray([0, 8*i]))
              while True:
                  values = q.get()
                  conn.write(values)
        except:
            pass
        time.sleep(1)


def socket_listen(queues):
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.bind((HOST, PORT))
  s.listen(1)
  while True:
    (conn, addr) = s.accept()
    print('Connected by', addr)
    while True:
      data = conn.recv(1024)
      if not data:
        break
      for queue in queues:
        queue.put(data)


ids = ['4931040','4933780','4933320','4933800','4919670','4931340','4933500']
# connections = [serial.Serial('/dev/serial/by-id/usb-Teensyduino_USB_Serial_'+id+'-if00', 115200, timeout=1) for id in ids]
queues = [Queue() for id in ids]
processes = [Process(target=send_to_teensy, args=(queues[i], ids[i], i)) for i, id in enumerate(ids)]

for process in processes:
    process.start()

server_process = Process(target=socket_listen, args=(queues,))
server_process.start()

def cleanup():
    for queue in queues:
        queue.close()
    for process in processes:
        process.terminate()

atexit.register(cleanup)

while True:
    time.sleep(.01)

import serial
import sys
import time
import atexit
import socket
import glob
from multiprocessing import Process, Queue

HOST = '192.168.0.10'
PORT = 65432

def get_from_bike(queue):
    while True:
        try:
            with serial.Serial('/dev/ttyUSB0', 115200, timeout=1) as conn:
                print("connected to bike")
                while True:
                    values = conn.read(size=2)
                    queue.put(values)
        except:
            pass
        time.sleep(1)
#
# def get_from_drum(queue):
#     while True:
#         try:
#             with serial.Serial('/dev/serial/by-id/usb-LeafLabs_Maple-if00', 115200, timeout=1) as conn:
#                 while True:
#                     values = conn.read(size=2)
#                     queue.put(values)
#         except:
#             pass
#         time.sleep(1)

def get_from_device(queue, path):
    while True:
        try:
            print('connecting...:', path)
            with serial.Serial(path, 115200, timeout=1) as conn:
                print('connected to', path)
                while True:
                    values = conn.read(size=2)
                    print "got",
                    for v in values:
                      print " ", ord(v),
                    print()
                    if len(values) == 2 and values[0] != 0:
                      queue.put(values)
        except:
            pass
        time.sleep(1)

def send_to_stage(queue, timing_queue):
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((HOST, PORT))
            while True:
                s.sendall(queue.get())
                timing_queue.put(1)
        except:
            pass
        time.sleep(1)

def screen_saver(queue, timing_queue):
  saver = 0
  while True:
    try:
      timing_queue.get(True, 60)
    except:
      queue.put(bytearray([5,saver%2]))
      saver+=1


read_queue = Queue()
timing_queue = Queue()

paths = ['/dev/ttyUSB0', '/dev/ttyACM0', '/dev/ttyACM1']
print(paths)
processes = [Process(target=get_from_device, args=(read_queue, path)) for path in paths]

for process in processes:
    process.start()
#
# bike_read_process = Process(target=get_from_bike, args=(read_queue,))
# bike_read_process.start()
#
# drum_read_process = Process(target=get_from_drum, args=(read_queue,))
# drum_read_process.start()

send_process = Process(target=send_to_stage, args=(read_queue,timing_queue))
send_process.start()

screen_saver_process = Process(target=screen_saver, args=(read_queue,timing_queue))
screen_saver_process.start()

while True:
    time.sleep(.01)

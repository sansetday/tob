indir = '../ipb1'
import os

import queue
q = queue.Queue()
l = []
with open('ip_int.txt') as f:
    l = f.read().splitlines()
    for i in l:
        q.put(i)
with open("base.buffering.100", "w") as file:
    for i in l:
        file.write("1::1::146::2019-03-06 19:01:30.679239::2023753::"+ q.get() + "::"+ q.get() +"::6::61335::33089::2::1::0::0::" + '\n' + "2::1::146::2023753::1::2019-03-06 19:01:30.679239::97::AAQj1jBYkBessLC7CABFcABTSbIAAHkGhUVbkL4sVCoEV++XgUH1AvhxFWRATlAYAQH/GgAAAwAAKybgAAAAAABDb29raWU6IG1zdHNoYXNoPWhlbGxvDQoBAAgAAwAAAA==::" + '\n')
file.close()
print('finish')

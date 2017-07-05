import re

'''from Tkinter import *
import Tkinter, Tkconstants, tkFileDialog

root = Tk()
root.filename = tkFileDialog.askopenfile("r", filetypes=(("trace files", "*.trc"), ("all files", "*.*")))
trace_file = root.filename.readlines()
root.filename.close()
'''


def Get_Id_SA(id):
    sa = id[6:8]


def Get_TP_CM(id, data, start_index=0):
    try:
        packet_info = []
        tp_cm_idx = 0
        tp_not_found = True
        while True:
            idx = id[start_index]
            # check for TP pgn
            if '18EC' in idx:
                if data[start_index].startswith('10'):  # check if TP is CM
                    tp_cm_idx = start_index  # get the position were TP CM was found
                    packet_info.append(start_index)
                    tp_not_found = False
                    break

            start_index += 1
        if tp_not_found == True:
            return packet_info
        # get the SA of the TP CM found
        tp_cm_sa = id[tp_cm_idx][6:8]
        # get the sum of packets expected
        tp_nof_packets = int(data[tp_cm_idx][9:11], 16)
        # Get the PGN
        tp_pgn = data[tp_cm_idx][15:20]

        start_packet = 1
        tp_cm_idx += 1  # go to next id
        packet = ''
        while start_packet < tp_nof_packets:
            if int(data[tp_cm_idx][0:2], 16) == start_packet:
                packet += data[tp_cm_idx][3:] + ' '
                start_packet += 1
            tp_cm_idx += 1

        packet = packet.replace(" ", "")
        ascii = packet.decode("hex")
        packet_info.append(tp_cm_idx)
        packet_info.append(ascii)
    except:
        print "somethnig wrong"
        packet_info = []
    return packet_info




file_tmp = open('my_trace.trc', 'r')
trace_file = file_tmp.readlines()
file_tmp.close()

J1939pgn = []
J1939_data = []
packet_list = []

for line in trace_file:
    msg = re.search("(?:Rx\s*)(.{8})(?:.{5})(.+)", line)
    if msg is not None:
        J1939pgn.append(msg.group(1))
        J1939_data.append(msg.group(2))


   # packet_list = Get_TP_CM(J1939pgn, J1939_data)
   # while packet_list != 0:
   #     packet_list = Get_TP_CM(J1939pgn, J1939_data, packet_list[0])
packet_list = Get_TP_CM(J1939pgn, J1939_data)
trace_file[16 + packet_list[0]] = trace_file[16 + packet_list[0]].rstrip()
trace_file[16 + packet_list[0]] += ' ' + packet_list[2] + '\n'
while len(packet_list) > 1:
    packet_list = Get_TP_CM(J1939pgn, J1939_data,packet_list[1])
    try:
        trace_file[16 + packet_list[0]] = trace_file[16 + packet_list[0]].rstrip()
        trace_file[16 + packet_list[0]] += ' ' +'=========' + packet_list[2] + '=======' + '\n'
        trace_file[16 + packet_list[1]] = trace_file[16 + packet_list[1]].rstrip()
        trace_file[16 + packet_list[1]] += ' ' + '=========' + 'END' + '=======' + '\n'

    except:
        print "error"
'''
trace_file[16 + first_packet[0] ] = trace_file[16 + first_packet[0] ].rstrip()

trace_file[16 + first_packet[0] ] += ' ' + first_packet[2] + '\n'
'''
with open('my_trace_process.trc','w') as ouputfile:
    ouputfile.writelines(trace_file)

print 'done'

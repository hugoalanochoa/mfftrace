import re # import regular expression module

# regular expression shall contain at least 2 groups CAN id and data (8 bytes)
re_searchpattern = "(?:Rx\s*)(.{8})(?:.{5})(.+)"

from Tkinter import *
import Tkinter, Tkconstants, tkFileDialog, tkMessageBox
from logging import exception

# Open a dialog to select the source trace file
tkMessageBox.showinfo("Select File", "Select Trace file to process")
root = Tk()
root.filename = tkFileDialog.askopenfile("r", filetypes=(("trace files", "*.trc"), ("all files", "*.*")))
trace_file = root.filename.readlines()
root.filename.close()


# definition of a TP Package object, start: position on list where TP CM was fond
# end: last package
# data: ascii data of the TP package
class TP_Package:
    def __init__(self, start, end, data):
        self.start = start
        self.end = end
        self.data = data

    def init_packet(self):
        self.start = 0
        self.end = 0
        self.data = ''

# Gets the SA of the id string
# i.e. id = '18EC80F9' -> F9 is SA
#
def Get_Id_SA(id):
    return id[6:8]

# Gets the total expected packets from the Transport
# Protocol CM message
#

def Get_TPCM_TotalPacks(data):
    return int(data[9:11], 16)
#
#
# Gets the PGN transmitted over TP

def Get_TPCM_PGN(data):
    return data[15:20]

#
#
# Gets the current pack number sent by TP DT message

def Get_TPDT_Pack_Num(data):
    return int(data[0:2], 16)

#
#
# Gets the Data from TP DT

def Get_TPDT_Data(data):
    return data[3:]
# This function start looking for a TP CM message that contains '10' in the first byte
# this indicates a ready to send command (RTS),  then when a RTS command is found starts
# looking for the data packets starting with 1, when it is done it returns teh Packet_info
# Object who contains the  position of the first package (start), position of the last package (end)
# and the concatenated data from all packages

def Get_TP_CM(id, data, id_index=0):
    Packet_info = TP_Package(0, 0, '')
    try:
        packet_info = []
        tp_cm_idx = 0
        tp_not_found = True
        while True:
            idx = id[id_index]
            # check for TP pgn
            if '18EC' in idx:
                if data[id_index].startswith('10'):  # check if TP is CM
                    tp_cm_idx = id_index  # get the position were TP CM was found
                    Packet_info.start = id_index  # set the start line of the CM found
                    if id_index + Get_TPCM_TotalPacks(data[id_index]) > len(
                            id):  # check that we are not at the very end of a file
                        Packet_info.init_packet()
                        return Packet_info
                    tp_not_found = False
                    break

            id_index += 1 # Go to the next id on the list
        if tp_not_found is True:
            # if no TP CM message is found return an empty object
            Packet_info.init_packet()
            return Packet_info
        # get the SA of the TP CM found
        tp_cm_sa = Get_Id_SA(id[id_index])
        # get the sum of packets expected
        tp_nof_packets = Get_TPCM_TotalPacks(data[id_index])
        # Get the PGN
        tp_pgn = Get_TPCM_PGN(data[id_index])

        packet_counter = 1  # start counter at 1
        tp_cm_idx += 1  # go to next id

        # loop until all packets are found
        while packet_counter < tp_nof_packets:
            # start looking for packages 1,2,3,4 etc
            # every time that a packet is found copy his data to
            # Packet_info.data
            if Get_TPDT_Pack_Num(data[tp_cm_idx]) == packet_counter:
                Packet_info.data += Get_TPDT_Data(data[tp_cm_idx]) + ' '
                # increment packet counter after a packet is found
                packet_counter += 1
            # Go to next packet id on the list
            tp_cm_idx += 1
        # Delete all spaces from .data
        Packet_info.data = Packet_info.data.replace(" ", "")
        # Convert the result from hex to ascii
        ascii = Packet_info.data.decode("hex")
        # save the position of the last packet
        Packet_info.end = tp_cm_idx
        # save the position of first packet
        Packet_info.data = ascii

    except:
        # if something goes wring just return an empty object
        Packet_info.init_packet()
    return Packet_info
# ----------------------------------------------------- MAIN PROGRAM----------------------------------------------------
#
# ----------------------------------------------------------------------------------------------------------------------

# List of all the CAN ids found on the file
CanId_List = []
# List of all data contained on the CAN messages
CAN_data = []
# Contains the line were the CAN files start
msg_start_line = 0

# Start looking for CAN messages using regular expressions
for line in trace_file:
    msg = re.search(re_searchpattern, line)  # search groups with regular expresion
    # if a message is found store it on the list
    # store CAN id and data in different lists
    if msg is not None:
        CanId_List.append(msg.group(1))
        CAN_data.append(msg.group(2))
    else:
        # count the number of lines were no CAN messages
        # are found ( in order to know at what line the CAN messages start)
        msg_start_line += 1

# start looking for the first CAN message
packet_list = Get_TP_CM(CanId_List, CAN_data)
# after first message is found we can now loop trough the entire file
while True:
    packet_list = Get_TP_CM(CanId_List, CAN_data, packet_list.end)
    if packet_list.end == 0:
        break
    # Remove the first new line \n
    trace_file[msg_start_line + packet_list.start] = trace_file[msg_start_line + packet_list.start].rstrip()
    # Add ASCII data to trace file at the beginning of the TP CM message
    trace_file[msg_start_line + packet_list.start] += ' ' + '=========>' + packet_list.data + '<=========' + '\n'
    # Remove the first new line \n
    trace_file[msg_start_line + packet_list.end] = trace_file[msg_start_line + packet_list.end].rstrip()
    # Place a marker on the last packet found
    trace_file[msg_start_line + packet_list.end] += ' ' + ('-'*9) + "END" + ('-'*9) + '\n'

# show a message box when is done
tkMessageBox.showinfo("Finish", "File Processed")

# ask for route were to save the processed file
save_file = Tk()
try:
    save_file.filename = tkFileDialog.asksaveasfile("w", filetypes=(("trace files", "*.txt"), ("all files", "*.*")))
    save_file.filename.writelines(trace_file)
    save_file.filename.close()
except:
    tkMessageBox.showinfo("Error", "No path selected")
print 'done'

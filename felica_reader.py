import usb1
import sys
import struct
import time



# SONY RC-S380
VENDOR_ID = 0x054C
PRODUCT_ID = 0x06C3
INTERFACE = 0
ENDPOINT_IN = 1
ENDPOINT_OUT = 2
ACK = bytes.fromhex('0000FF00FF00')

BUF_SIZE = 300



def read(handle, timeout=0):
    '''read a response from RCS380'''
    frame = handle.bulkRead(ENDPOINT_IN, BUF_SIZE, timeout)
    return frame


def write(handle, frame, timeout=0):
    '''write a frame to RCS380'''
    #print("frame=" + "".join(r'\x%02X' % x for x in frame))
    handle.bulkWrite(ENDPOINT_OUT, frame, timeout)


def send_ack(handle):
    '''send an ack to RCS380'''
    write(handle, ACK)


def make_frame(data):
    '''make a frame suitable for RCS380'''
    frame = bytearray(b"\x00\x00\xFF\xFF\xFF")
    frame += bytearray(struct.pack("<H", len(data)))  # Little endian, unsigned short
    frame += bytearray(struct.pack("B", (0x100 - sum(frame[5:7])) % 0x100))  # checksum, unsigned char
    frame += bytearray(data)
    frame += bytearray(struct.pack("B", (0x100 - sum(frame[8:])) % 0x100))  # checksum, unsigned char
    frame += bytearray(b"\x00")
    return bytes(frame)


def send_command(handle, cmd_code, cmd_data, timeout=0):
    '''send a command to RCS380'''
    cmd = b"\xD6" + cmd_code + cmd_data
    #print("cmd=", bytes(cmd))
    write(handle, make_frame(cmd), timeout)

    ret = read(handle, timeout)
    #print("ret=" + "".join(r'\x%02X' % x for x in ret))

    res = read(handle, timeout)
    #print("res=" + "".join(r'\x%02X' % x for x in res))

    return res


 
with usb1.USBContext() as context:
    handle = context.openByVendorIDAndProductID(
        VENDOR_ID,
        PRODUCT_ID,
        skip_on_error=True,
    )
    if handle is None:
        print("USB device not found")
        sys.exit()
    with handle.claimInterface(INTERFACE):
        # Do stuff with endpoints on claimed interface.
        # claim (= get exclusive access to)

        #print("send_ack")
        send_ack(handle)

        #print("SetCommandType")
        send_command(handle, b"\x2a", b"\x01")  # SetCommandType "1"

        #print("SwitchRF")
        send_command(handle, b"\x06", b"\x00")  # SwitchRF "off"

        #print("InSetRF")
        # settings
        # 212kbps type F: b"\x01\x01\x0F\x01", 
        # 424kbps type F: b"\x01\x02\x0F\x02"
        send_command(handle, b"\x00", b"\x01\x01\x0F\x01")  # InSetRF

        #print("InSetProtocol 1st")
        isp = bytes.fromhex("0018 0101 0201 0300 0400 0500 0600 " +
            "0708 0800 0900 0A00 0B00 0C00 0E04 0F00 1000 1100 1200 1306")
        send_command(handle, b"\x02", isp) # InSetProtocol

        #print("InSetProtocol 2nd")
        send_command(handle, b"\x02", b"\x00\x18")  # InSetProtocol

        print("Touch the reader.")
        
        #print("InCommRF")
        timeout = 110  # ms
        sensf_req = bytes.fromhex("00FFFF0100")
        while True:
            res = send_command(handle, b"\x04", 
                        struct.pack("<H", timeout) + 
                        struct.pack("B", len(sensf_req) + 1) + sensf_req, 
                        timeout=timeout)  # InCommRF
            if res != None and res[9] == 0x05 and res[10] == 0x00:
                break
            time.sleep(1)  # sleep one second
        
        #print("SwitchRF")
        send_command(handle, b"\x06", b"\x00")  # SwitchRF "off"

        #print("".join(r'\x%02X' % x for x in res))
        idm = "".join(r'%02X' % x for x in res[17:25])
        pmm = "".join(r'%02X' % x for x in res[25:33])
        if len(res) >= 37:
            sys = "".join(r'%02X' % x for x in res[33:35])
        else:
            sys = ""

print("idm=" + idm)
print("pmm=" + pmm)
print("sys=" + sys)



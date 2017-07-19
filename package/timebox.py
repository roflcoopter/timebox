"""Provides class TimeBox that encapsulates the TimeBox communication."""

import select
from bluetooth import BluetoothSocket, RFCOMM
from messages import TimeBoxMessages

class TimeBox:
    """Class TimeBox encapsulates the TimeBox communication."""
    
    DEFAULTHOST = "11:75:58:48:2F:DA"

    COMMANDS = {
        "switch radio": 0x05,
        "set volume": 0x08,
        "get volume": 0x09,
        "set mute": 0x0a,
        "get mute": 0x0b,
        "set date time": 0x18,
        "set image": 0x44,
        "set view": 0x45,
        "set animation frame": 0x49,
        "get temperature": 0x59,
        "get radio frequency": 0x60,
        "set radio frequency": 0x61
    }

    socket = None
    messages = None
    message_buf = []

    def __init__(self):
        self.messages = TimeBoxMessages()

    def connect(self, host=None, port=4):
        """Open a connection to the TimeBox."""
        # Create the client socket
        if host is None:
            host = self.DEFAULTHOST
        #print("connecting to %s at %s" % (self.host, self.port))
        self.socket = BluetoothSocket(RFCOMM)
        self.socket.connect((host, port))
        self.socket.setblocking(0)


    def close(self):
        """Closes the connection to the TimeBox."""
        self.socket.close()

    def receive(self, num_bytes=1024):
        """Receive n bytes of data from the TimeBox and put it in the input buffer."""
        ready = select.select([self.socket], [], [], 0.1)
        if ready[0]:
            self.message_buf += self.socket.recv(num_bytes)

    def send_raw(self, data):
        """Send raw data to the TimeBox."""
        return self.socket.send(data)

    def send_payload(self, payload):
        """Send raw payload to the TimeBox. (Will be escaped, checksumed and
        messaged between 0x01 and 0x02."""
        msg = self.messages.make_message(payload)
        return self.socket.send(bytes(msg))

    def send_command(self, command, args=None):
        """Send command with optional arguments"""
        if args is None:
            args = []
        if isinstance(command, str):
            command = self.COMMANDS[command]
        length = len(args)+3
        length_lsb = length & 0xff
        length_msb = length >> 8
        payload = [length_lsb, length_msb, command] + args
        self.send_payload(payload)

    def decode(self, msg):
        """remove leading 1, trailing 2 and checksum and un-escape"""
        return self.messages.decode(msg)

    def has_message(self):
        """Check if there is a complete message *or leading garbage data* in the input buffer."""
        if len(self.message_buf) == 0:
            return False
        if self.message_buf[0] != 0x01:
            return True
        endmarks = [x for x in self.message_buf if x == 0x02]
        return  len(endmarks) > 0

    def buffer_starts_with_garbage(self):
        """Check if the input buffer starts with data other than a message."""
        if len(self.message_buf) == 0:
            return False
        return self.message_buf[0] != 0x01

    def remove_garbage(self):
        """Remove data from the input buffer that is nof the start of a message."""
        if not 0x01 in self.message_buf:
            pos = len(self.message_buf)
        else:
            pos = self.message_buf.index(0x01)
        res = self.message_buf[0:pos]
        self.message_buf = self.message_buf[pos:len(self.message_buf)]
        return res

    def remove_message(self):
        """Remove a message from the input buffer and return it. Assumes it has been checked that
        there is a complete message without leading garbage data"""
        if not 0x02 in self.message_buf:
            raise Exception('There is no message')
        pos = self.message_buf.index(0x02)+1
        res = self.message_buf[0:pos]
        self.message_buf = self.message_buf[pos:len(self.message_buf)]
        return res

    def set_static_image(self, image):
        """Set the image on the TimeBox"""
        msg = self.messages.static_image_message(image)
        self.socket.send(bytes(msg))

    def set_dynamic_images(self, images, frame_delay):
        """Set the image on the TimeBox"""
        fnum = 0
        for img in images:
            msg = self.messages.dynamic_image_message(img, fnum, frame_delay)
            fnum = fnum + 1
            self.socket.send(bytes(msg))

    def show_temperature(self, color=None):
        """Show temperature on the TimeBox in Celsius"""
        args = [0x01, 0x00]
        if not color is None:
            args += color
        self.send_command("set view", args)

    def show_clock(self, color=None):
        """Show clock on the TimeBox in the color"""
        args = [0x00, 0x01]
        if not color is None:
            args += color
        self.send_command("set view", args)

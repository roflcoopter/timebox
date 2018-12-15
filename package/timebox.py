"""Provides class TimeBox that encapsulates the TimeBox communication."""

import select
from bluetooth import BluetoothSocket, RFCOMM
from messages import TimeBoxMessages
from utils.fonts import Fonts

FONTFILE = "./timebox-fonts/arcadeclassic.gif"

FONT = Fonts(FONTFILE, 9, 9, 10, 0.6)
SPACING = 2

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
        """Receive n bytes of data from the TimeBox and put it in the input buffer.
        Returns the number of bytes received."""
        ready = select.select([self.socket], [], [], 0.1)
        if ready[0]:
            data = self.socket.recv(num_bytes)
            self.message_buf += data
            return len(data)
        else:
            return 0

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
        #endmarks = [x for x in self.message_buf if x == 0x02]
        #return  len(endmarks) > 0
        return 0x02 in self.message_buf

    def buffer_starts_with_garbage(self):
        """Check if the input buffer starts with data other than a message."""
        if len(self.message_buf) == 0:
            return False
        return self.message_buf[0] != 0x01

    def remove_garbage(self):
        """Remove data from the input buffer that is not the start of a message."""
        pos = self.message_buf.index(0x01) if 0x01 in self.message_buf else len(self.message_buf)
        res = self.message_buf[0:pos]
        self.message_buf = self.message_buf[pos:]
        return res

    def remove_message(self):
        """Remove a message from the input buffer and return it. Assumes it has been checked that
        there is a complete message without leading garbage data"""
        if not 0x02 in self.message_buf:
            raise Exception('There is no message')
        pos = self.message_buf.index(0x02) + 1
        res = self.message_buf[0:pos]
        self.message_buf = self.message_buf[pos:]
        return res

    def drop_message_buffer(self):
        """Drop all dat currently in the message buffer,"""
        self.message_buf = []

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

    def clear_input_buffer(self):
        """Read all input from TimeBox and remove from buffer. """
        while self.receive() > 0:
            self.drop_message_buffer()

    def clear_input_buffer_quick(self):
        """Quickly read most input from TimeBox and remove from buffer. """
        while self.receive(512) == 512:
            self.drop_message_buffer()

    # offset determines the location of the first column of the display
    # relative to the entire text image
    def show_scrolling_text(self, text):
        for offset in range(-11, len(text)*(FONT.font_width + SPACING)+11):
            # create a new image for this frame
            # range over all columns on the display
            for xix in range(11):
                # compute the corresponding global x value
                gxix = offset + xix
                # compute the relative x value to the current character
                rxix = gxix % (FONT.font_width + SPACING)
                # check if rxix is inside a character or not
                if rxix < FONT.font_width:
                    # determine which character it is in
                    charnum = gxix // (FONT.font_width + SPACING)
                    # if it is inside the range of the text to display
                    if charnum in range(len(text)):
                        # get the character itself
                        char = text[charnum]
                        # iterate over the rows on the display
                        for yix in range(FONT.font_height):
                            # get the pixel color
                            pix = FONT.get_pixel(char, rxix, yix)
                            # set the Timebox image pixel
                            IMAGE.put_pixel(xix, yix+1, pix[0], pix[1], pix[2])
            # send the new image to the Timebox
            self.set_static_image(IMAGE)
            # sleep for the animation
            sleep(0.1)

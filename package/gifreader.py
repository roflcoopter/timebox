"""Quick and dirty GIF reader, as pillow does not work on Windows.
Handling the reading of GIF images and transforming them to TimeBox images."""

CLEARCODEVAL = -1
EOICODEVAL = -2

class CodeTable:
    """ Implements the code table for LZW decompression."""

    code_table: 0

    def __init__(self, lzw_min_code_sz, col_table_sz):
        """Initialize the table, depending on the specified lzw min code size and color table size."""
        self.code_table = dict()
        clear_code = 1<<lzw_min_code_sz
        eoi_code = clear_code + 1
        self.code_table[clear_code] = [CLEARCODEVAL]
        self.code_table[eoi_code] = [EOICODEVAL]
        for c in range(col_table_sz):
            self.code_table[c] = [c]
        
    def hasKeyWithValue(self, key, value):
        """Returns True if key exists and has the value. Otherwise it returns False."""
        if not (key in self.code_table):
            return False
        if self.code_table[key] != value:
            return False
        return True

    def hasKey(self, key):
        """Returns True if key exists. Otherwise it returns False."""
        return key in self.code_table


    def get(self, key):
        """Get the value for a key"""
        return self.code_table[key]

    def at_put(self, key, value):
        """Store a new value in the table for key"""
        self.code_table[key] = value

    def at_new_key_put(self, value):
        """Store a new value in the table for a new key"""
        key = self.new_key()
        self.code_table[key] = value

    def new_key(self):
        """Return the smallest unused key value"""
        return max(self.code_table.keys()) + 1


class CodeReader:
    """Read bit information from data block."""

    data = 0
    data_byte_idx = 0
    data_bit_idx = 0

    def __init__(self, dat):
        """Initialize as reader on dat"""
        self.data = dat
            
    def read(self, bits_per_code_word):
        """Read a new code word from the stream. Returns code, new data byte index, and new data bit index  """
        remaining_bits = bits_per_code_word
        acquired_bits = 0
        res = 0
        # while we need the remainder of the current byte
        while remaining_bits >= 8 -self.data_bit_idx:
            val = self.data[self.data_byte_idx] >> self.data_bit_idx
            res = res + (val << acquired_bits)
            remaining_bits = remaining_bits - (8 - self.data_bit_idx)
            acquired_bits = acquired_bits + (8 - self.data_bit_idx)
            self.data_byte_idx = self.data_byte_idx + 1
            self.data_bit_idx = 0
        # less than 8 (possibly 0) bits remain from last byte
        if remaining_bits>0:
            val = self.data[self.data_byte_idx] & ((1<<remaining_bits)-1)
            res = res + (val << acquired_bits)
            acquired_bits = acquired_bits + remaining_bits
            self.data_bit_idx = remaining_bits
            remaining_bits = 0
        return res

class GIFReader:
    """Support reading of GIF files"""

    file_name = 0
    file_content = 0
    canvas_width = 0
    canvas_height = 0

    lzw_min_code_sz = 0
    glob_col_table = 0
    glob_col_table_sz = 0 
    color_resolution = 0
    bits_per_pixel = 0
    sort_flag = 0
    bg_color_index = 0
    pix_asp_ratio = 0

    color_table = 0

    _data_idx = 0

    output_image = 0


    def decode_subblock(self, data):
        """Decode data from the subblock."""
        code_reader = CodeReader(data)
        # initialize output stream
        output = list()
        # Initialize code table
        code_table = CodeTable(self.lzw_min_code_sz, self.glob_col_table_sz)

        bits_per_code_word = self.lzw_min_code_sz + 1
        #let CODE be the first code in the code stream
        code = code_reader.read(bits_per_code_word)

        if not code_table.hasKeyWithValue(code, [CLEARCODEVAL]):
            raise Exception('Expected Clear Code.')
    
        # read next actual code
        code = code_reader.read(bits_per_code_word)

        # check if the code size needs to grow
        if code == (1<<bits_per_code_word) - 1:
            bits_per_code_word = bits_per_code_word + 1

        # check if table needs to re-initialized
        if code_table.hasKeyWithValue(code, [CLEARCODEVAL]):
            # Initialize code table
            code_table = CodeTable(self.lzw_min_code_sz, self.glob_col_table_sz)

        #output {CODE} to index stream
        output.extend(code_table.get(code))
    
        # until the End of Information code word is hit...
        while not code_table.hasKeyWithValue(code, [EOICODEVAL]):
            # remember previous code
            prev_code = code
            #let CODE be the next code in the code stream
            code = code_reader.read(bits_per_code_word)
            # check if the code size needs to grow
            if code == (1<<bits_per_code_word) - 1:
                bits_per_code_word = bits_per_code_word + 1
            # check if table needs to re-initialized
            if code_table.hasKeyWithValue(code, [CLEARCODEVAL]):
                # Initialize code table
                code_table = CodeTable(self.lzw_min_code_sz, self.glob_col_table_sz)

            if code_table.hasKeyWithValue(code, [EOICODEVAL]):
                break

            #is CODE in the code table?
            if code_table.hasKey(code):
                #output {CODE} to index stream
                output.extend(code_table.get(code))
                #let K be the first index in {CODE}
                idx_k = code_table.get(code)[0]
                #add {CODE-1}+K to the code table
                new_code_word = code_table.get(prev_code) + [idx_k]
                code_table.at_new_key_put(new_code_word)
            else:
                #let K be the first index of {CODE-1}
                idx_k = code_table.get(prev_code)[0]
                #output {CODE-1}+K to index stream
                output.extend(code_table.get(prev_code) + [idx_k])
                #add {CODE-1}+K to code table
                new_code_word = code_table.get(prev_code) + [idx_k]
                code_table.at_new_key_put(new_code_word)
        return output


    def _get_file_content(self):
        """Get the file content"""
        with open(self.file_name, mode='rb') as file: 
            self.file_content = file.read()

    def _decode_header(self):
        """Decodes the GIF header."""
        header = self.file_content[0:6]
        log_screen_descr = self.file_content[6:13]
        self.canvas_width = log_screen_descr[0] + (log_screen_descr[1]<<8)
        self.canvas_height = log_screen_descr[2] + (log_screen_descr[3]<<8)
        # is there a global color table? (usually yes)
        flags = log_screen_descr[4]
        self.glob_col_table = (flags & 0b10000000) != 0 

        # determine the number of bits per primary color value
        self.color_resolution = (flags & 0b01110000) >> 4
        self.bits_per_pixel = self.color_resolution + 1

        # If the value is 1, then the colors in the global color table are sorted in order of "decreasing importance," which typically means "decreasing frequency" in the image
        self.sort_flag = (flags & 0b00001000) != 0

        # If this value is N, then the actual table size is 2^(N+1). 
        self.glob_col_table_sz = 1 << ((flags & 0b00000111)+1)

        self.bg_color_index = log_screen_descr[5]
        self.pix_asp_ratio = log_screen_descr[6]

    def _read_color_table(self, color_table_bytes):
        """Read the color table information"""
        self.color_table = [[0 for c in range(3)] for n in range(self.glob_col_table_sz)]
        for n in range(self.glob_col_table_sz):
            self.color_table[n][0] = color_table_bytes[3*n]
            self.color_table[n][1] = color_table_bytes[3*n+1]
            self.color_table[n][2] = color_table_bytes[3*n+2]

    def _handle_extensions_blocks(self):
        """Handle the extension blocks. (For now just sip them.)"""
        # extension blocks
        while self.file_content[self.data_idx] == 0x21:
            block_size = self.file_content[self.data_idx + 2]
            ext = self.file_content[self.data_idx:self.data_idx + block_size + 4]
            self.data_idx = self.data_idx + block_size + 4


    def _handle_image_descriptors(self):
        """Handle the image descrriptors with image data"""
        while self.file_content[self.data_idx] == 0x2c:
            img_left = self.file_content[self.data_idx + 1] + (self.file_content[self.data_idx + 2] << 8)
            img_top = self.file_content[self.data_idx + 3] + (self.file_content[self.data_idx + 4] << 8)
            img_width = self.file_content[self.data_idx+5] + (self.file_content[self.data_idx + 6] << 8)
            img_height = self.file_content[self.data_idx+7] + (self.file_content[self.data_idx + 8] << 8)
            flags = self.file_content[self.data_idx + 9]
            local_col_table_flag = (flags & 0b10000000) != 0
            interlace_flag = (flags & 0b01000000) != 0
            self.data_idx = self.data_idx + 10
            if local_col_table_flag:
                # read local color table
                print('read local color table. Not implemented yet')

            self.lzw_min_code_sz = self.file_content[self.data_idx]
            self.data_idx = self.data_idx + 1

            pix_xix = img_left
            pix_yix = img_top
            while self.file_content[self.data_idx] != 0:
                subblock_sz = self.file_content[self.data_idx]
                self.data_idx = self.data_idx + 1
                subblock_data = self.file_content[self.data_idx:self.data_idx + subblock_sz]
                dec_data = self.decode_subblock(subblock_data)
                for d in dec_data:
                    self.output_image[pix_xix][pix_yix][0] = self.color_table[d][0]
                    self.output_image[pix_xix][pix_yix][1] = self.color_table[d][1]
                    self.output_image[pix_xix][pix_yix][2] = self.color_table[d][2]
                    pix_xix = pix_xix + 1
                    if pix_xix == img_left + img_width:
                        pix_xix = img_left
                        pix_yix = pix_yix + 1
                self.data_idx = self.data_idx + subblock_sz

            self.data_idx = self.data_idx + 1


    def read(self, fname):
        """Read and decode the specified GIF file."""
        # decoding following the description at: http://www.matthewflickinger.com/lab/whatsinagif/bits_and_bytes.asp

        self.file_name = fname

        self._get_file_content()
        print('Check')
        self._decode_header()

        # create output image
        self.output_image = [[[0 for c in range(3)] for y in range(self.canvas_height)] for x in range(self.canvas_width)]

        # the global color table will take up 3*2^(N+1) bytes in the stream. 
        self.data_idx = 13+3*self.glob_col_table_sz

        color_table_bytes = self.file_content[13:self.data_idx]
        self._read_color_table(color_table_bytes)

        self._handle_extensions_blocks()

        self._handle_image_descriptors()

        if self.file_content[self.data_idx] != 0x3b:
            raise Exception('Decoding of the GIF failed')

import os

import numpy as np

from utlis import *

table_names = ['dc_y', 'ac_y', 'dc_c', 'ac_c']
IMAGE_SIZE_BITS = 32
TABLE_SIZE_BITS = 16
DC_VLI_LENGTH_BITS = 4
DC_HUFFMAN_CODE_LENGTH_BITS = 4
AC_ZERO_RUN_LENGTH_BITS = 4
AC_VLI_LENGTH_BITS = 4
AC_HUFFMAN_CODE_LENGTH_BITS = 8  
N_BLOCKS_BITS = 32

def writefile(dc, ac, n_blocks, tables, n_rows, n_cols, outpath):
    filestr = ''
    filestr+=int2binstr(n_rows, IMAGE_SIZE_BITS)
    filestr+=int2binstr(n_cols, IMAGE_SIZE_BITS)
    for table_name in table_names:
        filestr+=int2binstr(len(tables[table_name]), TABLE_SIZE_BITS)
        for key, value in tables[table_name].items():
            if 'dc' in table_name:
                filestr += int2binstr(key, DC_VLI_LENGTH_BITS)
                filestr += int2binstr(len(value), DC_HUFFMAN_CODE_LENGTH_BITS)
                filestr += value
            else: 
                filestr += int2binstr(key[0], AC_ZERO_RUN_LENGTH_BITS)
                filestr += int2binstr(key[1], AC_VLI_LENGTH_BITS)
                filestr += int2binstr(len(value), AC_HUFFMAN_CODE_LENGTH_BITS)
                filestr += value
    filestr += int2binstr(n_blocks, N_BLOCKS_BITS)
    for b in range(n_blocks):
        for c in range(3):
            category = bits_required(dc[b, c])
            symbols, values = RLC(ac[b, :, c])
            dc_table = tables['dc_y'] if c == 0 else tables['dc_c']
            ac_table = tables['ac_y'] if c == 0 else tables['ac_c']

            filestr+=dc_table[category]
            filestr+=int2VLI(dc[b, c])

            for i in range(len(symbols)):
                filestr+=ac_table[tuple(symbols[i])]
                filestr+=int2VLI(values[i])

    try:
        f = open(outpath, 'w')
    except FileNotFoundError as e:
        raise FileNotFoundError(
                "No such directory: {}".format(
                    os.path.dirname(outpath))) from e
    f.write(filestr)
    return len(filestr)

class JepgFileReader:
    def __init__(self, inpath):
        try:
            self.__file = open(inpath, "r")
        except FileExistsError as e:
            raise FileExistsError(
                "No such file: {}".format(inpath)
            ) from e
    
    def __readStr(self, length):
        return self.__file.read(length)

    def readChar(self):
        return self.__readStr(1)

    def readInt(self, length):
        return binstr2int(self.__readStr(length))
    
    def readVLI(self, length):
        return VLI2int(self.__readStr(length))
    
    def read_dc_table(self):
        table = dict()
        table_size = self.readInt(TABLE_SIZE_BITS)
        for _ in range(table_size):
            category = self.readInt(DC_VLI_LENGTH_BITS)
            code_length = self.readInt(DC_HUFFMAN_CODE_LENGTH_BITS)
            code = self.__readStr(code_length)
            table[code] = category
        return table
    
    def read_ac_table(self):
        table = dict()
        table_size = self.readInt(TABLE_SIZE_BITS)
        for _ in range(table_size):
            zero_run_length = self.readInt(AC_ZERO_RUN_LENGTH_BITS)
            VLI_length = self.readInt(AC_VLI_LENGTH_BITS)
            code_length = self.readInt(AC_HUFFMAN_CODE_LENGTH_BITS)
            code = self.__readStr(code_length)
            table[code] = (zero_run_length, VLI_length)
        return table
    
    def read_huffman_code(self, table):
        prefix = ''
        while prefix not in table:
            prefix += self.readChar()
        return table[prefix]
    
def readfile(inpath):
    reader = JepgFileReader(inpath)
    n_rows = reader.readInt(IMAGE_SIZE_BITS)
    n_cols = reader.readInt(IMAGE_SIZE_BITS)
    tables = dict()
    for table_name in table_names:
        if 'dc' in table_name:
            tables[table_name] = reader.read_dc_table()
        else:
            tables[table_name] = reader.read_ac_table()
    n_blocks = reader.readInt(N_BLOCKS_BITS)
    dc = np.zeros((n_blocks, 3), dtype=np.int32)
    ac = np.zeros((n_blocks, 63, 3), dtype=np.int32)
    for block_index in range(n_blocks):
        for component in range(3):
            dc_table = tables['dc_y'] if component == 0 else tables['dc_c']
            ac_table = tables['ac_y'] if component == 0 else tables['ac_c']
            
            category = reader.read_huffman_code(dc_table)
            dc[block_index, component] = reader.readVLI(category)

            cells_count = 0
            while cells_count < 63:
                zero_run_length, VLI_length = reader.read_huffman_code(ac_table)
                if (zero_run_length, VLI_length) == (0, 0):
                    while cells_count < 63:
                        ac[block_index, cells_count, component] = 0
                        cells_count += 1
                else:
                    for _ in range(zero_run_length):
                        ac[block_index, cells_count, component] = 0
                        cells_count += 1
                    ac[block_index, cells_count, component] = reader.readVLI(VLI_length)
                    cells_count += 1
    return n_rows, n_cols, n_blocks, dc, ac
import os

import cv2
import fire
import numpy as np
import skimage

from utlis import *
from huffman import HuffmanTree

def RLC(arr):
    last_nonzero = -1
    for i, elem in enumerate(arr):
        if elem != 0:
            last_nonzero = i
    symbols, values, counter = [], [], 0
    for i,elem in enumerate(arr):
        if i > last_nonzero:
            symbols.append((0,0))
            values.append(0)
            break
        elif elem ==0 and counter < 15:
            counter += 1
        else:
            size = bits_required(elem)
            symbols.append((counter, size))
            values.append(elem)
            counter = 0
    return symbols, values

def writefile(dc, ac, n_blocks, tables, filepath='./comp.dat'):
    filestr = ''
    for table_name in ['dc_y', 'ac_y', 'dc_c', 'ac_c']:
        # 16 bits for 'table size'
        filestr+=int2binstr(len(tables[table_name]), 16)
        for key, value in tables[table_name].items():
            if table_name in {'dc_y', 'dc_c'}:
                # 4 bits for the 'category'
                # 4 bits for 'code_length'
                # 'code_length' bits for 'huffman_code'
                filestr += int2binstr(key, 4)
                filestr += int2binstr(len(value), 4)
                filestr += value
            else: 
                # 4 bits for 'run_length'
                # 4 bits for 'size'
                # 8 bits for 'code_length'
                # 'code _length' bits for 'huffman_code'
                filestr += int2binstr(key[0], 4)
                filestr += int2binstr(key[1], 4)
                filestr += int2binstr(len(value), 8)
                filestr += value

    # 32 bits for 'n_blocks'
    filestr += int2binstr(n_blocks, 32)
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
        f = open(filepath, 'w')
    except FileNotFoundError as e:
        raise FileNotFoundError(
                "No such directory: {}".format(
                    os.path.dirname(filepath))) from e
    f.write(filestr)
    return len(filestr)

def main(inputfile):    
    img_bgr = cv2.imread(inputfile)
    img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2YCrCb)

    n_rows, n_cols = img.shape[0], img.shape[1]

    if n_rows % 8 == n_cols % 8 == 0:
        n_blocks = n_rows // 8 * n_cols // 8
    else:
        raise ValueError(("the width and height of the image "
                            "should both be mutiples of 8"))

    dec_img = np.zeros((n_rows, n_cols, 3), dtype=np.uint8)
    dc = np.zeros((n_blocks, 3), dtype=np.int32)
    ac = np.zeros((n_blocks, 63, 3), dtype=np.int32)

    block_index = 0
    for i in range(0, n_rows, 8):
        for j in range(0, n_cols, 8):
            for k in range(3):
                block = img[i:i+8, j:j+8, k] - 128
                dct_block = dct_2d(block)
                quant_block = quantize(dct_block, 'lum' if k == 0 else 'chrom')
                zz = block2zigzag(quant_block)
                dc[block_index, k] = zz[0]
                ac[block_index, :, k] = zz[1:]

                dequant_block = dequantize(quant_block, 'lum' if k ==0 else 'chrom')
                idct_block = idct_2d(dequant_block)
                dec_img[i:i+8, j:j+8, k] = (idct_block + 128).round().astype(np.uint8)
            block_index += 1

    dec_img_bgr = cv2.cvtColor(dec_img, cv2.COLOR_YCrCb2BGR)
    cv2.imwrite('./out.png', dec_img_bgr)

    for i in range(n_blocks-1, 0, -1):
        dc[i] -= dc[i-1]
    
    def flatten(lst):
        return [x for sublist in lst for x in sublist]
    
    H_DC_Y = HuffmanTree(np.vectorize(bits_required)(dc[:, 0]))
    H_DC_C = HuffmanTree(np.vectorize(bits_required)(dc[:, 1:].flat))
    H_AC_Y = HuffmanTree(flatten([RLC(ac[i, :, 0])[0] 
                                    for i in range(n_blocks)]))
    H_AC_C = HuffmanTree(flatten([RLC(ac[i, :, j])[0]
                                    for i in range(n_blocks)
                                    for j in range(1,3)]))
    
    tables = {'dc_y': H_DC_Y.value_to_bitstring_table(),
              'ac_y': H_AC_Y.value_to_bitstring_table(),
              'dc_c': H_DC_C.value_to_bitstring_table(),
              'ac_c': H_AC_C.value_to_bitstring_table()}
    
    res_size = writefile(dc, ac, n_blocks, tables) / 8 / 8 / 1024

    psnr = skimage.measure.compare_psnr(img_bgr, dec_img_bgr, data_range=255)
    ssim = skimage.measure.compare_ssim(img_bgr, dec_img_bgr, data_range=255, multichannel=True)

    orig_size = n_rows * n_cols * 3 / 1024
    
    print('The size of the original image is %.2lf KB'%(orig_size))
    print('The size of the result image is %d KB'%(res_size))
    print("PSNR : %lfdB"%(psnr))
    print("MS-SSIM : %lf"%(ssim))
    print("Rate : %lfbpp"%(res_size / orig_size * 8))
    # print("Compression Ratio : %lf%%"%(res_size / orig_size * 100))

    
    # std_jpeg = cv2.imread('./lenna.jpg')
    # std_psnr = skimage.measure.compare_psnr(img_bgr, std_jpeg, data_range=255)
    # std_ssim = skimage.measure.compare_ssim(img_bgr, std_jpeg, data_range=255, multichannel=True)
    # print("std PSNR : %lfdB"%(std_psnr))
    # print("std SSIM : %lf"%(std_ssim))

if __name__ == "__main__":
    fire.Fire(main)

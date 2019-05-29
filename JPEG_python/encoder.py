import os

import cv2
import fire
import numpy as np
import skimage

from utils import *
from huffman import HuffmanTree
import JpegIO

def main(inpath='./lenna.png', outpath='./lenna.dat', tempoutpath='./tmp.png'):    
    img_bgr = cv2.imread(inpath)
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
    cv2.imwrite(tempoutpath, dec_img_bgr)

    for i in range(n_blocks-1, 0, -1):
        dc[i] -= dc[i-1]
    
    # dc: length of VLI, VLI
    # ac: (run length of zero, length of VLI), VLI
    # the former stored in hummfan code

    def flatten(lst):
        return [x for sublist in lst for x in sublist]
    
    H_DC_Y = HuffmanTree(np.vectorize(bits_required)(dc[:, 0]))
    H_DC_C = HuffmanTree(np.vectorize(bits_required)(dc[:, 1:].flat))
    H_AC_Y = HuffmanTree(flatten([RLE(ac[i, :, 0])[0] 
                                    for i in range(n_blocks)]))
    H_AC_C = HuffmanTree(flatten([RLE(ac[i, :, j])[0]
                                    for i in range(n_blocks)
                                    for j in range(1,3)]))
    
    tables = {'dc_y': H_DC_Y.value_to_bitstring_table(),
              'ac_y': H_AC_Y.value_to_bitstring_table(),
              'dc_c': H_DC_C.value_to_bitstring_table(),
              'ac_c': H_AC_C.value_to_bitstring_table()}
    
    res_size = JpegIO.writefile(dc, ac, n_blocks, tables, n_rows, n_cols, outpath) / 8 / 8 / 1024

    psnr = skimage.measure.compare_psnr(img_bgr, dec_img_bgr, data_range=255)
    ssim = skimage.measure.compare_ssim(img_bgr, dec_img_bgr, data_range=255, multichannel=True)

    orig_size = n_rows * n_cols * 3 / 1024
    
    print('The size of the original image is %.2lf KB'%(orig_size))
    print('The size of the result image is %.2lf KB'%(res_size))
    print("PSNR : %lfdB"%(psnr))
    print("MS-SSIM : %lf"%(ssim))
    print("Rate : %lfbpp"%(res_size / orig_size * 8))

if __name__ == "__main__":
    fire.Fire(main)

import os

import cv2
import fire
import numpy as np

from utlis import *
import JpegIO

def main(inpath, outpath='./decoded.png'):
    n_rows, n_cols, n_blocks, dc, ac = JpegIO.readfile(inpath)

    for i in range(1, n_blocks):
        dc[i] += dc[i-1]

    npmat = np.zeros((n_rows, n_cols, 3), dtype=np.uint8)

    block_index = 0
    for i in range(0, n_rows, 8):
        for j in range(0, n_cols, 8):
            for k in range(3):
                zigzag = [dc[block_index, k]] + list(ac[block_index, :, k])
                quant_mat = zigzag2block(8, 8, zigzag)
                dequant_mat = dequantize(quant_mat, 'lum' if k ==0 else 'chrom')
                block = idct_2d(dequant_mat)
                npmat[i:i+8, j:j+8, k] = (block + 128).round().astype(np.uint8)
            block_index +=1

    img_bgr = cv2.cvtColor(npmat, cv2.COLOR_YCrCb2BGR)
    cv2.imwrite(outpath, img_bgr)   

if __name__ == "__main__":
    fire.Fire(main)
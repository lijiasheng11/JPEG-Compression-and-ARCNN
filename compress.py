import os

import cv2
import fire
import matplotlib.pyplot as plt
import numpy as np

from utlis import *

def main(inputfile):
    img_bgr = cv2.imread(inputfile)
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2YCrCb)

    n_rows, n_cols = img.shape[0], img.shape[1]

    if n_rows % 8 == n_cols % 8 == 0:
        n_blocks = n_rows // 8 * n_cols // 8
    else:
        raise ValueError(("the width and height of the image "
                            "should both be mutiples of 8"))

    com_img = np.zeros((n_rows, n_cols, 3), dtype=np.uint8)

    for i in range(0, n_rows, 8):
        for j in range(0, n_cols, 8):
            for k in range(3):
                block = img[i:i+8, j:j+8, k] - 128

                dct_mat = dct_2d(block)

                quant_mat = quantize(dct_mat, 'lum' if k == 0 else 'chrom')

                dequant_mat = dequantize(quant_mat, 'lum' if k ==0 else 'chrom')

                com_block = idct_2d(dequant_mat)

                com_img[i:i+8, j:j+8, k] = (com_block + 128).round().astype(np.uint8)
                


    com_img_rgb = cv2.cvtColor(com_img, cv2.COLOR_YCrCb2RGB)

    plt.figure(figsize=(15, 15))
    plt.subplot(1, 2, 1)
    plt.title("Origin Image")
    plt.imshow(img_rgb)
    plt.subplot(1, 2, 2)
    plt.title("JPEG Compressed Image")
    plt.imshow(com_img_rgb)

    
    com_img_bgr = cv2.cvtColor(com_img, cv2.COLOR_YCrCb2BGR)
    cv2.imwrite('./compressed.png', com_img_bgr)

if __name__ == "__main__":
    fire.Fire(main)

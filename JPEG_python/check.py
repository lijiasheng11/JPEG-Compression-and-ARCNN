import cv2
import skimage

out_img = cv2.imread('./tmp.png')
dec_img = cv2.imread('./lenna_decoded.png')

ssim = skimage.measure.compare_ssim(out_img, dec_img, data_range=255, multichannel=True)

if abs(ssim - 1 ) < 1e-10:
    print("Accepted!")
else:
    print("Wrong Answer!")
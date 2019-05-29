# JPEG-Compression-and-ARCNN

This repository is implementation of JPEG basic system, enhancement filters and "[Deep Convolution Networks for Compression Artifacts Reduction][ARCNN]".

## JPEG-python

Implementation of JPEG is located at `JPEG_python`. Pipeline for JPEG basic system is following:

- Color Space Transformation(RGB2TCbCr)
- Block Splitting
- Discrete Cosine Transform(DCT)
- Quantization
- Zigzag Scanning
- Differential Pulse Code Modulation(DPCM) on DC component
- Run Length Encoding(RLE) on AC component
- VLI & Huffman Encoding

### Usage

```bash
cd JPEG_python
python encoder.py --inpath='./lenna.png'  \
                  --outpath='./lenna.dat' \
                  --tempoutpath='./tmp.png'

python decoder.py --inpath='./lenna.dat' \
                  --outpath='./lenna_decoded.png'
```

For convenience, compressed Codes will be stored in`lenna.dat`  in the format of 01 string, thus it takes roughly eight times more space than binary storage. 

## ARCNN

Implementation of [Artifacts Reduction Convolutional neural network(ARCNN)][ARCNN] is located in `arcnn`.  This implementation must be run under GPU pattern.

### Usage

As compressing images into jpeg format is time consuming, we recompress images every `n_cycles` epochs.

#### train

```bash
usage: main.py [-h] 
    [--arch ARCH]
    [--images_dir IMAGES_DIR]
    [--jpeg_quality JPEG_QUALITY] [--patch_size PATCH_SIZE]
    [--batch_size BATCH_SIZE]
    [--num_epochs NUM_EPOCHS]
    [--lr LR]
    [--threads THREADS]
    [--seed SEED]
    [--use_augmentation USE_AUGMENTATION]
    [--use_fast_loader USE_FAST_LOADER]
    [--model_weights MODEL_WEIGHTS]
    [--start_epoch START_EPOCH]
    [--n_cycles N_CYCLES]

optional arguments:
  -h, --help            show this help message and exit
  --arch ARCH           ARCNN or FastARCNN
  --images_dir IMAGES_DIR
  --jpeg_quality JPEG_QUALITY
  --patch_size PATCH_SIZE
  --batch_size BATCH_SIZE
  --num_epochs NUM_EPOCHS
  --lr LR
  --threads THREADS
  --seed SEED
  --use_augmentation USE_AUGMENTATION
  --use_fast_loader USE_FAST_LOADER
  --model_weights MODEL_WEIGHTS
  --start_epoch START_EPOCH
  --n_cycles N_CYCLES
```

#### test

```bash
usage: eval.py [-h] 
    --arch ARCH 
    --weights_path WEIGHTS_PATH 
    --image_path IMAGE_PATH 
    --outputs_dir OUTPUTS_DIR
    [--jpeg_quality JPEG_QUALITY]

optional arguments:
  -h, --help            show this help message and exit
  --arch ARCH           ARCNN or FastARCNN
  --weights_path WEIGHTS_PATH
  --image_path IMAGE_PATH
  --outputs_dir OUTPUTS_DIR
  --jpeg_quality JPEG_QUALITY
```



## Results

| Quality | |jpeg |      | |均值滤波|   | |中位数滤波| | |高斯滤波|  | |ARCNN |     | |FastARCNN| |
| ------- | ---------- | ---------- | ---------- | --------- | ---------- | --------- | ----------- | ----------- | ----------- | ----------- | ----------- | ----------- | -------- | --------- | -------- | -------- | --------- | -------- |
|| nrmse   | psnr       | ssim       | NRMSE      | PSNR      | SSIM       | NRMSE     | PSNR        | SSIM        | NRMSE       | PSNR        | SSIM        | NRMSE       | PSNR     | SSIM      | NRMSE    | PSNR     | SSIM               |
| 10      | 0.10759166 | 25.5687072 | 0.7349024  | 0.107284  | 25.5724143 | 0.740197  | 0.106622517 | 25.64854377 | 0.737160456 | 0.109893914 | 25.35919998 | 0.729683225 | **0.098770** | **26.344464** | **0.761270** | 0.100744 | 26.150947 | 0.761108 |
| 20      | 0.08471336 | 27.7564282 | 0.8103198  | 0.0901053 | 27.1655608 | 0.801463  | 0.087893714 | 27.43002385 | 0.803608685 | 0.091235394 | 27.05903444 | 0.796919993 | **0.078171** | **28.481314** | **0.829704** | 0.080431 | 28.195823 | 0.825750 |
| 30      | 0.07446662 | 28.9538491 | 0.8435141  | 0.0832965 | 27.8854824 | 0.827522  | 0.080300364 | 28.272947   | 0.831537618 | 0.083812947 | 27.83597909 | 0.82544385  | **0.068979** | **29.634973** | **0.858679** | 0.070016 | 29.490277 | 0.856202 |

[ARCNN]: http://mmlab.ie.cuhk.edu.hk/projects/ARCNN.html    "Deep Convolution Networks for Compression"


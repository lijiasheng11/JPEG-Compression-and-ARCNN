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

As compressing images into jpeg format is time consuming, we recompress images every `n_cycles`.

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



[ARCNN]: http://mmlab.ie.cuhk.edu.hk/projects/ARCNN.html	"Deep Convolution Networks for Compression"


# JPEG-Compression-and-ARCNN

This repository is implementation of JPEG basic system, enhancement filters and "Deep Convolution Networks for Compression Artifacts Reduction".



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

## References

[ARCNN]: http://mmlab.ie.cuhk.edu.hk/projects/ARCNN.html	"Deep Convolution Networks for Compression"


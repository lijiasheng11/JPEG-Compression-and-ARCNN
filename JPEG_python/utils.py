import numpy as np
from scipy import fftpack

def dct_2d(mat):
    return fftpack.dct(fftpack.dct(mat.T, norm='ortho').T, norm='ortho')

def idct_2d(mat):
    return fftpack.idct(fftpack.idct(mat.T, norm='ortho').T, norm='ortho')

def load_quantization_table(component):
    if component == 'lum':
        q = np.array([[2, 2, 2, 2, 3, 4, 5, 6],
                      [2, 2, 2, 2, 3, 4, 5, 6],
                      [2, 2, 2, 2, 4, 5, 7, 9],
                      [2, 2, 2, 4, 5, 7, 9, 12],
                      [3, 3, 4, 5, 8, 10, 12, 12],
                      [4, 4, 5, 7, 10, 12, 12, 12],
                      [5, 5, 7, 9, 12, 12, 12, 12],
                      [6, 6, 9, 12, 12, 12, 12, 12]])
    elif component == 'chrom':
        q = np.array([[3, 3, 5, 9, 13, 15, 15, 15],
                      [3, 4, 6, 11, 14, 12, 12, 12],
                      [5, 6, 9, 14, 12, 12, 12, 12],
                      [9, 11, 14, 12, 12, 12, 12, 12],
                      [13, 14, 12, 12, 12, 12, 12, 12],
                      [15, 12, 12, 12, 12, 12, 12, 12],
                      [15, 12, 12, 12, 12, 12, 12, 12],
                      [15, 12, 12, 12, 12, 12, 12, 12]])
    else:
        raise ValueError((
            "component should be either 'lum' or 'chrom', "
            "but '{comp}' was found").format(comp=component))

    return q


def quantize(mat, component):
    q = load_quantization_table(component)
    return (mat / q).round().astype(np.int32)

def dequantize(mat, component):
    q = load_quantization_table(component)
    return mat * q

def zigzag_points(rows, cols):
    # constants for directions
    UP, DOWN, RIGHT, LEFT, UP_RIGHT, DOWN_LEFT = range(6)

    # move the point in different directions
    def move(direction, point):
        return {
            UP: lambda point: (point[0] - 1, point[1]),
            DOWN: lambda point: (point[0] + 1, point[1]),
            LEFT: lambda point: (point[0], point[1] - 1),
            RIGHT: lambda point: (point[0], point[1] + 1),
            UP_RIGHT: lambda point: move(UP, move(RIGHT, point)),
            DOWN_LEFT: lambda point: move(DOWN, move(LEFT, point))
        }[direction](point)

    # return true if point is inside the block bounds
    def inbounds(point):
        return 0 <= point[0] < rows and 0 <= point[1] < cols

    # start in the top-left cell
    point = (0, 0)

    # True when moving up-right, False when moving down-left
    move_up = True

    for _ in range(rows * cols):
        yield point
        if move_up:
            if inbounds(move(UP_RIGHT, point)):
                point = move(UP_RIGHT, point)
            else:
                move_up = False
                if inbounds(move(RIGHT, point)):
                    point = move(RIGHT, point)
                else:
                    point = move(DOWN, point)
        else:
            if inbounds(move(DOWN_LEFT, point)):
                point = move(DOWN_LEFT, point)
            else:
                move_up = True
                if inbounds(move(DOWN, point)):
                    point = move(DOWN, point)
                else:
                    point = move(RIGHT, point)

def block2zigzag(block):
    return np.array([block[point] for point in zigzag_points(*block.shape)])

def zigzag2block(n_rows, n_cols, zigzag):
    block = np.zeros((n_rows, n_cols), np.int32)
    for i, point in enumerate(zigzag_points(n_rows, n_cols)):
        block[point] = zigzag[i]
    return block

def RLE(arr):
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

def int2binstr(x, length):
    return bin(x)[2:][-length:].zfill(length)

def binstr2int(binstr):
    if not set(binstr).issubset('01'):
        raise ValueError("binstr should have only '0's and '1's")
    return int(binstr, 2)

# functions for VLI

def bits_required(x):
    x = abs(x)
    return 0 if x == 0 else len(bin(x)[2:])

def binstrFlip(s):
    if not set(s).issubset('01'):
        raise ValueError("binstr should have only '0's and '1's")
    return ''.join(map(lambda a: '0' if a == '1' else '1', s))

def int2VLI(x):
    if x == 0:
        return ''
    binstr = bin(abs(x))[2:]
    if x < 0:
        binstr = binstrFlip(binstr)
    return binstr

def VLI2int(binstr):
    if len(binstr) == 0:
        return 0
    return binstr2int(binstr) if binstr[0] == '1' else -binstr2int(binstrFlip(binstr))
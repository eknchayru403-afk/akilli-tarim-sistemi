#!/usr/bin/env python
"""TensorFlow 2.x kurulum ve GPU/CPU doğrulama scripti."""

import sys

import tensorflow as tf


def main() -> int:
    print(f'Python: {sys.version.split()[0]}')
    print(f'TensorFlow: {tf.__version__}')
    print(f'Built with CUDA: {tf.test.is_built_with_cuda()}')

    gpus = tf.config.list_physical_devices('GPU')
    print(f'Physical GPUs: {gpus}')

    with tf.device('/CPU:0'):
        a = tf.constant([[1.0, 2.0], [3.0, 4.0]])
        b = tf.constant([[1.0, 1.0], [0.0, 1.0]])
        c = tf.matmul(a, b)
    print(f'CPU matmul: OK — {c.numpy().tolist()}')

    if gpus:
        with tf.device('/GPU:0'):
            d = tf.matmul(a, b)
        print(f'GPU matmul: OK — {d.numpy().tolist()}')
    else:
        print('GPU: not available (CPU-only build or no CUDA device)')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())

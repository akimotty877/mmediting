# Copyright (c) OpenMMLab. All rights reserved.
import argparse
import os

import cv2
import mmcv
import torch

import time
from tqdm import tqdm

from mmedit.apis import init_model, restoration_face_inference
from mmedit.utils import modify_args


def parse_args():
    modify_args()
    parser = argparse.ArgumentParser(description='Restoration demo')
    parser.add_argument('config', help='test config file path')
    parser.add_argument('checkpoint', help='checkpoint file')
    parser.add_argument('img_path', help='path to input image file')
    parser.add_argument('save_path', help='path to save restoration result')
    parser.add_argument(
        '--upscale-factor',
        type=int,
        default=1,
        help='the number of times the input image is upsampled.')
    parser.add_argument(
        '--face-size',
        type=int,
        default=1024,
        help='the size of the cropped and aligned faces..')
    parser.add_argument(
        '--imshow', action='store_true', help='whether show image with opencv')
    parser.add_argument('--device', type=int, default=0, help='CUDA device id')
    args = parser.parse_args()
    return args


def main():
    args = parse_args()

    # if not os.path.isfile(args.img_path):
    #     raise ValueError('It seems that you did not input a valid '
    #                      '"image_path". Please double check your input, or '
    #                      'you may want to use "restoration_video_demo.py" '
    #                      'for video restoration.')

    if args.device < 0 or not torch.cuda.is_available():
        device = torch.device('cpu')
    else:
        device = torch.device('cuda', args.device)

    model = init_model(args.config, args.checkpoint, device=device)

    files = os.listdir(args.img_path)
    files_file = [f for f in files if os.path.isfile(os.path.join(args.img_path, f))]
    tmp = cv2.imread(args.img_path + files_file[0])
    height, width, channels = tmp.shape[:3]
    for f in tqdm(files_file):
      output = restoration_face_inference(model, args.img_path + f,
                                          args.upscale_factor, args.face_size)

      output = mmcv.imresize(output, (width, height))
      mmcv.imwrite(output, args.save_path + f)
    # if args.imshow:
    #     mmcv.imshow(output, 'predicted restoration result')


if __name__ == '__main__':
    main()

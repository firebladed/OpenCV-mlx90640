from imutils.video import VideoStream
import argparse
import datetime
import imutils
import time
import cv2
import opencv_mlx90640
import numpy as np

from shutil import get_terminal_size
#import pandas as pd

#pd.set_option('display.width', get_terminal_size()[0])
np.set_printoptions(linewidth=get_terminal_size()[0])



device = "/dev/video0"

corrector  = opencv_mlx90640.mlx90640.mlx90640(device)

vs = cv2.VideoCapture(device)
vs.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('Y','1','6',' '))
vs.set(cv2.CAP_PROP_CONVERT_RGB, 0)


while True:

  ret, frame = vs.read()
  frame = corrector.correct_img(frame)

#  framele = frame.byteswap()
#  print(framele)

  frame8 = (frame/256).astype("uint8")

#  framebgr = cv2.cvtColor(frame8, cv2.COLOR_GRAY2BGR)
#  print(framebgr.dtype)
#  fbframe = cv2.resize(frame32, (1920,1080))
  im_color = cv2.applyColorMap(frame8, cv2.COLORMAP_JET)
  print(im_color.dtype)
  im_color = cv2.cvtColor(im_color, cv2.COLOR_BGR2BGRA)

  target = np.dot(im_color.shape[1::-1],9)
  print(target)
  #im_color = cv2.resize(im_color, tuple(target),interpolation = cv2.INTER_NEAREST)
  im_color = cv2.resize(im_color, tuple(target))

  height = 1080
  width = 1920

  blank_image = np.zeros((height,width,4), np.uint8)

  yoff = 0
  xoff = 0

  fbframe = blank_image
  fbframe[yoff:yoff+im_color.shape[0], xoff:xoff+im_color.shape[1]] = im_color

#  fbframe = cv2.resize(im_color, (1920,1080),interpolation = cv2.INTER_NEAREST)
  with open('/dev/fb0', 'rb+') as buf:
    buf.write(fbframe)

#opencv_mlx90640.py
#
import os
import cv2

class mlx90640:

  devpath = ""
  eeprom = None

  def __init__(self,devpath):
    self.devpath= devpath
    self.check_device()

  def check_device(self):

    with open("/sys/class/video4linux/"+os.path.basename(self.devpath)+"/device/name", 'r') as file:
      data = file.read()
      #print(data)
      if data.strip() != "mlx90640":
        raise Exception("Not mlx90640")

    with open("/sys/class/video4linux/"+os.path.basename(self.devpath)+"/device/mlx90640_nvram0/nvmem", mode='rb') as eeprom:
      self.eeprom = eeprom.read()

    print(self.eeprom)

  def correct_img(self)

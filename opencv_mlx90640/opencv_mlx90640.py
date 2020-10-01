#opencv-mlx90640.py
#
class mlx90640:

  devpath = ""

  def __init__(self,devpath):
    self.devpath= devpath
    self.check_device()

  def check_device(devpath):

    with open("/sys/class/video4linux/"+os.path.basename(self.devnum)+"/device/name", 'r') as file:
    data = file.read()
    if data != "mlx90640"
      raise Exception("Not mlx90640")


#opencv_mlx90640.py
#
import os
import cv2
import numpy as np
import binascii
import struct

class mlx90640:

  devpath = ""
  eeprom = None

  def __init__(self,devpath):
    self.devpath= devpath
    self.check_device()
    self.read_eeprom()

  def check_device(self):

    with open("/sys/class/video4linux/"+os.path.basename(self.devpath)+"/device/name", 'r') as file:
      data = file.read()
      #print(data)
      if data.strip() != "mlx90640":
        raise Exception("Not mlx90640")


  def read_eeprom(self):

    with open("/sys/class/video4linux/"+os.path.basename(self.devpath)+"/device/mlx90640_nvram0/nvmem", mode='rb') as eeprom:
      self.eeprom = eeprom.read()

    print(len(self.eeprom))
    print(binascii.hexlify(self.eeprom))


    # Calculate Calibration constants
    # eeprom start 0x2400 end 0x273F each 16bit local copy 0x2400 -> 0x0

    EE2410, = struct.unpack('<H',(self.eeprom[32:34])) # 2410 -> 0x10*2 = 32
    EE2411, = struct.unpack('<H',(self.eeprom[34:36])) # 2411 -> 0x11*2 = 34

    EE2430, = struct.unpack('<H',(self.eeprom[96:98])) # 2430 -> 0x30*2 = 96
    EE2431, = struct.unpack('<H',(self.eeprom[98:100])) # 2431 -> 0x31*2 = 98
    EE2432, = struct.unpack('<H',(self.eeprom[100:102])) # 2432 -> 0x32*2 = 100
    EE2433, = struct.unpack('<H',(self.eeprom[102:104])) # 2433 -> 0x33*2 = 102

    EE2436, = struct.unpack('<H',(self.eeprom[108:110])) # 2436 -> 0x36*2 = 108
    EE2437, = struct.unpack('<H',(self.eeprom[110:112])) # 2437 -> 0x37*2 = 110



    Kvdd  = (EE2433 & 0xFF00) >> 8
    if Kvdd > 127:
        Kvdd = Kvdd - 256
    self.Kvdd = Kvdd * 2**5

    Vdd25 = (EE2433 & 0x00FF)
    self.Vdd25 = (Vdd25 - 255) * 2**5 - 2**13

    Kvptat = (EE2432 & 0xFC00) >> 10
    if Kvptat > 31:
        Kvptat = Kvptat -64
    self.Kvptat = Kvptat / 2**12

    Ktptat = (EE2432 & 0x03FF)
    if Ktptat > 511:
        Ktptat = Ktptat -1024
    self.Ktptat = Ktptat / 2**3

    Gain = EE2430
    if Gain > 32767:
        Gain = Gain - 65536
    self.Gain = Gain

    Vptat25 = EE2431
    if Vptat25 > 32767:
        Vptat25 = Vptat25 - 65536
    self.Vptat25 = Vptat25

    Aptatee  = (EE2410 & 0xF000)  / 2**12
    Aptat = Aptatee / 2**2
    self.Aptat = Aptat + 8

    Scarow  = (EE2410 & 0x0F00)  / 2**8
    self.Scarow = Scarow

    Scacol  = (EE2410 & 0x00F0)  / 2**4
    self.Scacol = Scacol

    Scarem  = (EE2410 & 0x000F)
    self.Scarem = Scarem

    OffsetAvg = EE2411
    if OffsetAvg > 32767:
        OffsetAvg = OffsetAvg - 65536
    self.OffsetAvg = OffsetAvg

    KtaavgROCO = (EE2436 &  0xFF00)
    if KtaavgROCO > 127:
        KtaavgROCO = KtaavgROCO - 256
    self.KtaavgROCO = KtaavgROCO

    KtaavgRECO = (EE2436 &  0x00FF)
    if KtaavgRECO > 127:
        KtaavgRECO = KtaavgRECO - 256
    self.KtaavgRECO = KtaavgRECO

    KtaavgROCE = (EE2437 &  0xFF00)
    if KtaavgROCE > 127:
        KtaavgROCE = KtaavgROCE - 256
    self.KtaavgROCE = KtaavgROCE

    KtaavgRECE = (EE2437 &  0x00FF)
    if KtaavgRECE > 127:
        KtaavgRECE = KtaavgRECE - 256
    self.KtaavgRECE = KtaavgRECE

    #generate column offset arrays

    rowoffsets = np.zeros([6*4], dtype="int8")
    row4offsets = np.frombuffer(self.eeprom[36:48], dtype="uint16") # 2412 -> 0x12*2 = 36, 2418 -> 0x18*2 = 48
    print(row4offsets)
    r = 0
    for row4off in row4offsets:
        offtemp = (row4off & 0x000F)
        rowoffsets[r] = (offtemp if offtemp < 7 else offtemp -16)
        offtemp = ((row4off & 0x00F0) >> 4)
        rowoffsets[r+1]= (offtemp if offtemp < 7 else offtemp -16)
        offtemp = ((row4off & 0x0F00) >> 8)
        rowoffsets[r+2]= (offtemp if offtemp < 7 else offtemp -16)
        offtemp = ((row4off & 0xF000) >> 12)
        rowoffsets[r+3]= (offtemp if offtemp < 7 else offtemp -16)
        r = r+4
    self.rowoffsets= rowoffsets

    coloffsets = np.zeros([8*4], dtype="int8")
    col4offsets = np.frombuffer(self.eeprom[48:64], dtype="uint16") # 2418 -> 0x18*2 = 48, 2420 -> 0x20*2 = 64
    print(col4offsets)
    r = 0
    for col4off in col4offsets:
        offtemp = (col4off & 0x000F)
        coloffsets[r]= (offtemp if offtemp < 7 else offtemp -16)
        offtemp = ((col4off & 0x00F0) >> 4)
        coloffsets[r+1]= (offtemp if offtemp < 7 else offtemp -16)
        offtemp = ((col4off & 0x0F00) >> 8)
        coloffsets[r+2]= (offtemp if offtemp < 7 else offtemp -16)
        offtemp = ((col4off & 0xF000) >> 12)
        coloffsets[r+3]= (offtemp if offtemp < 7 else offtemp -16)
        r = r+4
    self.coloffsets = coloffsets


    print("\nRowOffsets")
    print(rowoffsets)
    print("\nColOffsets")
    print(coloffsets)


    # generate calibration maps
    # epprom registers start 0x2440 end 0x273F
    # nvram start 0x80 end 0x05FE
    # offset(6bit) alpha(6bit) kta(3bit) outlier(1bit) [16bit]

    print("\n")
    pixcal = np.frombuffer(self.eeprom[128:], dtype="uint16")

    print(pixcal.dtype)
    print(pixcal)
    print(pixcal.shape)
    Pixcor = np.reshape(pixcal,(24,32))
    print(Pixcor)
    print(Pixcor.dtype)
    print(Pixcor.shape)

#    zeros = np.zeros((2,Pixcor.shape[1]), dtype="uint16")
#    Pixcor = np.concatenate((Pixcor, zeros), axis=0)

    print(Pixcor)
    print(Pixcor.dtype)
    print(Pixcor.shape)


    # apply bitmasks to copies (offset 0xFC00, alpha 0x03F0, kta 0x000E, outlier 0x0001
    print("\n Pixoff")
    self.Pixoff = np.bitwise_and(np.copy(Pixcor),0xFC00) >> 10
    print(self.Pixoff)
    print("\n Pixalp")
    self.Pixalp = np.bitwise_and(np.copy(Pixcor),0x03F0) >> 8
    print(self.Pixalp)
    print("\n Pixkta")
    self.Pixkta = np.bitwise_and(np.copy(Pixcor),0x000E) >> 1
    print(self.Pixkta)
    print("\n Pixout")
    self.Pixout = np.bitwise_and(np.copy(Pixcor),0x0001)
    print(self.Pixout)
    print("\n")

    #generate ref offset map
    # pixoffref(x,y) = offsetavg + OCCrow(y) * 2**Occscalerow +OCCcol(x)* 2**Occscalecol + offset(x,y)*2**OCCscaleremnent
    # generate constant part via matrices

    rowoffmat = np.tile(rowoffsets,(coloffsets.shape[0],1)).transpose()
    coloffmat = np.tile(coloffsets,(rowoffsets.shape[0],1))

    print("\n coloffmat")
    print(coloffmat)
    print("\n rowoffmat")
    print(rowoffmat)


#    self.offsetmap = coloffmat + rowoffmat

    # dst = alpha * src1 + beta * src + gamma
    # dst = cv.addWeighted(src1, alpha, src2, beta, gamma)

    print("\n self.Scacol")
    print(self.Scacol)
    print("\n self.Scarow")
    print(self.Scarow)


    print("\n 2**self.Scacol")
    print(2**self.Scacol)
    print("\n 2**self.Scarow")
    print(2**self.Scarow)




    offsetrefmap = cv2.addWeighted(coloffmat,2**self.Scacol,rowoffmat,2**self.Scarow,self.OffsetAvg,0,dtype=cv2.CV_32S)
    print("\n offsetrefmap")
    print(offsetrefmap)



    print(self.Pixoff.shape)
    print(offsetrefmap.shape)
    print(self.Pixoff.dtype)
    print(offsetrefmap.dtype)




    self.offsetrefmap = cv2.addWeighted(self.Pixoff,2**self.Scarem,offsetrefmap,1,0,dtype=cv2.CV_32S)
    print(self.offsetrefmap)

   # zeros = np.zeros((2,Pixcor.shape[1]), dtype="uint16")
   # self.offsetrefmap = np.concatenate((self.offsetrefmap, zeros), axis=0)






    print("Kvdd: "+str(self.Kvdd)+" Vdd25: "+str(self.Vdd25)+" Kvptat: "+str(self.Kvptat)+" Ktptat: "+str(self.Ktptat)+" Gain: "+str(self.Gain))

  def correct_img(self,frame):

   #frame = np.uint16(frame)
   print(frame.dtype)
#   frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY, frame, cv2.CV_16UC1)
   print(frame.dtype)
   print("rows: "+str(frame.shape[0])+" cols: "+str(frame.shape[1]))
   # extract embbeded Data From Image RAM(0x700 - 0x73F) mapped to two rows of 32 pixels
   data = frame[24:26,0:32]
   print("data rows: "+str(data.shape[0])+" cols: "+str(data.shape[1])+" length:"+str(data.size) )
   print(binascii.hexlify(data[0:1,0:32]))
   print(binascii.hexlify(data[1:2,0:32]))
   print(data.dtype)

   #0123456789ABCDEF
   #AA######BB##CC##
   #DD######EE##FF##



   Ta_Vbe =  data[0,0] # 0x0700 2 byte pixel(25,1)
   if Ta_Vbe > 32767:
       Ta_Vbe = Ta_Vbe - 65536

   CPSP0 =   data[0,8] # 0x0708 2 byte pixel(25,8)
   Gain =    data[0,10] # 0x070A 2 byte pixel(25,10)
   if Gain > 32767:
        Gain = Gain - 65536


   Ta_PTAT = data[1,0] # 0x0720 2 byte pixel(26,1)
   if Ta_PTAT > 32767:
        Ta_PTAT = Ta_PTAT - 65536

   CPSP1 =   data[1,8] # 0x0728 2 byte pixel(26,8)
   VDDpix =  data[1,10] # 0x072A 2 byte pixel(26,10)

   #VDDpix = VDDpix * 256

   print("Ta_Vbe: "+str(Ta_Vbe)+" CPSP0: "+str(CPSP0)+" Gain: "+str(Gain)+" Ta_PTAT: "+str(Ta_PTAT)+" CPSP1:  "+str(CPSP1)+" VDDpix: "+str(VDDpix))
   # calculate Voltage VDD
   if VDDpix > 32767:
       VDDpix = VDDpix - 65536
   Vdd = 1*((VDDpix)-self.Vdd25)/self.Kvdd + 3.3


   # calculate Ambient Temperate
   dV = 1*((VDDpix)-self.Vdd25)/self.Kvdd

   Vptatart = (Ta_PTAT / (Ta_PTAT * self.Aptat + Ta_Vbe)) * (2**18)

   Ta = (((Vptatart/(1 + self.Kvptat * dV)) - self.Vptat25)/self.Ktptat)+25

   print("dV: "+str(dV)+" Vptatart: "+str(Vptatart)+" Aptat: "+str(self.Aptat))

   # calculate Gain
   Kgain = self.Gain/Gain

   print("Vdd: "+str(Vdd)+" Ta: "+str(Ta)+" Kgain: "+str(Kgain))
   # pixel Correction
   # pixel Gain Correction
#   kernel_size = 1
#   kernel = Kgain

   #reverse byte order
   frame = frame.byteswap()


#   frame = cv2.filter2D(frame, -1 , kernel)
   # pixel
   # pixoffref(x,y) = offsetavg + OCCrow(y) * 2**Occscalerow +OCCcol(x)* 2**Occscalecol {+ offset(x,y)*2**OCCscaleremnent}
   # dst = alpha * src1 + beta * src + gamma
   # dst = cv.addWeighted(src1, alpha, src2, beta, gamma)



   print(frame.shape)
   print(self.offsetrefmap.shape)


   frame = cv2.addWeighted(frame[0:24,0:32],Kgain,self.offsetrefmap,1,0,dtype=cv2.CV_16U)

   # add images
   frame = np.hstack((frame, self.Pixoff*2**10))
   frame = np.hstack((frame, self.Pixalp*2**10))
   frame = np.hstack((frame, self.Pixkta*2**13))
   frame = np.hstack((frame, self.Pixout*2**16))

   return frame

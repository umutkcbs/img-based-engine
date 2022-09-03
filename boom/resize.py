import os
import cv2
import glob
import time
import numpy as np
from PIL import ImageGrab

imglist = glob.glob("*.png")

for img in imglist:
    imgadi = img
    img = cv2.imread(img, -1)
    img = np.array(img)
    img = cv2.resize(img, (100, 100))
    cv2.imwrite(imgadi, img)
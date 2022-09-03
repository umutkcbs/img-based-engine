import cv2
import math
import time
import ctypes
import random
import keyboard
import numpy as np
from pygame import mixer
from scipy import ndimage

mixer.init()
mixer.music.load("the_rock.mp3")

cycle = 0
gameState = True

def overlay_image_alpha(img, img_overlay, x, y, alpha_mask):
    """
    Overlay `img_overlay` onto `img` at (x, y) and blend using `alpha_mask`.

    `alpha_mask` must have same HxW as `img_overlay` and values in range [0, 1].
    """
    # Image ranges
    y1, y2 = max(0, y), min(img.shape[0], y + img_overlay.shape[0])
    x1, x2 = max(0, x), min(img.shape[1], x + img_overlay.shape[1])

    # Overlay ranges
    y1o, y2o = max(0, -y), min(img_overlay.shape[0], img.shape[0] - y)
    x1o, x2o = max(0, -x), min(img_overlay.shape[1], img.shape[1] - x)

    # Exit if nothing to do
    if y1 >= y2 or x1 >= x2 or y1o >= y2o or x1o >= x2o:
        return

    # Blend overlay within the determined ranges
    img_crop = img[y1:y2, x1:x2]
    img_overlay_crop = img_overlay[y1o:y2o, x1o:x2o]
    alpha = alpha_mask[y1o:y2o, x1o:x2o, np.newaxis]
    alpha_inv = 1.0 - alpha

    img_crop[:] = alpha * img_overlay_crop + alpha_inv * img_crop
    return img_crop

def rotation(image, angleInDegrees):
    h, w = image.shape[:2]
    img_c = (w / 2, h / 2)

    rot = cv2.getRotationMatrix2D(img_c, angleInDegrees, 1)

    rad = math.radians(angleInDegrees)
    sin = math.sin(rad)
    cos = math.cos(rad)
    b_w = int((h * abs(sin)) + (w * abs(cos)))
    b_h = int((h * abs(cos)) + (w * abs(sin)))

    rot[0, 2] += ((b_w / 2) - img_c[0])
    rot[1, 2] += ((b_h / 2) - img_c[1])

    outImg = cv2.warpAffine(image, rot, (b_w, b_h), flags=cv2.INTER_LINEAR)
    return outImg


crosshair = cv2.imread("target.png", cv2.IMREAD_UNCHANGED)
crosshair = np.array(crosshair)
crosshair = cv2.resize(crosshair, (100, 100))

crater = cv2.imread("crater.png", cv2.IMREAD_UNCHANGED)
crater = np.array(crater)
crater = cv2.resize(crater, (100, 100))

Px, Py = 512, 512 # 800,50
aci = 0
hiz = 7

beep = cv2.imread('err.jpg')
beep = np.array(beep)

mapp = cv2.imread("ada.png")
mapp = np.array(mapp)
#mapp = cv2.rectangle(mapp, (0,0), (1024, 1024), (0,0,255), 30)
defaultMap = mapp.copy()

mappMask = cv2.imread("adamask.png", 0)
defaultMappMask = mappMask.copy()

road = np.zeros((1024,1024,1), np.uint8)

bomblist = []
collision = np.zeros((1024, 1024, 1), np.uint8)
#collision = cv2.rectangle(collision, (0,0), (1024, 1024), (255), 30)
collision = mappMask

def generate():
    for i in range(30):
        x = random.randint(0, 1024)
        y = random.randint(0, 1024)
        startTime = cycle + random.randint(10, 300)
        explosion = 0

        coordinates = [x, y, startTime, explosion];bomblist.append(coordinates)

generate()

def move():
    global Px, Py
    Px = Px + int(int(cos * hiz) / 1)
    Py = Py - int(int(sin * hiz) / 1)
def left():
    global aci
    aci += 10
    if aci > 360:
        aci = (aci - 360)
def right():
    global aci
    aci -= 10
    if aci < 0:
        aci = (360 - aci)

while True:
    #global mapp
    #map, road = renderBomb()
    for i in range(len(bomblist)):
        x = bomblist[i][0]
        y = bomblist[i][1]
        if bomblist[i][2] < cycle and bomblist[i][2] + 20 > cycle:
            #map = cv2.circle(map, (x, y), 50, (0,0,255), -1)
            alpha_mask = crosshair[:, :, 3] / 255.0
            mapp = mapp[:, :, :3].copy()
            img_overlay = crosshair[:, :, :3]
            overlay_image_alpha(mapp, img_overlay, x, y, alpha_mask)
            #road = cv2.circle(collision, (x+50, y+50), 50, 255, -1)
        #elif bomblist[i][2] + 20 <= cycle and bomblist[i][3] == 0:
        #    mapp[y:y+100, x:x+100] = defaultMap[y:y+100, x:x+100]

        if bomblist[i][2] + 20 <= cycle and bomblist[i][3] == 0:
            if cycle - bomblist[i][2] < 36:
                bum = cv2.imread(f'boom/{(cycle - bomblist[i][2])}.png', -1)
                alpha_mask = bum[:, :, 3] / 255.0
                mapp = mapp[:, :, :3].copy()
                img_overlay = bum[:, :, :3]
                overlay_image_alpha(mapp, img_overlay, x, y, alpha_mask)
                road = cv2.circle(collision, (x+50, y+50), 50, 255, -1)
            
            else:
                bomblist[i][3] = 1
                alpha_mask = crater[:, :, 3] / 255.0
                mapp = mapp[:, :, :3].copy()
                img_overlay = crater[:, :, :3]
                overlay_image_alpha(mapp, img_overlay, x, y, alpha_mask)
                road = cv2.circle(collision, (x+50, y+50), 50, 255, -1)
        if cycle - bomblist[i][2] == 36:
            mixer.music.play()

    if cycle % 100 == 0:
        mapp = defaultMap
        road = cv2.imread("adamask.png", 0)
        collision = cv2.imread("adamask.png", 0)
        generate()


    car = cv2.imread('c2.png', cv2.IMREAD_UNCHANGED)
    car = np.array(car)
    car = cv2.resize(car, (50, 50))

    if keyboard.is_pressed("a"):
        left()
    if keyboard.is_pressed("d"):
        right()
    #if keyboard.is_pressed("w"):
    #    move()


    #print(road[y, x])
    #road = cv2.circle(road, (x, y), 5, (0))
    #cv2.imshow('yol', road)
    cos = math.cos(math.radians(aci))
    sin = math.sin(math.radians(aci))
    move()


    #img_result = cv2.putText(mapp, str(cycle), (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 0, (0,0,0), 10)
    car = ndimage.rotate(car, aci)
    alpha_mask = car[:, :, 3] / 255.0
    img_result = mapp[:, :, :3].copy()
    img_overlay = car[:, :, :3]
    overlay_image_alpha(img_result, img_overlay, Px, Py, alpha_mask)
    img_result = cv2.putText(img_result, str(cycle), (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 5, (0,0,0), 10)
    #cv2.imshow('MAP', img_result) #cv2.resize(img_result, (1200,600))
    #cv2.imshow('A', road)

    if road[Py+25, Px+25] == 255:
        ctypes.windll.user32.MessageBoxW(0, str(cycle), "Score:", 16)
        break

    try:
        camera = img_result[(Py - 150):(Py + 200), (Px - 150):(Px + 200)]
        #it = ImageTransformer(camera, (500,500))a
        #camera = it.rotate_along_axis(theta=0, phi=0, gamma=0, dx=5, dy=0, dz=0)
        cv2.imshow("cam", cv2.resize(camera, (1024,1024)))
    except:
        camera = np.zeros((100,100,3), np.uint8)
        camera = cv2.putText(camera, "TURN", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 7)
        camera = cv2.putText(camera, "BACK", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 7)
        cv2.imshow("cam", cv2.resize(camera, (1024,1024)))

    cycle += 1

    cv2.waitKey(1)
    time.sleep(0.005)
    """
        Press "q" to exit
    """
    if keyboard.is_pressed("q"):
        cv2.destroyAllWindows()
        break

import mediapipe as mp
import numpy as np
import time
import math
import cv2
import handTrackModule as ht

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

cam = cv2.VideoCapture(0)
cam.set(3, 1280)
cam.set(4, 720)
pTime = 0
cTime = 0
detector = ht.handDetector(detectionCon=0.7)


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]

volBar = 400
volPer = 0


while True:
    success, frame = cam.read()
    frame = detector.findHands(frame=frame)
    lmList = detector.findPosition(frame, draw=False)
    if len(lmList) != 0:
        # print(lmList[4], lmList[8])
        ttX, ttY = lmList[4][1], lmList[4][2]
        itX, itY = lmList[8][1], lmList[8][2]
        cX, cY = (ttX + itX) // 2 , (ttY + itY) // 2

        cv2.circle(frame, (ttX, ttY), 13, (0, 0, 255), cv2.FILLED)
        cv2.circle(frame, (itX, itY), 13, (0, 0, 255), cv2.FILLED)
        cv2.line(frame, (ttX, ttY), (itX, itY), (255, 0, 255), 2)
        cv2.circle(frame, (cX, cY), 13, (0, 255, 0), cv2.FILLED)

        length = math.hypot(itX - ttX, itY - ttY)
        # print(length)

        # Hand Range : 25 - 240
        # pycaw volume range : -65 - 0

        vol = np.interp(length, [25, 240], [minVol, maxVol])
        volBar = np.interp(length, [25, 240], [400, 150])
        volPer = np.interp(length, [25, 240], [0, 100])
        print(int(length), vol)
        volume.SetMasterVolumeLevel(vol, None)

        if length < 22:
            cv2.circle(frame, (cX, cY), 13, (255, 0, 0), cv2.FILLED)

    cv2.rectangle(frame, (50, 150), (85, 400), (255, 0, 0), 3)
    cv2.rectangle(frame, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
    cv2.putText(frame, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX,
                1, (0, 0, 255), 3)

    cv2.putText(frame, 'Hand Gesture', (30, 20), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
    cv2.imshow('Live Stream', frame)

    if cv2.waitKey(1) & 0xff == ord('s'):
        break

cam.release()
cv2.destroyAllWindows()


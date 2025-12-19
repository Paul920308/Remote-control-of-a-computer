import math
import cv2
import mediapipe as mp
import time
import Fingerangle
import json
#import tkinter as tk
cv2.ocl.setUseOpenCL(True)
angle=Fingerangle

with open('data.txt', 'w') as file:
    pass

class HandDetector:

    def __init__(self, staticMode=False, maxHands=2, modelComplexity=1, detectionCon=0.4, minTrackCon=0.7):
        self.staticMode = staticMode #靜態模式
        self.modelComplexity = modelComplexity #模型複雜性
        self.maxHands = maxHands #最大手數
        self.detectionCon = detectionCon #檢測置信度
        self.minTrackCon = minTrackCon #最低追蹤置
        self.mpHands = mp.solutions.hands #手部偵測模組
        self.hands = self.mpHands.Hands(static_image_mode=self.staticMode,
                                        max_num_hands=self.maxHands,
                                        model_complexity=modelComplexity,
                                        min_detection_confidence=self.detectionCon,
                                        min_tracking_confidence=self.minTrackCon)
        self.mpDraw = mp.solutions.drawing_utils #繪製手部輪廓的函數
        self.pTime = 0 #previous time
        self.cTime = 0 #current time
        self.results = {} 
        self.tipIds = [4, 8, 12, 16, 20] # 指尖點位
        
        #cap = cv2.VideoCapture(0)

    def findHands(self, img, draw=True, flipType=True, handposition=True, box=True, Htext=True, fps=True, 
                  specific_point = {},Alonehand=True):
        """ draw=是否要繪製出手， flipType=鏡頭是否翻轉， handposition=是否繪製出點位， box=是否繪製出方框， Htext=是否顯示左右手， fps=是否顯示FPS
            specific_point=你要放大的點"""
        current_line_count = 0
        hand_roiA = None
        myHand={}
        #myHand=None
        # new_width, new_height = 640, 360 # 減小像素量，縮小3倍
        # img_small = cv2.resize(img, (new_width, new_height)) # 重新調整像素
        img_small_upsampled = cv2.pyrDown(img) #  進行下採樣
        # imgRGB = cv2.cvtColor(img_small_upsampled, cv2.COLOR_BGR2RGB)  # 轉換色彩由BGR轉RGB, 使用了下採樣
        imgRGB = cv2.cvtColor(img_small_upsampled, cv2.COLOR_BGR2RGB) #BGR轉成RGB
        self.result = self.hands.process(imgRGB) #用hands處理來自imgRGB的圖像
        allHands = [] #初始化為一個空的列表，存儲圖像中所有手部的資訊
        h, w, c = img.shape #圖像的高度、寬度、通道數
        #print(h,w)

        if self.result.multi_hand_landmarks: #如果有偵測到手
            #myHand=[]
            for handType, handLms in zip(self.result.multi_handedness, self.result.multi_hand_landmarks): #handType判斷左右手，handLms是手上點座標
                #myHand = {} # 存储手部方框
                mylmList = [] # 存储X,Y,Z座標
                xList = [] # 存储X座標
                yList = [] # 存储Y座標
                zList = [] # 存储z座標
                for i,lm in enumerate(handLms.landmark): # i為手上的點位 lm為座標
                    px, py, pz = int(lm.x * w), int(lm.y * h), int(lm.z * w)
                    mylmList.append([px, py, pz]) # append是指附加值
                    xList.append(px)
                    yList.append(py)
                    zList.append(pz)
                    
                    if handposition: #顯示出手上所有的點位
                        cv2.putText(img, str(i), (px-25, py), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2, cv2.LINE_AA) 
                    if i in specific_point: #放大特定點，是用set格式
                        cv2.circle(img, center=(px,py), radius=10, color=(0, 0, 255), thickness=cv2.FILLED)
                        #print(i, px, py)
                
                #with open('data.txt', 'a') as file:
                finger_angle = angle.hand_angle(mylmList)
                    #json.dump(finger_angle, file)# 將 Python 列表轉換為 JSON 字符串，然後追加到文件
                    #file.write('\n')  # 換行，以便每個數組都保存在新的一行
                # 取得當前行數
                #with open('data.txt', 'r') as file:
                    #current_line_count = sum(1 for line in file)
                #print(f"已經寫入 {current_line_count} 行資料。")
                text = angle.hand_pos(finger_angle) 
                cv2.putText(img, text, (30,450), cv2.FONT_HERSHEY_PLAIN, 10, (0, 255, 0), 5, cv2.LINE_AA) 

                xmin, xmax = min(xList), max(xList) #左上，右下 X軸的
                ymin, ymax = min(yList), max(yList) #左上，右下 Y軸的
                boxW, boxH = xmax - xmin, ymax - ymin #寬度和高度
                bbox = xmin, ymin, boxW, boxH #邊界框
                cx, cy = bbox[0] + (bbox[2] // 2), bbox[1] + (bbox[3] // 2) #中心點(xmin+(boxw//2)),(ymin+(boxH//2))
                cv2.circle(img, center=(cx,cy), radius=10, color=(255, 0, 0), thickness=cv2.FILLED)
                if Alonehand:
                    hand_roiA = img[bbox[1] - 20:bbox[1] + bbox[3] + 20, bbox[0] - 20:bbox[0] + bbox[2] + 20]
               
                
                #cx, cy = myHand["center"]
                #pyautogui.moveTo(cx,cy,5)


                myHand["lmList"] = mylmList #列表
                myHand["bbox"] = bbox #方框
                myHand["center"] = (cx, cy) #中心
                
                #cx, cy = myHand["center"]
                
                if flipType:#是否進行了翻轉
                    if handType.classification[0].label == "Left": #如果進行了翻轉，將手的類型取反
                        myHand["type"] = "Right"
                    
                    else:
                        myHand["type"] = "Left"
                    
                else: #如果沒有進行翻轉，直接使用手的類型
                        myHand["type"] = handType.classification[0].label
                allHands.append(myHand) #將手的類型儲存到列表中

                if draw: #畫手線的
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS) 
                    #self.mpDraw中的drawing_utils參數() 

                if box: #畫框
                    cv2.rectangle(img, (bbox[0] - 20, bbox[1] - 20),(bbox[0] + bbox[2] + 20, bbox[1] + bbox[3] + 20),(255, 0, 255), 2, cv2.LINE_AA) 
                     # (xmin(左上X軸的) - 20, ymin(左上Y軸的) - 20), (xmin(左上X軸的) + boxW(xmax - xmin) +20), (ymin(左上Y軸的) + boxH(ymax - ymin) + 20), 顏色, 粗細
                #hand_roi = img[bbox[1] - 20:bbox[1] + bbox[3] + 20, bbox[0] - 20:bbox[0] + bbox[2] + 20]
                    
                if Htext: #顯示左或右手
                    cv2.putText(img, myHand["type"], (bbox[0] - 30, bbox[1] - 30), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 2, cv2.LINE_AA) 
                    # (xmin(左上X軸的)-30,ymin(左上Y軸的)),字型樣式，字體大小，字體顏色，字體粗細  
                
        if fps:
            self.cTime = time.time() 
            fps = 1/(self.cTime-self.pTime)
            self.pTime=self.cTime
            cv2.putText(img, f"FPS:{int(fps)}" ,(30,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3) #顯示FPS , 轉換成int, 設定位置, 字體, , 顏色, 大小 
        return allHands, img, hand_roiA, myHand, current_line_count
    
    def fingersUp(self, myHand):
        """
        Finds how many fingers are open and returns in a list.
        Considers left and right hands separately
        :return: List of which fingers are up
        """
        fingers = []
        myHandType = myHand["type"]
        myLmList = myHand["lmList"]
        #if self.results.multi_hand_landmarks:
            # Thumb
        #print(myLmList,(myLmList[self.tipIds[0]][0],myLmList[self.tipIds[0]][1]))
        if myHandType == "Right":
            if myLmList[self.tipIds[0]][0] > myLmList[self.tipIds[0] - 1][0]:
                fingers.append(1)
            else:
                fingers.append(0)
        else:
            if myLmList[self.tipIds[0]][0] < myLmList[self.tipIds[0] - 1][0]:
                fingers.append(1)
            else:
                fingers.append(0)

        # 4 Fingers
        for id in range(1, 5):
            if myLmList[self.tipIds[id]][1] < myLmList[self.tipIds[id] - 2][1]:
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers
    
    def findDistance(self, myHand, img=None,finger1_index=0, finger2_index=1, color=(255, 0, 255), scale=5):
        
        myLmList = myHand["lmList"]
        # 獲取大拇指和食指的座標
        x1, y1, z1 = myLmList[self.tipIds[finger1_index]]
        x2, y2, z2 = myLmList[self.tipIds[finger2_index]]
        # x1, y1, z1 = (myLmList[self.tipIds[0]][0],myLmList[self.tipIds[0]][1],myLmList[self.tipIds[0]][2])
        # x2, y2, z2 = (myLmList[self.tipIds[1]][0],myLmList[self.tipIds[1]][1],myLmList[self.tipIds[1]][2])
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2 # 中心點位置
        length = round(math.hypot(x2 - x1, y2 - y1),2) # 畫兩點之間的線
        z=abs((z1+z2)//1.5) # 距離
        #print(z)
        #print(round(z//length, 3))
        # if z//length < -1:
        #     print("併攏" ,z//length)
        
        info = (x1, y1, x2, y2, cx, cy)
        #pyautogui.moveRel(x2, y2, duration = 1.5)
        
        if img is not None:
            cv2.putText(img, f"dfs: {z}",(30,250), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3) # Distance from screen
            cv2.putText(img, f"left: {length}",(30,300), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3) # length
            cv2.circle(img, (x1, y1), scale, color, cv2.FILLED) # 第一點
            cv2.circle(img, (x2, y2), scale, color, cv2.FILLED) # 第二點
            cv2.line(img, (x1, y1), (x2, y2), color, max(1, scale)) # 畫線
            cv2.circle(img, (cx, cy), scale, color, cv2.FILLED) # 中心點
            #pyautogui.moveRel(x2, y2, duration = 1.5)

        return length, info
    
    def findMiddleAndIndexDistance(self, myHand, img=None):
        myLmList = myHand["lmList"]

        # 確保有足夠的關鍵點
        if len(myLmList) < 3:
            return 0  # 若關鍵點不足，返回0

        # 獲取中指和食指的座標
        x1, y1 = myLmList[self.tipIds[1]][0], myLmList[self.tipIds[1]][1]  # 食指
        x2, y2 = myLmList[self.tipIds[2]][0], myLmList[self.tipIds[2]][1]  # 中指

        # 計算距離
        length = round(math.hypot(x2 - x1, y2 - y1), 2)

        if img is not None:
            cv2.putText(img, f"right: {length}",(30,350), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3) # length
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2  # 中心點位置
            cv2.circle(img, (x1, y1), 5, (0, 255, 0), cv2.FILLED)  # 食指
            cv2.circle(img, (x2, y2), 5, (0, 0, 255), cv2.FILLED)  # 中指
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 2)  # 連接食指和中指的線

        return length


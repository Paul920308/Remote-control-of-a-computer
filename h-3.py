import cv2
import tkinter as tk
from TEXE02 import HandDetector
from Test_UI_1 import HandApp
import pyautogui
import time
from HMC import Gesture

mouse_clicked = False
right_mouse_clicked = False
zoomed_out = False
zoomed_in=False
start_time = None


def setup_camera(cap):
    """設置攝像頭屬性"""
    screen_width, screen_height = pyautogui.size()
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, screen_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, screen_height)
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

def create_window():
    """創建顯示窗口"""
    cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Image", 960,540)

def handle_camera_error():
    """處理攝像頭錯誤並顯示錯誤窗口"""
    error_window = tk.Tk()
    error_window.title('錯誤 目前鏡頭不可用')
    error_window.geometry('600x50')
    label = tk.Label(error_window, text="無法使用鏡頭，按關閉以結束程式", font=('Arial', 18))
    label.pack()
    error_window.mainloop()

def update_window_size(current_width, current_height):
    """檢查並更新窗口大小"""
    new_width, new_height = cv2.getWindowImageRect("Image")[2:4]
    if (new_width, new_height) != (current_width, current_height):
        current_width, current_height = new_width, new_height
        new_height = int(current_width / (16 / 9))  # 維持寬高比
        cv2.resizeWindow("Image", current_width, new_height)
    return current_width, new_height


def process_frame(img, app, detector, gesture):
    """處理每一幀並檢測手部"""
    global mouse_clicked, start_time

    draw_hand_status = app.get_toggle_function("draw_hand")()
    flip_camera_status = app.get_toggle_function("flip_camera")()
    draw_handposition_status = app.get_toggle_function("draw_handposition")()
    draw_box_status = app.get_toggle_function("draw_box")()
    show_hand_text_status = app.get_toggle_function("show_hand_text")()
    show_fps_status = app.get_toggle_function("show_fps")()
    specific_point_status = app.get_specific_point()

    hands, img, hand_roiA, myHand, current_line_count = detector.findHands(
        img,
        draw=draw_hand_status,
        flipType=flip_camera_status,
        handposition=draw_handposition_status,
        box=draw_box_status,
        Htext=show_hand_text_status,
        fps=show_fps_status,
        specific_point=specific_point_status,
    )

    if myHand:
        fingers = detector.fingersUp(myHand)
        cv2.putText(img, str(fingers), (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)
        length, info = detector.findDistance(myHand, img)
        
        # 計算中指和食指的距離
        middle_index_length = detector.findMiddleAndIndexDistance(myHand, img)
        # 使用 Gesture 類處理手勢操作
        gesture.handle_mouse_clicks(fingers, length, middle_index_length)

        # 獲取手指的中心位置
        x, y = myHand['center']
        screen_width, screen_height = pyautogui.size()
        # 將座標轉換為螢幕座標
        x = int((screen_width - x*2) * screen_width  / img.shape[1])
        y = int(y * screen_height / img.shape[0])
        pyautogui.moveTo(x, y)  # 移動滑鼠
         # 計算食指和大拇指之間的距離
        length, info = detector.findDistance(myHand, img, finger1_index=0, finger2_index=1)

    return img, hand_roiA

def main_loop(app, detector, cap, root):
    """主循環，捕獲視頻流並處理每一幀"""
    gesture = Gesture()  # 創建 Gesture 類實例
    current_width, current_height = 960, 540  # 初始值
    while True:
        ret, img = cap.read()
        
        if not ret:
            handle_camera_error()
            break

        if cv2.getWindowProperty("Image", cv2.WND_PROP_VISIBLE) <= 0:
            break
        
        current_width, current_height = update_window_size(current_width, current_height)
        
        img, hand_roiA = process_frame(img, app, detector, gesture)


        cv2.putText(img, f"Resolution: {current_width} x {current_height}", (30, 200), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)

        cv2.imshow("Image", img)
        

        root.update()  # 更新 Tkinter 界面

        if cv2.waitKey(1) == 27:  # ESC key
            break

    cv2.destroyAllWindows()
    cap.release()

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)

    setup_camera(cap)
    create_window()
    detector = HandDetector()
    
    root = tk.Tk()
    app = HandApp(root)
    root.title("Hand Detector-1 App")

    try:
        main_loop(app, detector, cap, root)
    finally:
        root.destroy()
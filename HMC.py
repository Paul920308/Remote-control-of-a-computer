import time
import pyautogui

class Gesture:
    def __init__(self):
        self.status = {
            'mouse_clicked': False,
            'right_mouse_clicked': False,
            'zoomed_out': False,
            'zoomed_in': False,
            'start_time': None
        }

    def handle_mouse_clicks(self, fingers, length, middle_index_length):
        """處理滑鼠點擊事件和縮放操作"""
        # 處理左鍵點擊
        if 30 < length < 90 and fingers == [1, 1, 0, 0, 0]:  # 當拇指和食指靠近時觸發點擊
            if not self.status["mouse_clicked"]:
                self.status["mouse_clicked"] = True  # 設置滑鼠左鍵已被點擊
                self.status["start_time"] = time.time()  # 開始計時
                print("滑鼠左鍵被點擊")
            else:
                elapsed_time = time.time() - self.status["start_time"]  # 計算已經經過的時間
                if elapsed_time >= 1:
                    pyautogui.mouseDown()  # 按下滑鼠左鍵不放
        else:
            if self.status["mouse_clicked"]:  # 如果滑鼠左鍵已經點擊且手指分開
                elapsed_time = time.time() - self.status["start_time"]  # 計算已經經過的時間
                if elapsed_time < 1:
                    pyautogui.click()  # 進行單擊操作
                    print("滑鼠左鍵釋放")
                self.status["mouse_clicked"] = False  # 重置滑鼠左鍵點擊狀態
                self.status["start_time"] = None  # 重置計時器

        # 處理右鍵點擊
        if 30 < middle_index_length < 50 and fingers == [0, 1, 1, 0, 0]:  # 當食指和中指靠近時觸發右鍵點擊
            if not self.status["right_mouse_clicked"]:
                self.status["right_mouse_clicked"] = True  # 設置滑鼠右鍵已被點擊
                pyautogui.click(button='right')  # 進行右鍵點擊操作
                print("滑鼠右鍵被點擊")
        else:
            self.status["right_mouse_clicked"] = False  # 重置右鍵點擊狀態

        # 處理縮小操作
        if fingers == [0, 1, 1, 1, 0]:  # 當食指、中指和無名指舉起時進行縮小操作
            if not self.status["zoomed_out"]:
                pyautogui.hotkey('ctrl', '-')  # 使用 Ctrl + - 縮小瀏覽器
                self.status["zoomed_out"] = True  # 標記為已縮小
        else:
            self.status["zoomed_out"] = False  # 重置縮小狀態

        # 處理放大操作
        if fingers == [0, 1, 1, 1, 1]:  # 當食指、中指、無名指和小指舉起時進行放大操作
            if not self.status["zoomed_in"]:
                pyautogui.hotkey('ctrl', '+')  # 使用 Ctrl + + 放大瀏覽器
                self.status["zoomed_in"] = True  # 標記為已放大
        else:
            self.status["zoomed_in"] = False  # 重置放大狀態

        # 處理音量增大
        if fingers == [1, 0, 0, 0, 1]:  # 6
            pyautogui.hotkey('volumeup')  # 假設這個命令可以放大音量
            time.sleep(1)  # 避免重複觸發，暫停 1 秒

        # 處理音量減小
        if fingers == [1, 1, 1, 0, 0]:  # 8
            pyautogui.hotkey('volumedown')  # 假設這個命令可以減小音量
            time.sleep(1)  # 暫停 1 秒以避免重複觸發

        return fingers

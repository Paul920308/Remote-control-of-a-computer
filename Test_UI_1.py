# ui
import tkinter as tk
from tkinter import ttk
import json


class HandApp:
    def __init__(self, root):
        """
        初始化應用程序界面，使用 Tkinter 建立按鈕和選擇框來控制手部檢測的各種功能
        :param root: 根窗口
        """
        self.root = root  # 設置根窗口
        # self.root.title("Hand Detector-1 App")  # 可選擇為根窗口設置標題
        self.button_frame = ttk.Frame(root)  # 創建按鈕框架
        self.button_frame.pack()  # 添加按鈕框架到根窗口
        self.load_config()  # 加載配置文件中的設置

        button_style = ttk.Style()  # 初始化按鈕樣式

        # 創建各種功能的切換按鈕
        self.toggle_show_hand_text_button = self.create_toggle_button("顯示左右手", "show_hand_text")  # 顯示左右手的按鈕
        self.toggle_draw_handposition_button = self.create_toggle_button("繪製點位", "draw_handposition")  # 繪製手部點位的按鈕
        self.toggle_draw_box_button = self.create_toggle_button("繪製方框", "draw_box")  # 繪製手部邊框的按鈕
        self.toggle_flip_camera_button = self.create_toggle_button("翻轉鏡頭", "flip_camera")  # 翻轉攝像頭的按鈕
        self.toggle_show_fps_button = self.create_toggle_button("切換顯示FPS", "show_fps")  # 顯示 FPS 的按鈕
        self.toggle_draw_hand_button = self.create_toggle_button("繪製手", "draw_hand")  # 繪製手部的按鈕

        # 創建框架來容納 Checkbutton
        self.checkbox_frame = ttk.Frame(root)  # 創建 Checkbutton 的框架
        self.checkbox_frame.pack()  # 添加 Checkbutton 框架到根窗口
        # 手是從 0 開始到 20，總共 21 個點
        # 創建 21 個 Checkbutton
        self.checkbutton_vars = []  # 管理每個 Checkbutton 的選中狀態
        self.checkbuttons = []  # 保存所有 Checkbutton
        for i in range(21):
            # 使用 Frame 包裝每個 Checkbutton
            checkbutton_frame = ttk.Frame(self.checkbox_frame)
            checkbutton_frame.grid(row=i // 7, column=i % 7, padx=5, pady=5, sticky="w")  # 將 Checkbutton 安排到網格中

            # 初始化時都設定為上次選中的狀態
            checkbutton_var = tk.BooleanVar(value=i in self.specific_point)  # 設定初始值
            checkbutton = ttk.Checkbutton(checkbutton_frame, text=f"手上點位 {i}", variable=checkbutton_var,
                                          command=lambda i=i, var=checkbutton_var: self.update_specific_point(i,
                                                                                                              var))  # 創建 Checkbutton
            checkbutton.pack(side=tk.LEFT)  # 將 Checkbutton 添加到框架中

            self.checkbuttons.append(checkbutton)  # 保存 Checkbutton
            self.checkbutton_vars.append(checkbutton_var)  # 保存 Checkbutton 的狀態變量

        # 開始主循環
        self.update_image()  # 更新影像

    def create_toggle_button(self, label, attribute):
        """
        創建切換按鈕以控制特定功能的開關狀態
        :param label: 按鈕顯示的標籤
        :param attribute: 對應的功能屬性
        :return: 創建的按鈕
        """
        toggle_function = self.get_toggle_function(attribute)  # 獲取切換功能
        button = ttk.Button(self.button_frame, text=f"{label}:{'開' if getattr(self, attribute) else '關'}",
                            command=lambda: self.toggle_button(button, attribute, label, toggle_function))  # 創建按鈕
        # 使用 grid 進行按鈕排列，每行最多容納 3 個按鈕
        button.grid(row=len(self.button_frame.winfo_children()) % 2, column=len(self.button_frame.winfo_children()) % 3,
                    padx=5, pady=5, sticky="n")
        return button

    def toggle_button(self, button, attribute, label, command):
        """
        切換按鈕的狀態
        :param button: 按鈕對象
        :param attribute: 要切換的屬性
        :param label: 按鈕的標籤
        :param command: 按鈕對應的功能
        """
        setattr(self, attribute, not getattr(self, attribute))  # 切換屬性值
        button["text"] = f"{label}:{'開' if getattr(self, attribute) else '關'}"  # 更新按鈕的文本
        # print(f"{attribute} is now: {getattr(self, attribute)}")  # 可選的打印當前狀態
        self.save_config()  # 保存配置

    # 更新函數
    def update_image(self):
        """
        使用 after 方法持續調用自身，以達到更新界面的效果
        """
        self.root.after(10, self.update_image)  # 每隔 10 毫秒調用一次自身進行更新

    # 取得狀態函數
    def get_toggle_function(self, attribute):
        """
        根據屬性名稱獲取對應的功能
        :param attribute: 功能屬性名稱
        :return: 功能對應的函數
        """
        if attribute == "draw_hand":
            return lambda: self.draw_hand
        elif attribute == "flip_camera":
            return lambda: self.flip_camera
        elif attribute == "draw_handposition":
            return lambda: self.draw_handposition
        elif attribute == "draw_box":
            return lambda: self.draw_box
        elif attribute == "show_hand_text":
            return lambda: self.show_hand_text
        elif attribute == "show_fps":
            return lambda: self.show_fps

    # 更新勾選值函數
    def update_specific_point(self, value, var):
        """
        更新特定點位的選擇狀態
        :param value: 點位索引
        :param var: BooleanVar 對象，表示點位的選中狀態
        """
        if var.get():  # 如果選中
            self.specific_point.add(value)  # 添加到特定點列表
        else:  # 如果取消選中
            self.specific_point.discard(value)  # 從特定點列表中移除

    def get_specific_point(self):
        """
        獲取當前選中的特定點位
        :return: 選中的特定點位集合
        """
        return self.specific_point

    def save_config(self):
        """
        保存當前的配置信息到文件中
        """
        fileName = "Lens parameters.config"  # 配置文件名稱
        jsonString = {
            "draw_hand": self.draw_hand,
            "flip_camera": self.flip_camera,
            "draw_handposition": self.draw_handposition,
            "draw_box": self.draw_box,
            "show_hand_text": self.show_hand_text,
            "show_fps": self.show_fps,
            "specific_point": list(self.specific_point),
        }  # 構建配置字典
        with open(fileName, "w") as f:  # 打開文件寫入模式
            json.dump(jsonString, f)  # 將配置保存為 JSON 格式

    def load_config(self):
        """
        從配置文件中加載配置信息
        """
        try:
            with open("Lens parameters.config", "r") as f:  # 打開配置文件讀取模式
                config = json.load(f)  # 加載配置
                self.draw_hand = config.get("draw_hand", True)  # 獲取是否繪製手的設置
                self.flip_camera = config.get("flip_camera", False)  # 獲取是否翻轉攝像頭的設置
                self.draw_handposition = config.get("draw_handposition", True)  # 獲取是否繪製手部點位的設置
                self.draw_box = config.get("draw_box", True)  # 獲取是否繪製手部邊框的設置
                self.show_hand_text = config.get("show_hand_text", True)  # 獲取是否顯示手的類型的設置
                self.show_fps = config.get("show_fps", True)  # 獲取是否顯示 FPS 的設置
                self.specific_point = set(config.get("specific_point", {}))  # 獲取選中的特定點位
        except FileNotFoundError:  # 如果配置文件不存在
            # 使用默認值
            self.draw_hand = True
            self.flip_camera = False
            self.draw_handposition = True
            self.draw_box = True
            self.show_hand_text = True
            self.show_fps = True
            self.specific_point = set()
            self.save_config()  # 保存默認配置

# 單獨測試時才需要以下三行代碼
# root = tk.Tk()
# app = HandApp(root)
# root.mainloop()

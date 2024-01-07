import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from PIL import ImageDraw
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def getGrayDiff(img, currentPoint, tmpPoint):
    return abs(int(img[currentPoint.y, currentPoint.x]) - int(img[tmpPoint.y, tmpPoint.x]))

def selectConnects():
    connects = [Point(-1, -1), Point(0, -1), Point(1, -1), Point(1, 0), Point(1, 1), Point(0, 1), Point(-1, 1), Point(-1, 0)]
    return connects

def regionGrow(img, seeds, thresh):
    m, n = img.shape
    seedMark = np.zeros([m, n])
    seedList = []
    for seed in seeds:
        seedList.append(seed)
    label = 1
    connects = selectConnects()
    while (len(seedList) > 0):
        currentPoint = seedList.pop(0)
        seedMark[currentPoint.y, currentPoint.x] = label
        for i in range(8):
            tmpX = currentPoint.x + connects[i].x
            tmpY = currentPoint.y + connects[i].y
            if tmpX < 0 or tmpY < 0 or tmpX >= m or tmpY >= n:
                continue
            grayDiff = getGrayDiff(img, currentPoint, Point(tmpX, tmpY))
            if grayDiff < thresh and seedMark[tmpY, tmpX] == 0:
                seedMark[tmpY, tmpX] = label
                seedList.append(Point(tmpX, tmpY))
    return seedMark

class RegionGrowingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Region Growing")

        self.image_path = None
        self.image = None
        self.img_label = tk.Label(self.root)
        self.img_label.pack()

        self.seed_points = []
        self.threshold = tk.IntVar()
        self.threshold.set(5)

        self.load_button = tk.Button(self.root, text="Chọn ảnh", command=self.load_image)
        self.load_button.pack()
        self.seed_mode = False
        self.seed_button = tk.Button(self.root, text="Chọn điểm hạt giống", command=self.toggle_seed_mode)
        self.seed_button.pack()

        self.threshold_frame = tk.Frame(self.root)
        self.threshold_frame.pack()

        self.threshold_label = tk.Label(self.threshold_frame, text="Nhập ngưỡng:")
        self.threshold_label.pack(side=tk.LEFT)
        
        self.segment_button = tk.Button(self.root, text="Phân đoạn ảnh", command=self.segment_image)
        self.segment_button.pack()
        
        self.threshold_entry = tk.Entry(self.threshold_frame, textvariable=self.threshold)
        self.threshold_entry.pack(side=tk.LEFT)
        
        self.clear_button = tk.Button(self.root, text="Xóa điểm hạt giống", command=self.clear_seed_points)
        self.clear_button.pack()
        self.seed_points = []
        self.drawn_points = []
        self.canvas = tk.Canvas(self.root)
        self.canvas.pack()

        self.img_label.bind("<Button-1>", self.add_seed_point)

    def load_image(self):
        self.image_path = filedialog.askopenfilename()
        if self.image_path:
            self.image = cv2.imread(self.image_path, 0)
            self.show_image()

    def show_image(self):
        img = cv2.cvtColor(cv2.imread(self.image_path), cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img = ImageTk.PhotoImage(img)
        self.img_label.config(image=img)
        self.img_label.image = img

    def toggle_seed_mode(self):
        self.seed_mode = not self.seed_mode
        if self.seed_mode:
           self.seed_button.config(text="Đang chọn điểm hạt giống")
        else:
            self.seed_button.config(text="Chọn điểm hạt giống")

    def add_seed_point(self, event):
        if self.seed_mode:
            x, y = event.x, event.y
            self.seed_points.append(Point(x, y))

            img = cv2.cvtColor(cv2.imread(self.image_path), cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            draw = ImageDraw.Draw(img)
            for point in self.seed_points:
                draw.ellipse((point.x - 2, point.y - 2, point.x + 2, point.y + 2), outline="red", width=2)
            img = ImageTk.PhotoImage(img)
            self.img_label.config(image=img)
            self.img_label.image = img

    def segment_image(self):
        if self.image is not None and len(self.seed_points) > 0:
            seeds = self.seed_points
            thresh = self.threshold.get()
            img_result = regionGrow(self.image, seeds, thresh)

            cv2.imshow("Segmented Image", img_result)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
    def clear_seed_points(self):
        for point in self.drawn_points:
            self.canvas.delete(point)
        self.seed_points = []
        self.drawn_points = []

        img = cv2.cvtColor(cv2.imread(self.image_path), cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img = ImageTk.PhotoImage(img)
        self.img_label.config(image=img)
        self.img_label.image = img
root = tk.Tk()
app = RegionGrowingApp(root)
root.mainloop()

import re

import cv2
import numpy as np
import pyocr
from PIL import Image


class Tesseract:
    def __init__(self):
        pyocr.tesseract.TESSERACT_CMD = "C:/Program Files/Tesseract-OCR/tesseract.exe"
        self.tool = pyocr.get_available_tools()[0]

    def ocr(self, img_cv2):
        img = Image.fromarray(img_cv2)
        if img is None:
            return None

        try:
            # tesseract_layoutは下記のリンクを参照
            # https://web-lh.fromation.co.jp/archives/10000061001
            result = self.tool.image_to_string(
                img,
                lang="eng",
                builder=pyocr.builders.TextBuilder(tesseract_layout=7)
            )
            print("text", result)
            try:
                return int(re.sub(r"\D", "", result))
            except ValueError:
                print("ValueError")
                return 0
        except cv2.error:
            print("cv2.error")
            return 0


def extract_black(img):
    lower = np.array([16, 30, 74])
    upper = np.array([44, 107, 162])

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    return cv2.inRange(hsv, lower, upper)


# CLAHEと二値化を行う関数
def clahe_binarization(img):
    # グレースケール変換
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # CLAHE処理
    clahe = cv2.createCLAHE(clipLimit=7.0, tileGridSize=(8, 8))
    clahe_img = clahe.apply(gray)

    # 二値化
    _, binary_img = cv2.threshold(clahe_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return binary_img


def main():
    video_path = "data/processed/propeller/p2000_2/video_for_ocr.mp4"
    cap = cv2.VideoCapture(video_path)

    tesseract = Tesseract()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = frame[1097:1311, 218:776]
        # cv2.imwrite("crop.jpg", frame)
        # HSVで抽出
        # frame = extract_black(frame)
        # CLAHEと二値化
        frame = clahe_binarization(frame)
        text = tesseract.ocr(frame)

        cv2.imshow("frame", frame)
        if cv2.waitKey() & 0xff == 27:
            break

    cap.release()


if __name__ == "__main__":
    main()

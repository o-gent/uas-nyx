from typing import List
from nyx import target_recognition
from nyx.k_nearest_recognition import ocr
from nyx.utils import display, logger
import os
import cv2
import time

dataset = r"G:\targets"

video = cv2.VideoCapture(r'G:\GH010123.MP4')

results = []
for image in os.listdir(dataset):
    img = cv2.imread(os.path.join(dataset, image))
    results.append(target_recognition.find_targets(img))

success = True
count = 0
results = []
while success:
    try:
        _, image = video.read() 
        print(f'Read a new frame: {count}')
        r = target_recognition.find_targets(image)
        logger.info(r)
        results.append(r)
    except KeyboardInterrupt:
        raise
    except:
        logger.info("frame failed")
    count += 1

# post process
results_filtered:List[List[target_recognition.ImageRecognitionResult]] = [result for result in results if not []]
for result in results_filtered:
    image = result.cropped
    t = str(time.time()).split(".")[0] + "-" + str(time.time()).split(".")[1]
    cv2.imwrite(time.strftime(f"targets/%m-%d-%H:%M:%S-{t}.jpg"),image)

# # ocr
# opts = nn.Opts(
#     image_folder="./targets",
#     saved_model="./TPS-ResNet-BiLSTM-Attn-case-sensitive.pth",
#     imgH=
#     )






# image = r"C:\Users\olive\Downloads\images\07 02 17_27_55 1625243275-037503.jpg"
# img = cv2.imread(image)
# imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# imgBlurred = cv2.GaussianBlur(imgGray, (5, 5), 0)
# img_thresh = cv2.adaptiveThreshold(
#     imgBlurred,
#     255,
#     cv2.ADAPTIVE_THRESH_MEAN_C, 
#     cv2.THRESH_BINARY,
#     199,
#     -25
# )
# display(img_thresh)
from nyx import target_recognition
from nyx.k_nearest_recognition import ocr
from nyx.utils import display
import os
import cv2
import nyx.nn_ocr as nn

dataset = r"C:\Users\olive\Downloads\images"

results = []
for image in os.listdir(dataset):
    img = cv2.imread(os.path.join(dataset, image))
    results.append(target_recognition.find_targets(img))

# post process
results_filtered = [result for result in results if not []]
for result in results_filtered:
    r = result[0]
    image = r.cropped
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
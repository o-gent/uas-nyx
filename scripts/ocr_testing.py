from nyx import target_recognition
from nyx.k_nearest_recognition import ocr
from nyx.utils import display
import os
import cv2

dataset = r"C:\Users\olive\Downloads\images"

o = ocr.K_nearest_recognition()
method = o.k_nearest

for image in os.listdir(dataset):
    img = cv2.imread(os.path.join(dataset, image))
    #utils.display(img)
    print(target_recognition.findCharacters(img, method))


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
import logging
import math
import os
import sys
import time
from typing import List

import cv2
import numpy as np
from numpy.lib.function_base import average

from perspective import four_point_transform
from utils import resizeWithAspectRatio, display

MIN_AREA = 3000
EPSILON_MULTIPLY = 0.01
MIN_AREA_OCR = 100
RESIZED_WIDTH = 30
RESIZED_HEIGHT = 30
SCALE_FACTOR = 5


logger = logging.getLogger("ocr")
fh = logging.FileHandler(f"logs/ocr_{time.strftime('%Y%m%d-%H%M%S')}.log")
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(ch)
logger.addHandler(fh)


class DataContour:
    """ """
    intX = 0  # bounding rect top left corner x location
    intY = 0  # bounding rect top left corner y location
    intWidth = 0  # bounding rect width
    intHeight = 0  # bounding rect height
    floatArea = 0.0  # area of contour

    def checkIfContourIsValid(self):
        """ should have more conditions """
        if self.floatArea < MIN_AREA_OCR:
            return False
        return True


class Square:
    """ store square attributes """
    x1,x2,x3,x4 = 0,0,0,0 
    y1,y2,y3,y4 = 0,0,0,0
    len12, len23, len34, len41 = 0,0,0,0
    lengths: List[int] = []


def calcDistance(x1, y1, x2, y2):
    param1 = (x2 - x1)
    param2 = (y2 - y1)
    inside = (param1 * param1) + (param2 * param2)
    return math.sqrt(inside)


def cropMinAreaRect(img, rect):  # idk how this works but it does
    # rotate img
    angle = rect[2]
    rows, cols = img.shape[0], img.shape[1]
    M = cv2.getRotationMatrix2D((cols / 2, rows / 2), angle, 1)
    imgRot = cv2.warpAffine(img, M, (cols, rows))

    # rotate bounding box
    box = cv2.boxPoints(rect)
    pts = np.int0(cv2.transform(np.array([box]), M))[0]
    pts[pts < 0] = 0

    # crop
    img_crop = imgRot[
        pts[1][1]:pts[0][1],
        pts[1][0]:pts[2][0]
    ]

    return img_crop


def approxContour(contour):
    # fit contour to a simpler shape
    # accuracy is based on EPSILON_MULTIPLY
    epsilon = EPSILON_MULTIPLY * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)
    return approx


def getRectangle(npaContour) -> DataContour:
    """ given contours, calculate rectangle information """
    dataContour = DataContour()
    dataContour.intX, dataContour.intY, dataContour.intWidth, dataContour.intHeight = cv2.boundingRect(npaContour)
    dataContour.floatArea = cv2.contourArea(npaContour)
    if dataContour.checkIfContourIsValid():
        return dataContour
    else:
        raise Exception("contour invalid")


def resize(dataContour, img_thresh):
    """ convert from cropped orginal resolution to low res """
    # converts to from minimum bounding square to minimum bounding rectangle
    imgROI = img_thresh[
             dataContour.intY: dataContour.intY + dataContour.intHeight,
             dataContour.intX: dataContour.intX + dataContour.intWidth
             ]
    imgROIResized = cv2.resize(imgROI, (RESIZED_WIDTH, RESIZED_HEIGHT))
    npaROIResized = np.float32(imgROIResized.reshape((1, RESIZED_WIDTH * RESIZED_HEIGHT)))
    return npaROIResized


def ocr(img) -> str:
    """ given a cropped binary image of a charachter, return the charachter """
    npaContours, _npaHierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2:]

    if len(npaContours) > 1:
        raise Exception("should only have one contour here")

    dataContour = getRectangle(npaContours[0])
    resized = resize(dataContour, img)

    retval, npaResults, neigh_resp, dists = k_nearest.findNearest(resized, 3)
    return str(chr(int(npaResults[0][0])))


def getSquareLengths(approx: List[List[List[int]]]) -> Square:
    """ extract lengths from the co-ordinates """
    
    s = Square()
    
    s.x1, s.y1 = approx[0][0]
    s.x2, s.y2 = approx[1][0]
    s.x3, s.y3 = approx[2][0]
    s.x4, s.y4 = approx[3][0]

    s.len12 = calcDistance(s.x1, s.y1, s.x2, s.y2)
    s.len23 = calcDistance(s.x2, s.y2, s.x3, s.y3)
    s.len34 = calcDistance(s.x3, s.y3, s.x4, s.y4)
    s.len41 = calcDistance(s.x4, s.y4, s.x1, s.y1)

    s.lengths = [s.len12, s.len23, s.len34, s.len41]
    s.lengths.sort()

    return s


def isSquare(s: Square) -> bool:
    """ """
    return ((s.lengths[3] - s.lengths[0]) / s.lengths[3]) < 0.1


def filterContours(contours):
    """ """
    squareIndexes = []

    # filter contours
    for i, contour in enumerate(contours):  # for each of the found contours
        if cv2.contourArea(contour) > MIN_AREA:
            approx = approxContour(contour)
            if len(approx) == 4:
                #s = getSquareLengths(approx)
                squareIndexes.append(i)
    
    return squareIndexes


def filterImage(image: np.ndarray) -> np.ndarray:
    """ 
    given an image, return an image which shows only white 
    Uses K means
    """

    # downsample, and convert
    height, width = image.shape[:2]
    img = cv2.resize(image, (round(width / SCALE_FACTOR), round(height / SCALE_FACTOR)), interpolation=cv2.INTER_AREA)
    img_blurred = cv2.GaussianBlur(img, (5,5), 0)
    Z = img_blurred.reshape((-1,3))
    Z = np.float32(Z)

    # it's possible this criteria could be optimised
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    K = 2
    _ret, label, center=cv2.kmeans(Z,K,None,criteria,1,cv2.KMEANS_RANDOM_CENTERS)

    # convert back into uint8 and make original image
    center = np.uint8(center)
    res = center[label.flatten()]
    res2 = res.reshape((img.shape))

    # convert to black and white
    imgGray = cv2.cvtColor(res2, cv2.COLOR_BGR2GRAY)
    _thresh, imgf = cv2.threshold(imgGray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    return imgf


def calculateColour(image) -> List[float]:
    """ given a target, find the target colour """
    pixels = np.float32(image.reshape(-1, 3))
    n_colors = 2
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
    flags = cv2.KMEANS_RANDOM_CENTERS
    _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
    _, counts = np.unique(labels, return_counts=True)
    dominant = palette[np.argmax(counts)]
    return dominant.tolist()


def find_characters(image: np.ndarray):
    """ return the charachters present in the given image """
    
    imgGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    imgBlurred = cv2.GaussianBlur(imgGray, (5, 5), 0)
    _ret, img_thresh = cv2.threshold(imgBlurred, 180, 255, cv2.THRESH_BINARY)
    
    #img_thresh = filterImage(image)

    contours, hierarchy = cv2.findContours(img_thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2:]

    squareIndexes = filterContours(contours)
    
    # for i in squareIndexes:
    #     cv2.drawContours(image, contours[i], -1, (0, 255, 0), 3)
    #     display(image)
    
    results = []
    for index in squareIndexes:
        hier = hierarchy[0][index]
        if hier[3] in squareIndexes:  # if a square has a parent that is also a square
            target_contour = approxContour(contours[index])

            # find the square colour
            colour_cropped = four_point_transform(image, target_contour.reshape(4,2))
            colour = calculateColour(colour_cropped)
            
            display(colour_cropped)

            # deal with the perspective distortion
            cropped = four_point_transform(img_thresh, target_contour.reshape(4,2))

            #display(cropped)

            # TODO shave 10 pixels off from all edges to remove the frame..
            cropped_further = cropped[10:-10, 10:-10]

            #display(cropped_further)

            start = time.time()
            char = ocr(cropped_further)
            print(f"{time.time() - start} to process letter {char}")

            results.append([char, colour])

    return results


def load_model():
    """ load data sources and train model """
    try:
        npaClassifications = np.loadtxt('classifications.txt', np.float32)
        npaFlattenedImages = np.loadtxt('imageData.txt', np.float32)
    except:
        sys.exit('text files not present')

    npaClassifications = npaClassifications.reshape((npaClassifications.size, 1))
    k_nearest = cv2.ml.KNearest_create()
    k_nearest.train(npaFlattenedImages, cv2.ml.ROW_SAMPLE, npaClassifications)
    return k_nearest


if __name__ == '__main__':
    k_nearest = load_model()
    files = [f for f in os.listdir('./scaled/')]
    iterations = 1
    
    start = time.time()

    for i in range(iterations):
        for f in files:
            img = cv2.imread('./scaled/' + f)
            print(f"found charachters {find_characters(img)} in image")

    print(f"average time taken per image {(time.time() - start) / (len(files) * iterations)}")

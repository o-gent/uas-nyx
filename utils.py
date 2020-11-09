import cv2


def resizeWithAspectRatio(image, width=None, height=None, inter=cv2.INTER_AREA):
    """ return resized image """
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    return cv2.resize(image, dim, interpolation=inter)


def display(img) -> None:
    """ display 800px wide image and wait for enter """
    img = resizeWithAspectRatio(img, width=800)
    cv2.imshow("", img)
    cv2.waitKey(0)

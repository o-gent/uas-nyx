import cv2
import numpy as np


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


def imageOverlay(background, overlay, x, y, width):
    """ overlay an image and set the width of the overlay """
    
    dim = (width, width)
    # resize image
    overlay = cv2.resize(overlay, dim, interpolation = cv2.INTER_AREA)

    background_width = background.shape[1]
    background_height = background.shape[0]

    if x >= background_width or y >= background_height:
        return background

    h, w = overlay.shape[0], overlay.shape[1]

    if x + w > background_width:
        w = background_width - x
        overlay = overlay[:, :w]

    if y + h > background_height:
        h = background_height - y
        overlay = overlay[:h]

    if overlay.shape[2] < 4:
        overlay = np.concatenate(
            [
                overlay,
                np.ones((overlay.shape[0], overlay.shape[1], 1), dtype = overlay.dtype) * 255
            ],
            axis = 2,
        )

    overlay_image = overlay[..., :3]
    mask = overlay[..., 3:] / 255.0

    background[y:y+h, x:x+w] = (1.0 - mask) * background[y:y+h, x:x+w] + mask * overlay_image

    return background

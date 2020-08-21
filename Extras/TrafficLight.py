import cv2
import numpy as np


class TrafficLight:
    def __init__(self, visualize=False):
        # Range of Colours
        self.lower_red1 = np.array([0, 100, 100])
        self.upper_red1 = np.array([10, 255, 255])

        self.lower_red2 = np.array([160, 100, 100])
        self.upper_red2 = np.array([180, 255, 255])

        self.lower_green = np.array([40, 50, 50])
        self.upper_green = np.array([90, 255, 255])

        self.lower_yellow = np.array([15, 150, 150])
        self.upper_yellow = np.array([35, 255, 255])

        self.size = None
        self.visualize = visualize

    def light_detection(self, box, image):
        """
        Light detector for a traffic light.

        :param box: boundingbox of the traffic light detected
        :param image:  image where the traffic light is placed
        :return: string of "Green", "Red", "Yellow" if this color is detected, "Error" if 2 or more colors detected or "None" if nothing detected
        """
        (startX, startY, endX, endY) = box
        cropped_frame = image[startY:endY, startX:endX]
        hsv = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2HSV)
        mask1 = cv2.inRange(hsv, self.lower_red1, self.upper_red1)
        mask2 = cv2.inRange(hsv, self.lower_red2, self.upper_red2)
        maskg = cv2.inRange(hsv, self.lower_green, self.upper_green)
        masky = cv2.inRange(hsv, self.lower_yellow, self.upper_yellow)
        maskr = cv2.add(mask1, mask2)

        self.size = cropped_frame.shape

        # Hough transformation applied to circles
        # Circular masked applied to each object (red, greeen, yellow)
        r_circles = cv2.HoughCircles(maskr, cv2.HOUGH_GRADIENT, 1, 80, param1=50, param2=10, minRadius=0, maxRadius=30)
        g_circles = cv2.HoughCircles(maskg, cv2.HOUGH_GRADIENT, 1, 60, param1=50, param2=10, minRadius=0, maxRadius=30)
        y_circles = cv2.HoughCircles(masky, cv2.HOUGH_GRADIENT, 1, 30, param1=50, param2=5, minRadius=0, maxRadius=30)

        red = self.detect(r_circles, maskr, "Red", cropped_frame)
        green = self.detect(g_circles, maskg, "Green", cropped_frame)
        yellow = self.detect(y_circles, masky, "Yellow", cropped_frame)

        result = int(red) + int(green) + int(yellow)
        if result > 1:
            return "Error"
        if red:
            return "Red"
        elif yellow:
            return "Yellow"
        elif green:
            return "Green"
        else:
            return "None"

    def detect(self, circles, mask, text, image):
        """
        Algorithm to detect the colour of the light

        :param circles: circles detected though the Hough transform
        :param mask: Mask of the circle
        :param text: Text to write on the image
        :param image: image where the traffic light is seen
        :return:
        """
        r = 5
        bound = 4.0 / 10

        if circles is not None:
            y_circles = np.uint16(np.around(circles))

            for i in y_circles[0, :]:
                if i[0] > self.size[1] or i[1] > self.size[0] or i[1] > self.size[0] * bound:
                    continue

                h, s = 0.0, 0.0
                for m in range(-r, r):
                    for n in range(-r, r):

                        if (i[1] + m) >= self.size[0] or (i[0] + n) >= self.size[1]:
                            continue
                        h += mask[i[1] + m, i[0] + n]
                        s += 1
                if h / s > 50:
                    if self.visualize:
                        cv2.circle(image, (i[0], i[1]), i[2] + 10, (0, 255, 0), 2)
                        cv2.circle(mask, (i[0], i[1]), i[2] + 30, (255, 255, 255), 2)
                        cv2.putText(image, 'YELLOW', (i[0], i[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2,
                                    cv2.LINE_AA)
                    return True
        return False

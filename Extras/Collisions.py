from math import cos, sin, sqrt, pi


class Collisions:
    def __init__(self, screen_dimensions, thresholding = 0.6):
        self.width, self.height = screen_dimensions
        self.thresholding= thresholding
        self.camera_box = [(int(self.width/2 -200), self.height), (int(self.width/2 -200), self.height-80), (int(self.width/2 +200), self.height),(int(self.width/2 +200), self.height-80)]
        self.static_names = ["traffic light", "fire hydrant", "stop sign", "parking meter", "bench"]


    def checkAllCollisions(self, camera_velocity, velocities, boxes, category):
        """
        Check the possibility of collission between all objects and driver
        :param camera_velocity: velocity of the camera in the current moment (module, angle)
        :param distances: coordinates of the distances of the objects in this determined moment
        :param velocities: velocities of the object in this determined moment (module, angle)
        :param boxes: used to determined the size of the object
        :param category: used to determine if object is static or not
        :return: dictionary with ID and all the probability of collissions
        """
        probability = {}
        for id, velocity in velocities.items():
            if velocity is None:
                continue
                probability[id] = self.checkCollission(camera_velocity, velocity, boxes[id], category[id])

            try:
                probability[id] = self.checkCollission(camera_velocity, velocity, boxes[id], category[id])
            except Exception as ex:
                print("Error while checking collissions for object :" + str(category[id]))
                print(str(ex))
                print("Velocities: "+ str(velocities))
                print("Boxes: "+ str(boxes))
                print("Category: "+ str(category))


        return probability


    def checkCollission(self, vel_cam, vel_obj, box_obj, category):
        """
        Check the possibility of collission between determined object and driver. Done in Perspective Camera View
        :param vel_cam: velocity of the camera in the current moment (module, angle)
        :param dist: coordinates of the distance of the determined object in this determined moment
        :param vel_obj: velocity of the object in this determined moment (module, angle)
        :param box_obj: used to determined the size of the object : left, bottom, right, top
        :param category: used to determine if object is static or not --> Format: categ:id
        :return: probability of collission for the determined object
        """
        # Creating a list of items from 0 to 3 seconds in 0.5 interactions
        times = [x * 0.5 for x in range(0, 7)]
        name = str(category.split(':')[0])
        static = name in self.static_names
        if static:
            vel_obj = (0,0)
            # Creating a list of items from 0 to 2 seconds in 0.5 interactions as it is static
            times = [x * 0.5 for x in range(0, 5)]

        left, bottom, right, top = box_obj
        object_box = [(left, bottom), (left, top), (right, bottom), (right, top)]

        probability = []
        for t in times:
            next_obj = self.moveObject(object_box, vel_obj, t)
            cam_obj = self.moveObject(self.camera_box, vel_cam, t)
            probability.append(self.rectangleCollission(cam_obj, next_obj))

        # Get the indices of times of the probabilities which are are over the threshold
        indixes = [probability.index(x) for x in probability if x >= self.thresholding]
        if len(indixes)>0:
            return ([probability[i] for i in indixes], [times[i] for i in indixes])
        else:
            return (max(probability), None)

    def moveObject(self, box, velocity, factor=None):
        """
        From an initial box computes the next position of a box using module velocity (compute with factor time)
        :param box: coordinates of the object --> [(left, bottom), (left, top), (right, bottom), (right, top)]
        :param velocity: (module, angle) of the veolcity of the box
        :param factor: number of times the velocity is divided by (1/time)
        :return:  next box in the time for the velocity
        """
        width, height = abs(int(box[3][0]-box[0][0])), abs(int(box[3][1]-box[0][1]))
        old_centroid = (int((box[3][0]+box[0][0])/2),int((box[3][1]+box[0][1])/2))
        new_centroid = self.final_point(old_centroid, velocity, factor)
        factor_area = self.check_area(new_centroid, old_centroid)
        new_width, new_height = sqrt(factor_area) * width, sqrt(factor_area) * height
        new_box = self.defineRectangle(new_centroid, new_width, new_height)
        return new_box

    def defineRectangle(self, centroid, width, height):
        """
        Define a rectangle from the centroid and with its width and height
        :param centroid: centroid of the rectangle
        :param width: widht of the rectangle
        :param height: height of the rectangle
        :return: new box : [(left, bottom), (left, top), (right, bottom), (right, top)]
        """
        left = int(centroid[0] - width/2)
        right = int(centroid[0] + width/2)
        top = int(centroid[1] - height/2)
        bottom = int(centroid[1] + height/2)
        return [(left, bottom), (left, top), (right, bottom), (right, top)]


    def final_point(self, point, velocity, factor=None):
        """
        From an initial point computes the velocity to the next point where should be placed if the velocity persits
        :param point: initial centroid of the object
        :param velocity: velocity of the object in this determined moment
        :return: output
        """
        if factor is None:
            factor = 1
        if type(velocity) == int:
            norm = velocity
            angle = -pi /2
        else:
            norm, angle = velocity
        x_mod = norm*cos(angle) * factor
        y_mod = norm*sin(angle) * factor
        return (int(point[0]+x_mod), int(point[1]+y_mod))

    def check_area(self, new_centr, old_centr):
        """
        Gets the factor of the area that has to become bigger
        :param new_centr: new centroid of the object
        :param old_centr: old centroid of the object
        :return: the factor of the area that needs to enlarge
        """
        new_dist = self.getDistance(new_centr)
        old_dist = self.getDistance(old_centr)
        factor_area = 2**((old_dist - new_dist)/100)
        #factor_area = old_dist/new_dist
        return factor_area

    def getDistance(self, point):
        """
        :param point: centroid of the old point
        :return: module distance to the initial camera point
        """
        dist_oldX = abs(point[0] - int(self.width/2))
        dist_oldY = abs(point[1] - int(self.height/2))
        return sqrt(dist_oldX** 2 + dist_oldY ** 2)

    def rectangleCollission(self, rect1, rect2,):
        """
        Check if both coordinates of the box are colliding in this momment
        :param rect1: coordinates of the box of the object() --> object_box = [(left, bottom), (left, top), (right, bottom), (right, top)]
        :param rect1: coordinates of the box of the object() --> object_box = [(left, bottom), (left, top), (right, bottom), (right, top)]
        :return: probability of collission for the determined object
        """
        # Vertical check
        bt_rect1 = rect1[0][1]
        tp_rect1 = rect1[1][1]
        bt_rect2 = rect2[0][1]
        tp_rect2 = rect2[1][1]

        if max(bt_rect1, bt_rect2) == bt_rect2:
            gap_vertical = tp_rect2 - bt_rect1
        else:
            gap_vertical = tp_rect1 - bt_rect2

        # Horitzontal check
        l_rect1 = rect1[0][0]
        r_rect1 = rect1[2][0]
        l_rect2 = rect2[0][0]
        r_rect2 = rect2[2][0]

        if min(l_rect1, l_rect2) == l_rect2:
            gap_horitzontal = l_rect1 - r_rect2
        else:
            gap_horitzontal = l_rect2 - r_rect1

        return 1.5 * self.prob_function(gap_horitzontal, gap_vertical)

    def prob_function(self, x, y):
        return 2 ** (-(2 ** (x / 100) + 2 ** (y / 100)))

import cv2
import numpy as np
import cv2 as cv
from mss import mss
import time
from sklearn.cluster import KMeans
import keyboard
import GUI
import serial

"""
PLAN
screencap at adjustable rate
blur image
break into submatrix sections (1 per led)
find prominent color for each section (kmeans)
assemble colors into 2D array
send array (and brightness) to arduino (serial communication)

CHANGES
maybe quantize or artificially lower resolution to decrease processing time (resize command?)

60 leds = 60 sections

810 x 360mm = 2340mm perimeter / 60 = 39mm per led

810 / 39 = 21 leds per width
360 / 39 = 9 leds per height

(0,0)
|------------------------------|
|                              |
|                              |    
|                              |
|------------------------------|
                             (3440, 1440)


(0,0) (1,0) (2,0) (3,0) (4,0) (5,0) (6,0) (7,0) (8,0) (9,0) (10,0) (11,0) (12,0) (13,0) (14,0) (15,0) (16,0) (17,0) (18,0) (19,0) (20,0)
(0,1)                                                                                                                             (20,1)
(0,2)                                                                                                                             (20,2)
(0.3)                                                                                                                             (20,3)
(0.4)                                                                                                                             (20,4)
(0.5)                                                                                                                             (20,5)
(0.6)                                                                                                                             (20,6)
(0.7)                                                                                                                             (20,7)
(0,8) (1,8) (2,8) (3,8) (4,8) (5,8) (6,8) (7,8) (8,8) (9,8) (10,8) (11,8) (12,8) (13,8) (14,8) (15,8) (16,8) (17,8) (18,8) (19,8) (20,8)


"""


def find_dominant_color(image, k=3):  # new hopefully better cv2.kmeans
    # Reshape the image to a 2D array of pixels
    pixels = image.reshape((-1, 3))
    pixels = np.float32(pixels)

    # Define criteria for k-means clustering
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)

    # Perform k-means clustering
    _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

    # Find the most dominant color (the cluster with the most pixels)
    dominant_label = np.argmax(np.bincount(labels.flatten()))
    dominant_color = centers[dominant_label].astype(int)

    return dominant_color


def find_color(inmat):  # old sklearn kmeans
    pixels = inmat.reshape(-1, 3)

    kmeans = KMeans(n_clusters=k, max_iter=5)  # max_iter default to 300
    kmeans.fit(pixels)

    dominant = kmeans.cluster_centers_[np.argmax(np.bincount(kmeans.labels_))]

    return dominant


bounding_box = {'top': 200, 'left': 0, 'width': 1720, 'height': 900}

screen_size = (1720, 900)
scale_factor = 20 #  60
scaled_size = (int((screen_size[0] / scale_factor)), int(screen_size[1] / scale_factor))

period = 1 / 10  # frame cap rate, taking reciprocal of desired caps / second

# Assumes square blur, must be odd
BLUR_SCALE = int(19)

sct = mss()

curr = time.time()
last_time = curr
start_time = curr

k = 1

array_width = 21  # 21 leds
array_height = 9  # 9 leds

color_array = [[(0, 0, 0) for i in range(array_height)] for j in range(array_width)]
color_array = np.array(color_array)
result2 = color_array.tolist()

#  ser = serial.Serial('COM3', 9600)  # Serial Communication port, baud rate (must be same in uC code)


"""def send_color_data(array):
    array_str = ';'.join(['|'.join(map(lambda x: ','.join(map(str, x)), row)) for row in
                          array])  # convert 2D numpy tuple array to string

    ser.write(array_str.encode())


def read_uC_data():
    incoming_data = ser.readline().decode().strip()
    print("From Arduino: ", incoming_data)

def simple_test(data):
    #  data += "\n"
    ser.write(data.encode())"""

def horizontal_region(mat):
    for i in range(array_width):
        x1 = (scaled_size[0] / array_width) * i  # starting x pixel coordinate for submat
        x2 = ((scaled_size[0] / array_width) * (i + 1)) - 1  # ending x pixel coordinate for submat
        # This solution assumes each region will extend from center axis to edge of display
        new_high = mat[0:int((scaled_size[1] / 2)),
                   int(x1):int(x2)]  # Assuming submat = mat[y1:21, x1:x2] as per google
        new_low = mat[int((scaled_size[1] / 2)):scaled_size[1], int(x1):int(x2)]

        color_array[i][0] = find_dominant_color(new_high)
        color_array[i][array_height - 1] = find_dominant_color(new_low)


def vertical_region(mat):
    for i in range(array_height):
        y1 = (scaled_size[1] / array_height) * i  # starting x pixel coordinate for submat
        y2 = ((scaled_size[1] / array_height) * (i + 1)) - 1  # ending x pixel coordinate for submat
        # This solution assumes each region will extend from center axis to edge of display
        new_left = mat[int(y1):int(y2), 0:int((scaled_size[0] / 2))]  # !!!
        new_right = mat[int(y1):int(y2), int((scaled_size[0] / 2)):scaled_size[0]]  # !!!

        color_array[0][i] = find_dominant_color(new_left)
        color_array[array_width - 1][i] = find_dominant_color(new_right)


def draw_horizontal_regions(mat, array):
    for i in range(array_width):
        x1 = (screen_size[0] / array_width) * i  # starting x pixel coordinate for submat
        x2 = ((screen_size[0] / array_width) * (i + 1)) - 1  # ending x pixel coordinate for submat
        color = array[i][0]
        cv2.rectangle(mat, (int(x1), 0), (int(x2), 100), (int(color[0]), int(color[1]), int(color[2])), -1)
        color = array[i][array_height - 1]
        cv2.rectangle(mat, (int(x1), screen_size[1] - 100), (int(x2), screen_size[1]), (int(color[0]), int(color[1]), int(color[2])), -1)

    #  cv2.imshow("mat", mat)
    return mat


def draw_vertical_regions(mat, array):
    for i in range(array_height):
        y1 = (screen_size[1] / array_height) * i  # starting x pixel coordinate for submat
        y2 = ((screen_size[1] / array_height) * (i + 1)) - 1  # ending x pixel coordinate for submat
        color = array[0][i]
        cv2.rectangle(mat, (0, int(y1)), (100, int(y2)), (int(color[0]), int(color[1]), int(color[2])), -1)
        color = array[array_width - 1][i]
        cv2.rectangle(mat, (screen_size[0] - 100, int(y1)), (screen_size[0], int(y2)), (int(color[0]), int(color[1]), int(color[2])), -1)

    #  cv2.imshow("mat", mat)
    return mat


#  GUI.open_window()

while True:
    #  simple_test("blue")
    print("Sent \n")
    #  time.sleep(1)

    curr = time.time()

    #  read_uC_data()

    sct_img = sct.grab(bounding_box)

    mat1 = cv.cvtColor(np.array(sct_img), cv.COLOR_RGB2BGR)
    mat2 = cv.cvtColor(mat1, cv.COLOR_BGR2RGB)

    small_mat = cv2.resize(mat2, scaled_size)

    horizontal_region(small_mat)
    vertical_region(small_mat)
    result2 = color_array.tolist()

    draw_horizontal_regions(mat2, color_array)
    draw_vertical_regions(mat2, color_array)

    cv2.imshow("Test", mat2)

    last_time = curr

    #  send_color_data(color_array)

    #  print("Sent data \n")

    time.sleep(period)

    cv2.waitKey(1)

    if keyboard.is_pressed('c') and keyboard.is_pressed('c'):
        #  print("new array start \n")
        #  print(color_array)
        #  print("\n new array end")
        cv.destroyAllWindows()
        break


import cv2
import math
import os
import numpy as np
# import IAMLTools
import matplotlib.pyplot as plt


def main():
    data, video, image_map = load_data()

    hgm = load_or_create_homography(video, image_map)
    i = 0

    while True:
        ret, image = video.read()
        if not ret:
            break

        draw_rectangles(image, data, i)

        # <Exercise 4.2 (Task 2.3)>
        # TODO
        center = get_center(data['legs'], i)
        print("center")
        print(center)
        apply_homography(hgm, center)
        # print('center in while', center[0])
        # print(type(center[0]))
        # cv2.rectangle(image_map, center[0], (70,70), (0, 255, 0), 3)
        # cv2.circle(image_map, tuple(center.astype(int)), 200, (255, 0, 0))
        print(center)
        # <Exercise 4.2 (Task 2.4)>

        # Frame counter and display code
        i += 1
        cv2.imshow("map", image_map)
        # TODO Is it a sequence of frames? Yes
        cv2.imshow("image", image)
        key = cv2.waitKey(1)
        if key == ord("q"):
            break

    video.release()


def get_points_from_mouse(image1, image2, N=4):
    """
    get_points_from_mouse(image1, image2, N=4) -> points_source, points_destination

    Gets corresponding points in image1, image2 manually from user input.


    Returns: A list of corresponding points in the source and destination image.
    Parameters: N >= 4 is the number of expected mouse points in each image,
                when N < 0: then the corners of image "image1" will be used as input and thus only 4 mouse clicks are         needed in image "image2".

    Usage: Use left click to select a point and right click to remove the most recently selected point.
    """
    # Vector with all input images.
    images = []
    images.append(cv2.cvtColor(image1.copy(), cv2.COLOR_BGR2RGB))
    images.append(cv2.cvtColor(image2.copy(), cv2.COLOR_BGR2RGB))

    # Vector with the points selected in the input images.
    mousePoints = []

    # Control the number of processed images.
    firstImage = 0

    # When N < 0, then the corners of image "image1" will be used as input.
    if N < 0:
        # Force 4 points to be selected.
        N = 4
        firstImage = 1
        m, n = image1.shape[:2]

        # Define corner points from image "image1".
        mousePoints.append([(0, 0), (n, 0), (n, m), (0, m)])

    # Check if there is the minimum number of needed points to estimate the homography.
    if math.fabs(N) < 4:
        N = 4
        print("At least 4 points are needed!!!")

    # Make a pylab figure window.
    fig = plt.figure(1)

    # Get the correspoding points from the input images.
    for i in range(firstImage, 2):
        # Setup the pylab subplot.
        plt.subplot(1, 2, i + 1)
        plt.imshow(images[i])
        plt.axis("image")
        plt.title("Click " + str(N) + " times in this image.")
        fig.canvas.draw()

        # Get mouse inputs.
        mousePoints.append(fig.ginput(N, -1))

        # Draw selected points in the processed image.
        for point in mousePoints[i]:
            cv2.circle(images[i], (int(point[0]), int(
                point[1])), 3, (0, 255, 0), -1)
        plt.imshow(images[i])
        fig.canvas.draw()

    # Close the pylab figure window.
    plt.close(fig)

    # Convert to OpenCV format.
    points_source = np.array([[x, y] for (x, y) in mousePoints[0]])
    points_destination = np.array([[x, y] for (x, y) in mousePoints[1]])

    # Calculate the homography.
    return points_source, points_destination


def to_homogeneous(points):
    # Convert column vectors to row vectors
    if len(points.shape) == 1:
        points = points.reshape((*points.shape, 1))
    return np.vstack((points, np.ones((1, points.shape[1]))))


def to_euclidean(points):
    return points[:2] / points[2]


def load_data():
    """Loads the tracking data, the input video, and the map image.
    """
    # TODO How did you fund the points in trackingdata?
    filename = "inputs/trackingdata.dat"
    data = np.loadtxt(filename)
    data = {
        'body': data[:, :4],
        'legs': data[:, 4:8],
        'all': data[:, 8:]
    }

    videofile = "inputs/ITUStudent.mov"
    video = cv2.VideoCapture(videofile)

    imagename = "inputs/ITUMap.png"
    image_map = cv2.imread(imagename)

    return data, video, image_map


def load_or_create_homography(video, image_map):
    """Loads homography from file if it exists, otherwise creates a new one.
    """
    output = "outputs/homography.npy"

    # Check if saved file exists
    if os.path.isfile(output):
        # <Exercise 4.2 (Task 1.4)>
        # pass # Replace this
        return np.load('outputs/homography.npy', allow_pickle=True)


    else:
        ret, image_ground = video.read()
        if not ret:
            raise IOError("Could not read frame from Video.")

        # <Exercise 4.2 (Task 1.1)>
        p_source, p_destination = get_points_from_mouse(image_ground, image_map)

        # <Exercise 4.2 (Task 1.2)>
        H, _ = cv2.findHomography(p_source, p_destination) #findHomography returns a matrix using homogenous coordinates
        # <Exercise 4.2 (Task 1.3)>
        # if ! os._exists('outputs/'):
        #     os.mkdir('outputs/')

        np.save('outputs/homography', H)

        video.set(cv2.CAP_PROP_POS_FRAMES, 0)
    print("H")
    print(H)
    return H


def draw_part(image, part, color, i):
    """Draw rectangle of specific body part at time i.
    """
    cv2.rectangle(image, tuple(part[i, 0:2].astype(int)),
                  tuple(part[i, 2:4].astype(int)), color, thickness=1)


def draw_rectangles(image, data, i):
    """Draw all body parts at time i.
    """
    draw_part(image, data['body'], (0, 0, 255), i)
    draw_part(image, data['legs'], (255, 0, 0), i)
    draw_part(image, data['all'], (0, 255, 0), i)


# <Exercise 4.2 (Task 2.1)>
def get_center(part, i):
    """Returns center of body part in homogeneous coordinates.

    Parameters: part refers to a Nx4 array containing rectangle points for a specific
    body part. i refers to the frame index to fetch.
    """
    # TODO
    p_top = part[i][0:2]
    p_down = part[i][2:]

    w = p_down[0] - p_top[0]
    h = p_down[1] - p_top[1]
    print("w,h")
    print(w, h)
    f = to_homogeneous(np.array([(int(w / 2), int(h / 2))]).T)
    print("f")
    print(f)
    return f

    # return None  # Replace this
# data, video, image_map = load_data()

# print('getcenter', get_center(data['legs'], 5))

# <Exercise 4.2 (Task 2.2)>
def apply_homography(h, point):
    """Apply homography h to point."""
    print("h,p")
    print(h, point)
    #TODO
    return to_euclidean(h @ point)

    # return h @ point
    # return None  # Replace this


if __name__ == '__main__':
    main()

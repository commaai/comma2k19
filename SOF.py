import cv2 as cv
import numpy as np

def draw_trapezoid(frame, trapezoid):
    """Draw the trapezoid on the frame."""
    cv.polylines(frame, [np.array(trapezoid)], isClosed=True, color=(150, 10, 150), thickness=1)

def is_motion_inwards(point, trapezoid):
    """Check if the motion is coming inwards towards the trapezoid from the left or right."""
    pt = np.array(point, dtype=np.float32)
    # Check if the point is outside the trapezoid
    if cv.pointPolygonTest(np.array(trapezoid, dtype=np.float32), pt, False) < 0:
        # Get the x and y coordinates of the motion point
        x, y = point
        # Get the x-coordinates of the left and right boundaries of the trapezoid
        left_x, right_x = trapezoid[0][0], trapezoid[1][0]
        # Check if the point is between the left and right boundaries of the trapezoid
        if left_x < x < right_x:
            # Get the y-coordinates of the top and bottom boundaries of the trapezoid at the given x-coordinate
            top_y = np.interp(x, [trapezoid[0][0], trapezoid[1][0]], [trapezoid[0][1], trapezoid[1][1]])
            bottom_y = np.interp(x, [trapezoid[3][0], trapezoid[2][0]], [trapezoid[3][1], trapezoid[2][1]])
            # Check if the point is not above or below the trapezoid at the given x-coordinate
            if bottom_y < y < top_y:
                return True
    return False




paths = [
    '../comma2k/Chunk_1/b0c9d2329ad1606b|2018-08-17--14-55-39/7/video.hevc', # Jen's path
    '../comma2k/Chunk_2/b0c9d2329ad1606b|2018-10-09--14-06-32/10/video.hevc', #doesn't work well
    '../comma2k/Chunk_2/b0c9d2329ad1606b|2018-09-23--12-52-06/45/video.hevc', # detects all cut-ins, no false positives 
    '../comma2k/Chunk_2/b0c9d2329ad1606b|2018-10-09--15-48-37/16/video.hevc' # works well
]

my_path = paths[2]
maxCorners = 20
qualityLevel = 0.1
minDistance = 100
blockSize = 2
winsize = (15, 15)
maxLevel = 2
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 10, 0.03)

# Parameters for Shi-Tomasi corner detection minDistance defines how far side to side is required to identify the object.
feature_params = dict(maxCorners=maxCorners, qualityLevel=qualityLevel, minDistance=minDistance, blockSize=blockSize)
# Parameters for Lucas-Kanade optical flow
lk_params = dict(winSize=winsize, maxLevel=maxLevel, criteria=criteria)
# The video feed is read in as a VideoCapture object
cap = cv.VideoCapture(my_path)

# Define the trapezoid's corners
top_left = (550, 400)
top_right = (650, 400)
bottom_right = (850, 600)
bottom_left = (350, 600)
trapezoid = [top_left, top_right, bottom_right, bottom_left]

# Variable for color to draw optical flow track
color = (0, 255, 0)

# ret = a boolean return value from getting the frame, first_frame = the first frame in the entire video sequence
ret, first_frame = cap.read()
# Converts frame to grayscale because we only need the luminance channel for detecting edges - less computationally expensive
prev_gray = cv.cvtColor(first_frame, cv.COLOR_BGR2GRAY)
# Finds the strongest corners in the first frame by Shi-Tomasi method - we will track the optical flow for these corners
prev = cv.goodFeaturesToTrack(prev_gray, mask=None, **feature_params)
# Creates an image filled with zero intensities with the same dimensions as the frame - for later drawing purposes
mask = np.zeros_like(first_frame)

# Create a separate output window
cv.namedWindow("Output", cv.WINDOW_NORMAL)
cv.resizeWindow("Output", 1000, 800)

# Main loop
while(cap.isOpened()):
    # Clear the mask for drawing lines
    mask[:] = 0
    
    # ret = a boolean return value from getting the frame, frame = the current frame being projected in the video
    ret, frame = cap.read()
    if not ret:
        break

    # Converts each frame to grayscale - we previously only converted the first frame to grayscale
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    # Calculates sparse optical flow by Lucas-Kanade method
    prev = cv.goodFeaturesToTrack(prev_gray, mask=None, **feature_params)
    next, status, error = cv.calcOpticalFlowPyrLK(prev_gray, gray, prev, None, **lk_params)
    # Selects good feature points for previous position
    good_old = prev[status == 1].astype(int)
    # Selects good feature points for next position
    good_new = next[status == 1].astype(int)

    # Draw the optical flow tracks
    for i, (new, old) in enumerate(zip(good_new, good_old)):
        # Returns a contiguous flattened array as (x, y) coordinates for new point
        a, b = new.ravel()
        # Returns a contiguous flattened array as (x, y) coordinates for old point
        c, d = old.ravel()
        
        # If the motion is
        # If the motion is coming inwards towards the trapezoid
        if is_motion_inwards((a, b), trapezoid):
            # Draw the line
            mask = cv.line(mask, (a, b), (c, d), color, 2)
            # Draw the circle
            frame = cv.circle(frame, (a, b), 5, color, 3)
            
            # Additional checks to filter out noisy points
            if (0 <= a < frame.shape[1]) and (0 <= b < frame.shape[0]):
                # Mark the detected cut-in position with a red box
                cv.rectangle(frame, (a - 20, b - 20),(a + 20, b + 20), (0, 0, 255), 2)
                print("Cut-in at position:", (a, b))
                # Pause video and wait for user input
                cv.waitKey(0)

    # Overlays the optical flow tracks on the original frame
    output = cv.add(frame, mask)
    # Updates previous frame
    prev_gray = gray.copy()

    # Draw the trapezoid on the frame
    draw_trapezoid(output, trapezoid)

    # Opens a new window and displays the output frame
    cv.imshow("Output", output)
    # Frames are read by intervals of 10 milliseconds. The programs breaks out of the while loop when the user presses the 'q' key
    key = cv.waitKey(1)
    if key & 0xFF == ord('q'):
        break

# Release the VideoCapture object and close all windows
cap.release()
cv.destroyAllWindows()

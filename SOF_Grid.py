import cv2 as cv
import numpy as np

def draw_grid(frame, rows, cols):
    height, width = frame.shape[:2]
    # Calculate spacing
    gridline_width = width // cols
    gridline_height = height // rows

    # draw horizontal grid
    for i in range(1, rows):
        y = i * gridline_height
        cv.line(frame, (0, y), (width, y), (150, 10, 150), 1)
    # Vertical
    for i in range(1, cols):
        x = i * gridline_width
        cv.line(frame, (x, 0), (x, height), (150, 10, 150), 1)
        cv.putText(frame, str(i), (x + 10, 30), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

paths = [
    '../comma2k/Chunk_1/b0c9d2329ad1606b|2018-08-17--14-55-39/7/video.hevc', # Jen's path
    '../comma2k/Chunk_2/b0c9d2329ad1606b|2018-10-09--14-06-32/10/video.hevc', #doesnt work well
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
rows = 20 
cols = 20
# Variable for color to draw optical flow track
color = (0, 255, 0)
# ret = a boolean return value from getting the frame, first_frame = the first frame in the entire video sequence
ret, first_frame = cap.read()
# Converts frame to grayscale because we only need the luminance channel for detecting edges - less computationally expensive
prev_gray = cv.cvtColor(first_frame, cv.COLOR_BGR2GRAY)
# Finds the strongest corners in the first frame by Shi-Tomasi method - we will track the optical flow for these corners
# https://docs.opencv.org/3.0-beta/modules/imgproc/doc/feature_detection.html#goodfeaturestotrack
prev = cv.goodFeaturesToTrack(prev_gray, mask=None, **feature_params)
# Creates an image filled with zero intensities with the same dimensions as the frame - for later drawing purposes
mask = np.zeros_like(first_frame)

# Calculate gridline width and height
gridline_width = first_frame.shape[1] // cols
gridline_height = first_frame.shape[0] // rows

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
    draw_grid(frame, rows, cols)
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
        
        # Calculate the grid cell of the new position
        new_grid_col = min(max(0, a // gridline_width), cols - 1)
        new_grid_row = min(max(0, b // gridline_height), rows - 1)
        new_grid_cell = (new_grid_col, new_grid_row)
        
        # Calculate the column position of the new position
        new_col_position = new_grid_col
        
        # Get the column position of the old position
        old_col_position = min(max(0, c // gridline_width), cols - 1)
        
        # If both old and new column positions are not None and the feature point is in the included rows and columns
        if old_col_position is not None and new_col_position is not None:
            # Check if the feature point is in the included rows and columns
            if not (b < 7 * gridline_height or b >= 15 * gridline_height or (new_col_position <= 3 or new_col_position >= 17)):
                # Draw the line
                mask = cv.line(mask, (a, b), (c, d), color, 2)
                # Draw the circle
                frame = cv.circle(frame, (a, b), 5, color, 3)
                
                # Additional checks to filter out noisy points
                if (0 <= a < frame.shape[1]) and (0 <= b < frame.shape[0]):
                    # Check for the desired column transition
                    if (old_col_position in [7,8,11,12]) and (new_col_position in [9,10]):
                        # Mark the detected cut-in position with a red box
                        cv.rectangle(frame, (a - 20, b - 20),(a + 20, b + 20), (0, 0, 255), 2)
                        print("Cut-in at position:", (a, b), "in grid cell", new_grid_cell, "from column", old_col_position, "to column", new_col_position)
                        # Pause video and wait for user input
                        cv.waitKey(0)

    # Overlays the optical flow tracks on the original frame
    output = cv.add(frame, mask)
    # Updates previous frame
    prev_gray = gray.copy()

    # Opens a new window and displays the output frame
    cv.imshow("Output", output)
    # Frames are read by intervals of 10 milliseconds. The programs breaks out of the while loop when the user presses the 'q' key
    key = cv.waitKey(1)
    if key & 0xFF == ord('q'):
        break

# Release the VideoCapture object and close all windows
cap.release()
cv.destroyAllWindows()


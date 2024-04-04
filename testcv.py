import cv2
import numpy as np

def draw_grid(frame, rows, cols):
    height, width, = frame.shape[:2]
    #Calculate spacing
    gridline_width = width // cols
    gridline_height = height // rows

    #draw horizontal grid
    for i in range(1, rows):
        y = i * gridline_height
        cv2.line(frame, (0, y), (width, y), (0, 255, 0), 1)
    #Vertical
    for i in range(1, cols):
        x = i * gridline_width
        cv2.line(frame, (x, 0), (x, height), (0, 255, 0), 1)

#Open MP4
video_capture = cv2.VideoCapture('../comma2k/Chunk_1/b0c9d2329ad1606b|2018-07-27--06-03-57/3/video.hevc')
rows = 10
cols = 10
ret, first_frame = video_capture.read()
mask = np.zeros_like(first_frame)
prev_gray = cv2.cvtColor(first_frame, cv2.COLOR_BGR2GRAY)
mask[..., 1] = 255

#Loop frames
while True:
    if not video_capture.isOpened():
        print("error")
    #Read frames
    ret, frame = video_capture.read()
    draw_grid(frame, rows,cols)
    #convert to gray scale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #calc dense optical flow
    flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
    #compute magnitude
    magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
    #print magnitude and angle
    print("Magnitude:", magnitude)
    print("Angle:", angle)
    #set image hue
    mask[..., 0] = angle * 180 / np.pi /2
    #set image value
    mask[..., 2] = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)
    #convert hsv to rgb
    rgb = cv2.cvtColor(mask, cv2.COLOR_HSV2BGR)
    #overlay the vectors on the frame
    result = cv2.addWeighted(frame, 1, rgb, 2, 0)
    #result to see the vectors, frame to remove them.
    cv2.imshow("input", result)

    #update previous frame
    prev_gray = gray
    #Frames are read by intervals of 1 millisecond. The programs breaks out of the while loop when the user presses the "q" key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
#realese the video capture
cv2.getBuildInformation()
video_capture.release()
cv2.destroyAllWindows()
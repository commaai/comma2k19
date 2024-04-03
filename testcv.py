import cv2

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
video_capture = cv2.VideoCapture('../comma2k/Chunk_1/b0c9d2329ad1606b|2018-07-27--06-03-57/3/video.mp4')
rows = 10
cols = 10

#Loop frames
while True:
    if not video_capture.isOpened():
        print("error")
    #Read frames
    ret, frame = video_capture.read()

    #Check if frame was read
    if not ret:
        break
    draw_grid(frame, rows,cols)
    #Display frame
    cv2.imshow('Frame with grid', frame)
    #Check for key
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break
#realese the video capture
cv2.getBuildInformation()
video_capture.release()
cv2.destroyAllWindows()

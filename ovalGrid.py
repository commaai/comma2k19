import cv2

#Grid
def draw_circular_grid(frame, num_circles):
    height, width = frame.shape[:2]
    #calc center
    center = (width // 2, height // 2)
    #calc radious
    radius_increment = min(width, height) // (num_circles + 1)
    for i in range(1, num_circles +1):
        radius = i * radius_increment
        cv2.circle(frame, center, radius, (0, 255, 0), 1)

video_capture = cv2.VideoCapture('../comma2k/Chunk_1/b0c9d2329ad1606b|2018-07-27--06-03-57/3/video.mp4')
num_circles = 5
#Loop frames
while True:
    if not video_capture.isOpened():
        print("error")
    #Read frames
    ret, frame = video_capture.read()

    #Check if frame was read
    if not ret:
        break
    draw_circular_grid(frame, num_circles)
    #Display frame
    cv2.imshow('Frame with circular grid', frame)
    #Check for key
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break
#realese the video capture
cv2.getBuildInformation()
video_capture.release()
cv2.destroyAllWindows()


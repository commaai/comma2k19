import cv2
import numpy as np

# Function to draw star-shaped gridlines on a frame
def draw_star_grid(frame, stars):
    # Calculate the angle increment for each vertex
    angle_increment = 2 * np.pi / 5

    # Draw the stars
    for star in stars:
        # Get star position and size
        center_x, center_y, radius_outer = star

        # Calculate points for the outer circumference of the star
        points = []
        for i in range(5):
            angle = i * angle_increment
            x = center_x + int(radius_outer * np.cos(angle))
            y = center_y + int(radius_outer * np.sin(angle))
            points.append((x, y))
        
        # Draw lines connecting the outer circumference of the star
        for i in range(5):
            cv2.line(frame, points[i], points[(i + 2) % 5], (0, 255, 0), 1)

# Open the video file
video_capture = cv2.VideoCapture('../comma2k/Chunk_1/b0c9d2329ad1606b|2018-07-27--06-03-57/3/video.mp4')

# Define the number of stars
num_stars = 5

# Generate random positions for stars
stars = []
frame_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Define the initial radius of the outer circle
initial_radius_outer = min(frame_width, frame_height) // 8

for i in range(num_stars):
    # Set center of the star
    center_x = frame_width // 2
    center_y = frame_height // 2

    # Set radius of the outer circle, increasing gradually with index
    radius_outer = initial_radius_outer * (i + 1)

    stars.append((center_x, center_y, radius_outer))

# Loop through the frames
while True:
    # Read a frame from the video
    ret, frame = video_capture.read()

    # Check if the frame was successfully read
    if not ret:
        break

    # Draw star-shaped gridlines on the frame
    draw_star_grid(frame, stars)

    # Display the frame
    cv2.imshow('Frame with Star-shaped Grid', frame)

    # Check for key press to exit
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

# Release the video capture object and close the OpenCV windows
video_capture.release()
cv2.destroyAllWindows()
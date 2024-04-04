import cv2
import numpy as np

# Open video capture
cap = cv2.VideoCapture('../comma2k/Chunk_1/b0c9d2329ad1606b|2018-07-27--06-03-57/3/video.hevc')

# Initialize variables for previous frame and mask
ret, prev_frame = cap.read()
prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
mask = np.zeros_like(prev_frame)

while True:
    # Read current frame
    ret, frame = cap.read()
    if not ret:
        break
    
    # Convert current frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Calculate optical flow using Farneback method
    flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
    
    # Compute magnitude and angle
    magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
    
    # Create mask image
    mask[..., 1] = 255
    
    # Set image hue according to the angle
    mask[..., 0] = angle * 180 / np.pi / 2
    
    # Set image value according to the magnitude
    mask[..., 2] = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)
    
    # Convert HSV to BGR (for displaying)
    rgb = cv2.cvtColor(mask, cv2.COLOR_HSV2BGR)
    
    # Overlay motion vectors on the frame
    result = cv2.addWeighted(frame, 1, rgb, 2, 0)
    
    # Display the result
    cv2.imshow('Optical Flow', result)
    
    # Update previous frame
    prev_gray = gray
    
    # Check for 'q' key to quit
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

# Release video capture and close all windows
cap.release()
cv2.destroyAllWindows()

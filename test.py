import numpy as np
import math
import time

norm = np.linalg.norm(((0, 0), (0, 2))) > np.linalg.norm(((0, 0), (0, 1)))

print(norm)

def calculate_angle(p1, p2, p3):
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3

    # Calculate the slopes of the two lines
    slope1 = (y2 - y1) / (x2 - x1)
    slope2 = (y3 - y2) / (x3 - x2)

    # Calculate the angle between the two slopes in radians
    angle = math.atan(abs((slope1 - slope2) / (1 + slope1 * slope2)))
    angle = math.degrees(angle)
    print(angle)

    return angle

# Example initialization
player_choice = "Some choice"
hand_valid = False

while True:
    # This block will run only once when the condition is met
    if player_choice != "Nothing" and not hand_valid:
        current_time = time.time()  # Set current time only once
        hand_valid = True  # Prevent resetting current_time in future iterations

    # Print the elapsed time since current_time was set
    print(f"{time.time() - current_time:.3f}")
    
    # Simulate stopping after 5 seconds (optional, just for demonstration)
    if time.time() - current_time > 5:
        break

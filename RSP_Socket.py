import cv2
import mediapipe as mp
import random
from collections import deque
import statistics as st
import numpy as np
import math
import time
import socket


def calculate_winner(cpu_choice, player_choice):

   # Determines the winner of each round when passed the computer's and player's moves

   if player_choice == "Invalid":
       return "Invalid!"

   if player_choice == cpu_choice:
       return "Tie!"

   elif player_choice == "Rock" and cpu_choice == "Scissors":
       return "You win!"

   elif player_choice == "Rock" and cpu_choice == "Paper":
       return "CPU wins!"

   elif player_choice == "Scissors" and cpu_choice == "Rock":
       return "CPU wins!"

   elif player_choice == "Scissors" and cpu_choice == "Paper":
       return "You win!"

   elif player_choice == "Paper" and cpu_choice == "Rock":
       return "You win!"

   elif player_choice == "Paper" and cpu_choice == "Scissors":
       return "CPU wins!"

def calculate_angle(a, b, c):
   # a, b, c are points (x, y)
   ab = np.array([b[0] - a[0], b[1] - a[1]])
   bc = np.array([c[0] - b[0], c[1] - b[1]])
   
   cos_angle = np.dot(ab, bc) / (np.linalg.norm(ab) * np.linalg.norm(bc))
   angle = np.arccos(cos_angle)

   return np.degrees(angle)

def compute_fingers(hand_landmarks):

   # Coordinates are used to determine whether a finger is being held up or not
   # This is done by detemining wheter the distance between wrist and finger tip is greater than the distance between wrist and finger base
   # For the thumb it determines rather the angle between the tip and the base is greater than a treshold

   fingers_up = np.zeros(5)

   # Index Finger
   if math.dist((hand_landmarks[0][1], hand_landmarks[0][2]), (hand_landmarks[8][1], hand_landmarks[8][2])) > math.dist((hand_landmarks[0][1], hand_landmarks[0][2]), (hand_landmarks[5][1], hand_landmarks[5][2])):
       fingers_up[1] = 1
   else:
       fingers_up[1] = 0

   # Middle Finger
   if math.dist((hand_landmarks[0][1], hand_landmarks[0][2]), (hand_landmarks[12][1], hand_landmarks[12][2])) > math.dist((hand_landmarks[0][1], hand_landmarks[0][2]), (hand_landmarks[9][1], hand_landmarks[9][2])):
       fingers_up[2] = 1
   else:
       fingers_up[2] = 0

   # Ring Finger
   if math.dist((hand_landmarks[0][1], hand_landmarks[0][2]), (hand_landmarks[16][1], hand_landmarks[16][2])) > math.dist((hand_landmarks[0][1], hand_landmarks[0][2]), (hand_landmarks[13][1], hand_landmarks[13][2])):
       fingers_up[3] = 1
   else:
       fingers_up[3] = 0

   # Pinky Finger
   if math.dist((hand_landmarks[0][1], hand_landmarks[0][2]), (hand_landmarks[20][1], hand_landmarks[20][2])) > math.dist((hand_landmarks[0][1], hand_landmarks[0][2]), (hand_landmarks[17][1], hand_landmarks[17][2])):
       fingers_up[4] = 1
   else:
       fingers_up[4] = 0

   # Thumb
   angle = calculate_angle((hand_landmarks[2][1], hand_landmarks[2][2]), (hand_landmarks[3][1], hand_landmarks[3][2]), (hand_landmarks[4][1], hand_landmarks[4][2]))
   if angle < 30:
       fingers_up[0] = 1
   else:
       fingers_up[0] = 0

   return fingers_up

def display_values(fingers_up):
   # Check if no fingers are up (regardless of the thumb)
   if np.array_equal(fingers_up, np.array([0, 0, 0, 0, 0])) or np.array_equal(fingers_up, np.array([1, 0, 0, 0, 0])):
       result = "Rock"
   # Check if index and middle finger are up (regardless of the thumb)
   elif np.array_equal(fingers_up, np.array([0, 1, 1, 0, 0])) or np.array_equal(fingers_up, np.array([1, 1, 1, 0, 0])):
       result = "Scissors"
   # Check if all the fingers are up, thumb included
   elif np.array_equal(fingers_up, np.array([1, 1, 1, 1, 1])):
       result = "Paper"
   else:
       result = "Invalid"
   return result

def oposite_value(option):
   if option == "Rock" :
       result = 3
   elif option == "Paper":
       result = 1
   elif option == "Scissors":
       result = 2
   else: result = 1

   return result

# Loading in from mediapipe
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# Using OpenCV to capture from the webcam
webcam = cv2.VideoCapture(2)

#cv2.namedWindow("Rock, Paper, Scissors", cv2.WND_PROP_FULLSCREEN)
#cv2.setWindowProperty("Rock, Paper, Scissors", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

cpu_choices = ["Scissors", "Rock", "Paper"]
cpu_choice = "Nothing"
cpu_score, player_score = 0, 0
winner_colour = (0, 255, 0)
player_choice = "Nothing"
hand_valid = False
current_time = 1000
winner = "None"
de = deque(['Nothing'] * 5, maxlen=5)

def send_command_to_socket(command, host='localhost', port=65432):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(str(command).encode())
            print(f"Sent command: {command}")
            #data= connect.recv(1024)
    except Exception as e:
        print(f"Failed to send command: {e}")

def decode_choice(choice):
      if(choice == 1):
       result = "Scissors"
      elif(choice == 2):
       result = "Rock"
      elif(choice == 3):
       result = "Paper"
      else:
       result = "Nothing"
      return result

# def send_msg(msg):
#    client_socket.sendall(msg.encode('utf-8')) # type: ignore
#    data = client_socket.recv(1024)
#    print("server response: ", data.decode('utf-8'))

with mp_hands.Hands(
       model_complexity=0,
       min_detection_confidence=0.5,
       min_tracking_confidence=0.5) as hands:

   while webcam.isOpened():
       success, image = webcam.read()
       if not success:
           print("Camera isn't working")
           continue

       image = cv2.flip(image, 1)

       image.flags.writeable = False
       image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
       results = hands.process(image)

       image.flags.writeable = True
       image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

       handNumber = 0
       hand_landmarks = []
       isCounting = False
       fingers = np.zeros(5)

       # If at least one hand is detected this will execute.
       if results.multi_hand_landmarks:
           # hand_valid acts as a flag to not reset current_time
           if not hand_valid:
               current_time = time.time()
               send_command_to_socket(0)
               hand_valid = True
   
           isCounting = True

           if player_choice != "Nothing" and time.time()-current_time >= 3:
               # cpu_choice = random.choice(cpu_choices)
               cpu_choice = oposite_value(player_choice)
               send_command_to_socket(cpu_choice)
               time.sleep(3)
               
               winner = calculate_winner(cpu_choice, player_choice)

               # Incrementing scores of player or CPU
               if winner == "You win!":
                   player_score += 1
                   winner_colour = (255, 0, 0)
               elif winner == "CPU wins!":
                   cpu_score += 1
                   winner_colour = (0, 0, 255)
               elif winner == "Invalid!" or winner == "Tie!":
                   winner_colour = (0, 255, 0)
               
               hand_valid = False


           # Drawing the hand skeletons
           for hand in results.multi_hand_landmarks:
               mp_drawing.draw_landmarks(
                   image,
                   hand,
                   mp_hands.HAND_CONNECTIONS,
                   mp_drawing_styles.get_default_hand_landmarks_style(),
                   mp_drawing_styles.get_default_hand_connections_style())

               # Figures out whether it's a left hand or right hand in frame
               label = results.multi_handedness[handNumber].classification[0].label

               # Converts unit-less hand landmarks into pixel counts
               for id, landmark in enumerate(hand.landmark):
                   imgH, imgW, imgC = image.shape
                   xPos, yPos = int(landmark.x * imgW), int(landmark.y * imgH)

                   hand_landmarks.append([id, xPos, yPos, label])

               # Number of fingers held up are counted.
               fingers = compute_fingers(hand_landmarks)

               handNumber += 1
               #time.sleep(2)


       else:
           current_time = time.time()

       # The number of fingers being held up is used to determine which move is made by the player
       if isCounting and sum(fingers) <= 5:
           player_choice = display_values(fingers)
       elif isCounting:
           player_choice = "Invalid"
       else:
           player_choice = "Nothing"

       # Adding the detected move to the left of the double-ended queue
       de.appendleft(player_choice)

       # Instead of using the first move detected, the mode is taken so that it provides a more reliable move detection.
       try:
           player_choice = st.mode(de)
       except st.StatisticsError:
           print("Stats Error")
           continue
       

       cv2.imshow('Rock, Paper, Scissors', image)

       # Allows for the program to be closed by pressing the Escape key
       if cv2.waitKey(1) & 0xFF == 27:
           break

webcam.release()

# OpenCV Rock, Paper, Scissors

## Overview

- The user can play a game of rock, paper, scissors against the computer.
- Uses video input from the webcam to capture the user's move (rock, paper or scissors).
- The computer also generates its move.

The winner is calculated and the scores are incremented appropriately.
Ties contribute zero points while invalid hand signs are reported as invalid by the program.

# Getting Started

## Dependencies

* [Mediapipe](https://google.github.io/mediapipe/)
* [OpenCV](https://opencv.org).
* [Socket](https://github.com/python/cpython/tree/3.13/Lib/socket.py)

## Program Execution

To launch our program, after connecting to Meka, you should execute the file arm_interface.py in the terminal connected to meka@user using Python 2. Then, in another terminal, execute the file RPS_Socket.py with Python 3. The communication between the two programs throught socket should begin automatically. Must allow the program to use webcam. Depending on what USB port your camera (or webcam) is connected, an adaptations may be required to allow the code to access it properly: 

Change the 0 in line 120 - webcam = cv2.VideoCapture(0) to 1, 2, ..., untill the port in which your camera is connected is found.

Once everything is set up, a window will pop up displaying the video feed being recorded. You should present only one hand to allow for detection, and the game will begin in a few seconds. Meka will perform an up-and-down movements and, after 4 seconds, make its choice. You can select if she will play to allways win (comment line 185 - cpu_choice = random.choice(cpu_choices)) or if she will play randomly (comment line 186 - cpu_choice = oposite_value(player_choice)). You should allways keep your hand in the view of the camera, otherwise Meka will restart the countdown of 4 seconds.

## Detailed Explanation

Using OpenCV, the webcam input is read in frame by frame. The mediapipe library's hand module is called and isolates the hand's skeletal structure if it is in frame. An alogrithm* decides whether the player's move is rock, paper or scissors using the skeletal relative position from the module and the computer also plays a move. Every 4 seconds, if the hand's skeleton is keept in the camera's field of view, a round of the game is taken place.

*This algorithm works by counting the number of fingers that are open. For rock, this would be zero. For scissors, it verifies if index and middle fingers are both open. And finally, for paper, this would be 5 fingers. A fingers is counted as being open if the distance between the bottom of the hand to the fingertip is greater than the distance between the bottom of the hand to the begining of the finger. See figure for better exemple: index finger is considered open if the distance of the segment 0-8 is greater than 0-5, and so on. This strategie allows for identification of rock, paper or scrissors regardless on the orientation of the hand in the picture. The limitation of this strategy is that the palm needs to face the camera in order for the fingers to be counted perfectly. 

![image](https://github.com/user-attachments/assets/efa233e4-4059-459f-b365-62d9cd605255)

The code that controls Meka's movements waits for a command from Socket communication provided by the computer vision algorithm, and then performs the corresponding action. The different positions of the hand and arm are defined using vectors that specify the desired angles for each position. Timers and loops are employed to combine these positions and execute the defined movements.

The communication between the nodes is implemented using the M3 library, where a server socket is created to listen for the commands sent. When the hand appears in the sreen, 0 is sent, and the bouncing movement is executed. After 4 seconds, if a legal move is ready, a integer is sent corresponding to either rock, paper, or scissors, so that the gestures are performed by Meka.

## Authors

- Luiz Henrique Marques Gonçalves
- Mateus Galvão
- Rafael Fernandes Pignoli Benzi
- Tiago Lopes Rezende

## License

This project is licensed under the MIT License - see the LICENSE.md file for details

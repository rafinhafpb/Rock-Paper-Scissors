The user can play a game of rock, paper, scissors against the computer. The program uses input from the webcam to capture the user's move (rock, paper or scissors) and the computer also generates its move. The winner is calculated and the scores and incremented appropriately. Ties contribute zero points while invalid hand signs are reported as invalid by the program.
Created using Python, Mediapipe and OpenCV.
Using OpenCV the webcam input is read in frame by frame. The mediapipe library's hand module is called and isolated the hand's skeletal structure if it is in frame. An alogrithm decides whether the player's move is rock, paper or scissors using the skeletal coordinates from the module and the computer also plays a move. The user then needs to move their hand out of the frame and back in to play the next round. The winner is calculated each time the hand enters back into the frame after leaving and a running tally is maintained.

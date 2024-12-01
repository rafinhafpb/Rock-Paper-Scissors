#!/usr/bin/env python

import time
import m3.toolbox as m3t
import m3.rt_proxy as m3p
import m3.humanoid 
import m3.hand
import m3.gui as m3g
import m3.trajectory as m3jt
import numpy as nu
import yaml
from threading import Thread 
import sys
import random
import socket
import math

paper = [0, 0, 0, 0, 0]
scissors = [0, 250, 0, 0, 250]
rock = [0, 250, 250, 250, 250]

# host = '127.0.0.1'  # Local address
# port = 12345        # Port for communication

# # Create the socket
# server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_socket.bind((host, port))
# server_socket.listen(1)
# print("Server is waiting for connections...")
# conn, addr = server_socket.accept()
# print("Connected to:", addr)


class M3Proc:
  def __init__(self):
      self.proxy = m3p.M3RtProxy()
     
  def stop(self):
      self.proxy.stop()

  def start(self):
      # ######## Setup Proxy and Components #########################
      self.proxy.start()
      self.current_first = True

      
      bot_name=m3t.get_robot_name()
      if bot_name == "":
          print 'Error: no robot components found:', bot_names
          return
      self.bot=m3.humanoid.M3Humanoid(bot_name)    
      arm_names = self.bot.get_available_chains()    
      arm_names = [x for x in arm_names if x.find('arm')!=-1]
      if len(arm_names)==0:
          print 'No arms found'
          return
      
      ##PH
      self.arm_name='left_arm'
      ##PH

      # ####### Setup Hand #############
      hand_names = self.bot.get_available_chains()    
      hand_names = [x for x in hand_names if x.find('hand')!=-1]
      if len(hand_names)==0:
          print 'No hands found'
          return
      self.hand_name=hand_names[1]
      print(self.hand_name)
      # ####### Setup Proxy #############
      self.proxy.subscribe_status(self.bot)
      self.proxy.publish_command(self.bot)
      self.proxy.make_operational_all()
      self.bot.set_motor_power_on()
      self.ndof=self.bot.get_num_dof(self.arm_name)
      
      
      humanoid_shm_names=self.proxy.get_available_components('m3humanoid_shm')
      if len(humanoid_shm_names) > 0:

        self.proxy.make_safe_operational(humanoid_shm_names[0])

      self.poses={'holdup':{'right_arm':[15.0, 26.0, -8.0, 84.0, 119.0, -36.0, 2.0],'left_arm':[16.0, -26.0, 8.0, 84.0, -119.0, -36.0, -2.0]}} 
      self.stiffness=80
      self.velocity=[0]
      self.theta_curr = [0.0]*self.ndof
      self.off=False
      self.openHand=True
      self.handCloseLevel=60.0
      self.handTorqCoeff=nu.array([1.0,1.0,0.9,1.0])
      self.handStiffness=80.0

  def step(self):
      try:
          self.step_hold_up()
          self.proxy.step()

      except Exception,e:
          print e
          self.proxy.step()

  def step_openHand(self):
#        self.bot.set_mode_off(self.hand_name)q
      self.bot.set_stiffness(self.hand_name,[self.handStiffness/100.0]*5,[0,1,2,3,4])
      self.bot.set_slew_rate_proportion(self.hand_name,[1.0]*5,[0,1,2,3,4])
      self.bot.set_mode_theta_gc(self.hand_name,[0,1,2,3,4])
      hand_value = 100.0
      self.bot.set_theta_deg(self.hand_name,[hand_value]*5,[0,1,2,3,4])

  def step_setHand(self, hand_set):
      self.bot.set_stiffness(self.hand_name,[self.handStiffness/100.0]*5,[0,1,2,3,4])
      self.bot.set_slew_rate_proportion(self.hand_name,[0.5]*5,[0,1,2,3,4])
      self.bot.set_mode_theta_gc(self.hand_name,[0,1,2,3,4])
      self.bot.set_theta_deg(self.hand_name,hand_set,[0,1,2,3,4])

  def step_closeHand(self):
      self.bot.set_stiffness(self.hand_name,[self.handStiffness/100.0]*3,[2,3,4])
      self.bot.set_slew_rate_proportion(self.hand_name,[1.0]*3,[2,3,4])

      self.bot.set_mode_theta(self.hand_name,[0])
      # self.bot.set_mode_torque_gc(self.hand_name,[2,3,4])
      # self.bot.set_torque(self.hand_name,self.handTorqCoeff[1:]*150,[2,3,4])
      self.bot.set_theta_deg(self.hand_name,[10.0],[0])

      self.bot.set_mode_theta_gc(self.hand_name,[2,3,4])
      self.bot.set_theta_deg(self.hand_name,[self.handCloseLevel*3]*3,[2,3,4])     

  def step_hold_up(self):
      self.bot.set_mode_theta_gc(self.arm_name)
      self.bot.set_theta_deg(self.arm_name,self.poses['holdup'][self.arm_name])
      self.bot.set_stiffness(self.arm_name,[self.stiffness/100.0]*self.ndof)
      self.bot.set_slew_rate_proportion(self.arm_name,[1.0]*self.ndof)
      #self.bot.set_thetadot_deg(self.arm_name,[15.0]*self.ndof)

  def step_setArm(self, arm_set):
      armTorque = 0.5
      self.bot.set_mode_theta_gc(self.arm_name)
      self.bot.set_theta_deg(self.arm_name,arm_set)
      self.bot.set_stiffness(self.arm_name,[self.stiffness/100.0]*self.ndof)
      self.bot.set_slew_rate_proportion(self.arm_name,[10.0]*self.ndof)

      #self.bot.set_thetadot_deg(self.arm_name,[15.0]*self.ndof)

  def step_off(self):
      self.bot.set_mode_off(self.arm_name)
      self.bot.set_mode_off(self.hand_name)
  
  def bouncing(self):

      for i in range(3):
        hand_set = [0, 250, 250, 250, 250]
        arm_set = [0,-30, 20,120,-90,0, 30]

        self.step_setHand(hand_set)
        self.step_setArm(arm_set)
        self.proxy.step()

        time.sleep(0.5) 

        arm_set = [0,-10, 20,100,-90,0, -30]

        self.step_setHand(hand_set)
        self.step_setArm(arm_set)
        self.proxy.step()

        time.sleep(0.5)


  def doAction(self, choice):
      arm_set = [0, -10, 20, 100, -90, 0, -30]

      if(choice == 1):
       hand_set = scissors
      elif(choice == 2):
       hand_set = rock
      elif(choice == 3):
       hand_set = paper

      self.step_setHand(hand_set)
      self.step_setArm(arm_set)
      self.proxy.step()


if __name__ == '__main__':
  t=M3Proc()
  try:

    #   hand_set = [0, 250, 250, 250, 250]
    #   arm_set = [0,-10, 20,100,-90,0, -30]

      hand_set = [0, 250, 250, 250, 250]
      arm_set = [0,0, 0,0,0,0, 0]
      host = 'localhost'
      port = 65432
      socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      socket.bind((host, port))

      t.start()
      arm_set = [0, -10, 20, 100, -90, 0, -30]
  
      t.step_setHand(rock)
      t.step_setArm(arm_set)
      t.proxy.step()

      while(1):
        
        socket.listen(1)
        connection, address = socket.accept()
        try:
            data = connection.recv(1024)
            if not data:
                break
            command = int(data.decode())
            if command is not None:
               print(command)
               if(command == 0):
                  t.bouncing()
               else:
                  t.doAction(command)
                  time.sleep(3)

        except Exception as e:
            #print exception info
            print(e)
            proxy.stop()
            connection.close()
            break

  except (KeyboardInterrupt,EOFError):
      arm_set = [0,0, 0,0,0,0, 0]

      t.step_setHand(paper)
      t.step_setArm(arm_set)
      t.proxy.step()
      proxy.stop()
      connection.close()
      time.sleep(1)

  t.stop()

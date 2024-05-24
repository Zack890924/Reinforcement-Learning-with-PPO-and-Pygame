import gym
from gym import spaces
import pygame, sys, os, random
from pygame.locals import *
import numpy as np
from collections import deque
import cv2
from game import GAME



















	
class CustomEnv(gym.Env):
	"""Custom Environment that follows gym interface"""

	def __init__(self):
		super(CustomEnv, self).__init__()
		self.pygame = GAME()
		self.action_space = spaces.Discrete(4)
		self.observation_space = spaces.Box(low=0, high=255,
											shape=(84,84,3), dtype=np.uint8)
	
		
		self.game_length = 4500
	def step(self, action):
		self.pygame.action(action)

		
		# obs = self.preprocess(obs)
		# frame_delta = obs - self.prev_frame
		# self.prev_frame = obs
		# print(obs)
		self.pygame.update_and_show()
		obs = self.pygame.observe()
		obs = self.preprocess(obs)
		frame_delta = obs - self.prev_frame
		self.prev_frame = obs
		# self.pygame.done_()
		self.total_reward = self.pygame.reward
		self.reward = self.total_reward - self.prev_reward
		self.prev_reward = self.total_reward
		self.game_length-=1
		reward = self.reward
		if self.game_length !=0:
			done = False
		else:
			done = True
		if done:
			print(reward)

		# if done and reward>0:
		# 	reward += 20000
		# 	print(reward)
		# elif done and reward<0:
		# 	reward -= 20000
		# 	print(reward)


		# if done and reward>0:
		# 	reward += 20000
		# 	print(reward)


		# if done and reward > 0:
		# 	reward += 50000
		# 	print(reward)
		# elif done and reward < 0:
		# 	reward -= 50000
		# 	print(reward)
		# if done is True:
		# 	reward -=100
		return frame_delta, reward, done, {}

		...
	def preprocess(self, observation): 
		# Grayscaling 
		# gray = cv2.cvtColor(observation, cv2.COLOR_BGR2GRAY)
		# Resize 
		resize = cv2.resize(observation, (84,84), interpolation=cv2.INTER_CUBIC)
		# Add the channels value
		channels = np.reshape(resize, (84,84,3))
		return channels
	def reset(self):
		del self.pygame
		self.pygame = GAME()

		
		self.prev_reward = 0
		obs = self.pygame.observe()
		obs = self.preprocess(obs)
		self.prev_frame = obs
		
		self.game_length = 4500


		return obs  # reward, done, info can't be included
	def close(self):
		del self.pygame

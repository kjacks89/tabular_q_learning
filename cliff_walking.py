from __future__ import print_function
# ------------------------------------------------------------------------------------------------
# Copyright (c) 2016 Microsoft Corporation
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
# NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# ------------------------------------------------------------------------------------------------

# The "Cliff Walking" example using Q-learning.
# From pages 148-150 of:
# Richard S. Sutton and Andrews G. Barto
# Reinforcement Learning, An Introduction
# MIT Press, 1998

from future import standard_library
standard_library.install_aliases()
from builtins import range
from builtins import object
import MalmoPython
import json
import logging
import os
import random
import sys
import time
import numpy as np
if sys.version_info[0] == 2:
    # Workaround for https://github.com/PythonCharmers/python-future/issues/262
    import Tkinter as tk
else:
    import tkinter as tk

class TabQAgent(object):
    """Tabular Q-learning agent for discrete state/action spaces."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        if False: # True if you want to see more information
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
        self.logger.handlers = []
        self.logger.addHandler(logging.StreamHandler(sys.stdout))

        self.actions = ["movenorth 1", "movesouth 1", "movewest 1", "moveeast 1"]
        ###modified
        self.q_table = {}
        self.gamma = 0.9
        self.alpha = 0.1
        #since deterministic environment, a constant epsilon is best rather than having
        #a decay rate (decreasing epsilon after every epoch).  A convenient way to see learned
        #behavior is to turn off learning after a sufficient amount of time, which in this case
        #is the self.learn variable below
        self.epsilon = 0.1 #chance of taking random action instead of highest value action
        self.learn = True 
        self.optimal = False
        self.count = 0
        self.check = []
        self.s1 = False
        self.s2 = False
        self.s3 = False
        self.s4 = False
        self.s5 = False
        self.s6 = False
        ###/
        self.canvas = None
        self.root = None

    def updateQTable( self, reward, current_state ):
        """Change q_table to reflect what we have learnt."""
        ###modified
        previous_q_value = self.q_table[self.prev_s][self.prev_a]
        
        self.q_table[self.prev_s][self.prev_a] = previous_q_value + self.alpha * (reward + self.gamma * max(self.q_table[current_state]) - previous_q_value)
        
        #below is checking if q_table has reached optimal path
        difference = self.q_table[self.prev_s][self.prev_a] - previous_q_value #change in q value
        state_value = (self.prev_s, self.prev_a)
        if state_value not in self.check:
            self.check.append(state_value)
        if len(self.check) >= 44:#if all actions have been picked for all states (11 non-terminating states * 4 actions each = 44)
            if self.prev_s == "1:4" and difference < 0.01 and self.s1 == False:#if on optimal path and very little change in q-value
                self.count = self.count + 1
                self.s1 = True
            if self.prev_s == "1:3" and difference < 0.01 and self.s2 == False:
                self.count = self.count + 1
                self.s2 = True
            if self.prev_s == "2:3" and difference < 0.01 and self.s3 == False:
                self.count = self.count + 1
                self.s3 = True
            if self.prev_s == "3:3" and difference < 0.01 and self.s4 == False:
                self.count = self.count + 1
                self.s4 = True
            if self.prev_s == "4:3" and difference < 0.01 and self.s5 == False:
                self.count = self.count + 1
                self.s5 = True
            if self.prev_s == "5:3" and difference < 0.01 and self.s6 == False:
                self.count = self.count + 1
                self.s6 = True
        if self.count == 6:#if all states in optimal path have very little change in q-value, then there is convergence
            self.optimal = True
            for state in self.q_table:
                m = max(self.q_table[state]) #highest q value for previous state
                if state == "1:4" and self.q_table[state][2] != m:    
                    self.optimal = False
                if state == "1:3" and self.q_table[state][1] != m:    
                    self.optimal = False
                if state == "2:3" and self.q_table[state][1] != m:    
                    self.optimal = False
                if state == "3:3" and self.q_table[state][1] != m:    
                    self.optimal = False
                if state == "4:3" and self.q_table[state][1] != m:    
                    self.optimal = False
                if state == "5:3" and self.q_table[state][3] != m:    
                    self.optimal = False
        
    def updateQTableFromTerminatingState( self, reward ):
        """Change q_table to reflect what we have learnt, after reaching a terminal state."""
        ###modified
        previous_q_value = self.q_table[self.prev_s][self.prev_a]
        #print(self.prev_s)
        self.q_table[self.prev_s][self.prev_a] = self.q_table[self.prev_s][self.prev_a] + self.alpha * ( reward - self.q_table[self.prev_s][self.prev_a]) 
        
        #below is checking if q_table has reached optimal path
        #m = max(self.q_table[self.prev_s]) #highest q value for previous state
        difference = self.q_table[self.prev_s][self.prev_a] - previous_q_value #change in q value
        state_value = (self.prev_s, self.prev_a)
        if state_value not in self.check:
            self.check.append(state_value)
        if len(self.check) >= 44:#if all actions have been picked for all states (11 non-terminating states * 4 actions each = 44)
            if self.prev_s == "1:4" and difference < 0.01 and self.s1 == False:#if on optimal path and very little change in q-value
                self.count = self.count + 1
                self.s1 = True
            if self.prev_s == "1:3" and difference < 0.01 and self.s2 == False:
                self.count = self.count + 1
                self.s2 = True
            if self.prev_s == "2:3" and difference < 0.01 and self.s3 == False:
                self.count = self.count + 1
                self.s3 = True
            if self.prev_s == "3:3" and difference < 0.01 and self.s4 == False:
                self.count = self.count + 1
                self.s4 = True
            if self.prev_s == "4:3" and difference < 0.01 and self.s5 == False:
                self.count = self.count + 1
                self.s5 = True
            if self.prev_s == "5:3" and difference < 0.01 and self.s6 == False:
                self.count = self.count + 1
                self.s6 = True
        if self.count == 6:#if all states in optimal path have very little change in q-value, then there is convergence
            self.optimal = True
            for state in self.q_table:
                m = max(self.q_table[state]) #highest q value for previous state
                if state == "1:4" and self.q_table[state][2] != m:    
                    self.optimal = False
                if state == "1:3" and self.q_table[state][1] != m:    
                    self.optimal = False
                if state == "2:3" and self.q_table[state][1] != m:    
                    self.optimal = False
                if state == "3:3" and self.q_table[state][1] != m:    
                    self.optimal = False
                if state == "4:3" and self.q_table[state][1] != m:    
                    self.optimal = False
                if state == "5:3" and self.q_table[state][3] != m:    
                    self.optimal = False

    def act(self, world_state, agent_host, current_r ):
        """take 1 action in response to the current world state"""
        
        obs_text = world_state.observations[-1].text
        obs = json.loads(obs_text) # most recent observation
        self.logger.debug(obs)
        if not u'XPos' in obs or not u'ZPos' in obs:
            self.logger.error("Incomplete observation received: %s" % obs_text)
            return 0
		#changed current_s coordinate format to read row:column instead of column:row
        current_s = "%d:%d" % (int(obs[u'ZPos']), int(obs[u'XPos']))
        self.logger.debug("State: %s (z = %.2f, x = %.2f)" % (current_s, float(obs[u'ZPos']), float(obs[u'XPos'])))
        if current_s not in self.q_table:
            self.q_table[current_s] = ([0] * len(self.actions))

        # update Q values
        if self.prev_s is not None and self.prev_a is not None:
            self.updateQTable( current_r, current_s )
        else:
            initial_x = int(obs[u'ZPos'])
            initial_z = int(obs[u'XPos'])
            print('Initial position: ', initial_x,',',initial_z)
        self.drawQ( curr_x = int(obs[u'ZPos']), curr_y = int(obs[u'XPos']) )

        # selectrthe next action
        rnd = random.random()
        #if explore (rnd<epsilon), choose random action from action space
        if rnd < self.epsilon and self.learn:
            a = random.randint(0, len(self.actions) - 1)
            self.logger.info("Random action: %s" % self.actions[a])
        #else, m is max q value.  
        else:
            m = max(self.q_table[current_s])
            self.logger.debug("Current values: %s" % ",".join(str(x) for x in self.q_table[current_s]))
            l = list()
            #If max q value is shared between 2 or more actions, choose randomly from these.
            for x in range(0, len(self.actions)):
                if self.q_table[current_s][x] == m:
                    l.append(x)
            y = random.randint(0, len(l)-1)
            a = l[y]
            self.logger.info("Taking q action: %s" % self.actions[a])

        # try to send the selected action, only update prev_s if this succeeds
        try:
            agent_host.sendCommand(self.actions[a])
            self.prev_s = current_s
            self.prev_a = a

        except RuntimeError as e:
            self.logger.error("Failed to send command: %s" % e)

        return current_r
    #run the agent in current episode until reaching a terminating state
    def run(self, agent_host):
        """run the agent on the world"""

        total_reward = 0
        
        self.prev_s = None
        self.prev_a = None
        
        is_first_action = True
        
        # main loop:
        world_state = agent_host.getWorldState()
        while world_state.is_mission_running:

            current_r = 0
            
            if is_first_action:
                # wait until have received a valid observation
                while True:
                    time.sleep(0.1)
                    world_state = agent_host.getWorldState()
                    for error in world_state.errors:
                        self.logger.error("Error: %s" % error.text)
                    for reward in world_state.rewards:
                        current_r += reward.getValue()
                    if world_state.is_mission_running and len(world_state.observations)>0 and not world_state.observations[-1].text=="{}":
                        total_reward += self.act(world_state, agent_host, current_r)
                        break
                    if not world_state.is_mission_running:
                        break
                is_first_action = False
            else:
                # wait for non-zero reward
                while world_state.is_mission_running and current_r == 0:
                    time.sleep(0.1)
                    world_state = agent_host.getWorldState()
                    for error in world_state.errors:
                        self.logger.error("Error: %s" % error.text)
                    for reward in world_state.rewards:
                        current_r += reward.getValue()
                # allow time to stabilise after action
                while True:
                    time.sleep(0.1)
                    world_state = agent_host.getWorldState()
                    for error in world_state.errors:
                        self.logger.error("Error: %s" % error.text)
                    for reward in world_state.rewards:
                        current_r += reward.getValue()
                    if world_state.is_mission_running and len(world_state.observations)>0 and not world_state.observations[-1].text=="{}":
                        total_reward += self.act(world_state, agent_host, current_r)
                        break
                    if not world_state.is_mission_running:
                        break

        # process final reward
        self.logger.debug("Final reward: %d" % current_r)
        total_reward += current_r

        # update Q values
        if self.prev_s is not None and self.prev_a is not None:
            self.updateQTableFromTerminatingState( current_r )
            
        self.drawQ()
    
        return total_reward
        
    def drawQ( self, curr_x=None, curr_y=None ):
        scale = 40
        world_x = 6
        world_y = 14
        if self.canvas is None or self.root is None:
            self.root = tk.Tk()
            self.root.wm_title("Q-table")
            self.canvas = tk.Canvas(self.root, width=world_x*scale, height=world_y*scale, borderwidth=0, highlightthickness=0, bg="black")
            self.canvas.grid()
            self.root.update()
        self.canvas.delete("all")
        action_inset = 0.1
        action_radius = 0.1
        curr_radius = 0.2
        action_positions = [ ( 0.5, action_inset ), ( 0.5, 1-action_inset ), ( action_inset, 0.5 ), ( 1-action_inset, 0.5 ) ]
        # (NSWE to match action order)
        min_value = -20
        max_value = 20
        for x in range(world_x):
            for y in range(world_y):
                s = "%d:%d" % (x,y)
                self.canvas.create_rectangle( x*scale, y*scale, (x+1)*scale, (y+1)*scale, outline="#fff", fill="#000")
                for action in range(4):
                    if not s in self.q_table:
                        continue
                    value = self.q_table[s][action]
                    color = int( 255 * ( value - min_value ) / ( max_value - min_value )) # map value to 0-255
                    color = max( min( color, 255 ), 0 ) # ensure within [0,255]
                    color_string = '#%02x%02x%02x' % (255-color, color, 0)
                    self.canvas.create_oval( (x + action_positions[action][0] - action_radius ) *scale,
                                             (y + action_positions[action][1] - action_radius ) *scale,
                                             (x + action_positions[action][0] + action_radius ) *scale,
                                             (y + action_positions[action][1] + action_radius ) *scale, 
                                             outline=color_string, fill=color_string )
        if curr_x is not None and curr_y is not None:
            self.canvas.create_oval( (curr_x + 0.5 - curr_radius ) * scale, 
                                     (curr_y + 0.5 - curr_radius ) * scale, 
                                     (curr_x + 0.5 + curr_radius ) * scale, 
                                     (curr_y + 0.5 + curr_radius ) * scale, 
                                     outline="#fff", fill="#fff" )
        self.root.update()

if sys.version_info[0] == 2:
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately
else:
    import functools
    print = functools.partial(print, flush=True)

agent = TabQAgent()
agent_host = MalmoPython.AgentHost()
try:
    agent_host.parse( sys.argv )
except RuntimeError as e:
    print('ERROR:',e)
    print(agent_host.getUsage())
    exit(1)
if agent_host.receivedArgument("help"):
    print(agent_host.getUsage())
    exit(0)

# -- set up the mission -- #
mission_file = './cliff_walking.xml'
with open(mission_file, 'r') as f:
    print("Loading mission from %s" % mission_file)
    mission_xml = f.read()
    my_mission = MalmoPython.MissionSpec(mission_xml, True)
# add 20% holes for interest
#for x in range(1,4):
#    for z in range(1,13):
#        if random.random()<0.1:
#####################col##row
#my_mission.drawBlock( 1,45,7,"lava")
#my_mission.drawBlock( 3,45,2,"lava")

max_retries = 3

if agent_host.receivedArgument("test"):
    num_repeats = 1
else:
    num_repeats = 1000

cumulative_rewards = []
#run this number of episodes for the agent 
for i in range(num_repeats):
    if agent.optimal == True:
        break
    print()
    print('Repeat %d of %d' % ( i+1, num_repeats ))
    
    my_mission_record = MalmoPython.MissionRecordSpec()

    #if num_repeats % 20 == 0 and self.epsilon > 0:
    #    self.epsilon = self.epsilon - 0.01    

    for retry in range(max_retries):
        try:
            agent_host.startMission( my_mission, my_mission_record )
            break
        except RuntimeError as e:
            if retry == max_retries - 1:
                print("Error starting mission:",e)
                exit(1)
            else:
                time.sleep(2.5)

    print("Waiting for the mission to start", end=' ')
    world_state = agent_host.getWorldState()
    while not world_state.has_mission_begun:
        print(".", end="")
        time.sleep(0.1)
        world_state = agent_host.getWorldState()
        for error in world_state.errors:
            print("Error:",error.text)
    print()

    # -- run the agent in the world -- #
    cumulative_reward = agent.run(agent_host)
    print('Cumulative reward: %d' % cumulative_reward)
    cumulative_rewards += [ cumulative_reward ]

    print("All values in Q-Table for the following actions: ") 
    print("\t" + str(agent.actions))
    for observation in agent.q_table:
        colon = observation.index(":")
        row = observation[:colon]
        column = observation[colon+1:]
        coordinate = "(" + row + "," + column + ")"
        print(coordinate + ": " + str(agent.q_table[observation]))
    # -- clean up -- #
    time.sleep(0.5) # (let the Mod reset)
print("Done.")

print("Cumulative rewards for all %d runs:" % num_repeats)
print(cumulative_rewards)
print("All values in Q-Table for the following actions: ") 
print("\t" + str(agent.actions))
for observation in agent.q_table:
    colon = observation.index(":")
    row = observation[:colon]
    column = observation[colon+1:]
    coordinate = "(" + row + "," + column + ")"
    print(coordinate + ": " + str(agent.q_table[observation]))
if agent.optimal == True:
    print("Q-function converged")

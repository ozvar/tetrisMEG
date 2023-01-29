import os, sys
import pygame
import tkinter as tk
from tkinter import filedialog
import datetime
from collections import Counter as counter
import time #just for debugging

#TODO: fix all the stupid global references
#unimport time


tkroot = tk.Tk()
tkroot.withdraw()

simulate = True
fps = 60

start_time = datetime.datetime.now()
# 
dirname = filedialog.askdirectory(initialdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Data"))
session = dirname.split("/")[-1]

print("Opening file" + session)

print()
print()
print()
print()
print()
print()

#What we do here depends on whether it's MetaT or Meta2
#We can tell based on the directory contents which it is
contents = os.listdir(dirname)
print(contents)

#assume it's metaT unless proven otherwise
is_metaT = False
if dirname + "/" + "Complete_" + session + ".tsv" in contents:
    is_metaT = True
    


#converts strings from .tsv to appropriate types for analysis
def cast_game_state(entry, head_dict):
    entry[head_dict['ts']] = float(entry[head_dict['ts']])
    #entry[head_dict['delaying']] = bool(entry[head_dict['delaying']])
    #entry[head_dict['dropping']] = int(entry[head_dict['dropping']])
    #entry[head_dict['zoid_rot']] = int(entry[head_dict['zoid_rot']])
    #entry[head_dict['zoid_col']] = int(entry[head_dict['zoid_col']])
    #entry[head_dict['zoid_row']] = int(entry[head_dict['zoid_row']])  
    return entry

#converts strings from .tsv to appropriate types for analysis
#TODO: figure out why it was making these stupid castings
def cast_game_event(entry, head_dict):
    #for i, item in enumerate(entry):
    #    entry[i][1] = float(item[1])
    return entry

#Read in the meta2 game .tsv for playback
#return column indices and game state information
def import_meta2_game(game_tsv):
    f = open(game_tsv).readlines()
    
    header = f[0].replace('\n',"").split('\t')
    lines = f[1:]
    
    head_dict = {header[col]:col for col in range(0,len(header))}
    
    #Collect all game state rows
    game_states = []
    game_events = []
    for line in f:
        entry = line.replace('\n',"").split('\t')
        type = entry[head_dict['event_type']]
        if type == "GAME_STATE":
            game_state = cast_game_state(entry,head_dict)
            game_states.append(game_state)
        elif type == "GAME_EVENT":
            game_event = cast_game_event(entry,head_dict)
            game_events.append(game_event)
            
    f = None #TODO: decide if it's important to close the file thusly
    return head_dict, game_states, game_events

if not is_metaT:
    for game in contents:
        if ".tsv" in game:
            game_tsv = os.path.join(dirname,game)
            col_ix, game_states, game_events = import_meta2_game(game_tsv)
            print("Game state parsed after: " + str(datetime.datetime.now() - start_time))

    
def get_next_state(timestamp, game_states):
    """return the gamestate immediately after the timestamp"""
    i = 0
    try:
        while game_states[i][1] < timestamp:
            i+=1
        return game_states[i]
    except IndexError:
        return None
        

#idea here is to iterate over the list of game events - in each episode, look at next (by timestamp) zoid_rep within game_state
#if zoid is at right or left edge, trigger a wall collision. Reset at either inverse translation or at episode end
wall_collision_flag = None
ep_count = 0

#NOTE: collision into walls via rotation is a thing. Need to account for it somehow :-(
#NOTE: bounce away via rotation might be a thing too

def run_game():
    evt_id = col_ix['evt_id']
    evt_data1 = col_ix['evt_data1']
    evt_data2 = col_ix['evt_data2']
    board = col_ix['board_rep']
    zoids = col_ix['zoid_rep']
    
    paused = False
    game_over = False
    ep_count = 0 
    i = 0
    global fps
    while i < len(game_states):
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_over = True
                    break
                if event.key == pygame.K_UP:
                    fps += 10
                if event.key == pygame.K_DOWN:
                    fps -= 10
                if event.key == pygame.K_RIGHT:
                    #find next timestamp in game_event, then find next episode timestamp after that
                    #find index of game_state after that timestamp
                    next_event_index = 0
                    try:
                        while game_event[next_event_index][1] < game_states[i][1]:
                            next_event_index += 1
                    except IndexError:
                        pass
                    next_episode_index = next_event_index
                    try:
                        while not (game_event[next_episode_index][evt_id] == "EPISODE" and game_event[next_episode_index][evt_data1] == "BEGIN"):
                            next_episode_index += 1
                    except IndexError:
                        pass
                    timestamp = game_event[next_episode_index][1]
                    new_index = 0
                    try:
                        while game_states[new_index][1] < timestamp:
                            new_index += 1
                    except IndexError:
                        pass
                    i = new_index
                if event.key == pygame.K_LEFT:
                    #find next timestamp in game_event, then find previous episode timestamp.
                    #if prev_ep timestamp is within .5 seconds of current, go back again
                    #find index of game_state after that timestamp
                    next_event_index = 0
                    try:
                        while game_event[next_event_index][1] < game_states[i][1]:
                            next_event_index += 1
                    except IndexError:
                        pass
                    prev_episode_index = next_event_index
                    try:
                        while not (game_event[prev_episode_index][evt_id] == "EPISODE" and game_event[prev_episode_index][evt_data1] == "BEGIN"):
                            prev_episode_index -= 1
                    except IndexError:
                        prev_episode_index = 0
                    ep_count -= 1
                    if game_states[i][1] - game_event[prev_episode_index][1] < 0.5:
                        #go back one more
                        prev_episode_index -= 1
                        try:
                            while not (game_event[prev_episode_index][evt_id] == "EPISODE" and game_event[prev_episode_index][evt_data1] == "BEGIN"):
                                prev_episode_index -= 1
                        except IndexError:
                            prev_episode_index = 0
                        ep_count -= 1
                    timestamp = game_event[prev_episode_index][1]
                    new_index = 0
                    try:
                        while game_states[new_index][1] < timestamp:
                            new_index += 1
                    except IndexError:
                        pass
                    i = new_index
                if event.key == pygame.K_SPACE:
                    paused = True
        if game_over:
            break 
                       
        ##pause loop
        while paused:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        paused = False
            screen.blit(f.render("Paused", 0, (200,200,200)), (75, 190))
            pygame.display.flip()
        ##end pause loop
    
        screen.fill((0,0,0))
        
#TODO: put this int cleaning and shit higher/separate for greater modularity

        #draw the board from top to bottom
        game_state = game_states[i]
        currBoard = game_state[board].strip('[]\'').split('],[') #in MetaT, it's game_state[board].strip('[]\'').split('], [')
        currZoids = game_state[zoids].strip('[]\'').split('],[')
        for row in range(len(currBoard)):
            boardRow = currBoard[row].split(',')
            zoidRow  = currZoids[row].split(',')
            for col in range(len(boardRow)):
                if int(boardRow[col]) != 0:
                    screen.blit(blue, pygame.Rect(col*20, row*20, 20, 20))
                if int(zoidRow[col]) != 0:
                    screen.blit(green, pygame.Rect(col*20, row*20, 20, 20))
                
        screen.blit(f.render("Episode %d"%ep_count,1,(200,200,200)), (120, 6)) 
        screen.blit(f.render("FPS: %d"%fps,1,(200,200,200)), (10, 6))           
        pygame.display.flip()
        
        i += 1
        
if simulate:
    pygame.init()
    screen = pygame.display.set_mode((200, 400))
    clock = pygame.time.Clock()
    blue = pygame.Surface((20,20))
    blue.fill((64,64,255))
    green = pygame.Surface((20,20))
    green.fill((64,255,64))
    f = pygame.font.Font(None, 18)
    run_game()

# for i in range(10):
#     print(game_state[i]
# print(''
# for i in range(10):
#     print(game_event[i]

#c = counter([line[3] for line in f])
#print(dict(c)
#print([line for line in f if line[3] == "GAME_SUMM"]

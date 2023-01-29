#!/usr/bin/env python

"""
Marc Destefano and John K. Lindstedt
"""

"""
To-do:
  - need to account for games and episode rollover
  - need to display next zoid
  - need to add eyetracking data hooks
  - could add keypress overlay
  
  
  - need a parser to split up eyetracking files into small subfiles.

"""

import os, sys
import pygame
import tkFileDialog
import Tkinter as tk

#from collections import Counter as counter

tkroot = tk.Tk()
tkroot.withdraw()

fps = 30 #default

simulate = True
#f = open("lindstedt novice/101_2013_6_7_14-12-41.tsv").readlines()
dirname = tkFileDialog.askdirectory(initialdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../data"))
session = dirname.split("/")[-1]

try:
    config = open(dirname + "/" + "_config_" + session + ".config").readlines()
except:
    config = open(dirname + "/" + session + ".config").readlines()

fixed_log = False
for c in config:
    line = c.strip().split(" ")
    if line[0] == "fixed_log" and line[2].lower() == "true":
        fixed_log = True
    elif line[0] == "fps":
        fps = int(line[2])
print("fixed_log:" , fixed_log)
config = None

try:
    f = open(dirname + "/" + "complete_" + session + ".tsv").readlines()
except:
    f = open(dirname + "/" + session + ".tsv").readlines()

lines = [line.rstrip().split('\t') for line in f]

f = None



if fixed_log:
    header = lines[0]
    lines = lines[1:]
    print(header)
    event_type_ix = header.index("event_type")
    
    board_ix = header.index("board_rep")
    zoid_ix = header.index("zoid_rep")
    delaying_ix = header.index("delaying")
    dropping_ix = header.index("dropping")
    ts_ix = header.index("ts")
    rot_ix = header.index("zoid_rot")
    col_ix = header.index("zoid_col")
    row_ix = header.index("zoid_row")
    
    evt_id_ix = header.index("evt_id")
    evt_d1_ix = header.index("evt_data1")
    evt_d2_ix = header.index("evt_data2")

else:
    event_type_ix = lines[0].index(":event_type") + 1
    ts_ix = lines[0].index(":ts") + 1


"""
ts	event_type	SID	
session	game_type	game_number	
episode_number	level	score	
lines_cleared	completed	game_duration	
avg_ep_duration	zoid_sequence	curr_zoid	
next_zoid	danger_mode	evt_id	evt_data1	
evt_data2	delaying	dropping	zoid_rot	
zoid_col	zoid_row	board_rep	zoid_rep	
all_ht	all_trans	cleared	col_trans	column_9	
cuml_cleared	cuml_eroded	cuml_wells	deep_wells	
eroded_cells	landing_height	max_ht	max_ht_diff	
max_well	mean_ht	mean_pit_depth	min_ht	
min_ht_diff	pit_depth	pit_rows	pits	
row_trans	tetris	wells
"""


'''
index   value
0       ':ts'         (timestamp label)
1       float         (timestamp starting at 0)
2       ':event-type' (event-type label)
3       string        (e.g. SETUP_EVENT, GAME_EVENT, EYE_SAMP, GAME_STATE)
Everything becomes context-dependent after that.
'''
game_state = [l for l in lines if l[event_type_ix] == "GAME_STATE"]

if not fixed_log:
    board_ix = game_state[0].index(":board_rep") + 1
    zoid_ix = game_state[0].index(":zoid_rep") + 1
    delaying_ix = game_state[0].index(":delaying") + 1
    dropping_ix = game_state[0].index(":dropping") + 1
    rot_ix = game_state[0].index(":zoid_rot") + 1
    col_ix = game_state[0].index(":zoid_col") + 1
    row_ix = game_state[0].index(":zoid_row") + 1

'''
for GAME_STATE:
index   value
4       ':delaying'
5       boolean
6       ':dropping'
7       int
8       ':curr_zoid'
9       char
10      ':next_zoid'
11      char
12      ':zoid_rot'
13      int
14      ':zoid_col'
15      int
16      ':zoid_row'
17      int
18      ':board_rep'
19      list of list of ints
20      ':zoid_rep'
21      list of list of ints
'''

print("Translating appropriate data types...")

#translate appropriate data types
for i, item in enumerate(game_state):
    game_state[i][delaying_ix] = item[delaying_ix].lower() == "true"
    
    #try:
    game_state[i][ts_ix] = float(item[ts_ix])
    game_state[i][dropping_ix] = int(item[dropping_ix])
    game_state[i][rot_ix] = int(item[rot_ix])
    game_state[i][col_ix] = int(item[col_ix])
    game_state[i][row_ix] = int(item[row_ix])
    #except:
    #    print game_state[i]
    #    print game_state[i][7]
    #    print game_state[i][13]
    #    print game_state[i][15]
    #    print game_state[i][17]
    #    print "Exploded."
    #    assert False
    #the string actually starts with a ' character >:-(
    x = game_state[i][board_ix].strip('[]\'')
    x = x.split('], [')
    #list of list of strings
    x = [ele.split(', ') for ele in x]
    #convert to ints
    x = [map(int, item) for item in x]
    game_state[i][board_ix] = x
    
    #same deal for zoid_rep
    x = game_state[i][zoid_ix].strip('[]\'').split('], [')
    #list of list of strings
    x = [ele.split(', ') for ele in x]
    #convert to ints
    x = [map(int, item) for item in x]
    game_state[i][zoid_ix] = x

print("\t...done.")

game_event = [l for l in lines if l[event_type_ix] == "GAME_EVENT"]

if not fixed_log:
    evt_id_ix = game_event[0].index(":evt_id") + 1
    evt_d1_ix = game_event[0].index(":evt_data1") + 1
    evt_d2_ix = game_event[0].index(":evt_data2") + 1

'''
for GAME_EVENT:
index   value
4       ':evt_id'   
5       string      KEYPRESS, GAME, ZOID, EPISODE, SCREENSHOT, CALIBRATION, LOG_VERSION, \
                    EPISODE_LIMIT_REACHED, LEVELUP, PLACED, BOARD_INIT, MASK_TOGGLE, Clear, seed_sequence
6       ':evt_data1'
7       string      dependent on 5. RELEASE, PRESS, BEGIN, END, U-DOWN, ROTATE, TRANSLATE, etc.
8       ':evt_data2'
9       string      dependent on 5 and 7. might not exist (e.g. for evt_id BOARD_INIT)
'''
for i, item in enumerate(game_event):
    game_event[i][ts_ix] = float(item[ts_ix])
    
def get_next_state(timestamp):
    """return the gamestate immediately after the timestamp"""
    i = 0
    try:
        while game_state[i][ts_ix] < timestamp:
            i+=1
        return game_state[i]
    except IndexError:
        return None
        
def check_events(prevtime, currtime):
    """returns list of events between two timestamps"""
    l = []
    i = 0
    try:
        while game_event[i][ts_ix] < prevtime:
            i+=1
    except IndexError:
        return l
    #now we're at the first event after prevtime
    try:
        while game_event[i][ts_ix] < currtime:
            l.append(game_event[i])
            i += 1
        return l
    except IndexError:
        return l

#idea here is to iterate over the list of game events - in each episode, look at next (by timestamp) zoid_rep within game_state
#if zoid is at right or left edge, trigger a wall collision. Reset at either inverse translation or at episode end
wall_collision_flag = None
ep_count = 0

#NOTE: collision into walls via rotation is a thing. Need to account for it somehow :-(
#NOTE: bounce away via rotation might be a thing too

for evt in game_event:
    if evt[evt_id_ix] == "EPISODE" and evt[evt_d1_ix] == "BEGIN":
        wall_collision_flag = None
        ep_count += 1
    elif evt[evt_id_ix] == "ZOID" and evt[evt_d1_ix] == "TRANSLATE":
        if evt[evt_d2_ix] == '-1': #translate left
            if wall_collision_flag == None:
                #check zoid_rep (21)
                state = get_next_state(evt[ts_ix])
                for line in state[zoid_ix]:
                    if line[0] != 0:
                        wall_collision_flag = 'left'
                        print "left translation collision at %f (episode %d)"%(evt[ts_ix], ep_count)
                        break
            if wall_collision_flag == 'right':
                wall_collision_flag = None
                print 'translating left after right collision'
        elif evt[evt_d2_ix] == '1':
            if wall_collision_flag == None:
                #check zoid_rep (21)
                state = get_next_state(evt[ts_ix])
                for line in state[zoid_ix]:
                    if line[-1] != 0:
                        wall_collision_flag = 'right'
                        print "right translation collision at %f (episode %d)"%(evt[ts_ix], ep_count)
                        break
            if wall_collision_flag == 'left':
                wall_collision_flag = None
                print 'translating right after left collision'
    elif evt[evt_id_ix] == "ZOID" and evt[evt_d1_ix] == "ROTATE":
        state = get_next_state(evt[ts_ix])
        if wall_collision_flag == None:
            for line in state[zoid_ix]:
                if line[0] != 0:
                    wall_collision_flag = 'left'
                    print "left rotation collision at %f (episode %d)"%(evt[ts_ix], ep_count)
                    break
                elif line[-1] != 0:
                    wall_collision_flag = 'right'
                    print "right rotation collision at %f (episode %d)"%(evt[ts_ix], ep_count)
                    break
        elif wall_collision_flag == 'left':
            #left column now clear after rotation?
            clear = True
            for line in state[zoid_ix]:
                if line[0] != 0:
                    clear = False
                    break
            if clear:
                wall_collision_flag = None
                print "rotating away from left collision"
        elif wall_collision_flag == 'right':
            #right column now clear after rotation?
            clear = True
            for line in state[zoid_ix]:
                if line[-1] != 0:
                    clear = False
                    break
            if clear:
                wall_collision_flag = None
                print "rotating away from right collision"

def run_game():
    paused = False
    game_over = False
    ep_count = 0 
    i = 0
    global fps
    while i < len(game_state):
        screen.fill((200,200,200))
        print(ep_count, i)
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
                        while game_event[next_event_index][ts_ix] < game_state[i][ts_ix]:
                            next_event_index += 1
                    except IndexError:
                        pass
                    next_episode_index = next_event_index
                    try:
                        while not (game_event[next_episode_index][evt_id_ix] == "EPISODE" and game_event[next_episode_index][evt_d1_ix] == "BEGIN"):
                            next_episode_index += 1
                    except IndexError:
                        pass
                    timestamp = game_event[next_episode_index][ts_ix]
                    new_index = 0
                    try:
                        while game_state[new_index][ts_ix] < timestamp:
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
                        while game_event[next_event_index][ts_ix] < game_state[i][ts_ix]:
                            next_event_index += 1
                    except IndexError:
                        pass
                    prev_episode_index = next_event_index
                    try:
                        while not (game_event[prev_episode_index][evt_id_ix] == "EPISODE" and game_event[prev_episode_index][evt_d1_ix] == "BEGIN"):
                            prev_episode_index -= 1
                    except IndexError:
                        prev_episode_index = 0
                    ep_count -= 1
                    if game_state[i][ts_ix] - game_event[prev_episode_index][ts_ix] < 0.5:
                        #go back one more
                        prev_episode_index -= 1
                        try:
                            while not (game_event[prev_episode_index][evt_id_ix] == "EPISODE" and game_event[prev_episode_index][evt_d1_ix] == "BEGIN"):
                                prev_episode_index -= 1
                        except IndexError:
                            prev_episode_index = 0
                        ep_count -= 1
                    timestamp = game_event[prev_episode_index][ts_ix]
                    new_index = 0
                    try:
                        while game_state[new_index][ts_ix] < timestamp:
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
    
        #check between now and previous state for EPISODE BEGIN event
        if i>0:
            evts = check_events(game_state[i-1][ts_ix], game_state[i][ts_ix])
            for evt in evts:
                if evt[evt_id_ix] == "EPISODE" and evt[evt_d1_ix] == "BEGIN":
                    ep_count += 1
        screen.fill((0,0,0))
        #game_state[i][19] is board_rep
        for row in range(len(game_state[i][board_ix])):
            for column in range(len(game_state[i][board_ix][row])):
                block = game_state[i][board_ix][row][column] 
                if block != 0:
                    if block == 1:
                        screen.blit(cyan, pygame.Rect(column*20, row*20, 20, 20))
                    elif block == 2:
                        screen.blit(yellow, pygame.Rect(column*20, row*20, 20, 20))
                    elif block == 3:
                        screen.blit(purple, pygame.Rect(column*20, row*20, 20, 20))
                    elif block == 4:
                        screen.blit(green, pygame.Rect(column*20, row*20, 20, 20))
                    elif block == 5:
                        screen.blit(red, pygame.Rect(column*20, row*20, 20, 20))
                    elif block == 6:
                        screen.blit(blue, pygame.Rect(column*20, row*20, 20, 20))
                    elif block == 7:
                        screen.blit(orange, pygame.Rect(column*20, row*20, 20, 20))
                    else:
                        screen.blit(brown, pygame.Rect(column*20, row*20, 20, 20))
                    
                    #'I' 1 'O' 2 'T' 3 'S' 4 'Z' 5 'J' 6 'L' 7
               
                if game_state[i][zoid_ix][row][column] != 0 and not game_state[i][delaying_ix]:
                    screen.blit(white, pygame.Rect(column*20, row*20, 20, 20))
        screen.blit(f.render("Episode %d"%ep_count,1,(200,200,200)), (120, 6)) 
        screen.blit(f.render("FPS: %d"%fps,1,(200,200,200)), (10, 6))           
        pygame.display.flip()
        i += 1
        
if simulate:
    pygame.init()
    monitor = pygame.display.set_mode((800,600))
    screen = monitor.copy()
    screen_rect = screen.get_rect()
    pygame.display.set_caption("Meta-T Playback")
    clock = pygame.time.Clock()
    
    cyan = pygame.Surface((20,20))
    cyan.fill((64,255,255))
    yellow = pygame.Surface((20,20))
    yellow.fill((255,255,64))
    purple = pygame.Surface((20,20))
    purple.fill((255,64,255))
    green = pygame.Surface((20,20))
    green.fill((64,255,64))
    red = pygame.Surface((20,20))
    red.fill((255,64,64))
    blue = pygame.Surface((20,20))
    blue.fill((64,64,255))
    orange = pygame.Surface((20,20))
    orange.fill((255,176,64))
    brown = pygame.Surface((20,20))
    brown.fill((20,50,10))
    white = pygame.Surface((20,20))
    white.fill((250,245,250))
    
    f = pygame.font.Font(None, 18)
    run_game()

# for i in range(10):
#     print game_state[i]
# print ''
# for i in range(10):
#     print game_event[i]

#c = counter([line[3] for line in f])
#print dict(c)
#print [line for line in f if line[3] == "GAME_SUMM"]

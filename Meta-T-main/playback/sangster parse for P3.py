import os, sys
import pygame
import tkinter as tk
from tkinter import filedialog
import datetime
from collections import Counter as counter


tkroot = tk.Tk()
tkroot.withdraw()

simulate = True
fps = 60

print("Opening complete file")
start_time = datetime.datetime.now()
# 
dirname = filedialog.askdirectory(initialdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Data"))
session = dirname.split("/")[-1]
#f = open("lindstedt novice/101_2013_6_7_14-12-41.tsv").readlines()
# f = open("lindstedt intermediate/103_2013_6_11_13-55-34/103_2013_6_11_13-55-34.tsv").readlines()

print(session)
print(dirname)
print("Opening complete file")
try:
    f = open(dirname + "/" + "Complete_" + session + ".tsv").readlines()
    #ex: complete_1st_2014-3-3_11-1-27.tsv.gz
except:
    f = open(dirname + "/" + session + ".tsv").readlines()



# f = open("09_2016-3-6_11-41-46/Complete_09_2016-3-6_11-41-46.tsv").readlines()

f = [line.rstrip().split('\t') for line in f]
'''
index   value
0       ':ts'         (timestamp label)
1       float         (timestamp starting at 0)
2       ':event-type' (event-type label)
3       string        (e.g. SETUP_EVENT, GAME_EVENT, EYE_SAMP, GAME_STATE)
Everything becomes context-dependent after that.
'''
fixed_log = False
game_state = [line for line in f if line[3] == "GAME_STATE"]
if(len(game_state) == 0):
    fixed_log=True
print("Complete tsv read in after: " + str(datetime.datetime.now() - start_time))
if fixed_log:
    header = f[0]
    lines = f[1:]
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
    curr_ix = header.index("curr_zoid")
    next_ix = header.index("next_zoid")
    
    evt_id_ix = header.index("evt_id")
    evt_d1_ix = header.index("evt_data1")
    evt_d2_ix = header.index("evt_data2")
    try:
        eye_x_ix = header.index("smi_samp_x_l")
        eye_y_ix = header.index("smi_samp_y_l")
    except:
        eyedata = False
    
    game_state = [l for l in lines if l[event_type_ix] == "GAME_STATE"]
else:
    event_type_ix = lines[0].index(":event_type") + 1
    ts_ix = lines[0].index(":ts") + 1
    board_ix = game_state[0].index(":board_rep") + 1
    zoid_ix = game_state[0].index(":zoid_rep") + 1
    delaying_ix = game_state[0].index(":delaying") + 1
    dropping_ix = game_state[0].index(":dropping") + 1
    rot_ix = game_state[0].index(":zoid_rot") + 1
    col_ix = game_state[0].index(":zoid_col") + 1
    row_ix = game_state[0].index(":zoid_row") + 1
    curr_ix = game_state[0].index(":curr_zoid") + 1
    next_ix = game_state[0].index(":next_zoid") + 1

print("Game state parsed after: " + str(datetime.datetime.now() - start_time))
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
#translate appropriate data types
for i, item in enumerate(game_state):
    if not fixed_log:
        game_state[i][5] = bool(item[5])
        try:
            game_state[i][1] = float(item[1])
            game_state[i][7] = int(item[7])
            game_state[i][13] = int(item[13])
            game_state[i][15] = int(item[15])
            game_state[i][17] = int(item[17])
        except:
            print(game_state[i])
            print(game_state[i][7])
            print(game_state[i][13])
            print(game_state[i][15])
            print(game_state[i][17])
            assert False
    else:  
        game_state[i][5] = bool(item[delaying_ix])
        try:
            game_state[i][1] = float(item[ts_ix])
            game_state[i][7] = int(item[dropping_ix])
            game_state[i][13] = int(item[rot_ix])
            game_state[i][15] = int(item[col_ix])
            game_state[i][17] = int(item[row_ix])
        except:
            print(game_state[i])
            print(game_state[i][dropping_ix])
            print(game_state[i][rot_ix])
            print(game_state[i][col_ix])
            print(game_state[i][row_ix])
            assert False
    if not fixed_log:
    #the string actually starts with a ' character >:-(
        x = game_state[i][19].strip('[]\'')
    else:
        x = game_state[i][board_ix].strip('[]\'')
    x = x.split('], [')
    #list of list of strings
    x = [ele.split(', ') for ele in x]
    #convert to ints
    x = [map(int, item) for item in x]
    game_state[i][19] = x
    
    #same deal for zoid_rep
    if not fixed_log:
        x = game_state[i][21].strip('[]\'').split('], [')
    else:
        x = game_state[i][zoid_ix].strip('[]\'').split('], [')
    #list of list of strings
    x = [ele.split(', ') for ele in x]
    #convert to ints
    x = [map(int, item) for item in x]
    game_state[i][21] = x
      
game_event = [line for line in f if line[3] == "GAME_EVENT"]
f = None
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
    game_event[i][1] = float(item[1])
    
def get_next_state(timestamp):
    """return the gamestate immediately after the timestamp"""
    i = 0
    try:
        while game_state[i][1] < timestamp:
            i+=1
        return game_state[i]
    except IndexError:
        return None
        
def check_events(prevtime, currtime):
    """returns list of events between two timestamps"""
    l = []
    i = 0
    try:
        while game_event[i][1] < prevtime:
            i+=1
    except IndexError:
        return l
    #now we're at the first event after prevtime
    try:
        while game_event[i][1] < currtime:
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
    if evt[5] == "EPISODE" and evt[7] == "BEGIN":
        wall_collision_flag = None
        ep_count += 1
    elif evt[5] == "ZOID" and evt[7] == "TRANSLATE":
        if evt[9] == '-1': #translate left
            if wall_collision_flag == None:
                #check zoid_rep (21)
                state = get_next_state(evt[1])
                for line in state[21]:
                    if line[0] != 0:
                        wall_collision_flag = 'left'
                        print("left translation collision at %f (episode %d)"%(evt[1], ep_count))
                        break
            if wall_collision_flag == 'right':
                wall_collision_flag = None
                print('translating left after right collision')
        elif evt[9] == '1':
            if wall_collision_flag == None:
                #check zoid_rep (21)
                state = get_next_state(evt[1])
                for line in state[21]:
                    if line[-1] != 0:
                        wall_collision_flag = 'right'
                        print("right translation collision at %f (episode %d)"%(evt[1], ep_count))
                        break
            if wall_collision_flag == 'left':
                wall_collision_flag = None
                print('translating right after left collision')
    elif evt[5] == "ZOID" and evt[7] == "ROTATE":
        state = get_next_state(evt[1])
        if wall_collision_flag == None:
            for line in state[21]:
                if line[0] != 0:
                    wall_collision_flag = 'left'
                    print("left rotation collision at %f (episode %d)"%(evt[1], ep_count))
                    break
                elif line[-1] != 0:
                    wall_collision_flag = 'right'
                    print("right rotation collision at %f (episode %d)"%(evt[1], ep_count))
                    break
        elif wall_collision_flag == 'left':
            #left column now clear after rotation?
            clear = True
            for line in state[21]:
                if line[0] != 0:
                    clear = False
                    break
            if clear:
                wall_collision_flag = None
                print("rotating away from left collision")
        elif wall_collision_flag == 'right':
            #right column now clear after rotation?
            clear = True
            for line in state[21]:
                if line[-1] != 0:
                    clear = False
                    break
            if clear:
                wall_collision_flag = None
                print("rotating away from right collision")

def run_game():
    paused = False
    game_over = False
    ep_count = 0 
    i = 0
    global fps
    while i < len(game_state):
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
                        while game_event[next_event_index][1] < game_state[i][1]:
                            next_event_index += 1
                    except IndexError:
                        pass
                    next_episode_index = next_event_index
                    try:
                        while not (game_event[next_episode_index][5] == "EPISODE" and game_event[next_episode_index][7] == "BEGIN"):
                            next_episode_index += 1
                    except IndexError:
                        pass
                    timestamp = game_event[next_episode_index][1]
                    new_index = 0
                    try:
                        while game_state[new_index][1] < timestamp:
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
                        while game_event[next_event_index][1] < game_state[i][1]:
                            next_event_index += 1
                    except IndexError:
                        pass
                    prev_episode_index = next_event_index
                    try:
                        while not (game_event[prev_episode_index][5] == "EPISODE" and game_event[prev_episode_index][7] == "BEGIN"):
                            prev_episode_index -= 1
                    except IndexError:
                        prev_episode_index = 0
                    ep_count -= 1
                    if game_state[i][1] - game_event[prev_episode_index][1] < 0.5:
                        #go back one more
                        prev_episode_index -= 1
                        try:
                            while not (game_event[prev_episode_index][5] == "EPISODE" and game_event[prev_episode_index][7] == "BEGIN"):
                                prev_episode_index -= 1
                        except IndexError:
                            prev_episode_index = 0
                        ep_count -= 1
                    timestamp = game_event[prev_episode_index][1]
                    new_index = 0
                    try:
                        while game_state[new_index][1] < timestamp:
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
            evts = check_events(game_state[i-1][1], game_state[i][1])
            for evt in evts:
                if evt[5] == "EPISODE" and evt[7] == "BEGIN":
                    ep_count += 1
        screen.fill((0,0,0))
        #game_state[i][19] is board_rep
        for row in range(len(game_state[i][19])):
            columns = list(game_state[i][19][row])
            columns2 = list(game_state[i][21][row])
            for column in list(range(len(columns))):
                if columns[column] != 0:
                    screen.blit(blue, pygame.Rect(column*20, row*20, 20, 20))
                if columns2[column] != 0:
                    screen.blit(green, pygame.Rect(column*20, row*20, 20, 20))
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

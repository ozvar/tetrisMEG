from __future__ import division
import pygame
import sys, copy
import tkFileDialog

# class SlowButton(object):
#     def __init__(self):
#         super(SlowButton, self).__init__()
#         self.onsurface = pygame.image.load("images//slowon.png")
#         self.offsurface = pygame.image.load("images//slowoff.png")
#         self.surface = self.offsurface
#         self.rect = pygame.Rect(465,300,50,50)
#       
#     def toggle(self):
#         if self.surface == self.offsurface:
#             self.surface = self.onsurface
#             self.speed = 0.5
#         else:
#             self.surface = self.offsurface
#             self.speed = 1
#         return self.speed

      
m_filename = tkFileDialog.askopenfilename(title="Choose Tetris file", initialdir='.', filetypes=[("Merged Tetris data", '.txt')])
#m_filename = "/Users/jkl/Lab/Projects/2010_Tetris_Data/All_Tetris_Data_Collated/champion_data/2006_s16_m_2.txt"
m_log = open(m_filename).readlines()
starttime = int(m_log[0].strip('()').split(' ', 1)[0])
def process_log(log):
    """creates a new log in which each element is a list of actions within one episode"""
    newlog = []
    thisepisode=[]
    heldkeys=[]
    currenttime=0
    rflag = False
    lflag = False
    lenflag = False
    medflag = False
    strictflag = False
    hitwall = False
    translationcount = 0
    rotations = 0
    cflag = False
    ccflag = False
    bothrotationflag = False
    overflag = False
    currentpiece = ''
    episodecount = 0
    lenienttranslations = 0
    mediumtranslations = 0
    stricttranslations = 0
    bothrotationbuttons = 0
    overrotations = 0
    tag=[0,0,0,0,0] #translate lenient, medium, strict, overrotate, both rotate
    peek=0
    currentline=[]
    nextpiece=''
    currentpiece=''
    board=['(0000000000)'*20]

    for i, thisline in enumerate(log):
        currenttime = thisline[0]
        if thisline[2] == "next-piece":
            nextpiece=thisline[3]
        elif thisline[2] == "release":
            currentpiece=thisline[3]
        elif thisline[1] == 'tetris-board':
            board = thisline[2]
        elif thisline[2] == "press-left-key":
            heldkeys.append("left")
            lflag = True
            if rflag:
                #already pressed right this episode
                if not lenflag:
                    lenienttranslations += 1
                    tag[0] = 1
                    lenflag = True
                if hitwall:
                    #check for stricter criteria
                    translationcount += 1
                    if not medflag:
                        mediumtranslations += 1
                        tag[1] = 1
                        stricttranslations += 1
                        tag[2] = 1
                        medflag = True
                        strictflag = True
                    if translationcount > 3 and strictflag:
                        strictflag = False
                        tag[2] = 0
                        stricttranslations -= 1      
        elif thisline[2] == "press-right-key":
            heldkeys.append("right")
            rflag = True
            if lflag:
                #already pressed right this episode
                if not lenflag:
                    lenienttranslations += 1
                    tag[0] = 1
                    lenflag = True
                if hitwall:
                    #check for stricter criteria
                    translationcount += 1
                    if not medflag:
                        mediumtranslations += 1
                        tag[1] = 1
                        stricttranslations += 1
                        tag[2] = 1
                        medflag = True
                        strictflag = True
                    if translationcount > 3 and strictflag:
                        strictflag = False
                        tag[2] = 0
                        stricttranslations -= 1   
        elif thisline[2].find("collide-right") >= 0:
            hitwall = True
        elif thisline[2].find("collide-left") >= 0:
            hitwall = True
        elif thisline[2] == "press-down-key":
            heldkeys.append("down")
        elif thisline[2] == "press-rotate-key":
            heldkeys.append("rotate")
            cflag = True
            rotations += 1
            if ccflag:
                if not overflag:
                    overflag = True
                    bothrotationbuttons += 1
                    tag[4] = 1
            if not overflag:
                if currentpiece == 'O':
                    overflag = True
                    overrotations += 1
                    tag[3] = 1
                elif (currentpiece == "I" or currentpiece == "S" or currentpiece == "Z") and rotations > 1:
                    overflag = True
                    overrotations += 1
                    tag[3] = 1
                elif (currentpiece == "T" or currentpiece == "J" or currentpiece == "L") and rotations > 3:
                    overflag = True
                    overrotations += 1
                    tag[3] = 1
        elif thisline[2] == "press-counterrotate-key":
            heldkeys.append("counterrotate")
            ccflag = True
            rotations -= 1
            if cflag:
                if not overflag:
                    overflag = True
                    bothrotationbuttons += 1
                    tag[4] = 1
            if not overflag:
                if currentpiece == 'O':
                    overflag = True
                    overrotations += 1
                    tag[3] = 1
                elif (currentpiece == "I" or currentpiece == "S" or currentpiece == "Z") and rotations < -1:
                    overflag = True
                    overrotations += 1
                    tag[3] = 1
                elif (currentpiece == "T" or currentpiece == "J" or currentpiece == "L") and rotations < -3:
                    overflag = True
                    overrotations += 1
                    tag[3] = 1
        elif thisline[2] == "release-left-key":
            try:
                heldkeys.remove("left")
            except ValueError:
                print "Extra left at time %s"%thisline[0].lstrip("(")
        elif thisline[2] == "release-right-key":
            try:
                heldkeys.remove("right")
            except ValueError:
                print "Extra right at time %s"%thisline[0].lstrip("(")
        elif thisline[2] == "release-down-key":
            try:
                heldkeys.remove("down")
            except ValueError:
                print "Extra down at time %s"%thisline[0].lstrip("(")
        elif thisline[2] == "release-rotate-key":
            try:
                heldkeys.remove("rotate")
            except ValueError:
                print "Extra rotate at time %s"%thisline[0].lstrip("(")
        elif thisline[2] == "release-counterrotate-key":
            try:
                heldkeys.remove("counterrotate")
            except ValueError:
                print "Extra counterrotate at time %s"%thisline[0].lstrip("(")
        try:
            peek= log[i+1]
        except IndexError:
            break
        nexttime = peek[0]
        if nexttime>currenttime: #end of time block, write line
            currentline.append(currenttime)
            currentline.append(board)
            currentline.append(currentpiece)
            currentline.append(nextpiece)
            currentline.append(copy.copy(heldkeys))
            thisepisode.append(currentline)
            currentline=[]
        if thisline[2] == "end-trial": #is this where the error comes from?
            thisepisode[0].append(tag)
            tag=[0,0,0,0,0]
            rotatecount=0
            rflag = False
            lflag = False
            lenflag = False
            medflag = False
            strictflag = False
            hitwall = False
            translationcount = 0
            translationflag = False
            rotations = 0
            cflag = False
            ccflag = False
            bothrotationflag = False
            overflag = False
            currentpiece = ''
            newlog.append(thisepisode)
            thisepisode=[]
    return newlog
	#return episode_log
	#add piece x, y, rotation
	#
	#

def find_closest_eyegaze(time, gazelog):
    """for a given time in the tetris log, find the closest corresponding eyegaze entry"""
    index = 0
    for line in gazelog:
        if line[0] < time:
            index += 1
        else:
            break
    return gazelog[index]
    

#pull out eyegaze data into separate object
t_log = []
g_log = []
for line in m_log:
    entry = line.lstrip("(").rstrip(')\n').split()
    entry[0] = int(entry[0]) - starttime
    if entry[1] == "eye-gaze":
        entry[3] = int(entry[3])
        entry[4] = int(entry[4])
        g_log.append(entry)
    else:
        t_log.append(entry)

#fix eye gaze here, what's coordinate system?






#process the log to give us a new list, each element contains all the actions of one episode
episode_log = process_log(t_log)

gazetrail=[]
if len(g_log) == 0:
	print "No eye data"

playbackspeed=1
block_list=[0 for x in range(200)]

frame = pygame.image.load("images/frame.png")
framerect = frame.get_rect()
framerect.move_ip(5,42)
nextframe=pygame.image.load("images/nextframe.png")
nextframerect= nextframe.get_rect()
nextframerect.move_ip(225,172)

nextblk = pygame.image.load("images/zoid/80x40.png").get_rect()
nextblk.move_ip(nextframerect.left + nextframerect.width/2 - nextblk.width/2, nextframerect.top + nextframerect.height/2 - nextblk.height/2)
next_i = pygame.image.load("images/zoid/I.png")
next_l = pygame.image.load("images/zoid/L.png")
next_j = pygame.image.load("images/zoid/J.png")
next_t = pygame.image.load("images/zoid/T.png")
next_z = pygame.image.load("images/zoid/Z.png")
next_s = pygame.image.load("images/zoid/S.png")
next_o = pygame.image.load("images/zoid/O.png")


picker = pygame.image.load("images//picker.png")
alphapicker = pygame.surfarray.pixels_alpha(picker)
alphapicker[::]=(alphapicker*0.4).astype('b')
alphapicker=None
eyecursor = pygame.image.load("images/eyecursor.png")
alphaeye = pygame.surfarray.pixels_alpha(eyecursor)
alphaeye[::]=(alphaeye*0.80).astype('b')
alphaeye=None
eyecursorrect = eyecursor.get_rect()
pickerrect = picker.get_rect()
pickerrect.centery=530
block = pygame.image.load("images/block.png")
# lefton = pygame.image.load("images/leftbuttonon.png")
# leftoff = pygame.image.load("images/leftbuttonoff.png")
# leftrect = pygame.Rect(300,100,50,50)
# righton = pygame.image.load("images/rightbuttonon.png")
# rightoff = pygame.image.load("images/rightbuttonoff.png")
# rightrect = pygame.Rect(410,100,50,50)
# downon = pygame.image.load("images/downbuttonon.png")
# downoff = pygame.image.load("images/downbuttonoff.png")
# downrect = pygame.Rect(355,150,50,50)
# rotateon = pygame.image.load("images/rotatebuttonon.png")
# rotateoff = pygame.image.load("images/rotatebuttonoff.png")
# rotaterect = pygame.Rect(520,100,50,50)
# counterrotateon = pygame.image.load("images/counterrotatebuttonon.png")
# counterrotateoff = pygame.image.load("images/counterrotatebuttonoff.png")
# counterrotaterect = pygame.Rect(575,100,50,50)

# rewindon = pygame.image.load("images/rewindon.png")
# rewindoff= pygame.image.load("images/rewindoff.png")
# rewindrect=pygame.Rect(355,300,50,50)
# ffon= pygame.image.load("images/ffon.png")
# ffoff= pygame.image.load("images/ffoff.png")
# ffrect=pygame.Rect(520,300,50,50)

play= pygame.image.load("images/play.png")
playrect= pygame.Rect(480,300,50,50)
pause= pygame.image.load("images/pause.png")
skipon= pygame.image.load("images/skipon.png")
skipoff= pygame.image.load("images/skipoff.png")
skipsurface=skipoff
skiprect=pygame.Rect(580,300,50,50)
skipbackon= pygame.image.load("images/skipbackon.png")
skipbackoff= pygame.image.load("images/skipbackoff.png")
skipbackrect= pygame.Rect(380,300,50,50)
skipbacksurface=skipbackoff

vcontrol = pygame.Surface((25, 25))
vcontrol.fill((100, 0, 175))
vcontrolrect = pygame.Rect(488, 400, 25,25)

# slowbutton = SlowButton()

pygame.init()
#screen = pygame.display.set_mode((700,600), pygame.FULLSCREEN)
screen = pygame.display.set_mode((700,600))


#display "Parsing" text until playback begins
# font = pygame.font.Font(None, 36)
# text = font.render("Parsing", 1, (255,255,255))
# screen.blit(text, text.get_rect(centerx=screen.get_width()/2))
# pygame.display.flip()








#takes in string from logfile detailing boardstate and updates the list accordingly
def update_list(posstring):
    pos = 0
    for symbol in posstring:
        if symbol == 'O':
            pos+=1
        if symbol == 'X':
            block_list[pos]=pygame.Rect(10+(20*(pos%10)),47+(20*(pos//10)),20,20)
            pos+=1

#Hold list of tagged items in log to display tick marks along slider
numepisodes = len(episode_log)
taglist=[]
for i, each in enumerate(episode_log):
  if each[0][5] != [0,0,0,0,0]: # if it's got something: translate lenient, medium, strict, overrotate, both rotate
    taglist.append([i, each[0][5]])
tagged_episodes = [item[0] for item in taglist]
# print tagged_episodes
# print taglist
	  
lastreadtime=0
lastspeed=1
	  
episode=0
action=0
mousestate="up"
time = pygame.time.Clock()


#provisions for episodelock mode
episodelock = False
eplock_rect= pygame.Rect(skipbackrect.left + skipbackrect.width, skipbackrect.top, playrect.left - skipbackrect.left,skipbackrect.height)
eplock_color = (40, 240, 40)



#provisions for taglock mode
taglock = False
taglock_rect = pygame.Rect(playrect.left + playrect.width/2 -125, playrect.top + playrect.height + 10, 250, 15)
taglock_color = (0, 180, 0)

def find_next_tagged():
  for i, each in enumerate(episode_log[episode+1:]):
    if each[0][5] != [0,0,0,0,0]:
      return episode + 1 + i
  return episode

def find_last_tagged():
  for i in range(episode):
    if episode_log[episode-1-i][0][5] != [0,0,0,0,0]:
      return episode - 1 - i
  return episode



#provisions for playspeed indicator
playspeed_rect = pygame.Rect(playrect.left+playrect.width/2-80, playrect.top-15, 160, 10)
playspeed_color = (70, 70, 70)

momenta = [-8, -4, -2, -1, -.5, -.25, 0, .25, .5, 1, 2, 4, 8]


speedbox = pygame.Rect(480, 100, 40, 40)
epbox = pygame.Rect(530, 100, 40, 40)
actbox = pygame.Rect(580, 100, 40, 40)


eyelock = True



#main "game" loop
while True: 
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            sys.exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            sys.exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_1:
            playbackspeed= momenta[0] #-8
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_2:
            playbackspeed= momenta[2] #-2
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_3:
            playbackspeed= momenta[3] #-1
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_4:
            playbackspeed= momenta[4] #-.5
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_5:
            playbackspeed= momenta[5] #-.25
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_6:
            playbackspeed= momenta[7] #.25
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_7:
            playbackspeed= momenta[8] #.5
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_8:
            playbackspeed= momenta[9] #1
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_9:
            playbackspeed= momenta[10]#2
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_0:
            playbackspeed= momenta[12]#8
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if playbackspeed!=0:
                lastspeed=playbackspeed
                playbackspeed=0
            else:
                playbackspeed=lastspeed
        
        #Increase forward momentum
        elif event.type == pygame.KEYDOWN and (event.key == pygame.K_d or event.key == pygame.K_RIGHT):
          if playbackspeed in momenta:
            m_i = momenta.index(playbackspeed)
            if m_i + 1< len(momenta):
              playbackspeed = momenta[m_i+1]
          else:
            playbackspeed = 1
        
        #Increase backward momentum
        elif event.type == pygame.KEYDOWN and (event.key == pygame.K_a or event.key == pygame.K_LEFT):
          if playbackspeed in momenta:
            m_i = momenta.index(playbackspeed)
            if m_i - 1 >= 0:
              playbackspeed = momenta[m_i-1]
          else:
            playbackspeed = -1

        #Reverse the polarity!
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
          if playbackspeed != 0:
            playbackspeed = 0 - playbackspeed
          else:
            playbackspeed = 0 - lastspeed
        #Same functionality of NEXT button via mouse
        elif event.type == pygame.KEYDOWN and (event.key == pygame.K_s or event.key == pygame.K_DOWN):
                skipsurface=skipon
                if episode != len(episode_log):
                    if taglock:
                      episode = find_next_tagged()
                    else:
                      #if we're not at the end
                      if episode+1 >= len(episode_log):
                        pass
                      else:
                        episode+=1
                    #if we're close to the end of a trial, and going backward, skip to the end of the next trial (so we can make reverse progress
                    if playbackspeed < 0 and (episode_log[episode-1][len(episode_log[episode-1])-1][0] - lastreadtime) < 1000:
                      action=len(episode_log[episode])-1
                    else:
                      action=0
                    lastreadtime=episode_log[episode][action][0]
                    #if in episodelock mode, resume from paused
                    if episodelock:
                      playbackspeed = lastspeed
        
        #Same functionality as BACK button via mouse
        elif event.type == pygame.KEYDOWN and (event.key == pygame.K_w or event.key == pygame.K_UP):
                skipbacksurface= skipbackon
                if episode != 0:
                    #if it's been less than a second, go back
                    if (lastreadtime - episode_log[episode][0][0]) < 1000:
                      if taglock:
                        episode = find_last_tagged()
                      else:
                        episode -= 1
                      action=0
                      lastreadtime=episode_log[episode][action][0]
                    #otherwise, just repeat this trial
                    else:
                      action=0
                      lastreadtime=episode_log[episode][action][0]
                      #if in episodelock mode, resume from paused
                      if episodelock:
                        playbackspeed = lastspeed
                        
                        
                        
        #Back a step
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_COMMA:
          if playbackspeed == 0:
            if action-1 >= 0:
              action-=1
              lastreadtime = episode_log[episode][action][0]
        
        #Forward a step
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_PERIOD:
          if playbackspeed == 0:
            if action+1 < len(episode_log[episode]):
              action+=1
              lastreadtime = episode_log[episode][action][0]
            
	#skip to next tagged action
	elif event.type == pygame.KEYDOWN and event.key == pygame.K_t:
                taglock = not taglock
        
        #sets episodelock mode
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            episodelock = not episodelock
           
        #turn eyegaze data on or off
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_i:
            eyelock = not eyelock
 
        elif (event.type == pygame.MOUSEBUTTONDOWN and mousestate!="moving"): # or event.type == pygame.KEYDOWN:
            mousestate="down"
            # if slowbutton.rect.collidepoint(pygame.mouse.get_pos()):
            #   playbackspeed = slowbutton.toggle()
            if skiprect.collidepoint(pygame.mouse.get_pos()): #or event.key == pygame.K_s:
                skipsurface=skipon
                if episode != len(episode_log):
                    episode+=1
                    action=0
                    lastreadtime=episode_log[episode][action][0]
                    #if in episodelock mode, resume from paused
                    if episodelock:
                      playbackspeed = lastspeed
            elif skipbackrect.collidepoint(pygame.mouse.get_pos()): #or event.key == pygame.K_w:
                skipbacksurface= skipbackon
                if episode != 0:
                    #if it's been less than a second, go back
                    if (lastreadtime - episode_log[episode][0][0]) < 1000:
                      episode -= 1
                      action=0
                      lastreadtime=episode_log[episode][action][0]
                    #otherwise, just repeat this trial
                    else:
                      action=0
                      lastreadtime=episode_log[episode][action][0]
                      #if in episodelock mode, resume from paused
                      if episodelock:
                        playbackspeed = lastspeed
                  
            elif playrect.collidepoint(pygame.mouse.get_pos()):
                if playbackspeed!=0:
                    playbackspeed=0
                    vcontrolrect.centerx = 400
                else:
                    playbackspeed=1
                    vcontrolrect.centerx = 500
        elif event.type == pygame.MOUSEBUTTONUP:
            if mousestate == "vel":
                vcontrolrect.centerx = 500
                playbackspeed = 1
            mousestate="up"


    if mousestate=="down" and pickerrect.collidepoint(pygame.mouse.get_pos()):
        mousestate="moving"

    if mousestate=="down" and vcontrolrect.collidepoint(pygame.mouse.get_pos()):
        mousestate="vel"

    if mousestate=="moving": #dragging to right edge gives IndexError
        lastspeed=playbackspeed
        playbackspeed=0
        mousex=pygame.mouse.get_pos()[0]
        if mousex<31: mousex=31
        if mousex>669: mousex=669
        pickerrect.centerx = mousex
        action=0
        episode=int((mousex-30)*numepisodes/640)
        lastreadtime=episode_log[episode][action][0]
    else:
        pickerrect.centerx = (episode*640/numepisodes + 30) 

    if mousestate == "vel":
        mousex=pygame.mouse.get_pos()[0]
        if mousex<262: mousex=262
        if mousex>638: mousex=638
        vcontrolrect.centerx = mousex
        #adjust playback speed:  262 = -max, 400 = 0, 500 = 1, 638 = max (10?)
        if mousex == 400:
            playbackspeed = 0
        elif mousex == 500:
            playbackspeed = 1
        elif 401 <= mousex <= 499:
            playbackspeed = (mousex - 400)/100.0
        elif 262 <= mousex <= 399: #-10 to -0.01
            playbackspeed = -1
            #playbackspeed = (262 - mousex)/13.7 #137 pixels in the bar section's range
        else: #1.01 to 11
            playbackspeed = (mousex - 501)/13.8 + 1
        
        

    currentaction = episode_log[episode][action]
    currentgaze = find_closest_eyegaze(currentaction[0], g_log)

    update_list(currentaction[1]) #updates block_list

	#figure out where eyetracking cursor should be
    # if currentaction[0] > gazelog.currentgaze[1]:
    #   gazelog.increment()
    #   gazelog.tag=0
    # if (gazelog.currentgaze[0] <= currentaction[0] <= gazelog.currentgaze[0]) and gazelog.tag==0:
    #eyecursorrect.centerx = currentgaze[3]/1.92 - 184 #1.92 = 768/400
    #eyecursorrect.centery = currentgaze[4]/2.1787 #2.1787 = 1024/470

    eyecursorrect.centerx = (currentgaze[3]-204)/2.1787 - 5 
    eyecursorrect.centery = currentgaze[4]/2.1787 - 8 

    gazetrail.append([eyecursorrect.centerx, eyecursorrect.centery])
    while len(gazetrail) > 10:
        gazetrail.pop(0)
    # gazelog.tag=1

#700 by 600 window

    screen.fill((35,35,35))    



    #frame is 210 x 410, at 5, 42
    framecolor = (255,255,255)
    

    #draw speed indicator
    pygame.draw.rect(screen, playspeed_color, playspeed_rect, 0)
    pygame.draw.line(screen, (100, 100, 100), (playspeed_rect.left + playspeed_rect.width/2, playspeed_rect.top-5), (playspeed_rect.left + playspeed_rect.width/2, playspeed_rect.top+playspeed_rect.height))

    #if we have some speed
    if playbackspeed in momenta:

      #get speed level for meter
      speed_w = playspeed_rect.width / len(momenta)
      speed_h = playspeed_rect.height*abs(playbackspeed)
      speedrect = pygame.Rect(playspeed_rect.left + (momenta.index(playbackspeed) * speed_w), playspeed_rect.top + playspeed_rect.height - speed_h, speed_w, speed_h)
      
      #get ghost of the speed in memory
      lspeed_h = playspeed_rect.height*abs(lastspeed)
      lastspeedrect = pygame.Rect(playspeed_rect.left + (momenta.index(lastspeed) * speed_w), playspeed_rect.top + playspeed_rect.height - lspeed_h, speed_w, lspeed_h)

      #draw!
      pygame.draw.rect(screen, (40, 40, 40), lastspeedrect, 0)
      pygame.draw.rect(screen, (0, 200, 120), speedrect, 0)

      
    #
    

    #draw episodelock indicator
    if episodelock:
      pygame.draw.rect(screen, eplock_color, eplock_rect, 0)
    else:
      pygame.draw.rect(screen, (0, 0, 0), eplock_rect, 0)
    


    #draw taglock indicator
    if taglock:
      pygame.draw.rect(screen, (0, 0, 0), taglock_rect, 0)
    else:
      pygame.draw.rect(screen, (30, 30, 30), taglock_rect, 0)
    

    #screen.blit( Font.render(playbackspeed, False, (255, 255, 255)), speedbox)
    pygame.draw.rect(screen, (0,0,0), speedbox, 0) 
    pygame.draw.rect(screen, (0,0,0), epbox, 0) 
    pygame.draw.rect(screen, (0,0,0), actbox, 0)
    

    #draw epistemic episodes on position bar by showing tagged items as hash marks
    if not taglock:
      pygame.draw.line(screen, (255,255,255), (30,530), (670, 530), 2)
    tag_inc = 0
    for each in taglist:
        if each[1][2]: #strict translation
            color = (255,0,0) #red
        elif each[1][1]: #medium translation
            color = (255,255,0) #yellow
        elif each[1][0]: #lenient translation 
            color = (0,128,0) #green
        
        #draw if one exists
        if each[1][0] or each[1][1] or each[1][2]:
	        pygame.draw.line(screen, color, (each[0]*640/numepisodes + 30,510), (each[0]*640/numepisodes + 30, 530))
	        #if taglock is on, draw the tags smashed together to indicate meaning of taglock mode
	        if taglock:
	          pygame.draw.line(screen, color, (taglock_rect.left + 2*tag_inc, taglock_rect.top), (taglock_rect.left + 2*tag_inc, taglock_rect.top + taglock_rect.height/2))
            
        if each[1][3] and each[1][4]: #both over and both rotation
            color = (255, 0, 255) #Fuchia
        elif each[1][3]: #over rotation
            color = (0, 128, 128) #teal
        elif each[1][4]: #both rotations
            color = (0, 0, 255) #blue
        
        #draw if one exists
        if each[1][3] or each[1][4]:
    	    pygame.draw.line(screen, color, (each[0]*640/numepisodes + 30,530), (each[0]*640/numepisodes + 30, 550))
    	    if taglock:
    	      pygame.draw.line(screen, color, (taglock_rect.left + 2*tag_inc, taglock_rect.top+taglock_rect.height/2), (taglock_rect.left + 2*tag_inc, taglock_rect.top + taglock_rect.height))
    	tag_inc += 1
    

    #change color of frame if we're on an epistemic episode
    if episode in tagged_episodes:
        index = tagged_episodes.index(episode) #find which element in the taglist corresponds to the current episode
        if taglist[index][1][0]: #lenient
            framecolor = (0, 255, 0)
        if taglist[index][1][1]: #medium
            framecolor = (255, 255, 0)
        if taglist[index][1][2]: #strict
            framecolor = (255, 0, 0)
        if taglist[index][1][3]: #over
            framecolor = (0, 128, 128)
        if taglist[index][1][4]: #both
            framecolor = (0, 0, 255)
    pygame.draw.lines(frame, framecolor, 1, [(0,0), (209, 0), (209, 409), (0, 409)], 8)
    screen.blit(frame, framerect)
    screen.blit(nextframe, nextframerect)

    #draw blocks
    for eachrect in block_list:
        if(eachrect != 0):
            screen.blit(block,eachrect)

	#draw icons		
	# if "left" in currentaction[4]:
	#      screen.blit(lefton,leftrect)
	#  else:
	#      screen.blit(leftoff,leftrect)
	#  if "right" in currentaction[4]:
	#      screen.blit(righton,rightrect)
	#  else:
	#      screen.blit(rightoff,rightrect)
	#  if "down" in currentaction[4]:
	#      screen.blit(downon,downrect)
	#  else:
	#      screen.blit(downoff,downrect)
	#  if "rotate" in currentaction[4]:
	#      screen.blit(rotateon,rotaterect)
	#  else:
	#      screen.blit(rotateoff,rotaterect)
	#  if "counterrotate" in currentaction[4]:
	#      screen.blit(counterrotateon,counterrotaterect)
	#  else:
	#      screen.blit(counterrotateoff,counterrotaterect)
	
    screen.blit(skipbacksurface,skipbackrect)
    if skipbacksurface == skipbackon:
    	skipbacksurface = skipbackoff
	    
    nxt = episode_log[episode][action][3]
    if nxt=="I":
		screen.blit(next_i, nextblk) 
    elif nxt=="L": 
		screen.blit(next_l, nextblk)
    elif nxt=="J":
		screen.blit(next_j, nextblk)
    elif nxt=="T":
		screen.blit(next_t, nextblk)
    elif nxt=="Z":
		screen.blit(next_z, nextblk)
    elif nxt=="S":
		screen.blit(next_s, nextblk)
    else: #elif nxt=="O":
		screen.blit(next_o, nextblk)


    # if mousestate == "down" and rewindrect.collidepoint(pygame.mouse.get_pos()):
    #   screen.blit(rewindon, rewindrect)
    #   playbackspeed=-1
    # elif mousestate=="up" and rewindrect.collidepoint(pygame.mouse.get_pos()):
    #   screen.blit(rewindoff,rewindrect)
    #   playbackspeed=1
    # else:
    #   screen.blit(rewindoff,rewindrect)

    if playbackspeed==0:
        screen.blit(pause,playrect)
    else:
        screen.blit(play,playrect)

    # screen.blit(slowbutton.surface, slowbutton.rect)
    # 
    # if mousestate == "down" and ffrect.collidepoint(pygame.mouse.get_pos()):
    #   screen.blit(ffon, ffrect)
    #   playbackspeed=5
    # elif mousestate=="up" and ffrect.collidepoint(pygame.mouse.get_pos()):
    #   screen.blit(ffoff,ffrect)
    #   playbackspeed=1
    # else:
    #   screen.blit(ffoff, ffrect)

    screen.blit(skipsurface,skiprect)
    if skipsurface == skipon:
        skipsurface=skipoff

    screen.blit(picker,pickerrect)	


	#hiding VControl
    ##draw velocity control - indigo!
    #pygame.draw.lines(screen, (74,0,130), 1, [(250, 400), (650, 400), (650, 425), (250, 425)], 2)
    #screen.blit(vcontrol, vcontrolrect)
    ##hash marks for speed = 0 and = 1
    #pygame.draw.line(screen, (150,0, 250), (400, 400), (400, 425), 2)
    #pygame.draw.line(screen, (150,0, 250), (500, 400), (500, 425), 2)



    if eyelock:
      #eyecursorrect.centerx, eyecursorrect.centery = 50, 200
      screen.blit(eyecursor, eyecursorrect)
      #print gazetrail
      if len(gazetrail) > 1:
          for i, each in enumerate(gazetrail):
              if i+1 != len(gazetrail):
                  #want green level of gazetrail to range from ~50 to 200 in increments of 15
                  #until list is length of 10, need to "cut off" dim values (higher i = "brighter" trail)
                  pygame.draw.line(screen, (0, 200-15*len(gazetrail)+15*i, 0), (each[0], each[1]), (gazetrail[i+1][0], gazetrail[i+1][1]))
                  
                  
    pygame.display.flip()
    
    
    

    #clear block_list
    block_list = [0 for x in range(200)]

    #get next action - if end of episode, get first action in next episode
    delta = time.tick(60)

    if playbackspeed > 0:
        lastreadtime+= delta * playbackspeed
        if lastreadtime > episode_log[episode][action][0]: #time of current action
            if action+1 >= len(episode_log[episode]): #end of episode
              #if episodelock mode, stop at the end of an episode
              if episodelock:
                lastspeed = playbackspeed
                playbackspeed = 0
              else:
                if episode+1 >= len(episode_log): #end of game
                    lastspeed = playbackspeed
                    playbackspeed = 0
                    pass
                else:
                    if taglock:
                      episode = find_next_tagged()
                    else:
                      episode+=1
                    action=0
              #update concept of time
              lastreadtime = episode_log[episode][action][0]
            else:
                action+=1
    elif playbackspeed<0: #don't bother with timing, just go one action at a time
        #Bothering with timing.
        lastreadtime+= delta * playbackspeed
        if lastreadtime < episode_log[episode][action][0]:
          if action ==0: #beginning of episode
            #if episodelock mode, stop at the start of an episode
            if episodelock:
              lastspeed = playbackspeed
              playbackspeed = 0
              #lastreadtime = episode_log[episode][action][0]
            else:
              if episode == 0: #beginning of game
                  lastspeed = playbackspeed
                  playbackspeed = 0
                  pass
              else:
                  if taglock:
                    episode = find_last_tagged()
                  else:
                    episode-=1
                  action = len(episode_log[episode])-1
            #update concept of time
            lastreadtime = episode_log[episode][action][0]
          else:
              action-=1

    #print playbackspeed

#end main game loop
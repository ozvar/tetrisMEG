The following are all of the currently implemented parameters specifiable in a .config file.
The default assignment is shown, followed by the variable's type, and description.
    variable_name = default_value [type]
    - description
e.g.:
    SID = Test [string]
    - sets the subject ID, as specified by the experimenter.
    
    The subject ID (SID) is of type [string] and defaults to "Test". 
    

[integer] requires whole numbers.
[integer list] accept whole numbers separated by commas.
[color] accepts precisely three whole numbers (red, green, blue values between 0 and 255), separated by commas.
[float] can accept decimal points.
[string] does not require quotation marks ("") around the item. 
    e.g. when specifying the logging directory, entering:
        logdir = data
    is preferable to 
        logdir = "data"
[boolean] accepts true, t, yes, or y as a True value (case ignored). All others are considered false.
    e.g. when specifying full screen mode:
        fullscreen = y (or) fullscreen = True
    will enable full screen mode, while
        fullscreen = no (or) fullscreen = f (or) fullscreen = abcd (or) fullscreen = Tru
    will all evaluate to false, disabling full screen mode.

Some parameters allow only a small set of values, as specified in their descriptions. 


Logging

    logdir = data [string]
    - specify the logging directory for new data files (within the root package).

    fixed_log = True [boolean]
    - use fixed column width logging format. Disable for keyword-access format.

    ep_log = True [boolean]
    - enable an additional reduced-form log storing only episode- and game-summaries.
    game_log = True [boolean]
    - enable an additional reduced-form log storing only game-summaries.
    
    ep_screenshots = False [boolean]
    -enable screenshots to be taken at the end of each episode.

Identifiers
    SID = Test [string]
    - sets the subject ID, as specified by the experimenter.
    
    RIN = 000000000 [string]
    - sets an encrypt-able universal identifier (school ID or SSN).
    
    ECID = NIL [string]
    - sets the experimental condition ID, if know at runtime.

    game_type = standard [string]
    - sets the game type label, as specified by the experimenter.


Rules and scoring

    game_ht = 20 [integer]
    - set number of rows in game space.
    
    game_wd = 10 [integer]
    - set number of columns in game space.

    lines_per_lvl = 10 [integer]
    - set the number of lines to be cleared before difficulty increases
        
    scoring = 40,100,300,1200,6000 [integer list]
    - set the default value (at level 0) of clearing 1, 2, 3, 4 (or 5 in Pentix) lines.
    
    drop_bonus = True [boolean]
    - enable a small point bonus for dropping manually dropping the zoid.
    
    starting_level = 0 [integer]
    - set the game's starting level.

    continues = 0 [integer]
    - set number of games to be played.
    - 0 allows for infinite games.

    time_limit = 3600 [integer]
    - set time limit in seconds
    - defaults to one hour

    max_eps = -1 [integer]
    - maximum episodes allowed per game.
    - set to -1 for infinite episodes.

    tetris_zoids = True [boolean]
    - enable the normal Tetris zoids (the 4-segment "IOTSZJL" set)
    
    pentix_zoids = False [boolean]
    - enable a set of additional, larger zoids (5 segments)
    
    tiny_zoids = False [boolean]
    - enable a set of additional, smaller zoids (1, 2, and 3 segments)
    
    
    

Timing

    fps = 30 [integer]
    - set number of frames drawn per second. 
    - higher values are more processor intensive. lower values are more distracting.
    
    tps = 60 [integer]
    - set number of "ticks" per second, i.e. how often the game logic updates. 
    - higher values result in faster gameplay, regardless of the value of fps.
    - defaults are advised.
    
    gravity = True [boolean]
    - enables time pressured difficulty, i.e. whether or not the zoid drops automatically.
    
    intervals = 48, 43, 38, 33, 28, 23, 18, 13, 8, 6, 5, 5, 5, 4, 4, 4, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1 [integer list]
    - set the difficulty for each game level, i.e. speed at which the zoid naturally falls.
    - measured in "ticks". If "tps" is set to 60, a value of 30 results in a zoid dropping two rows per second.
 
 
 
Game controls
 
    pause_enabled = true [boolean]
    - enables pausing the game
    - default key is P
    
    two_player = False [boolean]
    - enables two-player mode, in which one player controls rotations while the other controls translations and dropping.
    
    joystick_type = NES_RETRO-USB [string]
    - set the type of joystick to be used. Supports classic Nintendo Entertainment System USB controllers
    - accepts only NES_RETRO-USB or NES_TOMEE-CONVERTED

    undo = False [boolean]
    - allows the player to undo all zoid movement this episode up to, but not including, a zoid placement.
    - default key is R
    
    zoid_slam = False [boolean]
    - allows player to instantaneously "slam" the zoid down its current column into the pile.
    - default key is Spacebar
    
    keep_zoid = False [boolean]
    - allows the player to "keep" a zoid to be switched out later for better placement.
    - default key is E
    
    wall_kicking = False [boolean]
    - enables zoid rotations to "kick" off of walls or the pile
    - rotations that would normally fail due to collision are bumped left or right.
    
    drop_interval = 2 [integer]
    - set the speed at which the player may manually drop the zoid.
    - default values result in a zoid being able to be dropped at 30 rows per second.

    das_delay = 16 [integer]
    - time in "ticks" the left or right key must be held before "delayed auto shift" begins
    - default values result in waiting 4/15
    
    das_repeat = 6 [integer]
    - number of "ticks" between automatic column translations once "delayed auto shift" begins
    - default values result in 10 columns per second
    
    das_chargeable = true [boolean] 
    - enable the player to hold the key before a zoid appears to prepare a "delayed auto shift" in advance
    
    das_reversible = true [boolean] 
    - enable the player to move the zoid in the opposite direction, but preserve the "delayed auto shift" speed.

    are_delay = 10 [integer]
    - sets the delay before a new zoid enters play, measured in ticks.
    - defaults to 1/6 of a second
        
    lc_delay = 20 [integer]
    - sets the animation duration for line clears, adding to the are_delay.
    - defaults to 1/3 or a second


Randomness
    
    fixed_seeds = false [boolean]
    - specify whether to use a fixed set of random seeds at all.
    
    random_seeds = 1, 22, 3000000, 456789 [integer list]
    - specify which, if any, random seeds to use. 

    permute_seeds = true [boolean]
    - specify whether to randomize the order of the chosen random seeds.
    
    seven_bag_switch = False [boolean]
    - enable the 7-bag zoid randomization mode
    - guarantees all 7 default zoid types will appear in each set of 7 zoids presented.

Look-ahead
    look_ahead = 1 [integer]
    - sets how many upcoming zoids are displayed
    - currently only accepts 0 and 1
    
    far_next = False [boolean]
    - if enabled, moves the Next Box (look_ahead) to the far right of the screen.
    
    next_dim = False [boolean]
    - if enabled, dims the next box with transparency
    
    next_dim_alpha = 50 [integer]
    - sets how dim the next box should be, if dimmed.

    next_mask = False [boolean]
    - if enabled, places a mask over the next box that must be removed
    - default key for removal is Q
    
    board_mask = False [boolean]
    - if enabled, masks the board while the Q key is held, forcing players to focus on one or the other.

Audio
    music_vol=0.5 [float]
    - set the volume of the music. 
    - 0.0 is muted, 1.0 is full.
    
    sfx_vol=1.0 [float]
    - set the volume of the sound effects.
    - 0.0 is muted, 1.0 is full.
    
    song=gb-a [string]
    - set the game's song. 
    - choose from: gb-a, gb-b, nes-a, nes-b, nes-c



Video and display

    fullscreen = False [boolean]
    - set the game to fill up the display

    bg_color = 0,0,0 [color]
    - set the background color of the game space

    border_color = 250,250,250 [color]
    - set the border color of the game space

    kept_bgc = 50,50,50 [color]
    - set the background color of the "kept zoid" area, if enabled.

    gridlines_x = False [boolean]
    - enable perceptually helpful lines along the columns
    
    gridlines_y = False [boolean]
    - enable perceptually helpful lines along the rows
    
    gridlines_color = 50,50,50 [color]
    - set color for any gridlines
    
    show_high_score = False [boolean]
    - display the highes game score from this session

    inverted = False [boolean]
    - invert the game space such that up and down are reversed (zoids fall up!)

    visible_board = True [boolean]
    - disable to make the pile invisible
    
    visible_zoid = True [boolean]
    - disable to make the zoid invisible
    
    board_echo_placed = True [boolean]
    - enable to make the pile temporarily visible when a zoid is placed
    
    board_echo_lc = True [boolean]
    - enable to make the pile temporarily visible when a line is cleared

    dimtris = False [boolean]
    - enable to make the pile gradually disappear as the difficulty level rises
    
    dimtris_alphas = 255,225,200,175,150,125,100,75,50,25,0 [integer list]
    - set the transparency values (0 - 255) for dimtris mode
    
    ghost_zoid = False [boolean]
    - enable a helpful ghost zoid
    - shows where the zoid would end up if dropped from the current column

    
    
    
    
Artificial Intelligence

    controller = dellacherie [string]
    - set the controller to be used for AI decisions
    - default controller attempts to optimize simple line-clearing behavior
    - select from the /controllers directory (omit .control)

    solve_button = false [boolean]
    - enables a keypress to automatically "solve" the current zoid according to the AI controller chosen.
    - solve key is N, press M to enable auto-solve mode.
    
    auto_solve = false [boolean]
    - enables a self-playing, automatic solving game mode, determined by the AI controller chosen.

    hint_zoid = false [boolean]
    - displays a dim zoid, similar to the ghost_zoid, at the location chosen by the AI controller.
    
    hint_button = false [boolean]
    - enables a hint to be displayed only if desired by keypress. Designed for training.
    - hint key is H.
    
    hint_release = True [boolean]
    - enables the hint to be seen only while the hint key is held.
    
    hint_limit = -1 [integer]
    - sets a limit for the number of hints allowed per game.
    - set to -1 for unlimited hints.



Classic experiments

    n_back = False [boolean]
    - enables a mode where zoids are only placed if they match the zoid placed n-many back
    
    nback_n = 2 [integer]
    - sets the n for n_back mode

    ax_cpt = False [boolean]
    - enables a mode wherein if a target zoid follows a cue zoid, it is not placed and instead vanishes
    
    ax_cue = O [string]
    - sets the cue zoid for ax_cpt mode
    - choose from I, O, T, S, Z, J, and L
    
    ax_target = I [string]
    - sets the target zoid fro ax_cpt mode
    - choose from I, O, T, S, Z, J, and L
    
    


Eyetracking
    
    
    draw_samps = False [boolean]
    draw_avg = False [boolean]
    draw_fixation = False [boolean]
    draw_err = False [boolean]
    gaze_window = 30 [integer]
    
    spotlight = False [boolean]
    spot_radius = 350 [integer]
    spot_color = 50,50,50
    spot_alpha = 255 [integer]
    spot_gradient = True [boolean]

    eye_conf_borders = false [boolean]
    
    eye_mask = False [boolean]




Deprecated or unimplemented

    grace_period = 0 [integer]
    - a grace period counter allowing a block to "sit" on the pile briefly before it would be locked into place.
    - unimplemented
    
    grace_refresh = False [boolean]
    - would enable keypresses to refresh the grace period
    - unimplemented
        
    feedback_mode = False [boolean]
    - would display various behavioral stats from the log as immediate feedback to the player.
    - unimplemented

    misdirection = False [boolean]
    - eyetracking mode wherein saccades away from the game board would alter it
    - unimplemented
    
    distance_from_screen = -1.0 [float] 
    - distance in centimeters of the eyes from the screen
    - deprecated, unused

    das_delay_ms = 266 [integer]
    - time in milliseconds after keypress until the "delayed auto shift" begins
    - deprecated, unused
    
    das_repeat_ms = 100 [integer]
    - time between automatic column "shifts" after "delayed auto shift" begins
    - deprecated, unused
    
    
    
Tetris
======

A PyGame/Twisted implementation of Tetris designed for Cognitive Science research.

Copyright
---------
GPL-3


Features
--------

* Extremely detailed logging
* Support for SMI eye trackers

Gameplay
--------

Arrange the blocks to fill and clear lines horizontally. 

Arrow keys (or WASD):
  - Left and Right: translate zoid left or right one column
  - Up and Shift + Up: rotate zoid clockwise / counterclockwise, respectively.
  - Down: Drop zoid quickly into place.

Q: When Masks are enabled, toggles mask

E: When Kept-Zoid is enabled, keeps or swaps current zoid

R: When Undo is enabled, resets current zoid to its starting position

Esc: Ends game cleanly and immediately.

P: Pauses game

Spacebar: Advances screen prompts
    - When zoid-slamming is enabled, slams zoid to bottom of screen
    - When gravity is disabled, confirms placement of zoid

I: Take screenshot of current world-surface, put in ./screenshots

Usage
-----

Use .config files in the /config directory to manipulate the gameplay.

    > python tetris.py -c [filename without .config extension]

The list of config files includes:

    default.config
    inverted.config
    lockout.config
    modern.config
    pentix.config
    rational.config
    test.config [good for figuring out what parameters do]

Example:

    To run the default NES version of the game, 
    
        > python tetris.py -c default
        
    To run the game of Pentix,
    
        > python tetris.py -c pentix



Custom Config files:

    In a blank text document, simply define each parameter on its own line.
        - Title the document [your_version_name].config
        - Comments can be added after any # symbol
        - Empty lines are ignored
        - Omitted parameters are set to the default NES values
    
    [Refer to /configs/default.config for parameter explanations and default values]
        
    Example:
    
        To make a game with double the board height and width: 
        
        Filename: doublesized.config
        +-------------------------
        |
        |#double width
        |game_wd = 20
        |
        |#double height
        |game_ht = 40
        |
        |
        |
        
        Save this file in the /configs directory.
        
        To run this configuration:
        
        > python tetris.py -c doublesized
    
        
    




Argument Overrides from command line:  

usage: tetris.py [-h] [-c CONFIG_NAME] [-L LOGFILE] [-d LOGDIR]
                 [-F FULLSCREEN] [-s {gb-a,gb-b,nes-a,nes-b,nes-c}]
                 [--music_vol MUSIC_VOL] [--sfx_vol SFX_VOL] [-ct CONTINUES]
                 [-wd GAME_WD] [-ht GAME_HT] [-la LOOK_AHEAD] [-g GRAVITY]
                 [-sd DISTANCE_FROM_SCREEN] [-id SID] [--stats]

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG_NAME, --config CONFIG_NAME
                        Set the filename of the .config file to be used
                        (default: default)
  -L LOGFILE, --logfile LOGFILE
                        Pipe results to given filename; "[year_month_day_hour-
                        min-sec].tsv" by default. (default:
                        2012_10_31_13-21-38)
  -d LOGDIR, --logdir LOGDIR
                        Logging directory; "./data" by default. (default:
                        None)
  -F FULLSCREEN, --fullscreen FULLSCREEN
                        Run in fullscreen mode. (default: None)
  -s {gb-a,gb-b,nes-a,nes-b,nes-c}, --song {gb-a,gb-b,nes-a,nes-b,nes-c}
                        Background song/music to play. (default: None)
  --music_vol MUSIC_VOL
                        Set music volume. (default: None)
  --sfx_vol SFX_VOL     Set sound effects volume. (default: None)
  -ct CONTINUES, --continues CONTINUES
                        Sets number of games to be played this session. Set to
                        0 for infinite. (default: None)
  -wd GAME_WD, --width GAME_WD
                        Sets width of game board; 10 by default (change to 16
                        for Pentix default) (default: None)
  -ht GAME_HT, --height GAME_HT
                        Sets height of game board; 20 by default (change to 25
                        for Pentix default) (default: None)
  -la LOOK_AHEAD, --lookahead LOOK_AHEAD
                        Sets look-ahead, i.e. next box; 0 = none, 1 = default,
                        2... = not yet implemented (default: None)
  -g GRAVITY, --gravity GRAVITY
                        Sets or removes gravity; 0 = Rational mode, 1 =
                        Default time pressure (default: None)
  -sd DISTANCE_FROM_SCREEN, --screen_dist DISTANCE_FROM_SCREEN
                        Set distance (in inches) from screen for fixed-
                        placement eyetrackers. Defaults to standard distance
                        of 22 in. (default: None)
  -id SID, --SID SID    Set subject ID. (default: None)
  --stats               Show board optimality metrics (default: False)



Priority is:
    1. Argument overrides from command line
        - for experimenter twiddling and testing or session-variables like Subject ID
    2. Config file settings
        - use these for stable, reusable combinations of factors.
    3. Defaults, hard coded
        - all default values are according to the original NES specifications.




Data output
-----------

Outputs game event data and game state data into a timestamped data file in /Data. 

History file includes:
    - game mechanics definitions, 
    - element locations, 
    - experimental manipulation condition,
    - as well as session variables (subject ID, eyetracker distance)

Includes:
 - game mode variables
 - game element location variables (x,y,wd,ht)
 - level and score variables
 - whole game board representation
 - game board statistics
 - among several others.



Desgin References
-----------------

* `Official Tetris Guidelines`_
* `Super Rotation System`_.


.. _`Official Tetris Guidelines`: http://tetris.wikia.com/wiki/Tetris_Guideline
.. _`Super Rotation System`: http://tetris.wikia.com/wiki/SRS

License
-------

This work is licensed under a GNU GENERAL PUBLIC LICENSE, Version 3 (29 June 2007). 
For a complete version of the license, see file COPYING in the root directory.

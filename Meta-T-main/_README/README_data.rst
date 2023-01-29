This readme details the values produced by the MultiTetris system in the output logs.


                        
ts	- time stamp in seconds since the beginning of the session
event_type	- designates the type of entry this row represents in the log
SID	- the Subject ID
ECID	- the Experimental Condition ID
session	- the date and time of the start of the session
game_type	- the game type label
game_number	- the number of the current game this session
episode_number	- the number of the current episode this game
level	- the current level this game
score	- the current score this game
lines_cleared	- the number of lines cleared this game
tetrises_game	- number of tetrises scored this game
tetrises_level	- number of tetrises scored this level

Game summary
completed	- whether or not a game was completed or terminated early (manually or by failure)
game_duration	- length in seconds of the game
avg_ep_duration	- length of the average episode this game
zoid_sequence	- the exact sequence of zoids seen this game (of the types I, O, T, S, Z, J, and L)

Immediate event data
evt_id	- the ID of the current event. This is highly flexible and depends on the event.
evt_data1	- the first value of the current event. depends heavily on evt_id
evt_data2	- the second value of the current event. depends heavily on evt_id

Game state information
curr_zoid	- the current zoid this episode (of I, O, T, S, Z, J, and L)
next_zoid	- the upcoming zoid for the next episode (of I, O, T, S, Z, J, and L)
danger_mode	- whether the maximum height of any one column is greater than 15 (game music speeds up!)
delaying	- whether the game is currently delaying, waiting for a new zoid to appear
dropping	- whether the player is currently dropping the zoid
zoid_rot	- current rotation of the zoid (between 0 and 3 for T, J, and L; 0 and 1 for I, S, and Z; 0 for O)
zoid_col	- current column of the upperleft-most square of the zoid's bounding box
zoid_row	- current row of the upperleft-most square of the zoid's bounding box
board_rep	- exact visual representation of the pile (without the current zoid)
zoid_rep	- exact visual representation of the zoid's current position.

Episode summary
evt_sequence	- sequences of keypresses and events taken this episode. 
rots	- number of rotations performed
trans	- number of translation (left or right) performed
path_length	- total number of rotations and translations
min_rots	- minimum possible rotations to reach destination
min_trans	- minimum possible translations to reach destination
min_path	- minimum possible total path to reach destination
min_rots_diff	- number of unnecessary rotations
min_trans_diff	- number of unnecessary translations
min_path_diff	- total number of unnecessary rotations and translations
u_drops	- number of rows the zoid traversed due to player dropping
s_drops	- number of rows traversed by the zoid due to system gravity
prop_u_drops	- proportion of user-initiated row traversals to total row traversals
initial_lat	- latency in milliseconds of the first keypress in an episode
drop_lat	- latency in milliseconds until zoid is dropped in an episode
avg_lat	- average latency between keypresses this episode


Features

These are numerical features of the state of the pile and each zoid's placement.
Many of these features are only subtly different from one another, but some argue that these subtle differences would differentiate skilled performance.
All of these features have been used in Artificial Intelligence work to train artificial controllers to maximize different decisions. 
Many of these controllers are capable of clearing millions of lines in a single game!

mean_ht	- mean height of all columns
max_ht	- highest height of any one column
min_ht	- height of the shortest column
all_ht	- sum of the height of all columns.
max_ht_diff	- difference between max_ht and mean_ht
min_ht_diff	- differnce between mean_ht and min_ht
column_9	- height of the 9th column

cleared	- number of lines cleared by this zoid placement
cuml_cleared	- cumulatively weighted number of lines cleared (1=1, 2=1+2, 3=1+2+3...)
tetris	- whether or not a tetris was scored by this zoid placement
move_score	- points scored by this zoid placement (needs line clear)

col_trans	- total number of transitions from filled to empty (or reverse) for all columns
row_trans	- total number of transitions from filled to empty (or reverse) for all rows
all_trans	- sum of the transitions from filled to empty (or reverse) for all rows and columns

wells - number of wells, divots with at least one filled cell on either side.
cuml_wells	- cumulatively weighted depth of all wells in the pile (1=1, 2=1+2, 3=1+2+3...)
deep_wells	- number of wells of depth 2 or greater
max_well	- deepest depth of any one well

pits	- number of unworkable holes (empty, but vertically obstructed) in the pile
pit_rows	- number of rows containing pits (as they will be uncovered simultaneously)
lumped_pits	- number of pits wherein contiguous pits count only once
pit_depth	- sum of all pits, weighted by their depths beneath the surface
mean_pit_depth	- mean depth of all pits (pits buried deeper count more)

cd_1	- difference in height between columns 0 and 1
cd_2	- difference in height between columns 1 and 2
cd_3	- difference in height between columns 2 and 3
cd_4	- difference in height between columns 3 and 4
cd_5	- difference in height between columns 4 and 5
cd_6	- difference in height between columns 5 and 6
cd_7	- difference in height between columns 6 and 7
cd_8	- difference in height between columns 7 and 8
cd_9	- difference in height between columns 8 and 9
all_diffs	- sum of the differences in height between all columns.
max_diffs	- highest height difference between two columns
jaggedness	- length of the perimeter of the pile (higher is more jagged)

d_mean_ht	- change in mean_ht from before this zoid placement to after
d_max_ht	- change in max_ht from before this zoid placement to after
d_all_ht	- change in all_ht from before this zoid placement to after
d_pits	- change in pits from before this zoid placement to after

landing_height	- row at which this zoid was placed

pattern_div	- number of unique transitions between two columns. measures diversity of pattern.

matches	- number of segments about the perimeter of the zoid matching its placement in the pile

tetris_progress	- number of contiguous, uncovered rows with exactly 9 cells filled. 
nine_filled	- number of rows with exactly 9 filled columns

full_cells	- number of filled cells on the board
weighted_cells	- sum of all filled cells, weighted by their height

eroded_cells	- number of segments of the current zoid eroded (cleared) by this zoid placement

cuml_eroded	- cumulatively weighted number of cells eroded (1=1, 2=1+2, 3=1+2+3...)




Eye tracking values
smi_ts - timestamp reported by the eyetracker
smi_eyes - which eyes are visible ("b" for both, "l" or "r" for left or right)
smi_samp_x_l - x gaze position (left to right), left eye
smi_samp_x_r - x gaze position (left to right), right eye
smi_samp_y_l - y gaze position (top down), left eye
smi_samp_y_r - y gaze position (top down), right eye
smi_diam_x_l - pupil diameter x (left to right), left eye
smi_diam_x_r - pupil diameter x (left to right), right eye
smi_diam_y_l - pupil diameter y (top down), left eye
smi_diam_y_r - pupil diameter y (top down), right eye
smi_eye_x_l - 3d eye position x (left to right), left eye
smi_eye_x_r - 3d eye position x (left to right), right eye
smi_eye_y_l - 3d eye position y (top down), left eye
smi_eye_y_r - 3d eye position y (top down), right eye
smi_eye_z_l - 3d eye position z (depth), left eye
smi_eye_z_r - 3d eye position z (depth), right eye
fix_x - on-the-fly calculation of fixation position x (inaccurate)
fix_y - on-the-fly calculation of fixation position y (inaccurate)
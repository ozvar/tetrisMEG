#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import numpy as np
import pandas as pd
import pickle as pk

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy.io import loadmat

from glob import glob


def read_episodes_file(R_no, file_type, input_path):
    '''Return pandas dataframe of behavioural .tsv for participant with
    specified R number at specified input path. File type refers to game
    summary, episodes, or complete .tsv'''
    if file_type == 'processed_episodes':
        file_suffix = '*.csv'
    else:
        file_suffix = '*.tsv'
    try:
        data_dir = [d for d in os.listdir(input_path) if d.startswith(R_no)][0]

        file_path = glob(os.path.join(input_path,
                                      data_dir,
                                      file_type + file_suffix))[0]
    except IndexError:
        print(f"Unable to find R number '{R_no}' or file type '{file_type}'")
        return None
    try:
        if file_type == 'processed_episodes':
            df = pd.read_csv(file_path)
        else:
            df = pd.read_csv(file_path, sep='\t')
    except:
        print("Invalid file path, check that file \
              type has been specified correctly")
        return None

    return df


def parse_FFT_mats(R_no, input_path, null_model=False):
    '''Return pandas dataframe of parsed matlab structs containing data 
    for each FFT of scouts for each epoch in the specified participant's
    games'''
    if not null_model:
        dir_pattern = 'game_*_state_*'
    else:
        dir_pattern = 'game_*_null_model_state_*'

    try:
        participant_dir = [d for d in os.listdir(input_path) if d.startswith(R_no)][0]
        # bit hacky but this ensures we parse either states or null states but not both
        top_dir = os.path.join(input_path, participant_dir)
        data_dirs = glob(os.path.join(input_path, participant_dir, dir_pattern))
        data_dirs = [d for d in data_dirs if len(dir_pattern) == (len(d) - len(top_dir) - 1)]

    except IndexError:
        print(f"Unable to find R number '{R_no}'")
        return None

    # set up dataframe
    dataframes = []
    print(data_dirs)
    for d in data_dirs:
        rows = []
        mats = glob(os.path.join(d, 'timefreq*'))
        scout_labels = loadmat(mats[0])['RowNames'][0]
        scout_labels = [scout[0].split('@')[0][:-1] for scout in scout_labels]
        print(d)
        for mat in mats:
            FFT = loadmat(mat)
            for i, scout in enumerate(FFT['RowNames'][0]):
                if not null_model:
                    game_number = d[-9]
                else:
                    game_number = d[-20]
                row_start = pd.Series({
                        'SID': R_no,
                        'game_number': game_number,
                        'state': d[-1],
                        'scout': scout[0].split('@')[0][:-1],
                        'file_name': FFT['DataFile'][0]
                        })
                columns = [str(int(round(x)))+'Hz' for x in FFT['Freqs'][0][1:]] 
                row_end = pd.Series(
                        data=FFT['TF'][i][0][1:],
                        index=columns)
                row = pd.concat([row_start, row_end])
                rows.append(row)

        # append data from this state and game to dataframe collector
        labels = row.index.tolist()
        dataframes.append(pd.DataFrame(rows, columns=labels))

    df = pd.concat(dataframes, ignore_index=True)
    df['SID'] = [R_no] * len(df)
    df['scout'] = df['scout'].str.replace(' ', '_')
    df = df.sort_values(by=['SID', 'game_number', 'state', 'file_name', 'scout']).reset_index(drop=True)
        
    return df
	

def parse_all_FFT_mats(participants_to_ignore, input_path, output_path, null_model=False):
    '''Iterate over all participants in input_path directory, parsing 
    matlab structs of scout FFTs for each participant before merging
    into one pandas dataframe and saving in top level project dir.'''
    participant_dirs = [d for d in os.listdir(input_path) if d.startswith('R')]
    dataframes=[]
    for d in participant_dirs:
        R_no = d[:5]
        if R_no in participants_to_ignore:
            # don't preprocess data of listed R_no's episodes file
            continue
        else:
            print(f'working on {R_no}')
            df = parse_FFT_mats(R_no, input_path, null_model)
            print(f'{R_no} df: {df.columns}')
            print('appending df to container')
            dataframes.append(df)

    # merge all the dataframes that we've generated and save
    print('merging dataframes')
    all_FFT_df = pd.concat(dataframes, ignore_index=True)
    all_FFT_df = all_FFT_df.sort_values(by=[
        'SID',
        'game_number',
        'state',
        'file_name',
        'scout']).reset_index(drop=True)
    
    if not null_model:
        file_name = 'all_FFT_df.csv'
    else:
        file_name = 'null_model_all_FFT_df.csv'
    file_path = os.path.join(output_path, file_name)
    all_FFT_df.to_csv(file_path, index=False)

    return all_FFT_df


def trim_episodes_dataframe(eps, features_to_drop):
    '''Prepare episodes dataframe for preprocessing by dropping game summary
    columns and removing features not included in PCA'''
    # drop uneeded columns
    eps = eps[eps['event_type'] != 'GAME_SUMM']
    eps = eps.reset_index(drop=True)
    # drop unneeded columns
    trimmed_eps = eps.drop(columns=features_to_drop, errors='ignore')

    return eps, trimmed_eps


def princomp(file_name,
             features_to_drop,
             input_path,
             n_components=3,
             cutoff=None,
             display_loadings=False):
    """Conduct principal components analysis of file_name using sklearn's PCA,
    returning eigenvalues and factor loadings"""
    # read df
    eps = pd.read_csv(os.path.join(input_path, file_name),
                      header=0,
                      sep='\t',
                      low_memory=False)
    # drop features that are not considered in pca
    trimmed_eps = eps.drop(columns=features_to_drop, errors='ignore')
    # standardise all variables
    scaled_eps = StandardScaler().fit_transform(trimmed_eps)
    scaled_eps = pd.DataFrame(scaled_eps, columns=trimmed_eps.columns)
    # Standardise the data
    scaled_eps = pd.DataFrame(scaled_eps,
                              index=np.arange(0, len(scaled_eps)),
                              columns=scaled_eps.columns)

    # fit PCA
    pca = PCA(n_components=n_components)
    pca.fit(scaled_eps)

    # generate loadings table
    headers = [str(i) for i in np.arange(1, n_components+1)]
    loadings = pd.DataFrame(pca.components_.T,
                            index=scaled_eps.columns, 
                            columns=headers)

    # create sorted dataframe of loadings above a certain cutoff
    if cutoff != None:
        loadings = loadings.where(abs(loadings).gt(cutoff))
        loadings = loadings.sort_values(by=headers, ascending=False)
        loadings = loadings.replace(np.nan, '', regex=True)
    
    if display_loadings is True:
        display(loadings)

    # write pca for loading reloading in other analyses
    pk.dump(pca, open(os.path.join(input_path, 'pca.pkl'), 'wb'))

    return loadings, pca


def add_pca_features(eps, 
                     trimmed_eps,
                     component_labels,
                     input_path):
    '''Read pickled pca model and fit_transform to participant R_no's data to
    generate features to be used in modelling. Write to episodes df as 
    new columns.'''
    
    # load pickled pca
    pca_path = os.path.join(input_path, 'pca.pkl')
    pca = pk.load(open(pca_path, 'rb'))
    
    # standardise all variables
    scaled_eps = StandardScaler().fit_transform(trimmed_eps)
    scaled_eps = pd.DataFrame(scaled_eps, columns=trimmed_eps.columns)
    scaled_eps = scaled_eps
    # fit pca to participant data to generate component columns
    comps = pd.DataFrame(pca.transform(scaled_eps), 
                         columns=component_labels)
    # append columns
    pca_eps = eps.join(comps)
    # add diff of disarray
    pca_eps['diff_disarray'] = pca_eps['disarray'].diff()
    # set disarray delta at first row of each new game to 0
    dropped_rows = pca_eps[pca_eps['game_number'].diff() != 0].index.tolist()
    for row in dropped_rows:
        pca_eps.at[row, 'diff_disarray'] = 0
    
    return pca_eps


def standardise_pca_features(df, components):
    '''Standardise (z-score) pca-derived feature columns in specified df, and append to df as new columns
    pre-fixed with "z_"'''
    labels = list(components.keys())
    for label in labels:
        component = np.array(df[label]).reshape(-1, 1)
        df[f'z_{label}'] = StandardScaler().fit_transform(component)

    return df


def read_trigger_record(R_no, nth_game, input_path):
    '''Return pandas dataframe of MEG trigger record for participant with
    specified R number at specified input path'''
    try:
        data_dir = [d for d in os.listdir(input_path) if d.startswith(R_no)][0]
        file_path = os.path.join(input_path,
                                 data_dir,
                                 f'triggers_{R_no}_game_{nth_game}.csv')
    except IndexError: 
        print("Unable to find R or game number")
        return None
    try:
        df = pd.read_csv(file_path,
                         names=['trigger', 'ts', 'trigger_length'])        

    except:
        print("Invalid file path, check that file \
              type has been specified correctly")
        return None
    
    return df


def get_trigger_timestamps(eps, R_no, input_path):
    '''Remove time offset from episodes time series and write to episodes
    file as new column "meg_ts"'''   
    # identify all .csv trigger records
    trigger_records = glob(os.path.join(input_path,
                                        f'{R_no}*',
                                        'triggers*'))
    # set up data structure to store triggers
    triggers_df = pd.DataFrame({'meg_ts': [],
                                'ep_duration': [],
                                'game_number': []})
    # sort by game number
    trigger_records = sorted(trigger_records)
    # abort if no trigger records are present
    if trigger_records == []:
        print(f"No trigger records associated with participant {R_no}, \
              aborting preprocessing.")
        return None
    # loop over each trigger file, appending data to triggers_df
    else:
        for file_path in trigger_records:
            nth_game = file_path[-5]  # game number should always be this char
            df = read_trigger_record(R_no, nth_game, input_path)
            new_df = pd.DataFrame({'meg_ts': [],
                                   'ep_duration': [],
                                   'game_number': []})
            # timestamps for placement of each tetromino (trigger # 17)
            new_df['meg_ts'] = df[df['trigger'] == '17']['ts']
            # substract game start offset (trigger #64) from our new timestamps
            game_start_ts = df[df['trigger'] == '64']['ts'].values
            new_df['ep_duration'] = new_df['meg_ts'] - game_start_ts
            # now compute duration of each episode
            ep_durations = new_df['ep_duration'].diff().fillna(new_df['ep_duration'])
            new_df['ep_duration'] = ep_durations
            # finally, include the current game number     
            new_df['game_number'] = len(new_df)*[nth_game]
            new_df['game_number'] = new_df['game_number'].astype('int64')
            triggers_df = triggers_df.append(new_df)
            #triggers_df['game_number'] = triggers_df['game_number'].astype('int64')


    triggers_df = triggers_df.reset_index(drop=True)
    #triggers_df = triggers_df.rename(columns={'ts': 'meg_ts'})
    
    return triggers_df


def add_trigger_timestamps_to_eps(R_no, trigger_ts, eps):
    '''Add column to eps dataframe comprising timestamps for each trigger 
    in the MEG record'''
    # check we have same number of timestamps in both files
    trigger_record_lengths = trigger_ts.groupby('game_number').size()
    eps_lengths = trigger_ts.groupby('game_number').size()
    if (trigger_record_lengths != eps_lengths).any():
        print(f"Mismatched timestamp lengths in participant {R_no}'s \
              dataframes. Aborting preprocessing at this stage.")
        return None
    else:
        eps.insert(0, 'meg_ts', trigger_ts['meg_ts'])
        eps.insert(1, 'ep_duration', trigger_ts['ep_duration'])

    return eps


def preprocess_episodes_file(R_no,
                        features_to_drop,
                        component_labels,
                        input_path):
    '''For participant with given R_no, read .csv containing episodes across
    all games, reduce data to required columns and append engineered features 
    before writing to participant data directory'''
    # read raw episodes data file
    eps = read_episodes_file(R_no, file_type='episodes', input_path=input_path)
    # for dim reduction, remove 'GAME_SUMM' rows and unnecessary columns
    eps, trimmed_eps = trim_episodes_dataframe(eps, features_to_drop)
    # add our pca components to the episodes dataframe
    pca_eps = add_pca_features(eps, trimmed_eps, component_labels, input_path)
    # add timestamps from the trigger record to the dataframe
    trigger_ts = get_trigger_timestamps(pca_eps, R_no, input_path)
    # add trigger timestamps to original episodes dataframe
    preprocessed_eps = add_trigger_timestamps_to_eps(R_no, trigger_ts, pca_eps)
    # write preprocessed behavioural data to participant directory
    data_dir = [d for d in os.listdir(input_path) if d.startswith(R_no)][0]
    file_path = os.path.join(input_path,
                             data_dir,
                             f'processed_episodes_{R_no}.csv')
    preprocessed_eps.to_csv(file_path, index=False)
    
    return preprocessed_eps


def preprocess_all_episodes_files(features_to_drop,
                                  components,
                                  component_labels,
                                  participants_to_ignore,
                                  input_path):
    '''Generate preprocessed episodes .csv for all participants that exist
    in behavioural data directory. Concatenate all preprocessed episodes 
    dataframes into single .csv and write to top level behavioural data
    directory.'''
    participant_dirs = [d for d in os.listdir(input_path) if d.startswith('R')]
    dataframes=[]
    for d in participant_dirs:
        R_no = d[:5]
        if R_no in participants_to_ignore:
            # don't preprocess data of listed R_no's episodes file
            continue
        else:
            df = preprocess_episodes_file(R_no=R_no,
                                          features_to_drop=features_to_drop,
                                          component_labels=component_labels,
                                          input_path=input_path)
            dataframes.append(df)
    # merge all the preprocessed dataframes that we've generated
    all_episodes = pd.concat(dataframes, ignore_index=True)
    # add columns of standardised performance components
    all_episodes = standardise_pca_features(df=all_episodes,
                                            components=components) 
    # save to data directory
    file_path = os.path.join(input_path, f'all_preprocessed_episodes.csv')
    all_episodes.to_csv(file_path, index=False)
    
    return all_episodes


def gen_state_timestamps_for_game(preprocessed_eps,
                                  R_no, 
                                  nth_game,
                                  slice_length,
                                  input_path,
                                  null_model=False):
    '''For specified participant and game, identify the points at which 
    participant switched behavioural state in dataframe "preprocessed_eps",
    then generate a .csv of timestamped epochs of length slice_length for 
    each state across the entire game. File is saved to participant specific 
    behavioural data directory.'''
    triggers = read_trigger_record(R_no, nth_game, input_path)
    game_start = triggers[triggers['trigger'] == '64']['ts'].iloc[0]
    
    game = preprocessed_eps[preprocessed_eps['SID'] == R_no]
    game = game[game['game_number'] == nth_game] 
    # identify time stamps at which participant switched states
    if not null_model:
        state_var = 'HMM_state'
    else:
        state_var = 'null_HMM_state'
    state_switches = game[state_var].diff().fillna(1)
    switch_indices = state_switches[state_switches != 0].index
    state_switches = game.loc[switch_indices][['meg_ts', state_var]]
    # brainstorm accepts trigger files with the column structure below
    state_timestamps = pd.DataFrame({'trigger': [],
                                     'ts': []})
    # iterate over each state switch point
    for i, switch_point in enumerate(state_switches.index):
        # create dataframe
        s_ts = pd.DataFrame({'trigger': [],
                             'ts': []})
        # generate the label for the current HMM state
        if not null_model:
            state = 'state ' + str(int(state_switches.iloc[i][state_var]))
        else:
            state = 'null model state ' + str(int(state_switches.iloc[i][state_var]))
        # for each state switch, compute amount of time ppt stayed in the state for
        # if it's the first tetromino drop, time range goes from game start to next state switch
        if i == 0:
            time_range = state_switches.iloc[i+1]['meg_ts'] - game_start
            timestamps = np.arange(0, time_range, slice_length) + game_start
        # if it's the last drop, time range goes from state switch to final tetromino drop
        elif i+1 == len(state_switches):
            start = state_switches.iloc[i]['meg_ts']
            time_range = game.iloc[-1]['meg_ts'] - start
            timestamps = np.arange(0, time_range, slice_length) + start
        # for all other state switches, time range lasts from moment of switch to the next switch
        else:
            start = state_switches.iloc[i]['meg_ts']
            time_range = state_switches.iloc[i+1]['meg_ts'] - start
            timestamps = np.arange(0, time_range, slice_length) + start
        # insert data into local dataframe
        s_ts['ts'] = timestamps
        s_ts['trigger'] = len(timestamps) * [state]
        # append local dataframe to global HMM state timestamps record
        state_timestamps = state_timestamps.append(s_ts)
    
    # reset the index
    state_timestamps = state_timestamps.reset_index(drop=True)
    # remove epochs with bad meg recordings from the dataframe
    bad_epochs = triggers[triggers['trigger'] == 'BAD']
    if bad_epochs.count()['trigger'] > 0:
        bad_epochs['ts_end'] = bad_epochs['ts'] + bad_epochs['trigger_length']
        for row in range(len(bad_epochs)):
            ts_to_drop = state_timestamps[state_timestamps['ts'].between(
                    bad_epochs.iloc[row]['ts'],
                    bad_epochs.iloc[row]['ts_end'])]
            ts_to_drop = ts_to_drop.index.tolist()
            state_timestamps.drop(ts_to_drop, inplace=True)
    # write the state timestamps to relevant directory

    print(f'null model is {null_model}')
    if not null_model:
        file_name = f'state_timestamps_{R_no}_game_{nth_game}.csv'
    else:
        file_name = f'null_model_state_timestamps_{R_no}_game_{nth_game}.csv'

    print(f'saving {file_name}')
    data_dir = [d for d in os.listdir(input_path) if d.startswith(R_no)][0]
    file_path = os.path.join(input_path, data_dir, file_name)
    state_timestamps.to_csv(file_path, index=False, header=False)
 
    return state_timestamps


def generate_all_state_timestamps(preprocessed_eps,
                                  slice_length,
                                  participants_to_ignore,
                                  input_path,
                                  null_model=False):
    '''For each participant and game in the input_path, generate a .csv of 
    timestamped epochs of length slice_length and save the file to participant
    specific behavioural data directory.'''
    participant_dirs = [d for d in os.listdir(input_path) if d.startswith('R')]
    dataframes=[]
    for d in participant_dirs:
        R_no = d[:5]
        if R_no in participants_to_ignore:
            # don't preprocess data of listed R_no's episodes file
            continue
        else:
            # identify how many games current ppt played
            n_games = preprocessed_eps[preprocessed_eps['SID'] == R_no]['game_number'].nunique()
            # generate state timestamps file for each game for current ppt
            for nth_game in range(1, n_games+1):
                gen_state_timestamps_for_game(preprocessed_eps,
                                              R_no,
                                              nth_game,
                                              slice_length,
                                              input_path,
                                              null_model)

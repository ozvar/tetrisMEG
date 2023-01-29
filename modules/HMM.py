#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pandas as pd
import numpy as np
import scipy.stats as scipy
import pickle as pk

from hmmlearn import hmm


def rand_start_prob(n_states):
    start_prob = np.random.rand(n_states)
    start_prob = start_prob / sum(start_prob)

    # subtract any imprecision from array to ensure it sums to 1
    diff = sum(start_prob) - 1
    start_prob[0] -= diff
    
    return start_prob


def fit_HMM(df, 
            n_states, 
            components, 
            component_labels, 
            player_id, 
            nth_game, 
            n_iter, 
            verbose=True, 
            covar_type='diag', 
            null_model=False,
            model_dir=None):
    """Fit HMM, using arrays of components as observed states, to single tetris 
    game of specified player - returns model, state probabilities, and input
    array, printing transition matrix and descriptive metrics"""
    # instantiate model
    model = hmm.GaussianHMM(n_components = n_states,
                            covariance_type=covar_type,
                            n_iter=n_iter)
    # structure data 
    game = df[(df['SID'] == player_id )
              & (df['game_number'] == nth_game)]
    # reshape arrays
    component_arrays = [np.array(game[component]) for component in components]
    # reshuffle data if null model is of interest
    if null_model:
        component_arrays = [np.random.choice(array, len(array), replace=False)
                            for array in component_arrays]
    # reshape data for fitting
    X = np.column_stack(component_arrays)
    # fit model
    model.fit(X)
    post_prob = model.predict_proba(X)
    
    LL = np.round(model.score(X), 2)
    
    if verbose:
        if null_model is False:
            print(f'Fitting {n_states} state model to game {nth_game} of player {player_id}')
        print('---------------------------\n'
              'Transition probabilities:\n'
              '---------------------------')
        print(tabulate_trans_probs(model, n_states), '\n')

        print('---------------------------\n'
              'Component means for each state:\n'
              '---------------------------\n')
        print(tabulate_means(model, components, component_labels, n_states), '\n')
        
        print('---------------------------\n'
              'Fractional occupancy for each state:\n'
              '---------------------------\n')      
        print(fractional_occupancy(model, X, n_states, components).to_string(header=False), '\n')
        
        print(f'Switch rate of model is {switch_rate(model, X)}\n')

        print(f'Log-likelihood of model is {LL}')
    
    if model_dir != None:
        if null_model:
            pickle_name = f'null_model_{n_states}_state__HMM_subject_{player_id}_game_{nth_game}_{len(components)}_components.pkl'
        else:
            pickle_name = f'{n_states}_state_HMM_subject_{player_id}_game_{nth_game}_{len(components)}_components.pkl'

    data = [model, post_prob, X, LL]
    with open (os.path.join(model_dir, pickle_name), "wb") as f:
        pk.dump(len(data), f)
        for datum in data:
            pk.dump(datum, f)

    return model, post_prob, X, LL


def fit_group_HMM(df, 
                  n_states, 
                  components, 
                  component_labels, 
                  n_iter=200, 
                  verbose=True, 
                  covar_type='diag', 
                  null_model=False,
                  nth_fit=1,
                  model_dir=None):
    """Fit HMM, using arrays of components as observed states, to all tetris
    games of all players in data set - returns model, state probabilities,
    and input array, printing transition matrix and descriptive metrics"""
    # instantiate model
    start_prob = rand_start_prob(n_states)
    model = hmm.GaussianHMM(n_components = n_states,
                        covariance_type=covar_type,
                        n_iter=n_iter)
    # structure data 
    component_arrays = [np.array(df[component]) for component in components]
    # reshuffle data if null model is of interest
    if null_model:
        component_arrays = [np.random.choice(array, len(array), replace=False)
                            for array in component_arrays]
    # reshape data for fitting
    X = np.column_stack(component_arrays)
    # fit model
    model.fit(X)
    post_prob = model.predict_proba(X)
    
    LL = np.round(model.score(X), 2)
    
    if verbose:
        if not null_model:
            print(f'Fitting {n_states} state model to all games of all players')
        else:
            print(f'Fitting {n_states} state NULL MODEL to all games of all players')

        print('---------------------------\n'
              'Transition probabilities:\n'
              '---------------------------')
        print(tabulate_trans_probs(model, n_states), '\n')

        print('---------------------------\n'
              'Component means for each state:\n'
              '---------------------------\n')
        print(tabulate_means(model, components, component_labels, n_states), '\n')

        print(f'Switch rate of model is {switch_rate(model, X)}\n')

        print(f'Log-likelihood of model is {LL}')
    
    if model_dir != None:
        data = [model, post_prob, X, LL, start_prob]
        save_group_HMM(
                data,
                n_states,
                components,
                null_model,
                nth_fit,
                model_dir)

    return model, post_prob, X, LL, start_prob


def save_group_HMM(
        data,
        n_states,
        components,
        null_model,
        nth_fit,
        model_dir):
        
        
        n_comps = len(components)
        if null_model:
            pickle_name = f'{n_states}_state_{n_comps}_components_chance_model_fit_{nth_fit}.pkl'
            model_dir = os.path.join(
                    model_dir,
                    f'{n_states}_state_{n_comps}_component_chance_model'
                    )
        else:
            pickle_name = f'{n_states}_state_{n_comps}_component_group_HMM_fit_{nth_fit}.pkl'
            model_dir = os.path.join(
                    model_dir,
                    f'{n_states}_state_{n_comps}_component_HMM'
                    )

        if not os.path.isdir(model_dir):
            os.mkdir(model_dir)
        else:
            with open (os.path.join(model_dir, pickle_name), "wb") as f:
                pk.dump(len(data), f)
                for datum in data:
                    pk.dump(datum, f)


def load_pickled_HMM(
        HMM_dir,
        model_dir,
        group_model,
        n_states,
        components,
        nth_fit=1,
        null_model=False
        ):
    
    n_comps = len(components)
    if group_model:
        if null_model:
            model_dir = f'{n_states}_state_{n_comps}_component_chance_model'
            pickle_name = f'{n_states}_state_{n_comps}_components_chance_model_fit_{nth_fit}.pkl'
        else:
            model_dir = f'{n_states}_state_{n_comps}_component_HMM'
            pickle_name = f'{n_states}_state_{n_comps}_component_group_HMM_fit_{nth_fit}.pkl'
    else:
        if null_model:
            pickle_name = f'null_model_{n_states}_state_HMM_subject_{player_id}_game_{nth_game}_{n_comps}_components.pkl'
        else:
            pickle_name = f'{n_states}_state_HMM_subject_{player_id}_game_{nth_game}_{n_comps}_components.pkl'

    file_path = os.path.join(HMM_dir, model_dir, pickle_name)
    print(file_path)
    if not os.path.isfile(file_path):
        print("Pickled model with specified parameters could not be found at this directory")

        return None

    else: 
        data = []
        with open (file_path, "rb") as f:
            for datum in range(pk.load(f)):
                data.append(pk.load(f))
                
    model, post_prob, X, LL = data[0], data[1], data[2], data[3]

    return model, post_prob, X, LL


def tabulate_means(model, components, component_labels, n_states):
    
    means = np.transpose(model.means_)
    means_df = pd.DataFrame(means)

    row_names = {int(i): component_labels[components[i]] for i in range(len(components))}
    col_names = {int(i): f'State {i+1}' for i in range(n_states)}

    means_df.rename(index=row_names, inplace=True)
    means_df.rename(columns=col_names, inplace=True)

    return means_df


def tabulate_trans_probs(model, n_states):
    
    trans_mat = np.round(model.transmat_, 2)
    trans_df = pd.DataFrame(trans_mat)
    
    row_names = col_names = {int(i): f'State {i+1}' for i in range(n_states)}
    
    trans_df.rename(index=row_names, inplace=True)
    trans_df.rename(columns=col_names, inplace=True)
    
    return trans_df


def fractional_occupancy(df, for_each_participant=False, null_model=False):
    '''Calculate for each state the time all participants spent in that state as
    a fraction of total game time, and return as a list'''
    total_time = df['ep_duration'].sum()
    if not null_model:
        state = 'HMM_state'
    else:
        state = 'null_HMM_state'
    if not for_each_participant:
        groupby_cols = [state]
    else:
        groupby_cols = ['SID', state]
    frac_occ = df.groupby(by=groupby_cols)['ep_duration'].sum() / total_time
    frac_occ = frac_occ.reset_index()

    return frac_occ


def max_fractional_occupancy(df):
    '''Calculate for each game the maximum fractional occupancy, that is, the fraction of total time spent
    in the state that is occupied for the most amount of time in that game. Return the values representing
    maximum fractional occupancy in each game as an array.'''
    groupby_cols = ['SID', 'game_number', 'HMM_state']
    state_durations = df.groupby(by=groupby_cols)['ep_duration'].sum().reset_index()
    duration_totals = state_durations.groupby(by=['SID', 'game_number'])['ep_duration'].sum()
    duration_max = state_durations.groupby(by=['SID', 'game_number'])['ep_duration'].max()
    
    max_frac_occ = duration_max.values / duration_totals.values

    return max_frac_occ


def state_fractional_occupancy_at_each_game(df, n_states, state):
    '''For each participant and game, compute the fractional occupancy of a specified state
    and return the results as a new dataframe'''
    total_time = df['ep_duration'].sum()
    frac_occ = df.groupby(by=['SID', 'game_number', 'HMM_state'])['ep_duration'].sum()
    frac_occ = frac_occ.reset_index()
    frac_occ = frac_occ[frac_occ['HMM_state'] == state]
    game_lengths = df.groupby(['SID', 'game_number'])['ep_duration'].sum().reset_index()

    frac_occ = frac_occ['ep_duration'].values / game_lengths['ep_duration'].values

    return frac_occ


def switch_rate(model, observed_states):
    '''Calculate rate of switches between states, calculated as number of 
    switches divided by total state occurrences'''
    states = model.predict(observed_states)
    switch_count = np.count_nonzero(np.diff(states))

    rate = switch_count / len(states - 1)
    rate = np.round(rate, 4)
    
    return rate

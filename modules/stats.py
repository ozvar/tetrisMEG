#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

def compute_means(df, var, n):
    """Return an array containing the mean of variable 'var' at each match 
    for all subject IDs and games in dataframe 'df' over 'n' episodes"""
    games = df.groupby(['SID', 'game_number'], sort=False).head(n)
    means = games.groupby('episode_number', sort=False)[var].mean().tolist()

    return means


def compute_errors(df, var, n):
    """Return an array containing the standard error of variable 'var' at 
    each match for all account_ids in dataframe 'df' over 'n' matches"""
    games = df.groupby(['SID', 'game_number'], sort=False).head(n)
    errors = games.groupby('episode_number', sort=False)[var].sem().tolist()

    return errors


def compute_RMS(obs, axis):
    """Compute root mean square for array of values"""
    RMS = np.sqrt(np.mean(obs, axis=axis)) 

    return RMS

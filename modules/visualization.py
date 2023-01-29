#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib as mpl
import matplotlib.patches as mpatches 
import seaborn as sns

from glob import glob
from scipy.io import loadmat
from matplotlib.collections import PatchCollection
from modules.HMM import tabulate_means
from modules.HMM import fractional_occupancy
from modules.HMM import max_fractional_occupancy


# configure pandas table display
pd.set_option('display.max_columns', 100)
pd.set_option('display.max_rows', 100)
pd.set_option('display.float_format', lambda x: '%.4f' % x)


def sns_styleset():
    """Configure parameters for plotting"""
    sns.set_theme(context='paper',
                  style='whitegrid',
                  # palette='deep',
                  palette=['#c44e52',
                           '#8c8c8c',
                           '#937860',
                           '#ccb974',
                           '#4c72b0',
                           '#dd8452'],
                  font='Arial')
    matplotlib.rcParams['figure.dpi']        = 300
    matplotlib.rcParams['axes.linewidth']    = 1
    matplotlib.rcParams['grid.color']        = '.8'
    matplotlib.rcParams['axes.edgecolor']    = '.15'
    mpl.rcParams['axes.spines.right']        = False
    mpl.rcParams['axes.spines.top']          = False
    matplotlib.rcParams['xtick.bottom']      = True
    matplotlib.rcParams['ytick.left']        = True
    matplotlib.rcParams['xtick.major.width'] = 1
    matplotlib.rcParams['ytick.major.width'] = 1
    matplotlib.rcParams['xtick.color']       = '.15'
    matplotlib.rcParams['ytick.color']       = '.15'
    matplotlib.rcParams['xtick.major.size']  = 3
    matplotlib.rcParams['ytick.major.size']  = 3
    matplotlib.rcParams['font.size']         = 14
    matplotlib.rcParams['axes.titlesize']    = 14
    matplotlib.rcParams['axes.labelsize']    = 13
    matplotlib.rcParams['legend.fontsize']   = 14
    matplotlib.rcParams['legend.frameon']    = False
    matplotlib.rcParams['xtick.labelsize']   = 13
    matplotlib.rcParams['ytick.labelsize']   = 13


def viz_states(df,
               n_states,
               post_prob,
               components,
               component_labels,
               player_id,
               nth_game,
               show_plot=False,
               cmap='tab10',
               null_model=False,
               fig_dir=None):
    """Create joint plot of latent state probabilities and observed states 
    across tetris episodes"""
    # figure parameters      
    state_colours = matplotlib.cm.get_cmap(cmap)
    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, sharex=True)
    # slice rows for the player and game we want to visualize
    game = df[(df['SID'] == player_id) & (df['game_number'] == nth_game)]
    indices = game.index.tolist()
    n_episodes = len(game)
    # plot state transitions
    states_legend = []
    for state in range(0, n_states):
        ax1.plot(np.arange(1, n_episodes+1), 
                 post_prob[indices, state],
                 color=state_colours(state))
        states_legend.append(f'State {state+1}')

    ax1.set_ylabel('Probability of state')
    ax1.legend(states_legend, 
               loc='upper left', 
               bbox_to_anchor=(1.05, 1), 
               frameon=False
               )
    # plot the observed variables
    components_legend = [component_labels[component] for component in components]
    for component in components:
        ax2.plot(np.arange(1, n_episodes+1), game[component][:n_episodes])

    ax2.set_ylabel('Component score')
    ax2.set_xlabel('Episode')
    ax2.legend(components_legend, 
               loc='upper left', 
               bbox_to_anchor=(1.05, 1), 
               frameon=False, 
               )
    fig.align_ylabels()
    
    if not null_model:
        fig.suptitle(f'Player {player_id} Game {nth_game}: {n_states}-State Model')
    else:
        fig.suptitle(f'Player {player_id} Game {nth_game}: {n_states}-State Null Model')

    if fig_dir:
        if not null_model:
            fig_name = f'{player_id}_{n_states}_state_HMM_game_{nth_game}.svg'
        else:
            fig_name = f'null_model_{player_id}_{n_states}_state_HMM_game_{nth_game}.svg'

        if not os.path.isdir(fig_dir):
            os.mkdir(fig_dir)
        plt.savefig(os.path.join(fig_dir, fig_name), bbox_inches='tight')
    plt.close()


def line_plot_avg_button_press_activity_one_side(R_no, button_side, input_path, fig_dir=None):
    '''Produce line plot of time series of amplitudes of neural activity during button presses across all MEG channels in the parsed .mat file'''
    file_pattern = f'{R_no}_timeseries_AvgStd_{button_side}*'
    file_path = glob(os.path.join(input_path, R_no, file_pattern))
    data = loadmat(file_path[0])

    avg_ts = data['F'][0][0]
    times = data['Time'][0]
    for channel in avg_ts:
        plt.plot(
                times, 
                channel, 
                color='dimgray', 
                linewidth=0.5)

    plt.vlines(
            0.085,
            plt.ylim()[0],
            plt.ylim()[1],
            color='red',
            linestyle='--',
            zorder=300)

    plt.xlabel('Time (s)', fontsize=16)
    plt.ylabel('Amplitude', fontsize=16)

    if fig_dir != None:
        fig_name = f'{R_no}_line_plot_avg_{button_side}_button_press_activity.svg'
        plt.savefig(os.path.join(fig_dir, fig_name))
    plt.close()
            

def line_plot_avg_button_press_activity(R_no, input_path, fig_dir=None):
    '''Produce line plot of time series of amplitudes of neural activity during button presses across all MEG channels in the parsed .mat file'''
    fig, axs = plt.subplots(
            nrows=1,
            ncols=2,
            sharey=True,
            figsize=(7, 3))
    
    for side, ax in zip(['left', 'right'], axs):
        file_pattern = f'{R_no}_timeseries_AvgStd_{side}*'
        file_path = glob(os.path.join(input_path, R_no, file_pattern))
        data = loadmat(file_path[0])

        avg_ts = data['F'][0][0]
        times = data['Time'][0]
        for channel in avg_ts:
            ax.plot(
                times, 
                channel, 
                color='dimgray', 
                linewidth=0.5)

        ax.vlines(
            0.085,
            plt.ylim()[0],
            plt.ylim()[1],
            color='red',
            linestyle='--',
            linewidth=0.8,
            zorder=300)

    fig.text(0.5, 0.0001, 'Time (s)', ha='center')
    axs[0].set_ylabel('Amplitude (fT)', fontsize=16)

    if fig_dir != None:
        fig_name = f'{R_no}_line_plot_avg_button_press_activity.svg'
        plt.savefig(os.path.join(fig_dir, fig_name), bbox_inches='tight')
    plt.close()


def line_plot_left_right_button_decoding(R_no, input_path, fig_dir=None):
    '''Produce line plot of time series of decoding accuracy for binary SVM classifier
    of left versus right thumb button inputs'''
    file_pattern = f'{R_no}_timeseries_left_right_input_decoding.mat'
    file_path = glob(os.path.join(input_path, R_no, file_pattern))
    data = loadmat(file_path[0])

    ts = data['F'][0][0][0]
    times = data['Time'][0]

    plt.plot(
            times,
            ts,
            color='green',
            linewidth=0.7)

    plt.vlines(
            0.085,
            plt.ylim()[0],
            plt.ylim()[1],
            color='red',
            linestyle='--',
            zorder=1)

    plt.xlabel('Time (s)', fontsize=16)
    plt.ylabel('Decoding accuracy (%)', fontsize=16)

    if fig_dir != None:
        fig_name = f'{R_no}_line_plot_left_right_button_inputs_SVM_decoding_accuracy.svg'
        plt.savefig(os.path.join(fig_dir, fig_name))
    plt.close()


def bar_plot_state_means(model, components, n_states, null_model=False, fig_dir=None):
    '''Produce bar plot of mean component scores for each behavioural state in 
    specified Hidden Markov model and save to directory "fig_dir" if desired'''

    means = tabulate_means(
            model=model,
            components=list(components.keys()),
            component_labels=components,
            n_states=n_states)

    state_labels = [f'State {n}' for n in range(1, n_state+1)]
    means['Component'] = means.index
    means.reset_index(drop=True, inplace=True)
    means = pd.melt(
                frame=means,
                id_vars='Component',
                value_vars=state_labels,
                var_name='State',
                value_name='Component Score')
    
    ax = sns.barplot(
            data=means,
            x='State',
            y='Component Score',
            hue='Component'
            )
    
    #sns.movelegend(ax, "upper left", bbox_to_anchor=(1, 1))
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

    if fig_dir != None:
        if not null_model:
            fig_name = f'{n_states}_state_{len(components)}_component_HMM_comp_means_bar_plot.svg'
        else:
            fig_name = f'null_model_{n_states}_state_{len(components)}_component_HMM_comp_means_bar_plot.svg'
        plt.savefig(os.path.join(fig_dir, fig_name), bbox_inches='tight')
    plt.close()
        

def boxplot_state_component_scores(df, components, n_states, violin=False, null_model=False,
                                   fig_dir=None):
    '''Produce boxplot of component scores for each behavioural state in 
    specified Hidden Markov model and save to "fig_dir" if desired'''
    if not null_model:
        state_var = 'HMM_state'
    else:
        state_var = 'null_HMM_state'
    df = pd.melt(
            frame=df,
            id_vars=state_var,
            value_vars=list(components.keys()),
            var_name='Component',
            value_name='Component score')
    
    if not violin:
        if not null_model:
            fig_name = f'{n_states}_state_{len(components)}_component_HMM_comp_score_box_plot.svg'
        else:
            fig_name = f'null_model_{n_states}_state_{len(components)}_component_HMM_comp_score_box_plot.svg'
        ax = sns.boxplot(
                data=df,
                x=state_var,
                y='Component score',
                hue='Component',
                linewidth=0.8)
    
    else:
        if not null_model:
            fig_name = f'{n_states}_state_{len(components)}_component_HMM_comp_score_violin_plot.svg'
        else:
            fig_name = f'null_model_{n_states}_state_{len(components)}_component_HMM_comp_score_violin_plot.svg'
        ax = sns.violinplot(
                data=df,
                x=state_var,
                y='Component score',
                hue='Component',
                linewidth=0.8)
    
    ax.set_xlabel('State')
    handles, _ = ax.get_legend_handles_labels()
    components_legend = list(components.values())
    plt.legend(
            handles,
            components_legend,
            bbox_to_anchor=(1.05, 1),
            loc=2
            )
    
    if fig_dir != None:
        plt.savefig(os.path.join(fig_dir, fig_name), bbox_inches='tight')
    plt.close()


def plot_transition_matrix(model, components, n_states, null_model=False, fig_dir=None):
    '''Produce heat map of transition matrix annotated with transition probabilities for specified model
    and save to directory "fig_dir"'''
    # define figure parameters
    fig, ax = plt.subplots()
    transmat = model.transmat_
    colors = sns.color_palette("Blues_r", as_cmap=True)
    tick_labels = np.arange(1, n_states+1)
    # plot heatmap
    sns.heatmap(
            data=transmat,
            cmap=colors,
            annot=True,
            linewidths=0.5,
            ax=ax,
            xticklabels=tick_labels,
            yticklabels=tick_labels
            )
    plt.xlabel('State at tetromino t', fontsize=16)
    plt.ylabel('State at tetromino t-1', fontsize=16)
    # save figure if directory is specified
    if fig_dir != None:
        if not null_model:
            fig_name = f'{n_states}_state_{len(components)}_component_model_transition_matrix.svg'
        else:
            fig_name = f'{n_states}_state_{len(components)}_component_null_model_transition_matrix.svg'
        plt.savefig(os.path.join(fig_dir, fig_name))
    plt.close()


def freq_distributions_component_scores_across_states(df, components, n_states, null_model=False,
                                        fig_dir=None):
    '''Produce histograms of component scores for each behavioural state in
    specified Hidden Markov model and save to "fig_dir" if desired'''
    if not null_model:
        state_var = 'HMM_state'
    else:
        state_var = 'null_HMM_state'
    for state in range(df[state_var].nunique()):
        for comp, label in components.items():
            x = df[df[state_var] == state+1][comp]
            plt.hist(x, bins=50)
            plt.xlabel(f'{label} score')
            plt.ylabel('Frequency')
            
            if fig_dir != None:
                if not null_model:
                    fig_name = f'{n_states}_state_{len(components)}_component_HMM_histogram_of_{comp}_in_state_{state+1}.svg'
                else:
                    fig_name = f'null_model_{n_states}_state_{len(components)}_component_HMM_histogram_of_{comp}_in_state_{state+1}.svg'
                plt.savefig(os.path.join(fig_dir, fig_name))
            plt.close() 


def freq_distributions_global_component_scores(df, components, standardised=False,
                                        fig_dir=None):
    '''Produce histograms of component scores for each behavioural state in
    specified Hidden Markov model and save to "fig_dir" if desired'''
    # create individual plot for each component
    for component, label in components.items():
        x = df[component]
        plt.hist(x, bins=50)
        plt.xlabel(f'{label} score')
        plt.ylabel('Frequency')
        
        if fig_dir != None:
            if not standardised:
                fig_name = f'histogram_of_{component}_scores_across_all_episodes.svg'
            else:
                fig_name = f'histogram_of_standardised_{component}_scores_across_all_episodes.svg'
            plt.savefig(os.path.join(fig_dir, fig_name))
        plt.close() 


def multiplot_freq_distributions_global_component_scores(df, components, standardised=False,
                                        fig_dir=None):
    '''Produce multiplot of histograms of component scores for each behavioural state in
    specified Hidden Markov model and save to "fig_dir" if desired'''
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(8,5), sharex=True, sharey=True)
    for component, ax in zip(components.items(), [ax1, ax2, ax3, ax4]):

        x = df[component[0]]
        ax.hist(x, bins=40)
        if ax == ax1 or ax == ax2:
            ax.set_xlabel(f'{component[1]}', labelpad=10)
        else:
            ax.set_xlabel(f'{component[1]}')
    
    ax1.set_ylabel('Frequency')
    ax3.set_ylabel('Freqeuncy')

    fig.tight_layout()
        
    if fig_dir != None:
        if not standardised:
            fig_name = f'multiplot_histograms_of_component_scores_across_all_episodes.svg'
        else:
            fig_name = f'multiplot_histograms_of_standardised_component_scores_across_all_episodes.svg'
        plt.savefig(os.path.join(fig_dir, fig_name))

    plt.close() 


def multiplot_freq_distributions_ROI_amplitudes(df, components, n_states,
                                        fig_dir=None):
    '''Produce multiplot of histograms of neural amplitudes across ROIs in
    specified Hidden Markov model and save to "fig_dir" if desired'''
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(8,5), sharex=True, sharey=True)

    V1_L_df = df[df['scout'] == 'V1_exvivo_L']
    V1_R_df = df[df['scout'] == 'V1_exvivo_R']
    M1_L_df = df[df['scout'] == 'BA6_exvivo_L']
    M1_R_df = df[df['scout'] == 'BA6_exvivo_R']

    ax1.hist(V1_L_df['RMS_alpha'], bins=10)
    ax2.hist(V1_R_df['RMS_alpha'], bins=10)
    ax3.hist(M1_L_df['RMS_mu'], bins=10)
    ax4.hist(M1_R_df['RMS_mu'], bins=10)

    ax1.set_ylabel('Frequency')
    ax3.set_ylabel('Frequency')
    
    ax1.set_xlabel('Left V1 RMS alpha', labelpad=15)
    ax2.set_xlabel('Right V1 RMS alpha', labelpad=15)
    ax3.set_xlabel('Left M1 RMS mu')
    ax4.set_xlabel('Right M1 RMS mu')
    
    fig.tight_layout()
        
    if fig_dir != None:
        fig_name = f'{n_states}_state_{len(components)}_component_HMM_multiplot_histograms_of_ROI_amplitudes.svg'
        plt.savefig(os.path.join(fig_dir, fig_name))

    plt.close() 


def freq_distributions_ROI_amplitudes(df, components, n_states, scouts, freq_band,
                                 bins=20, null_model=False, fig_dir=None):
    '''Produce histograms of RMS alpha for each behavioural state in
    specified Hidden Markov model and save to "fig_dir" if desired'''
    for scout in scouts:
        scout_df = df[df['scout'] == scout]
        x = scout_df[freq_band]
        plt.hist(x.values, bins=bins)
        plt.xlabel('Frequency')
        plt.ylabel(f'{freq_band}')
            
        if fig_dir != None:
            if not null_model:
                fig_name = f'{n_states}_state_{len(components)}_component_HMM_histogram_of_{freq_band}_{scout}.svg'
            else:
                fig_name = f'null_model_{n_states}_state_{len(components)}_component_HMM_histogram_of_RMS_{freq_band}_{scout}.svg'
            plt.savefig(os.path.join(fig_dir, fig_name))
        plt.close()

            
def viz_power_by_state(df,
                       scout, 
                       freq_bands_dict,
                       cutoff=20,
                       freq_band='all_freqs',
                       R_no='all_participants',
                       null_model=False,
                       cmap='tab10',
                       fig_dir=None):
    '''Produce bar plot of power at each frequency for given scout. Power 
    is plotted for each state side by side, and plot is saved to fig_dir
    if directory is specified.'''
    # plot single participant's data if R_no is specified
    if R_no is not 'all_participants':
        df = df[df['SID'] == R_no]
    # retain only frequency bands of interest 
    if freq_band is not 'all_freqs':
        try:
           freqs = freq_bands_dict[freq_band]
        except KeyError:
            print(f'{freq+band} is not a valid frequency band, aborting viz')
            return None
        cols_to_retain = ['SID', 'game_number', 'state', 'file_name', 'scout'] + freqs
    else:
        freqs = [str(x+1)+'Hz' for x in range(cutoff)]
        cols_to_retain = ['SID', 'game_number', 'state', 'file_name', 'scout'] + freqs
    df = df.reindex(columns=cols_to_retain)
    # specify scout 
    df = df[df['scout'] == scout]
    # reshape data to long form for plotting with seaborn
    df = pd.melt(
            df,
            id_vars=['game_number', 'state', 'file_name'],
            value_vars=freqs,
            var_name='Freq',
            value_name='Power')
    df = df.sort_values(by=['game_number', 'state', 'file_name']).reset_index(drop=True)
    # configure colour palette
    state_colours = matplotlib.cm.get_cmap(cmap)
    state_colours = [state_colours(x) for x in range(n_states)]
    # produce bar plot
    sns.barplot(data=df, 
                x='Freq', 
                y='Power', 
                hue='state',
                errwidth=0.5,
                palette=state_colours)
    plt.xticks(rotation=45)

    if fig_dir != None:
        if not null_model:
            fig_name=f'{R_no}_{freq_band}_{scout}_power_by_state.svg'
        else:
            fig_name=f'null_model_{R_no}_{freq_band}_{scout}_power_by_state.svg'
        plt.savefig(os.path.join(fig_dir, fig_name), bbox_inches='tight')
    plt.close()


def bar_chart_of_fractional_occupancies(df,
                                        n_states,
                                        components,
                                        null_model=False,
                                        cmap='tab10',
                                        fig_dir=None):
    '''Produce bar chart of fractional occupancies for each state, where fractional occupancy is defined as the fraction
    of total time participants spend in any given state. The figure is saved to fig_dir if specified'''
    # compute fractional occupancies
    frac_occ = fractional_occupancy(
            df=df,
            for_each_participant=False,
            null_model=null_model)
    if not null_model:
        state = 'HMM_state'
    else: 
        state = 'null_HMM_state'
    # set parameters and plot
    state_colours = matplotlib.cm.get_cmap(cmap)
    state_colours = [state_colours(x) for x in range(n_states)]
    sns.barplot(
            data=frac_occ,
            x=state,
            y='ep_duration',
            palette=state_colours
            )
    # set axis labels
    plt.xlabel('State', fontsize=16)
    plt.ylabel('Frac. occupancy', fontsize=16)
    # save figure if directory is specified
    if fig_dir != None:
        if not null_model:
            fig_name = f'{n_states}_state_{len(components)}_component_model_bar_chart_of_fractional_occupancies.svg'
        else:
            fig_name = f'{n_states}_state_{len(components)}_component_null_model_bar_chart_of_fractional_occupancies.svg'

        plt.savefig(os.path.join(fig_dir, fig_name))
    plt.close()


def histogram_max_frac_occ(
        df,
        n_states,
        components,
        fig_dir=None):
    '''Produce histogram of maximum fractional occupancy across all sessions in the data set, that is, the
    fraction of total time spent in the state that is occupied for the most amount of time in a given game.'''
    max_frac_occ = max_fractional_occupancy(df) 
    plt.hist(
            max_frac_occ,
            color='#8c8c8c')
    plt.xlabel('Max. fractional occupancy', fontsize=16)
    plt.ylabel('No. acquisitions', fontsize=16)
    if fig_dir != None:
       fig_name = f'{n_states}_state_{len(components)}_component_model_histogram_of_max_fractional_occupancies.svg'
       plt.savefig(os.path.join(fig_dir, fig_name))
    plt.close()


def bar_chart_of_lines_cleared_across_states(df,
                                             n_states,
                                             components,
                                             null_model=False,
                                             cmap='tab10',
                                             fig_dir=None):
    '''Produce bar chart of sum total of lines cleared within each state. The figure is saved to
    fig_dir if specified'''
    if not null_model:
        state = 'HMM_state'
    else: 
        state = 'null_HMM_state'
    # get line clears df
    clears = df.groupby(state)['cleared'].sum().reset_index()
    # set parameters and plot
    state_colours = matplotlib.cm.get_cmap(cmap)
    state_colours = [state_colours(x) for x in range(n_states)]
    sns.barplot(
            data=clears,
            x=state,
            y='cleared',
            palette=state_colours
            )
    # set axis labels
    plt.xlabel('State')
    plt.ylabel('# lines cleared')
    # save figure if directory is specified
    if fig_dir != None:
        if not null_model:
            fig_name = f'{n_states}_state_{len(components)}_component_model_bar_chart_of_total_line_clears_across_states.svg'
        else:
            fig_name = f'{n_states}_state_{len(components)}_component_null_model_bar_chart_of_total_line_clears_across_states.svg'

        plt.savefig(os.path.join(fig_dir, fig_name))
    plt.close()


def viz_power_diff_between_states(FFT_df,
                                  scout,
                                  cutoff=20,
                                  fig_dir=None):
    '''For given scout, produce bar plot of differences in power between each 
    pair of states in given dataframe and save to fig_dir'''
    
    
    pass


def boxplot_RMS_alpha_between_states(df, scout, n_states, 
                                     components, R_no='all_participants', 
                                     null_model=False, violin=False, cmap='tab10', 
                                     fig_dir=None):
    '''Produce boxplot (or violin plot if desired) comparing RMS alpha per epoch between behavioural states, 
    in specified brain region (scout) and participant, where plot is produced for all participants
    if no R number is specified'''
    state_colours = matplotlib.cm.get_cmap(cmap)
    state_colours = [state_colours(x) for x in range(n_states)]
    # plot single participant's data if R_no is specified
    if R_no is not 'all_participants':
        df = df[df['SID'] == R_no]
    # specify scout 
    df = df[df['scout'] == scout]

    if not violin:
        if not null_model:
            fig_name = f'{R_no}_{n_states}_state_{len(components)}_component_HMM_{scout}_RMS_alpha_box_plot.svg'
        else:
            fig_name = f'null_model_{R_no}_{n_states}_state_{len(components)}_component_HMM_{scout}_RMS_alpha_box_plot.svg'
        ax = sns.boxplot(
                x=df['state'],
                y=df['RMS_alpha'],
                linewidth=0.8,
                palette=state_colours)
    
    else:
        if not null_model:
            fig_name = f'{R_no}_{n_states}_state_{len(components)}_component_HMM_{scout}_RMS_alpha_violin_plot.svg'
        else:
            fig_name = f'null_model_{R_no}_{n_states}_state_{len(components)}_component_HMM_{scout}_RMS_alpha_violin_plot.svg'
        ax = sns.violinplot(
                x=df['state'],
                y=df['RMS_alpha'],
                linewidth=0.8,
                palette=state_colours)

    if fig_dir != None:
        plt.savefig(os.path.join(fig_dir, fig_name), bbox_inches='tight')
    plt.close()


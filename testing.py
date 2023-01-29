#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from modules import *
from statistics import *
from features import *

import pingouin as pg
import json

with open('params.json') as file:
    params = json.load(file)

# output directories
FIG_DIR = params['fig_dir']
BEHAVIOUR_DIR = params['behaviour_dir']
BRAINSTORM_DIR = params['brainstorm_dir']

# preprocessing params
PARTICIPANTS = params['participants']
IGNORE_PARTICIPANTS = params['participants_to_ignore']

# analysis config
N_STATES = params['n_states']
SECONDS_PER_EPOCH = params['seconds_per_epoch']
COMPONENTS = params['components']
Z_COMPONENTS = params['z_components']

FREQUENCY_BANDS = params['frequency_bands']
SCOUTS = params['regions_of_interest']

FFT_df_path = os.path.join(BEHAVIOUR_DIR, 'all_FFT_df.csv')
null_FFT_df_path = os.path.join(BEHAVIOUR_DIR, 'null_model_all_FFT_df.csv')

if os.path.isfile(FFT_df_path):
    print('loading FFT df')
    FFT_df = pd.read_csv(FFT_df_path)
else:
    print('parsing FFTs for HMM states')
    FFT_df = parse_all_FFT_mats(
            participants_to_ignore=IGNORE_PARTICIPANTS,
            input_path=BRAINSTORM_DIR,
            output_path=BEHAVIOUR_DIR,
            null_model=False)

if os.path.isfile(null_FFT_df_path):
    print('loading null model FFT df')
    null_FFT_df = pd.read_csv(FFT_df_path)
else:
    print('parsing FFTs for null model states')
    null_FFT_df = parse_all_FFT_mats(
            participants_to_ignore=IGNORE_PARTICIPANTS,
            input_path=BRAINSTORM_DIR,
            output_path=BEHAVIOUR_DIR,
            null_model=True)

# plot line graphs of neural activity for button presses
print('Plot time series of neural activity in left and right hemisphere for during left and right button presses for specified participant')

line_plot_avg_button_press_activity(
        R_no='R3154',
        input_path=BRAINSTORM_DIR,
        fig_dir=FIG_DIR)

# plot line graph of SVM decoding
line_plot_left_right_button_decoding(
        R_no='R3154',
        input_path=BRAINSTORM_DIR,
        fig_dir=FIG_DIR)

# compute RMS alpha and append it to our FFT dataframe 
FFT_alpha = FFT_df.reindex(columns=FREQUENCY_BANDS['alpha'])
FFT_mu = FFT_df.reindex(columns=FREQUENCY_BANDS['mu'])
FFT_theta = FFT_df.reindex(columns=FREQUENCY_BANDS['theta'])

FFT_df['RMS_alpha'] = statistics.compute_RMS(FFT_alpha, axis=1)
FFT_df['RMS_mu'] = statistics.compute_RMS(FFT_mu, axis=1)
FFT_df['RMS_theta'] = statistics.compute_RMS(FFT_theta, axis=1)


# same for null model
null_FFT_alpha = null_FFT_df.reindex(columns=FREQUENCY_BANDS['alpha'])
null_FFT_mu = null_FFT_df.reindex(columns=FREQUENCY_BANDS['mu'])
null_FFT_theta = null_FFT_df.reindex(columns=FREQUENCY_BANDS['theta'])

null_FFT_df['RMS_alpha'] = statistics.compute_RMS(null_FFT_alpha, axis=1)
null_FFT_df['RMS_mu'] = statistics.compute_RMS(null_FFT_mu, axis=1)
null_FFT_df['RMS_theta'] = statistics.compute_RMS(null_FFT_theta, axis=1)


# prepare new data structure for our mixed ANOVA
analysis_df = FFT_df.groupby(by=['SID', 'scout', 'state'])[
        ['RMS_alpha', 'RMS_mu', 'RMS_theta']].mean().reset_index()

null_analysis_df = null_FFT_df.groupby(by=['SID', 'scout', 'state'])[
        ['RMS_alpha', 'RMS_mu', 'RMS_theta']].mean().reset_index()


# produce box and violin plots for each scout, comparing RMS alpha between states
for scout in SCOUTS:
    boxplot_RMS_alpha_between_states(
            df=analysis_df,
            scout=scout,
            n_states=N_STATES,
            components=COMPONENTS,
            R_no='all_participants',
            violin=False,
            fig_dir=FIG_DIR)

# check distributions of DV here when function is fixed
'''freq_distributions_RMS_alpha(
        df=FFT_df,
        components=COMPONENTS,
        scouts=SCOUTS,
        n_states=N_STATES,
        null_model=False,
        fig_dir=FIG_DIR)

freq_distributions_RMS_alpha(
        df=FFT_df,
        components=COMPONENTS,
        scouts=SCOUTS,
        n_states=N_STATES,
        null_model=True,
        fig_dir=FIG_DIR)'''


# first look exclusively at V1, averaging left and right hemispheres
analysis_df = analysis_df[analysis_df['scout'].isin(SCOUTS[:2])].reset_index(drop=True)
null_analysis_df = null_analysis_df[null_analysis_df['scout'].isin(SCOUTS[:2])].reset_index(drop=True)

V1_df = analysis_df.groupby(by=['SID', 'state'])['RMS_alpha'].mean().reset_index()
V1_df['scout'] = ['V1'] * len(V1_df)
null_V1_df = null_analysis_df.groupby(by=['SID', 'state'])['RMS_alpha'].mean().reset_index()

freq_distributions_RMS_alpha(
        df=V1_df,
        components=COMPONENTS,
        n_states=N_STATES,
        scouts=['V1'],
        bins=10,
        null_model=False,
        fig_dir=FIG_DIR)

freq_distributions_RMS_alpha(
        df=analysis_df,
        components=COMPONENTS,
        n_states=N_STATES,
        scouts=SCOUTS[:2],
        bins=10,
        null_model=False,
        fig_dir=FIG_DIR)

alpha_aov = pg.rm_anova(
        data=V1_df,
        dv='RMS_alpha',
        within=['state'],
        subject='SID',
        detailed=True)

print('---\nRMS alpha V1 averaged\n---')
print(alpha_aov)

alpha_aov = pg.rm_anova(
        data=analysis_df[analysis_df['scout'] == 'V1_exvivo_L'],
        dv='RMS_alpha',
        within=['state'],
        subject='SID',
        detailed=False)
print('---\nRMS alpha V1 left\n---')
print(alpha_aov)

alpha_aov = pg.rm_anova(
        data=analysis_df[analysis_df['scout'] == 'V1_exvivo_R'],
        dv='RMS_alpha',
        within=['state'],
        subject='SID',
        detailed=False)

print('---\nRMS alpha V1 right\n---')
print(alpha_aov)

# run pairwise tests for RMS alpha
alpha_posthoc = pg.pairwise_ttests(
        data=V1_df,
        dv='RMS_alpha',
        within=['state'],
        subject='SID',
        alpha=0.05,
        padjust='holm',
        effsize='cohen')
        
print('---\nposthoc tests RMS alpha for V1 averaged\n---')
print(alpha_posthoc)

alpha_posthoc = pg.pairwise_ttests(
        data=V1_df,
        dv='RMS_alpha',
        within=['state'],
        subject='SID',
        alpha=0.05,
        padjust='holm',
        effsize='cohen')
        
print('---\nposthoc tests RMS alpha for V1 left\n---')
print(alpha_posthoc)

alpha_posthoc = pg.pairwise_ttests(
        data=analysis_df[analysis_df['scout'] == 'V1_exvivo_L'],
        dv='RMS_alpha',
        within=['state'],
        subject='SID',
        alpha=0.05,
        padjust='holm',
        effsize='cohen')
        
print('---\nposthoc tests RMS alpha for V1 right\n---')
print(alpha_posthoc)

'''
theta_aov = pg.rm_anova(
        data=analysis_df,
        dv='RMS_theta',
        within=['state', 'scout'],
        subject='SID',
        detailed=True)

print('---\nRMS theta\n---')
print(theta_aov)

null_alpha_aov = pg.rm_anova(
        data=null_analysis_df,
        dv='RMS_alpha',
        within=['state', 'scout'],
        subject='SID',
        detailed=True)

print('---\nnull model RMS alpha\n---')
print(null_alpha_aov)


null_theta_aov = pg.rm_anova(
        data=null_analysis_df,
        dv='RMS_theta',
        within=['state', 'scout'],
        subject='SID',
        detailed=True)

print('---\nnull model RMS theta\n---')
print(null_theta_aov)

# run pairwise tests for RMS alpha
alpha_posthoc = pg.pairwise_ttests(
        data=analysis_df,
        dv='RMS_alpha',
        within=['scout', 'state'],
        subject='SID',
        alpha=0.05,
        padjust='holm',
        effsize='cohen')
        
print('---\nposthoc tests RMS alpha\n---')
print(alpha_posthoc)
'''

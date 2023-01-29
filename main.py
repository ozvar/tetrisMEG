#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from modules import *
from statistics import *
from features import *

import pingouin as pg

# initialise selected visualisation parameters
sns_styleset()
np.set_printoptions(suppress=True)

DF_FILE_NAME = 'all_preprocessed_episodes.csv'
# output directories
FIG_DIR = os.path.join(PROJECT_PATH, 'results', 'figures')
RESULTS_DIR = os.path.join(PROJECT_PATH, 'results')
HMM_DIR = os.path.join(PROJECT_PATH, 'results', 'HMMs')

# parameters for preprocessing
IGNORE_FEATURES = summary_features + game_state_features
IGNORE_PARTICIPANTS = ['R6044','R6055']
PARTICIPANTS = [p[:5] for p in os.listdir(BEHAVIOUR_PATH) if p.startswith('R') and p[:5] not in IGNORE_PARTICIPANTS]

# parameters for analysis
N_STATES = 3
COMPONENTS = {
        'well_prep': 'Well preparation',
        'action_inefficiency': 'Action inefficiency',
        'dec_act_latency': 'Decision-action latency',
        'diff_disarray': 'Change in disarray'}
Z_COMPONENTS = {
        'z_well_prep': 'Well preparation (standardised)',
        'z_action_inefficiency': 'Action inefficiency (standardised)',
        'z_dec_act_latency': 'Decision-action latency (standardised)',
        'z_diff_disarray': 'Change in disarray (standardised)'}
SECONDS_PER_EPOCH = 1

# endogenous rhythms of interest
FREQUENCY_BANDS  = {'alpha': ['8Hz', '9Hz', '10Hz', '11Hz', '12Hz'],
                    'mu': ['8Hz', '9Hz', '10Hz', '11Hz', '12Hz', '13Hz'],
                    'theta': ['3Hz', '4Hz', '5Hz', '6Hz', '7Hz']}

# ROIs
SCOUTS = ['V1_exvivo_L', 'V1_exvivo_R', 
          'BA4a_exvivo_L', 'BA4a_exvivo_R', 
          'BA6_exvivo_L', 'BA6_exvivo_R']

# add an if statement here to check whether pca model is present, if not 
# run pca

#loadings, pca = princomp(file_name='lindstedt_archival_episodes.tsv', 
#                         features_to_drop=IGNORE_FEATURES,
#                         n_components=4, 
#                         cutoff=0.2,
#                         display_loadings=True)


# if behavioural data has been preprocessed, read the dataframe
df_path = os.path.join(BEHAVIOUR_PATH, DF_FILE_NAME)
if os.path.isfile(df_path):
    df = pd.read_csv(df_path)
# otherwise preprocess it
else:
    df = preprocess_all_episodes_files(features_to_drop=IGNORE_FEATURES, 
                                       component_labels=comp_names,
                                       participants_to_ignore=IGNORE_PARTICIPANTS,
                                       input_path=BEHAVIOUR_PATH)


# plot distributions of our observations 
print('histograms of component scores across all states and episodes')
freq_distributions_global_component_scores(
        df=df,
        components=COMPONENTS,
        n_states=N_STATES,
        standardised=False,
        fig_dir=FIG_DIR)

freq_distributions_global_component_scores(
        df=df,
        components=Z_COMPONENTS,
        n_states=N_STATES,
        standardised=True,
        fig_dir=FIG_DIR)

print('histograms of component scores across all states and episodes - this time a multiplot')
multiplot_freq_distributions_global_component_scores(
        df=df,
        components=COMPONENTS,
        n_states=N_STATES,
        standardised=False,
        fig_dir=FIG_DIR)

multiplot_freq_distributions_global_component_scores(
        df=df,
        components=Z_COMPONENTS,
        n_states=N_STATES,
        standardised=True,
        fig_dir=FIG_DIR)

# if specified HMMs have already been generated, read them
null_model_name = f'null_model_{N_STATES}_state_group_HMM_{len(COMPONENTS)}_components.pkl'
model_name = f'{N_STATES}_state_group_HMM_{len(COMPONENTS)}_components.pkl'
if os.path.isfile(os.path.join(HMM_DIR, model_name)):
    MODEL, POST_PROB, X, LL = load_pickled_HMM(
                                        model_dir=HMM_DIR,
                                        group_model=True,
                                        n_states=3,
                                        components=COMPONENTS,
                                        null_model=False)
# otherwise generate them
else:
    MODEL, POST_PROB, X, LL = fit_group_HMM(df, 
                                            n_states=N_STATES, 
                                            components=list(COMPONENTS.keys()), 
                                            component_labels=COMPONENTS, 
                                            n_iter=200, 
                                            verbose=True, 
                                            covar_type='diag', 
                                            null_model=False,
                                            model_dir=HMM_DIR)

# same for null model
if os.path.isfile(os.path.join(HMM_DIR, null_model_name)):
    NULL_MODEL, NULL_POST_PROB, NULL_X, NULL_LL = load_pickled_HMM(
                                        model_dir=HMM_DIR,
                                        group_model=True,
                                        n_states=3,
                                        components=COMPONENTS,
                                        null_model=True)

else:
    NULL_MODEL, NULL_POST_PROB, NULL_X, NULL_LL = fit_group_HMM(df, 
                                            n_states=N_STATES, 
                                            components=list(COMPONENTS.keys()), 
                                            component_labels=COMPONENTS, 
                                            n_iter=200, 
                                            verbose=True, 
                                            covar_type='diag', 
                                            null_model=True,
                                            model_dir=HMM_DIR)

# get list of most likely states using viterbi algorithm
HMM_states_list = MODEL.decode(X)[1].tolist()
null_HMM_states_list = NULL_MODEL.decode(X)[1].tolist()
# append to dataframe
df['HMM_state'] = np.array(HMM_states_list)+1
df['null_HMM_state'] = np.array(null_HMM_states_list)+1

# produce descriptive plots of each behavioural state
boxplot_state_component_scores(
                df=df,
                components=COMPONENTS,
                n_states=N_STATES,
                violin=False,
                fig_dir=FIG_DIR)

boxplot_state_component_scores(
                df=df,
                components=COMPONENTS,
                n_states=N_STATES,
                violin=True,
                fig_dir=FIG_DIR)

# same for null model
boxplot_state_component_scores(
                df=df,
                components=COMPONENTS,
                n_states=N_STATES,
                null_model=True,
                violin=False,
                fig_dir=FIG_DIR)

boxplot_state_component_scores(
                df=df,
                components=COMPONENTS,
                n_states=N_STATES,
                null_model=True,
                violin=True,
                fig_dir=FIG_DIR)

# visualise histograms of scores for each component across each state
freq_distributions_component_scores_across_states(
        df=df,
        components=COMPONENTS,
        n_states=N_STATES,
        fig_dir=FIG_DIR)
    
# same for null model
freq_distributions_component_scores_across_states(
        df=df,
        components=COMPONENTS,
        n_states=N_STATES,
        null_model=True,
        fig_dir=FIG_DIR)

# plot transition matrix of the model
plot_transition_matrix(
        model=MODEL,
        components=COMPONENTS,
        n_states=N_STATES,
        null_model=False,
        fig_dir=FIG_DIR)

# same for null model 
plot_transition_matrix(
        model=MODEL,
        components=COMPONENTS,
        n_states=N_STATES,
        null_model=True,
        fig_dir=FIG_DIR)

# plot bar chart of state fractional occupancies
bar_chart_of_fractional_occupancies(
        df=df,
        n_states=N_STATES,
        components=COMPONENTS,
        null_model=False,
        cmap='tab10',
        fig_dir=FIG_DIR)

# same for null model 
bar_chart_of_fractional_occupancies(
        df=df,
        n_states=N_STATES,
        components=COMPONENTS,
        null_model=True,
        cmap='tab10',
        fig_dir=FIG_DIR)

# plot bar chart of sum total line clears across states')
bar_chart_of_lines_cleared_across_states(
        df=df,
        n_states=N_STATES,
        components=COMPONENTS,
        null_model=False,
        cmap='tab10',
        fig_dir=FIG_DIR)

# same for null model
bar_chart_of_lines_cleared_across_states(
        df=df,
        n_states=N_STATES,
        components=COMPONENTS,
        null_model=True,
        cmap='tab10',
        fig_dir=FIG_DIR)

# produce visualisation of state sequence and observations for each game
for participant in PARTICIPANTS:
    n_games = df[df['SID'] == participant]['game_number'].nunique()
    for game_number in range(1, n_games+1):
        print(f'plotting state sequence and observations for participant {participant} game {game_number}')
        viz_states(df, 
                   n_states=N_STATES,
                   post_prob=POST_PROB,
                   components=list(COMPONENTS.keys()), 
                   component_labels=COMPONENTS, 
                   player_id=participant,
                   nth_game=game_number,
                   show_plot=False,
                   null_model=False,
                   cmap='tab10', 
                   fig_dir=FIG_DIR)

# repeat for null model
for participant in PARTICIPANTS:
    n_games = df[df['SID'] == participant]['game_number'].nunique()
    for game_number in range(1, n_games+1):
        print(f'plotting null model state sequence and observations for participant {participant} game {game_number}')
        viz_states(df, 
                   n_states=N_STATES,
                   post_prob=NULL_POST_PROB,
                   components=list(COMPONENTS.keys()), 
                   component_labels=COMPONENTS, 
                   player_id=participant,
                   nth_game=game_number,
                   show_plot=False,
                   cmap='tab10', 
                   null_model=True,
                   fig_dir=FIG_DIR)

# generate .csv files containing state epochs and timestamps to import to brainstorm
generate_all_state_timestamps(
        preprocessed_eps=df,
        participants_to_ignore=IGNORE_PARTICIPANTS,
        slice_length=SECONDS_PER_EPOCH,
        input_path=BEHAVIOUR_PATH)

# same for null model
generate_all_state_timestamps(
        preprocessed_eps=df,
        participants_to_ignore=IGNORE_PARTICIPANTS,
        slice_length=SECONDS_PER_EPOCH,
        input_path=BEHAVIOUR_PATH)

# at this point several matlab scripts to extract neural oscillations from specified scouts 

FFT_df_path = os.path.join(BEHAVIOUR_PATH, 'all_FFT_df.csv')
null_FFT_df_path = os.path.join(BEHAVIOUR_PATH, 'null_model_all_FFT_df.csv')

if os.path.isfile(FFT_df_path):
    print('loading FFT df')
    FFT_df = pd.read_csv(FFT_df_path)
else:
    print('parsing FFTs for HMM states')
    FFT_df = parse_all_FFT_mats(
            null_model=False,
            participants_to_ignore=IGNORE_PARTICIPANTS)

if os.path.isfile(null_FFT_df_path):
    print('loading null model FFT df')
    null_FFT_df = pd.read_csv(FFT_df_path)
else:
    print('parsing FFTs for null model states')
    null_FFT_df = parse_all_FFT_mats(
            null_model=True,
            participants_to_ignore=IGNORE_PARTICIPANTS)

# compare power spectrum of neural oscillations between states, for all participants and scouts
for scout in SCOUTS:
    viz_power_by_state(
            df=FFT_df,
            scout=scout,
            freq_bands_dict=FREQUENCY_BANDS,
            cutoff=20,
            freq_band='all_freqs',
            R_no='all_participants',
            fig_dir=FIG_DIR)

# the same specifically for alpha
for scout in SCOUTS:
    viz_power_by_state(
            df=FFT_df,
            scout=scout,
            freq_bands_dict=FREQUENCY_BANDS,
            cutoff=20,
            freq_band='alpha',
            R_no='all_participants',
            fig_dir=FIG_DIR)

# the same as the above two for each participant separately
for scout in SCOUTS:
    for participant in PARTICIPANTS:
        print(f'plotting all activity in scout {scout} for participant {participant}')
        viz_power_by_state(
                df=FFT_df,
                scout=scout,
                freq_bands_dict=FREQUENCY_BANDS,
                cutoff=20,
                freq_band='all_freqs',
                R_no=participant,
                fig_dir=FIG_DIR)

# the same specifically for alpha
for scout in SCOUTS:
    for participant in PARTICIPANTS:
        print(f'plotting alpha activity in scout {scout} for participant {participant}')
        viz_power_by_state(
                df=FFT_df,
                scout=scout,
                freq_bands_dict=FREQUENCY_BANDS,
                cutoff=20,
                freq_band='alpha',
                R_no=participant,
                null_model=True,
                fig_dir=FIG_DIR)

# repeat for null model
for scout in SCOUTS:
    viz_power_by_state(
            df=FFT_df,
            scout=scout,
            freq_bands_dict=FREQUENCY_BANDS,
            cutoff=20,
            freq_band='all_freqs',
            R_no='all_participants',
            null_model=True,
            fig_dir=FIG_DIR)

for scout in SCOUTS:
    viz_power_by_state(
            df=FFT_df,
            scout=scout,
            freq_bands_dict=FREQUENCY_BANDS,
            cutoff=20,
            freq_band='alpha',
            R_no='all_participants',
            null_model=True,
            fig_dir=FIG_DIR)

# null model, for each participant separately
for scout in SCOUTS:
    for participant in PARTICIPANTS:
        print(f'plotting all activity in scout {scout} for participant {participant}')
        viz_power_by_state(
                df=FFT_df,
                scout=scout,
                freq_bands_dict=FREQUENCY_BANDS,
                cutoff=20,
                freq_band='all_freqs',
                R_no=participant,
                null_model=True,
                fig_dir=FIG_DIR)

# the same specifically for alpha
for scout in SCOUTS:
    for participant in PARTICIPANTS:
        print(f'plotting alpha activity in scout {scout} for participant {participant}')
        viz_power_by_state(
                df=FFT_df,
                scout=scout,
                freq_bands_dict=FREQUENCY_BANDS,
                cutoff=20,
                freq_band='alpha',
                R_no=participant,
                null_model=True,
                fig_dir=FIG_DIR)

# compute RMS alpha and append it to our FFT dataframe 
FFT_alpha = FFT_df.reindex(columns=FREQUENCY_BANDS['alpha'])
FFT_mu = FFT_df.reindex(columns=FREQUENCY_BANDS['mu'])
FFT_theta = FFT_df.reindex(columns=FREQUENCY_BANDS['theta'])

FFT_df['RMS_alpha'] = compute_RMS(FFT_alpha, axis=1)
FFT_df['RMS_mu'] = compute_RMS(FFT_mu, axis=1)
FFT_df['RMS_theta'] = compute_RMS(FFT_theta, axis=1)


# same for null model
null_FFT_alpha = null_FFT_df.reindex(columns=FREQUENCY_BANDS['alpha'])
null_FFT_mu = null_FFT_df.reindex(columns=FREQUENCY_BANDS['mu'])
null_FFT_theta = null_FFT_df.reindex(columns=FREQUENCY_BANDS['theta'])

null_FFT_df['RMS_alpha'] = compute_RMS(null_FFT_alpha, axis=1)
null_FFT_df['RMS_mu'] = compute_RMS(null_FFT_mu, axis=1)
null_FFT_df['RMS_theta'] = compute_RMS(null_FFT_theta, axis=1)


# prepare new data structure for our mixed ANOVA
analysis_df = FFT_df.groupby(by=['SID', 'scout', 'state'])[
        ['RMS_alpha', 'RMS_mu', 'RMS_theta']].mean().reset_index()

null_analysis_df = FFT_df.groupby(by=['SID', 'scout', 'state'])[
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

    boxplot_RMS_alpha_between_states(
            df=analysis_df,
            scout=scout,
            n_states=N_STATES,
            components=COMPONENTS,
            R_no='all_participants',
            violin=True,
            fig_dir=FIG_DIR)

# repeat for each participant
for scout in SCOUTS:
    for participant in PARTICIPANTS:
        boxplot_RMS_alpha_between_states(
                df=FFT_df,
                scout=scout,
                n_states=N_STATES,
                components=COMPONENTS,
                R_no=participant,
                violin=False,
                fig_dir=FIG_DIR)

        boxplot_RMS_alpha_between_states(
                df=FFT_df,
                scout=scout,
                n_states=N_STATES,
                components=COMPONENTS,
                R_no=participant,
                violin=True,
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

FFT_df['scaled_RMS_alpha'] = FFT_df['RMS_alpha']*10**12

from scipy.stats.mstats import winsorize

# 90% winsorization to protect from extreme outliers
#winsorized_RMS_alpha = FFT_df.groupby('SID').apply(lambda x: winsorize(x['RMS_alpha'], limits=(0.1, 0.1))).reset_index()
#FFT_df['RMS_alpha'] = np.concatenate(winsorized_RMS_alpha[0])

# prepare new data structure for our mixed ANOVA
analysis_df = FFT_df.groupby(by=['SID', 'scout', 'state'])['RMS_alpha'].mean().reset_index()
#analysis_df = analysis_df[analysis_df['game_number'] <= 2].reset_index(drop=True)

print(analysis_df.head())

analysis_df['scaled_RMS_alpha'] = analysis_df['RMS_alpha']*10**12

aov = pg.rm_anova(
        data=analysis_df,
        dv='scaled_RMS_alpha',
        within=['state', 'scout'],
        subject='SID',
        detailed=True)
print(aov)

test = analysis_df[analysis_df['scout'].isin(SCOUTS[:2])]

aov = pg.rm_anova(
        data=test,
        dv='scaled_RMS_alpha',
        within=['state', 'scout'],
        subject='SID',
        detailed=True)
print(aov)

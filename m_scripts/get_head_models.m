brainstormdb = '/scratch/groups/Projects/P1454/brainstormdb/Tetris/data';
behaviouralData = '/groups/Projects/P1454/behavioural_data';

% get list of subjects in brainstorm database
subjectBrainstormPattern = fullfile(brainstormdb, 'R*');
subjectsBrainstormDB = dir(subjectBrainstormPattern);

% get list of subjects in project database
subjectBehaviouralDataPattern = fullfile(behaviouralData, 'R*');
subjectsBehaviouralData = dir(subjectBehaviouralDataPattern);
% FOR TESTING, DELETE LATER
subjectsBrainstormDB = subjectsBrainstormDB([1:10, 12:end]);
subjectsBehaviouralData = subjectsBehaviouralData([1:10, 12:end]);


for n = 1 : length(subjectsBrainstormDB)
    % declare current subject
    subjectName = subjectsBrainstormDB(n).name;
    % declare subject's acquisition files in brainstormdb
    acqBrainstormPattern = fullfile(brainstormdb, subjectName, '*resample_band', 'data*.mat');
    acquisitions = dir(acqBrainstormPattern);
    % declare empty room file
    emptyRoomDir = dir(fullfile(brainstormdb, subjectName, 'Empty_room', 'data*'));
    emptyRoomFile = fullfile(emptyRoomDir.folder, emptyRoomDir.name);
    emptyRoomFile = {extractAfter(emptyRoomFile, 'data')};
   
    % compute noise covariance from empty room and copy to adjacent folders
    sFiles = bst_process('CallProcess', 'process_noisecov', emptyRoomFile, [], ...
        'baseline',       [0, 1000], ...
        'datatimewindow', [0, 1000], ...
        'sensortypes',    'MEG', ...st
        'target',         1, ...  % Noise covariance (covariance over baseline time window)
        'dcoffset',       1, ...  % Block by block, to avoid effects of slow shifts in data
        'identity',       0, ...
        'copycond',       1, ...
        'copysubj',       0, ...
        'copymatch',      0, ...
        'replacefile',    1);  % Replace

    for acq = 1: length(acquisitions)
        % identify state directories for current acquisition
        dirNamePattern = strcat('game_', num2str(acq), '*');
        statesDirPattern = fullfile(brainstormdb, subjectName, dirNamePattern);
        statesDir = dir(statesDirPattern);
        for state = 1:length(statesDir)
            % declare list of epoch files for each state for this acq.
            statesFilePattern = fullfile(statesDir(state).folder, statesDir(state).name, 'data*');
            filesStruct = dir(statesFilePattern);
			% create empty container for list of file names as string
            stateFiles = cell(1,length(filesStruct));
            for i = 1 : length(filesStruct)
                fileName = fullfile(filesStruct(i).folder, filesStruct(i).name);
                fileName = extractAfter(fileName, 'data');
                stateFiles{i} = fileName;
            end

        % compute head model for current state
        sFiles = bst_process('CallProcess', 'process_headmodel', stateFiles, [], ...
            'Comment',     '', ...
            'sourcespace', 1, ...  % Cortex surface
            'volumegrid',  struct(...
            'Method',        'isotropic', ...
            'nLayers',       17, ...
            'Reduction',     3, ...
            'nVerticesInit', 4000, ...
            'Resolution',    0.005, ...
            'FileName',      ''), ...
            'meg',         3, ...  % Overlapping spheres
            'eeg',         3, ...  % OpenMEEG BEM
            'ecog',        2, ...  % OpenMEEG BEM
            'seeg',        2, ...  % OpenMEEG BEM
            'openmeeg',    struct(...
            'BemFiles',     {{}}, ...
            'BemNames',     {{'Scalp', 'Skull', 'Brain'}}, ...
            'BemCond',      [1, 0.0125, 1], ...
            'BemSelect',    [1, 1, 1], ...
            'isAdjoint',    0, ...
            'isAdaptative', 1, ...
            'isSplit',      0, ...
            'SplitLength',  4000));

        % compute data covariance for current state epochs
        sFiles = bst_process('CallProcess', 'process_noisecov', stateFiles, [], ...
            'baseline',       [0, 1.0], ...
            'datatimewindow', [0, 1.0], ...
            'sensortypes',    'MEG', ...
            'target',         2, ...  % Data covariance      (covariance over data time window)
            'dcoffset',       1, ...  % Block by block, to avoid effects of slow shifts in data
            'identity',       0, ...
            'copycond',       0, ...
            'copysubj',       0, ...
            'copymatch',      0, ...
            'replacefile',    1);  % Replace

        sFiles = bst_process('CallProcess', 'process_inverse_2018', sFiles, [], ...
            'output',  1, ...  % Kernel only: shared
            'inverse', struct(...
                 'Comment',        'MN: MEG', ...
                 'InverseMethod',  'minnorm', ...
                 'InverseMeasure', 'amplitude', ...
                 'SourceOrient',   {{'fixed'}}, ...
                 'Loose',          0.2, ...
                 'UseDepth',       1, ...
                 'WeightExp',      0.5, ...
                 'WeightLimit',    10, ...
                 'NoiseMethod',    'reg', ...
                 'NoiseReg',       0.1, ...
                 'SnrMethod',      'fixed', ...
                 'SnrRms',         1e-06, ...
                 'SnrFixed',       3, ...
                 'ComputeKernel',  1, ...
                 'DataTypes',      {{'MEG'}}));

        end
    end
end
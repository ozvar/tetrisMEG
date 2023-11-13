# Meta-T

Modified version of John Lindstedt's original pygame implementation of Tetris, updated for Python 3 and to accommodate MEG scanning.

## Requirements

python == 3.8.1

### Install Dependencies

```bash
git clone <GITHUB_REPO_URL>
cd tetrisMEG/Meta-T-main

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Usage

Activate the virtual environment installed above using `source venv/bin/activate`. Run `python meta-t -c default` to launch with default configuration. Additional configurations (e.g. experimental conditions) are listed in Meta-T/configs.

# Readme

[SNAP-TB](https://bmcmedicine.biomedcentral.com/articles/10.1186/s12916-019-1452-0) is an agent based model that simulates TB epidemiology in the five highest TB burden countries.

## Running SNAP-TB

### Python 2.7

Originally written in Python 2.7, this software has been ported to Python 3+. 

### Python 3.7.6

Getting running in 3.7.6

#### Conda:

Install conda/miniconda from:  
* [Link](https://docs.conda.io/en/latest/miniconda.html)  
* [Docs index](https://docs.conda.io/projects/conda/en/latest/user-guide/index.html)

Once Installed:

Create the conda environment from the `yml` file.  
`conda env create -f conda_environment.yml` 

If necessary, the pinned version can also be used.  
`conda env create -f conda_environment_freeze.yml`

Activate the conda environment.  
`conda activate snap-tb`

Run the model  
`python3 test.py`

## Configuring SNAP-TB  

- Configuring SNAP-TB via spreadsheets
    - Important spreadsheets for testing seem to be:
        - `common_parameters.xlsx`
        - `console.xlsx`
    - Would be useful to change these to be `tsv`/`csv`/"flat file" format so it is easier to configure from the command line. 
        - Otherwise generating excel spreadsheets is also possible for unit testing.
        - Should add to spreadsheet a parameter to set the seed.
    - `console.xlsx`
        - n_runs - Number of runs per scenario per simulation
        - n_years - Length of the simulation in years
        - duration_burning_demo - Number of years before introducing TB to the population
        - duration_burning_tb - Number of years after introducing TB before starting the full simulation

###  Pinning Down the Randomness

- The randomness lives in five files. 
    - `agent.py`, `autumn_tool_kit.py`, `household.py`, `model.py`, `test.py`
    - Of these five, four of them use Numpy's randomness, and one uses Python's Random module.
        - Python's Random:
            - `autumn_tool_kit.py`
        - Numpy
            - `agent.py`
            - `household.py`
            - `model.py`
            - `test.py`
    - Would be useful if it was eventually changed use all either standard Random or Numpy's random.


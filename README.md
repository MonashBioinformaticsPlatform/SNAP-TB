# Readme

[SNAP-TB](https://bmcmedicine.biomedcentral.com/articles/10.1186/s12916-019-1452-0) is an agent based model that simulates TB epidemiology in the five highest TB burden countries.

## Running SNAP-TB

### Python 2.7

Originally written in Python 2.7, this software needs to be ported to Python 3+. 

However, to run in 2.7:

#### Conda:

Create the conda environment from the `yml` file.  
`conda env create -f conda_environment.yml`

If necessary, the pinned version can also be used.  
`conda env create -f conda_environment_freeze.yml`

Activate the conda environment.  
`conda activate snap-tb`

Run the model  
`python test.py`

## Configuring SNAP-TB  

- Configuring SNAP-TB via spreadsheets
    - Important spreadsheets for testing seem to be:
        - `common_parameters.xlsx`
        - `console.xlsx`
    - Would be useful to change these to be `tsv`/`csv`/"flat file" format so it is easier to configure from the command line. 


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
    - Would be useful if it was eventually changed use either standard Random or Numpy's random.


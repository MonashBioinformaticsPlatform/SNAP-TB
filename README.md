# Readme

[SNAP-TB](https://bmcmedicine.biomedcentral.com/articles/10.1186/s12916-019-1452-0) is an agent based model that simulates TB epidemiology in the five highest TB burden countries.

## How SNAP-TB is installed:

Clone this repo to get the code and Conda environment files.

### Conda environment:

Conda is the simplest way to install and run dependencies for SNAP-TB

Install conda/miniconda from:  
- [Link](https://docs.conda.io/en/latest/miniconda.html)  
- [Docs index](https://docs.conda.io/projects/conda/en/latest/user-guide/index.html)

Once Installed:

Exit the `(base)` environment.  
`conda deactivate`

Create the conda environment from the `conda_environment.yml` file.  
`conda env create -f conda_environment.yml` 

If necessary, the pinned version can also be used.  
`conda env create -f conda_environment_freeze.yml`

Activate the conda environment.  
`conda activate snap-tb`

Run the model  
`python3 test_disease_harness.py`

## Running SNAP-TB

### Python 2.7

This branch is the original iteration of SNAP-TB. This version exists on `master` and has not been modified.

### Python 3.7.6

The branch `get_running37` is an updated version of SNAP-TB that was refactored to Python 3.7.6. This branch also has a couple of optimisations around the way it calls randomness that speed up simulations.

It is useful to note that this uses an older version of `numpy` (`1.16.4`); newer versions use a different pseudorandom generator which seems to be faster. The version included in the conda environment was to maintain a bit more backwards compatibilty of some results. In future this may help squeeze out results faster. 

`split_tb` includes the changes from `get_running37` and has refactors which move disease related functions/methods into their own classes. This has produced new disease specific classes detailed below.

## Refactor:

Two main additions/refactors to where logic is stored

- "Disease" class - e.g. TestDisease
    - This class produces a disease object which each individual owns an instance of.
    - Contains the state of disease for a given individual
    - Disease is now modelled (at least partly) using disease states as defined by `disease_states`
        - These are simply a dict which contains parameters relevant to that state.
        - The TestDisease contains logic about when progress the disease and adds the trigger to the TestModel
- "DiseaseModel" class - e.g. TestModel
    - This class inherits from the `Model` class and has disease specific functions and logic.
    - The `Model` class now only has "population methods"

### How SNAP-TB thinks about diseases

SNAP-TB has two main parts, an ABM which is disease agnostic which has individuals, and a model, which acts on individuals (who move around, are born, age and go to work/school). In order to impose a disease, we give each Individual a disease object (of class Disease) which carries all the methods and properties of the specific disease we're simulating.

- Each disease is its own class 
    - `TbDisease` and `TestDisease` are examples
    - Each disease requires a model class that knows how to move forward using that specific disease:
        - `move_forward()`
        - `make_individual_die()`
        - `update_programmed_events()`
        - `store_variables()`
    - `move_forward()` is used to call and insert a function that runs TB related cleanup 

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


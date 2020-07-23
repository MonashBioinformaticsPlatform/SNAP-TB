import os

import numpy as np
from numpy import random, linspace
import model
import agent
import importData
from importData import read_sheet, sheet_to_dict

np.random.seed(1)

calibration_params = {None: {'proba_infection_per_contact': linspace(start=0.002, stop=0.0025, num=2)},
                'India': {'proba_infection_per_contact': linspace(start=0.0014, stop=0.0014, num=1)},
                'Indonesia': {'proba_infection_per_contact': linspace(start=0.0017, stop=0.0017, num=1)},
                'China': {'proba_infection_per_contact': linspace(start=0.0014, stop=0.0014, num=1)},
                'Philippines': {'proba_infection_per_contact': linspace(start=0.0021, stop=0.0021, num=1)},
                'Pakistan': {'proba_infection_per_contact': linspace(start=0.0016, stop=0.0016, num=1)}
                }

# for LHS calibration method:
uncertainty_params = {'proba_infection_per_contact': {'distri': 'uniform', 'pars': (0.0030, 0.0045)},
                    'infectiousness_switching_age': {'distri': 'triangular', 'pars': (10., 20.)},
                    'g_child': {'distri': 'beta', 'pars': (73.27, 40.46)},
                    'g_teen': {'distri': 'beta', 'pars': (147., 34.84)},
                    'g_adult': {'distri': 'beta', 'pars': (584.30, 28.53)},
                    'rate_sp_cure_smearpos': {'distri': 'triangular', 'pars': (0.16, 0.31)},
                    'rate_sp_cure_closed_tb': {'distri': 'triangular', 'pars': (0.05, 0.25)},
                    'rate_tb_mortality_smearpos': {'distri': 'triangular', 'pars': (0.31, 0.47)},
                    'rate_tb_mortality_closed_tb': {'distri': 'triangular', 'pars': (0.013, 0.039)},
                    'time_to_treatment': {'distri': 'triangular', 'pars': (0., 14.)},
                    'n_colleagues': {'distri': 'triangular', 'pars': (10., 30.)}
                    }

file_path = os.path.join('spreadsheets', 'console.xlsx')
sheet = read_sheet(file_path)
par_dict = sheet_to_dict(sheet)
countries = par_dict['country']
country_list = countries.split('/')
load_calibrated_models = par_dict['load_calibrated_models']
calibrated_models_directory = par_dict['calibrated_models_directory']
running_mode = par_dict['running_mode']

data = importData.data(None, calibration_params[countries], uncertainty_params)

# TbModel = model.TbModel(data, 1, "scenario_1", 1, 1)
# TbModel.initialise_model(data)
# TbModel.set_initial_infection_states()
# TbModel.set_initial_tb_states()
# TbModel.move_forward()
# print('wait')

#Lets try and initialise a model and run it for ~100 years with no disease
#max time 36525

mymodel = model.TestModel(data, 1, "scenario_1", 1, False)
mymodel.initialised = True
mymodel.run()
# mymodel.initialise_model(data)
# mymodel.move_forward()

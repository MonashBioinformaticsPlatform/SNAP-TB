import unittest
from unittest.mock import MagicMock
import disease
import numpy as np
import tb_activation

class TestDiseaseMethods(unittest.TestCase):
    def setUp(self):
        np.random.seed(1580943402)
        # random.seed(1580943402)
        #Create disease mockup
        self.mock_disease = disease.Disease("TB", {})

    def test_detect_tb(self):
        self.mock_disease.tb_detected = False
        self.mock_disease.detect_tb()
        #Check if detect_tb() sets tb_detected to True
        self.assertTrue(self.mock_disease.tb_detected, msg="tb_detected not set")

    def test_activate_tb(self):
        self.mock_disease.active_tb = False
        self.mock_disease.ltbi = True
        #Check if activate_tb() is able to invert active_tb, ltbi
        self.mock_disease.activate_tb()
        self.assertTrue(self.mock_disease.active_tb, msg="active_tb not set")
        self.assertFalse(self.mock_disease.ltbi, msg="ltbi not set")

    def test_get_relative_susceptibility(self):
        """
        need to refactor ltbi into becoming an argument
        """
        #max efficiency - 0.7
        #start waning - 15
        #end waning - 30
        setup_params = {'bcg_start_waning_year': 15, 
                        'bcg_end_waning_year': 30,
                        'bcg_maximal_efficacy': 0.5,
                        'latent_protection_multiplier': 0.20
                        }
        #IS vaccinated && NOT ltbi
        #Before waning start
        self.mock_disease.vaccinated = True
        self.mock_disease.ltbi = False
        self.assertEqual(self.mock_disease.get_relative_susceptibility(5, setup_params), 0.5)
        #After waning start, before waning end
        self.assertEqual(self.mock_disease.get_relative_susceptibility(21, setup_params), 0.7)
        #After waning end
        self.assertEqual(self.mock_disease.get_relative_susceptibility(31, setup_params), 1)

        #NOT vaccinated && IS ltbi
        #Before waning start
        self.mock_disease.vaccinated = False
        self.mock_disease.ltbi = True
        self.assertEqual(self.mock_disease.get_relative_susceptibility(5, setup_params), 0.2)
        #After waning start, before waning end
        self.assertEqual(self.mock_disease.get_relative_susceptibility(21, setup_params), 0.2)
        #After waning end
        self.assertEqual(self.mock_disease.get_relative_susceptibility(31, setup_params), 0.2)

    def test_get_relative_infectiousness(self):
        #We have linear_scaleup set to false in spreadsheet for simulation - branch is ignored for now
        setup_params = {'infectiousness_switching_age': 15, #age at which infectiousness multiplier reaches .5
                        'rel_infectiousness_smearneg': 0.25,
                        'rel_infectiousness_after_detect': 0.5,
                        'linear_scaleup_infectiousness': False}
        self.mock_disease.programmed['detection'] = 1

        self.mock_disease.tb_organ = "_extrapulmonary"
        self.assertEqual(self.mock_disease.get_relative_infectiousness({}, 0, 0), 0)
        self.mock_disease.tb_organ = "_smearneg"
        self.assertEqual(self.mock_disease.get_relative_infectiousness(setup_params, 100, 15), 0.0625)

        self.mock_disease.tb_organ = "_smearpos"
        self.assertEqual(self.mock_disease.get_relative_infectiousness(setup_params, 100, 15), 0.25)

        self.mock_disease.programmed['detection'] = -1
        self.assertEqual(self.mock_disease.get_relative_infectiousness(setup_params, 100, 15), 0.5)

    def test_infect_individual(self):
        #The determine_activation usually does not return anything
        #We just assert it was called by infect_individual

        self.mock_disease.ltbi = False
        self.mock_disease.tb_strain = "empty"

        self.mock_disease.determine_activation = MagicMock(return_value=None)
        self.mock_disease.infect_individual(100, {}, "mdr", 20, {})

        self.assertTrue(self.mock_disease.ltbi)
        self.assertEqual(self.mock_disease.tb_strain, "mdr")
        self.mock_disease.determine_activation.assert_called_with(100, {}, 20, {})

    def test_determine_activation(self):
        tb_activation.generate_an_activation_profile = MagicMock(return_value=np.array([300]))

        self.mock_disease.determine_activation(1000, {}, 20, 1500)
        self.assertEqual(self.mock_disease.programmed['activation'], 1300)
    
    def test_test_individual_for_latent_infection(self):
        self.mock_disease.ltbi = True
        setup_params = {'ltbi_test_specificity_if_bcg': 0.1, 
                        'ltbi_test_sensitivity': 0.1}
        # self.assertIsInstance(self.mock_disease.test_individual_for_latent_infection(setup_params), bool)
        self.assertFalse(self.mock_disease.test_individual_for_latent_infection(setup_params))

    # def test_get_preventive_treatment(self):


if __name__ == '__main__':
    unittest.main()

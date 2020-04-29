import numpy as np
import tb_activation

class Disease:
    """Defines what will be a generic disease
    
    For now it is very TB specific.

    This class carries properties related to the current state of the disease in
    the agent as well as functions for permuting those. Due to the structure of 
    the model it is accessed via property decorated functions in the Individual.

    This class takes a variable number of keyword arguments, it requires a 
    minimum of:

    """
    def __init__(self, disease_params, name=""):
        self.name = name # Name of the disease params
        self.ltbi = False
        self.tb_strain = None  # 'ds' or 'mdr'
        self.active_tb = False
        self.tb_organ = None
        self.tb_detected = False
        self.tb_treated = False
        self.die_with_tb = False
        self.vaccinated = False
        self.vaccine_immunity_duration = 15.  # in years
        self.params = disease_params # This should be initialised from a specific dictionary
        
        #Individual has some programmed events - Disease specific ones are "activation", "detection", "recovery"
        #   Because of the way this currently works, we will need to pass the non-programmed parts back
        #   These functions will need have some logic moved back into the individual
        self.programmed = {'activation': -1, 'detection': -1, 'recovery': -1}
        
        #@TODO:Need to devise schema for diseases

    # Methods accessible from the agent
    def detect_tb(self):
        self.tb_detected = True

    def activate_tb(self):
        self.active_tb = True
        self.ltbi = False  # convention

    def get_relative_susceptibility(self, age, params):
        rr = 1.
        if self.vaccinated:
            if age <= params['bcg_start_waning_year']:
                efficacy = params['bcg_maximal_efficacy']
            elif age <= params['bcg_end_waning_year']:
                efficacy = params['bcg_maximal_efficacy'] - \
                           (age - params['bcg_start_waning_year']) * \
                                                            params['bcg_maximal_efficacy'] / \
                                                            (params['bcg_end_waning_year'] - params['bcg_start_waning_year'])
            else:
                efficacy = 0.
            rr *= 1. - efficacy

        if self.ltbi:
            rr *= params['latent_protection_multiplier']
        #assert 0 <= rr <= 1
        return rr
    
    def get_relative_infectiousness(self, params, time, age):
        if self.tb_organ == '_extrapulmonary':
            return 0.

        # age-specific profile for infectiousness
        if params['linear_scaleup_infectiousness']:
            if age <= 10.:
                rr = 0.
            elif age >= 15:
                rr = 1.
            else:
                rr = 0.2 * age - 2.
        else:
            # sigmoidal scale-up
            rr = 1. / (1. + np.exp(-(age - params['infectiousness_switching_age'])))

        # organ-manifestation
        if self.tb_organ == '_smearneg':
            rr *= params['rel_infectiousness_smearneg']

        # detection status
        if self.programmed['detection'] > -1 and time >= self.programmed['detection']:
                rr *= params['rel_infectiousness_after_detect']

        return rr

    def infect_individual(self, time, params, strain, age, ind_programmed):
        self.ltbi = True
        self.tb_strain = strain
        self.determine_activation(time, params, age, ind_programmed)

    def determine_activation(self, time, params, age, death_time):
        time_to_activation = tb_activation.generate_an_activation_profile(age, params)

        #  if time_to_activation is not None:
        if np.rint(time + time_to_activation) < death_time:
            # the individual will activate TB
            self.programmed['activation'] = int(np.rint(time + time_to_activation)[0])

    def test_individual_for_latent_infection(self, params):
        """
        Apply screening to an individual. This individual may or may not be infected.
        return: a boolean variable indicating the result of the test (True for positif test)
        """
        if self.ltbi:  # infected individual.
            test_result = bool(np.random.binomial(n=1, p=params['ltbi_test_sensitivity']))
        else:  # not infected
            if self.vaccinated:  # bcg affects specificity
                test_result = bool(np.random.binomial(n=1, p=1. - params['ltbi_test_specificity_if_bcg']))
            else:
                test_result = bool(np.random.binomial(n=1, p=1. - params['ltbi_test_specificity_no_bcg']))
        return test_result

    def get_preventive_treatment(self, params, time, delayed):
        """
        The individual receives preventive treatment. If the individual is currently infected, infection vanishes with
        probability pt_efficacy. The efficacy parameter represents a combined rate of adherence and treatment efficacy.
        Return the date of prevented activation, which is the date of TB activation in the event that the individual was
        meant to progress to active TB.
        """
        date_prevented_activation = None
        if self.ltbi:
            success = np.random.binomial(n=1, p=params['pt_efficacy'])
            if success == 1:
                self.ltbi = False
                # if 'activation' in list(self.programmed.keys()):
                if self.programmed['activation'] > -1:
                    if not delayed or (delayed and (time + params['pt_delay_due_to_tst']) <= self.programmed['activation']):
                        date_prevented_activation = self.programmed['activation']
                        del self.programmed['activation']

        return date_prevented_activation

    def define_tb_outcome(self, time, params, tx_success_prop, death_time):
        """
        This method determines the outcome of the individual's active TB episode, accounting for both natural history
         and clinical management.
        :return:
        A dictionary containing the information to be recorded from the model perspective in case the programmed events
        dictionary needs to be updated. The keys of the returned dictionary may be "death", "recovery" and/or "detection".
        The values are the dates of the associated events.
        """
        # Smear-positive or Smear-negative
        organ_probas = [params['perc_smearpos']/100.,  # smear_pos
                        (100. - params['perc_smearpos'] - params['perc_extrapulmonary'])/100.,  # smear_neg
                        params['perc_extrapulmonary']/100.]  # extrapulmonary

        draw = np.random.multinomial(1, organ_probas)
        index = int(np.nonzero(draw)[0])
        self.tb_organ = ['_smearpos', '_smearneg', '_extrapulmonary'][index]

        # Natural history of TB
        if self.tb_organ == '_smearpos':
            organ_for_natural_history = '_smearpos'
        else:
            organ_for_natural_history = '_closed_tb'

        t_to_sp_cure = round(365.25 * np.random.exponential(scale=1. / params['rate_sp_cure' +
                                                                           organ_for_natural_history]))
        t_to_tb_death = round(365.25 * np.random.exponential(scale=1. / params['rate_tb_mortality' +
                                                                            organ_for_natural_history]))
        if t_to_sp_cure <= t_to_tb_death:
            sp_cure = 1
            t_s = t_to_sp_cure
            t_m = float('inf')
        else:
            sp_cure = 0
            t_s = float('inf')
            t_m = t_to_tb_death

        # np.random generation of programmatic durations
        [t_d, t_t] = np.random.exponential(scale=[365.25/params['lambda_timeto_detection' + organ_for_natural_history],
                                               params['time_to_treatment']])
        t_d = round(t_d)
        t_t = round(t_t)

        # In case of spontaneous cure occurring before detection
        if sp_cure == 1 and t_d >= t_s:
            # In case spontaneous cure occurs before natural death
            if time + t_s < death_time:
                self.programmed['recovery'] = time + t_s
                return {'recovery': time + t_s, 'time_active': t_s}
            else:  # natural death occurs before sp cure. Death will be registered as TB death
                self.die_with_tb = True
                return {'time_active': death_time - time}
        # In case of tb death before detection
        elif sp_cure == 0 and t_d >= t_m:
            self.die_with_tb = True
            if time + t_m < death_time:
                return {'death': time + t_m, 'time_active': t_m}
            else:
                return {'time_active': death_time - time}
        # In case of detection effectively happening
        elif time + t_d < death_time:
            self.programmed['detection'] = time + t_d
            to_be_returned = {'detection': self.programmed['detection'],
                              'time_active': death_time - time}
            # In case of sp cure occurring after detection and before natural death
            if sp_cure == 1 and time + t_s < death_time:
                self.programmed['recovery'] = time + t_s
                to_be_returned['recovery'] = self.programmed['recovery']
                to_be_returned['time_active'] = t_s
            # In case of treatment effectively happening
            if time + t_d + t_t < death_time:
                strain_multiplier = 1.
                if self.tb_strain == 'mdr':
                    strain_multiplier = params['perc_dst_coverage'] / 100.
                    strain_multiplier *= params['relative_treatment_success_rate_mdr']
                tx_cure = np.random.binomial(n=1, p=tx_success_prop * strain_multiplier)
                if tx_cure == 1:
                    if t_d + t_t < t_s: # will not overwrite the sp_cure date if it happens before treatment
                        self.programmed['recovery'] = time + t_d + t_t
                        to_be_returned['recovery'] = self.programmed['recovery']
                        to_be_returned['time_active'] = t_d + t_t
                elif tx_cure == 0 and self.tb_strain == 'ds':  # there is a risk of DR amplification
                    ampli = np.random.binomial(n=1, p=params['perc_risk_amplification'] / 100.)
                    if ampli == 1:
                        self.tb_strain = 'mdr'  # may be improved in the future as the amplification should occur later
                        to_be_returned['dr_amplification'] = time + t_d + t_t
            return to_be_returned
        # Otherwise, natural death occurs before detection
        else:
            return {'time_active': death_time - time}

    def overwrite_tb_outcome_after_acf_detection(self, time, params, tx_success_prop, death_time):
        self.detect_tb()
        # work out treatment outcome
        t_t = round(np.random.exponential(scale=params['time_to_treatment']))

        self.programmed['detection'] = time
        to_be_returned = {}  #'detection': self.programmed['detection']}
        if time + t_t < death_time:
            strain_multiplier = 1.
            if self.tb_strain == 'mdr':
                strain_multiplier = params['perc_dst_coverage'] / 100.
                strain_multiplier *= params['relative_treatment_success_rate_mdr']
            tx_cure = np.random.binomial(n=1, p=tx_success_prop * strain_multiplier)
            if tx_cure == 1:
                if self.programmed['recovery'] > -1 or self.programmed['recovery'] > time + t_t:
                    self.programmed['recovery'] = time + t_t
                to_be_returned['recovery'] = self.programmed['recovery']
            elif tx_cure == 0 and self.tb_strain == 'ds':  # there is a risk of DR amplification
                ampli = np.random.binomial(n=1, p=params['perc_risk_amplification'] / 100.)
                if ampli == 1:
                    self.tb_strain = 'mdr'  # may be improved in the future as the amplification should occur later
                    to_be_returned['dr_amplification'] = time + t_t
        return to_be_returned

    def recover(self):
        #reset all disease related attributes "healthy" state
        self.active_tb = False
        self.ltbi = False
        self.tb_strain = None
        self.tb_organ = None
        self.tb_detected = False
        self.tb_treated = False
        #This one is a bit weird to have in the disease class
        self.die_with_tb = False 
        self.programmed['activation'] = -1
        self.programmed['recovery'] = -1
        #Do we need detection to be reset as well?

    def assign_vaccination_status(self, coverage):
        raise NotImplementedError

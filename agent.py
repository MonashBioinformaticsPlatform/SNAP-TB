# from numpy import random, nonzero, exp, linspace
import numpy as np
import tb_activation
import disease

#Set np.randomness for testing
np.random.seed(1580943402)

def draw_life_duration_using_death_rates():
        """Unused for the moment"""

        # example dict with death rates by age for this individual, i.e. already accounting for their dob.
        death_rates = {0: .006, 5: .0006, 10: .0006, 15: .0015, 20: .0015, 25: .0015, 30: .002,
                       35: .0035, 40: .0035, 45: .0035, 50: .005, 55: .007, 60: .01, 65: .01,
                       70: .1, 75: .1, 80: .2, 85: .3, 90: .5, 95: 1.}

        scales = [1./death_rates[int(i)] for i in np.linspace(0, 95, num=20)]
        times = np.random.exponential(scales)
        found_a_time = False
        for i, time in enumerate(times):
            if time <= 5.:
                life_duration = 5.*i + time
                found_a_time = True
                break
        if not found_a_time:
            life_duration = 100.

        return life_duration


class Individual:
    """
    This class defines the individuals

    An individual is intended to only know about its own function. Anything 
    related to disease is intended to be in a disease object.
    """
    def __init__(self, id, household_id, dOB):
        # individual non TB-specific characteristics
        self.id = id  # integer
        self.household_id = household_id     # integer
        self.dOB = dOB   # integer corresponding to the date of birth
        self.contacts_while_disease = {'household': set([]), 'school': set([]), 'workplace': set([]), 'community': set([])}

        # variables below are not used for the moment
        self.diabetes = False   # boolean
        self.hiv = False    # boolean

        # Create disease object from disease class.
        self.disease = disease.Disease("TB", {})
        # is_infected                       T/F
        # is_latent                         T/F - T is latent, F is active. Some diseases may never beome latent
        # infected_organs                   string array, None
        # is_vaccinated                     T/F - is the disease vaccinated
        # vaccine_immunity_duration         int - in years
        # disease_strain                    string "ds", "mdr" etc
        # is_detected                       T/F - is the infection detected
        # is_treated                        T/F - is the disease treated
        # individual TB-specific characteristics

        # individual group characteristics (school and work related)
        self.group_ids = []  # list of ids of the groups to which the individual is currently belonging
        self.is_ever_gonna_work = False

        # programmed events
        self.programmed = {'death': None, 'leave_home': None, 'go_to_school': None, 'leave_school': None,
                           'leave_work': None}


    # Methods related to moving properties to disease class
    @property
    def active_tb(self):
        return self.disease.active_tb 

    @active_tb.setter
    def active_tb(self, value):
        self.disease.active_tb = value

    @property
    def ltbi(self):
        return self.disease.ltbi

    @ltbi.setter
    def ltbi(self, value):
        self.disease.ltbi = value

    @property
    def tb_strain(self):
        return self.disease.tb_strain
    
    @tb_strain.setter
    def tb_strain(self, value):
        self.disease.tb_strain = value

    @property
    def tb_organ(self):
        return self.disease.tb_organ

    @tb_organ.setter
    def tb_organ(self, value):
        self.disease.tb_organ = value

    @property
    def vaccinated(self):
        return self.disease.vaccinated
    
    @vaccinated.setter
    def vaccinated(self, value):
        self.disease.vaccinated = value

    @property
    def tb_detected(self):
        return self.disease.tb_detected

    @tb_detected.setter
    def tb_detected(self, value):
        self.disease.tb_detected = value

    @property
    def tb_treated(self):
        return self.disease.tb_treated

    @tb_treated.setter
    def tb_treated(self, value):
        self.disease.tb_treated = value

## Strictly Individual related methods ->
    def set_dOB(self, age, current_time, time_step=None):
        """
        Given a specific age (in years) at the time of initialisation, defines the date of birth of an individual.
        The dOB attribute is therefore assigned with a negative integer, corresponding to the number of days elapsed
        between the birth and the model initialisation.
        """
        self.dOB = current_time - round(age*365.25)
        if age == 0.:
            self.dOB = current_time - round(np.random.uniform(low=0., high=time_step))

    def set_death_date(self, life_duration):
        """
        Defines the death date. This concerns natural death so this date might change in case of active TB
        """
        proposed_dOD = self.dOB + round(life_duration*365.25)
        if proposed_dOD > 0.:
            self.programmed['death'] = proposed_dOD
        else:
            self.programmed['death'] = np.random.randint(0, 10.*365.25, 1)[0]

    def set_date_leaving_home(self, params, minimum_date=None):
        """
        Define the date at which individuals will be leaving the household
        :param minimum_date: if specified, lower bound for the leaving date
        """
        self.programmed['leave_home'] = round(self.dOB + 365.25 *\
                                                   np.random.uniform(params['minimal_age_leave_hh'],
                                                                  params['maximal_age_leave_hh']))
        if minimum_date is not None:
            self.programmed['leave_home'] = max(self.programmed['leave_home'], minimum_date)

    def set_school_and_work_details(self, params):
        """
        Define the three following dates:
         - go_to_school_date
         - out_of_school_date
         - out_of_work_date
        """
        age_go_to_school = params['school_age'] * 365.25 + np.random.uniform(-1., 1.) * 365.25  # in days
        age_out_of_school = params['active_age_low'] * 365.25 + np.random.uniform(-3., 3.) * 365.25  # in days
        age_out_of_work = np.random.uniform(55., 70.) * 365.25  # in days

        self.programmed['go_to_school'] = self.dOB + round(age_go_to_school)
        self.programmed['leave_school'] = self.dOB + round(age_out_of_school)
        self.programmed['leave_work'] = self.dOB + round(age_out_of_work)

        active = np.random.binomial(1, params['perc_active']/100.)
        if active == 1:
            self.is_ever_gonna_work = True

    def get_age_in_years(self, time):
        return (time - self.dOB)/365.25

    def is_in_subgroup(self, subgroup, time=None):
        """
        Binary test to inform whether the individual belongs to a specific subgroup.
        subgroup is one of "children" (0-15 yo), "young_children" (0-5 yo)), "adult" (15yo+)
        return: boolean variable
        """
        test = False

        if subgroup == 'children':
            age = self.get_age_in_years(time)
            if age <= 15.:
                test = True
        elif subgroup == 'young_children':
            age = self.get_age_in_years(time)
            if age <= 5.:
                test = True
        elif subgroup == 'adult':
            age = self.get_age_in_years(time)
            if age > 15.:
                test = True
        else:
            print("subgroup is not admissible")

        return test

## Mixed or Disease related function ->

    def get_relative_susceptibility(self, time, params):
        """
        Return the relative susceptibility to infection of the individual. This quantity depends on the following factors:
         vaccination status, age ...
        Returns the relative susceptibility. Baseline is for a non-vaccinated individual.
        """
        return self.disease.get_relative_susceptibility(self.get_age_in_years(time), params)

    def get_relative_infectiousness(self, params, time):
        """
            Return the relative infectiousness of the individual. This quantity depends on the following factors:
            detection status, treatment status. Smear status
            Returns the relative infectiousness. Baseline is for an undetected Smear-positive TB case.
        """
        return self.disease.get_relative_infectiousness(params, time, self.get_age_in_years(time))

    def infect_individual(self, time, params, strain):
        """
        The individual gets infected with LTBI at time "time".
        """
        return self.disease.infect_individual(time, params, strain, self.get_age_in_years(time), self.programmed['death'])

    def determine_activation(self, time, params):
        """
        Determine whether and when the infected individual will activate TB.
        """
        time_to_activation = tb_activation.generate_an_activation_profile(self.get_age_in_years(time), params)

        #  if time_to_activation is not None:
        if np.rint(time + time_to_activation) < self.programmed['death']:
            # the individual will activate TB
            self.disease.programmed['activation'] = int(np.rint(time + time_to_activation)[0])

    def test_individual_for_ltbi(self, params):
        """
        Apply screening to an individual. This individual may or may not be infected.
        return: a boolean variable indicating the result of the test (True for positif test)
        """
        return self.disease.test_individual_for_latent_infection(params)

    def get_preventive_treatment(self, params, time=0, delayed=False):
        """
        The individual receives preventive treatment. If the individual is currently infected, infection vanishes with
        probability pt_efficacy. The efficacy parameter represents a combined rate of adherence and treatment efficacy.
        Return the date of prevented activation, which is the date of TB activation in the event that the individual was
        meant to progress to active TB.
        """
        return self.disease.get_preventive_treatment(params, time, delayed)
        

    def activate_tb(self):
        """
        Make the individual activate TB
        """
        self.disease.activate_tb()

    def define_tb_outcome(self, time, params, tx_success_prop):
        """
        This method determines the outcome of the individual's active TB episode, accounting for both natural history
         and clinical management.
        :return:
        A dictionary containing the information to be recorded from the model perspective in case the programmed events
        dictionary needs to be updated. The keys of the returned dictionary may be "death", "recovery" and/or "detection".
        The values are the dates of the associated events.
        """
        return self.disease.define_tb_outcome(time, params, tx_success_prop, self.programmed['death'])

    def overwrite_tb_outcome_after_acf_detection(self, time, params, tx_success_prop):
        self.disease.overwrite_tb_outcome_after_acf_detection(time, params, tx_success_prop, self.programmed['death'])

    def detect_tb(self):
        self.disease.detect_tb()

    def recover(self):
        """
        Make the individual recover from TB
        """
        # Reset contacts
        self.contacts_while_tb = {'household': set([]), 'school': set([]), 'workplace': set([]), 'community': set([])}
        self.disease.recover()

    def assign_vaccination_status(self, coverage):
        """
        When an individual is born, vaccination occurs with probability 'coverage'
        """
        vacc = np.random.binomial(1, coverage)
        if vacc == 1:
            self.vaccinated = True

if __name__ == '__main__':
    ages = []
    for i in range(10000):
        ages.append(draw_life_duration_using_death_rates())

    print(sum(ages)/len(ages))

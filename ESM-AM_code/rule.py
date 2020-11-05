import math
import pandas as pd
import statsmodels.api as sm
from lifelines import KaplanMeierFitter


class Rule:

    def __init__(self, dataset, alpha):
        self.antecedent = {}
        self.sub_group_cases = dataset.get_instances()
        self.no_covered_cases = len(self.sub_group_cases)
        self.fitness = 0.0
        self.p_value = 0.0
        self.string_repr = ()
        self.KMmodel = {'subgroup': KaplanMeierFitter(), 'complement': KaplanMeierFitter()}
        self._complement_cases = []
        self._quality = None
        self._size_component = None
        self._Dataset = dataset
        self._alpha = alpha

    def set_cases(self, cases):
        self.sub_group_cases = cases
        self.no_covered_cases = len(cases)
        self._complement_cases = list(set(self.sub_group_cases) ^ set(self._Dataset.get_instances()))
        return

    def set_fitness(self):
        sg = pd.Series('sub_group', index=self.sub_group_cases)
        cpm = pd.Series('complement', index=self._complement_cases)
        group = pd.concat([sg, cpm], axis=0, ignore_index=False).sort_index()
        _, self.p_value = sm.duration.survdiff(self._Dataset.survival_times[1], self._Dataset.events[1], group)

        self._quality = 1 - self.p_value
        self.fitness = 1 - self.p_value
        return

    def construct(self, terms_mgr, min_case_per_rule):
        while terms_mgr.available(): # antecedent construction
            term = terms_mgr.sort_term()
            covered_cases = list(set(term.covered_cases) & set(self.sub_group_cases))
            if len(covered_cases) >= min_case_per_rule:
                self.antecedent[term.attribute] = term.value
                self.set_cases(covered_cases)
                terms_mgr.update_availability(term.attribute)
            else:
                break
        self.set_fitness()

        return

    def equals(self, prev_rule):
        antecedent_this = list(self.antecedent.keys())
        antecedent_prev = list(prev_rule.antecedent.keys())
        if len(set(antecedent_this) ^ set(antecedent_prev)) == 0:   # both have same keys
            for attr in antecedent_this:
                if self.antecedent[attr] != prev_rule.antecedent[attr]:
                    return False
        else: return False
        return True

    def set_string_repr(self, index):
        rule_id = 'R' + str(index)
        average_survival = self._Dataset.survival_times[1].iloc[self.sub_group_cases].mean()
        string = 'IF <' +\
                 '> AND <'.join(['{} = {}'.format(key, value) for (key, value) in self.antecedent.items()]) +\
                 '> THAN <average_survival = {0:.4f}>'.format(average_survival)
        self.string_repr = (rule_id, string)
        return

    def set_KMmodel(self):
        # Sub group and Complement of induced rule
        sub_group_times = self._Dataset.survival_times[1].iloc[self.sub_group_cases]
        sub_group_events = self._Dataset.events[1].iloc[self.sub_group_cases]
        complement_times = self._Dataset.survival_times[1].iloc[self._complement_cases]
        complement_events = self._Dataset.events[1].iloc[self._complement_cases]

        self.KMmodel['subgroup'].fit(sub_group_times, sub_group_events,
                                     label='KM estimates for subgroup', alpha=self._alpha)
        self.KMmodel['complement'].fit(complement_times, complement_events,
                                       label='KM estimates for complement', alpha=self._alpha)
        return

    def print_rule(self, file):
        f = open(file, "a+")
        f.write('\n' + self.string_repr[0] + ': ' + self.string_repr[1])
        f.write(' (num-cases={}/{}; p-value={}; fitness={})'.format(self.no_covered_cases,
                                                                    self._Dataset.get_data().shape[0],
                                                                    self.p_value,
                                                                    self.fitness))
        f.close()
        return
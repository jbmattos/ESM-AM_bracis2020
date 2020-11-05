import copy
import json
import pandas as pd
from datetime import datetime
from lifelines import KaplanMeierFitter

from terms_manager import TermsManager
from rule import Rule
from dataset import Dataset
from pruner import Pruner


class ESMAM:

    def __init__(self, no_of_ants, min_case_per_rule, max_uncovered_cases, no_rules_converg, alpha):
        self.no_of_ants = no_of_ants
        self.min_case_per_rule = min_case_per_rule
        self.max_uncovered_cases = max_uncovered_cases
        self.no_rules_converg = no_rules_converg
        self.alpha = alpha

        self.discovered_rule_list = []
        self._Dataset = None
        self._TermsManager = None
        self._Pruner = None
        self._data_path = None
        self._population_survModel = None
        self._no_of_uncovered_cases = None
        self._iterations = 0
        self._run_time = None

    def _get_population_Survival(self):

        kmf = KaplanMeierFitter()
        kmf.fit(self._Dataset.survival_times[1], self._Dataset.events[1],
                label='KM estimates for population', alpha=self.alpha)
        self._population_survModel = kmf
        return

    def _save_SurvivalFunctions(self, prefix):

        index = self._population_survModel.survival_function_.index.copy()
        columns = ['times', 'population'] + [rule.string_repr[0] for rule in self.discovered_rule_list]
        df = pd.DataFrame(columns=columns)
        df.times = index.values
        df.population = self._population_survModel.survival_function_.values

        for rule in self.discovered_rule_list:
            survival_fnc = rule.KMmodel['subgroup'].survival_function_.reindex(index)
            survival_fnc.fillna(method='ffill', inplace=True)
            df[rule.string_repr[0]] = survival_fnc.values

        log_file = '{}_KM-Estimates.txt'.format(prefix)
        df.to_csv(log_file, index=False, header=True)

        return

    def _global_stopping_condition(self):
        if self._no_of_uncovered_cases <= self.max_uncovered_cases:
            return True
        if self._iterations >= self.no_of_ants:
            return True
        return False

    def _local_stopping_condition(self, ant_index, converg_test_index):
        if ant_index >= self.no_of_ants:
            return True
        elif converg_test_index >= self.no_rules_converg:
            return True
        return False

    def _can_add_rule(self, new_rule):
        # check if generated rule already exists on the list
        for rule in self.discovered_rule_list:
            if new_rule.equals(rule):
                return False
        return True

    def read_data(self, data_path, dtype_path,
                  attr_survival_name, attr_event_name):

        if dtype_path:
            with open(dtype_path, 'r') as f: dtypes = json.load(f)
            data = pd.read_csv(data_path, delimiter=',', header=0, index_col=False, dtype=dtypes)
            data.reset_index(drop=True, inplace=True)
        else:
            data = pd.read_csv(data_path, delimiter=',', header=0, index_col=False)
            data.reset_index(drop=True, inplace=True)
        
        self._data_path = data_path
        self._Dataset = Dataset(data, attr_survival_name, attr_event_name)
        return

    def fit(self):
        begin = datetime.now()
        
        # Initialization
        self._TermsManager = TermsManager(self._Dataset, self.min_case_per_rule)
        self._Pruner = Pruner(self._Dataset, self._TermsManager, self.alpha)
        self._no_of_uncovered_cases = self._Dataset.get_no_of_uncovered_cases()
        self._get_population_Survival()

        while not self._global_stopping_condition():

            # local variables
            ant_index = 0
            converg_test_index = 1

            # Initialize rules
            previous_rule = Rule(self._Dataset, self.alpha)
            best_rule = copy.deepcopy(previous_rule)

            # Local search
            while not self._local_stopping_condition(ant_index, converg_test_index):

                current_rule = Rule(self._Dataset, self.alpha)
                current_rule.construct(self._TermsManager, self.min_case_per_rule)
                current_rule = self._Pruner.prune(current_rule)

                if current_rule.equals(previous_rule):
                    converg_test_index += 1
                else:
                    converg_test_index = 1
                    if current_rule.fitness > best_rule.fitness:
                        best_rule = copy.deepcopy(current_rule)

                self._TermsManager.pheromone_updating(current_rule.antecedent, current_rule.fitness)
                previous_rule = copy.deepcopy(current_rule)
                ant_index += 1

            # case: local search didnt find any exceptional rules
            if best_rule.fitness < 1 - self.alpha:
                break
            # saving local search results
            elif self._can_add_rule(best_rule):   # check if rule already exists on the list
                self.discovered_rule_list.append(best_rule)
                self._Dataset.update_covered_cases(best_rule.sub_group_cases)
                self._no_of_uncovered_cases = self._Dataset.get_no_of_uncovered_cases()
            self._TermsManager.pheromone_init()
            self._iterations += 1
        self._run_time = datetime.now() - begin
        
        # generates the rules representative strings
        for index, rule in enumerate(self.discovered_rule_list):
            rule.set_string_repr(index)
            rule.set_KMmodel()
        return

    def save_results(self, prefix):

        log_file = '{}_log.txt'.format(prefix)
        # LOG FILE FOR GENERAL INFO:
        f = open(log_file, "a+")
        f.write('\n\n====== ESMAM PARAMETERS ======')
        f.write('\nNumber of ants: {}'.format(self.no_of_ants))
        f.write('\nNumber of minimum cases per rule: {}'.format(self.min_case_per_rule))
        f.write('\nNumber of maximum uncovered cases: {}'.format(self.max_uncovered_cases))
        f.write('\nNumber of rules for convergence: {}'.format(self.no_rules_converg))
        f.write('\nAlpha value for LogRank confidence: {}'.format(self.alpha))
        f.write('\n\n====== RUN INFO ======')
        f.write('\nDatabase path: {}'.format(self._data_path))
        f.write('\nInstances: {}'.format(self._Dataset.data.shape[0]))
        f.write('\nAttributes: {}'.format(self._Dataset.data.shape[1]))
        f.write('\n# discovered rules: {}'.format(len(self.discovered_rule_list)))
        f.write('\nremaining uncovered cases (%): {}'.format((self._no_of_uncovered_cases/self._Dataset.data.shape[0])))
        f.write('\n>run-time: {}'.format(self._run_time))
        f.close()

        # RULE-SET FILE (RULE MODEL INFO):
        rules_file = '{}_RuleSet.txt'.format(prefix)
        f = open(rules_file, "a+")
        f.write('> Average survival on dataset: {}'.format(self._Dataset.average_survival))
        f.write('\nDISCOVERED RULES:')
        f.close()
        for index, rule in enumerate(self.discovered_rule_list): # print all rules representatives and plots
            rule.print_rule(rules_file)

        # LOG FILE FOR KM ESTIMATES
        self._save_SurvivalFunctions(prefix)

        return

import numpy as np
import math
from term import Term


class TermsManager:

    def __init__(self, dataset, min_case_per_rule):
        self._terms = {}
        self._attr_values = {}
        self._availability = {}
        self._pheromone_table = {}
        self._heuristic_table = {}
        self._no_of_terms = 0
        np.random.seed(0)

        # build object
        self._constructor(dataset, min_case_per_rule)

    def _constructor(self, dataset, min_case_per_rule):

        attr_values = dataset.attr_values.copy()    # Attribute-Values from the entire dataset
        heuristic_accum = 0

        # TERMS:
        # constructs _terms, _availability and _attr_values with the available attribute-values
        for attr, values in attr_values.items():
            attr_available_values = []
            available_values_terms = {}
            for value in values:
                term_obj = Term(attr, value, dataset, min_case_per_rule)
                if term_obj.available():
                    available_values_terms[value] = term_obj
                    attr_available_values.append(value)
                    self._no_of_terms += 1
                    heuristic_accum += term_obj.get_heuristic()
            if attr_available_values:
                self._terms[attr] = available_values_terms.copy()
                self._attr_values[attr] = attr_available_values[:]
                self._availability[attr] = True
            else:
                self._availability[attr] = False

        # TABLES:
        # _pheromone_table: {Attr : {Value : Pheromone}} | _heuristic_table: {Attr : {Value : Heuristic}}
        initial_pheromone = 1 / self._no_of_terms
        for attr, values in self._attr_values.items():
            self._pheromone_table[attr] = {}.fromkeys(values, initial_pheromone)
            self._heuristic_table[attr] = {}.fromkeys(values)
            for value in values:
                self._heuristic_table[attr][value] = (self._terms[attr][value].get_heuristic() / heuristic_accum)

        return

    def _get_prob_accum(self):

        accum = 0
        for attr, values in self._attr_values.items():
            if self._availability[attr]:
                for value in values:
                    accum += self._heuristic_table[attr][value] * self._pheromone_table[attr][value]
        return accum

    def _get_pheromone_accum(self):

        accum = 0
        for attr, values in self._attr_values.items():
            for value in values:
                accum += self._pheromone_table[attr][value]

        return accum

    def _reset_availability(self):

        attrs = list(self._attr_values.keys())
        self._availability = {}.fromkeys(attrs, True)

        return

    def _get_probabilities(self):

        prob_accum = self._get_prob_accum()
        probabilities = []

        for attr, values in self._attr_values.items():
            if self._availability[attr]:
                for value in values:
                    prob = (self._heuristic_table[attr][value] * self._pheromone_table[attr][value]) / prob_accum
                    probabilities.append((prob, self._terms[attr][value]))

        return probabilities

    def size(self):
        return self._no_of_terms

    def available(self):

        for attr in self._availability:
            if self._availability[attr]:
                return True

        return False

    def sort_term(self):

        probabilities = self._get_probabilities()

        nan_check = [math.isnan(p[0]) for p in probabilities]
        if any(nan_check): # !! resolve this problem better
            choice_idx = np.random.choice(len(probabilities), size=1)[0] # random with equal probs
        else:
            probs = [prob[0] for prob in probabilities]
            choice_idx = np.random.choice(len(probabilities), size=1, p=probs)[0]

        return probabilities[choice_idx][1]

    def update_availability(self, attr):
        self._availability[attr] = False
        return

    def get_cases(self, antecedent):

        all_cases = []
        for attr, value in antecedent.items():
            all_cases.append(self._terms[attr][value].covered_cases)

        cases = all_cases.pop()
        for case_set in all_cases:
            cases = list(set(cases) & set(case_set))

        return cases

    def pheromone_updating(self, antecedent, quality):

        # increasing pheromone of used terms
        for attr, value in antecedent.items():
            self._pheromone_table[attr][value] += self._pheromone_table[attr][value] * quality

        # Decreasing not used terms: normalization
        pheromone_normalization = self._get_pheromone_accum()
        for attr, values in self._attr_values.items():
            for value in values:
                self._pheromone_table[attr][value] = self._pheromone_table[attr][value] / pheromone_normalization

        self._reset_availability()

        return

    def pheromone_init(self):
        # Restores pheromone initial configuration
        initial_pheromone = 1 / self._no_of_terms
        self._pheromone_table = {}
        for attr, values in self._attr_values.items():
            self._pheromone_table[attr] = {}.fromkeys(values, initial_pheromone)
        return

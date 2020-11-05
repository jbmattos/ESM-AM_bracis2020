import numpy as np
from heuristics import Heuristics


class Term:

    def __init__(self, attribute, value, dataset, min_case_per_rule):
        self.attribute = attribute
        self.value = value
        self.covered_cases = self._get_cases(dataset.data, dataset.get_col_index(attribute), value)
        self._heuristic = Heuristics(dataset).get_heuristic(attribute, value)
        self._available = self._set_availability(min_case_per_rule)

    def _set_availability(self, min_case_per_rule):
        if len(self.covered_cases) < min_case_per_rule:
            return False
        if self._heuristic == 0:
            return False
        return True

    @staticmethod
    def _get_cases(np_data, attribute_idx, value):
        return list(np.asarray(np_data[:, attribute_idx] == value).nonzero()[0])

    def get_heuristic(self):
        return self._heuristic

    def available(self):
        return self._available

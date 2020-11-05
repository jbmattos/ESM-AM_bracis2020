import copy
from rule import Rule


class Pruner:

    def __init__(self, dataset, terms_mgr, alpha):
        self._terms_mgr = terms_mgr
        self._dataset = dataset
        self.current_rule = None
        self._alpha = alpha

    def prune(self, rule):
        self.current_rule = copy.deepcopy(rule)
        it = 0
        while len(self.current_rule.antecedent) > 1:
            it += 1
            pruning_flag = False
            current_antecedent = self.current_rule.antecedent.copy()

            for attr in current_antecedent:
                # new pruned rule antecedent and cases
                pruned_rule = Rule(self._dataset, self._alpha)
                pruned_rule.antecedent = current_antecedent.copy()
                pruned_rule.antecedent.pop(attr, None)
                pruned_rule.set_cases(self._terms_mgr.get_cases(pruned_rule.antecedent))
                pruned_rule.set_fitness()

                if pruned_rule.fitness >= self.current_rule.fitness:
                    pruning_flag = True
                    self.current_rule = copy.deepcopy(pruned_rule)

            if not pruning_flag:
                break
        return self.current_rule
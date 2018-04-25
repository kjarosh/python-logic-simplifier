from collections import defaultdict
from logic_simplifier.parser import parse
from logic_simplifier.perm import ReducedPermutation


class SimplificationTable(object):
    "Proper implementation of the Quine–McCluskey algorithm"
    
    def __init__(self, grouped):
        self._stages = [grouped]
        """List of stages.
        
        Every stage consists of grouped permutations, i.e. a dictionary
        
            { n: set, ... }
        
        where 'n' is a number of 1's and 'set' is a set of permutation
        which have 'n' ones.
        """
        
        def _default_measure(res):
            ret = 0
            for perm in res:
                ret += len(perm.get_reduced().keys())
            return ret
        
        self.measure = _default_measure
        """A measure used for results.
        
        A function that returns a comparable object for given
        set of reduced permutations.
        
        The algorithm will minimize reduced results based on value returned
        by this measure.
        
        By default it minimizes for number of terms in and-or-and
        expression. For example, for:
        
            a & ~b | b & c
        
        the measure will return 4, as there are 4 terms.
        
        The result given as an argument is in the same format as the
        value returned by 'results()'.
        """
    
    def next_stage(self):
        """Processes the last stage.
        
        If any new reduced permutations are available, it appends the
        new stage and returns 'True'. Otherwise it returns 'False'.
        
        This is the core method for the Quine–McCluskey algorithm.
        """
        
        # get last stage
        stage = self._stages[-1]
        # and initialize a new stage
        newstage = defaultdict(lambda: set())
        
        # for each group
        for gid, perms in stage.items():
            # if it's the last group, skip it
            if not (gid + 1) in stage: continue
            
            # for each permutation from this group
            for perm in perms:
                # for each corresponding permutation
                #   from next stage
                for perm2 in stage[gid + 1]:
                    reduced = perm.reduce(perm2)
                    if reduced != None:
                        # can reduce
                        newstage[gid].add(reduced)
                        perm.processed = True
                        perm2.processed = True
        
        # if newstage is not empty, append it
        if newstage:
            self._stages.append(newstage)
            return True
        
        return False
    
    def fill_stages(self):
        "Processes stages until no more reductions can be done."
        
        while self.next_stage():
            continue
    
    def each_permutation(self, handler):
        "Executes 'handler' for each permutation in each stage."
        
        # for each stage
        for stage in self._stages:
            # for each group in stage
            for _, perms in stage.items():
                # for each permutation in group
                for perm in perms:
                    handler(perm)
    
    def results(self):
        """Gathers resulting permutations from all stages.
        
        It will not return duplicated permutations, i.e. when
        permutation A was reduced from B and C, then neither B
        nor C will be returned.
        
        The returned value is a set of reduced permutations.
        Its representation is following: each reduced permutation
        shall be treated as a conjunction, between reduced permutations
        there shall be a disjunction sign.
        """
        
        ret = set()  # returned value
        
        def handler(perm):
            if not hasattr(perm, 'processed'):
                ret.add(perm)
        
        self.each_permutation(handler);
        
        return ret
    
    def grouped_results(self):
        """Return grouped results.
        
        They are grouped by permutations. A dictionary in the
        following form is returned:
        
            { permutation: set of reduced permutations, ... }
        
        Each dictionary entry is a group.
        """
        
        grouped = defaultdict(lambda: set())
        for reduced in self.results():
            for f in reduced._perms:
                grouped[f].add(reduced)
        
        return grouped
    
    def _exclude_reduced(self, grouped, to_exclude):
        """Exclude given reduced permutation from the grouped permutations.
        
        It means that each group which contains 'to_exclude' will be removed.
        This method returns a modified copy of the grouped results.
        """
        
        ret = grouped.copy()
        
        # search for other permutations
        #   dependent on the reduced term
        #   and delete them
        for perm, reduced in grouped.items():
            if len(reduced) == 0 or to_exclude in reduced:
                del ret[perm]
        
        return ret
    
    def _extract_essentials(self, grouped):
        """Extracts all essentials from a group with the minimal degree.
        
        An 'essential' with a 'degree' D is a reduced permutation from a group
        that has exactly D reduced permutations. Each such group will have
        exactly D essentials.
        
        The algorithm needs to select the best one in each iteration. They are
        chosen with respect to the measure.
        """
        
        min_degree = None
        min_reduced = None
        
        for _, reduced in grouped.items():
            # we want only essential terms
            #   with the given degree
            if min_degree == None or len(reduced) < min_degree:
                min_reduced = reduced
        
        if min_reduced == None: return {}
        
        ret = {}
        
        # it's an essential term,
        #   return every possibility
        for essential in min_reduced:
            ret[essential] = self._exclude_reduced(grouped, essential)
        
        return ret
    
    def _minimal_results_for(self, grouped):
        """Minimize result for the given grouped results.
        
        Grouped results are in the format described in 'grouped_results()'.
        
        The returned value is in the format returned by 'results()'.
        """
        
        min_res = None
        
        # for every essential
        for essential, extracted in self._extract_essentials(grouped).items():
            # minimize!
            res = self._minimal_results_for(extracted)
            res.append(essential)
            if min_res == None or \
                    self.measure(res) < self.measure(min_res):
                min_res = res
        
        if min_res != None:
            # essentials found
            return min_res
        
        # no essentials :(
        return []
    
    def minimal_results(self):
        """Minimize result set from 'results()'.
        
        The returned value is in the format returned by 'results()'.
        """
        
        return self._minimal_results_for(self.grouped_results())
    
    def __str__(self):
        ret = 'SimplificationTable(\n'
        for stage in self._stages:
            ret += '== Stage\n'
            for gid, perms in stage.items():
                ret += str(gid) + ': ' + repr(perms) + '\n'
        ret += ')'
        return ret
    
    @classmethod
    def for_expr(cls, expr):
        positives = expr.generate_positives()
        return cls.group_values(positives)
    
    @staticmethod
    def group_values(values):
        ret = defaultdict(lambda: [])
        for val in values:
            reduced = ReducedPermutation.from_permutation(val)
            ret[val.count_positives()].append(reduced)
        return SimplificationTable(ret)


def main():
    # parsed = parse('~a&b&~c&~d | a&~b&~c&d | a&~b&~c&~d')
    # parsed = parse('b | ~b')
    # parsed = parse('b & ~b')
    
    # example from Wikipedia Quine–McCluskey_algorithm
    # parsed = parse('~a&b&~c&~d | a&~b&~c&~d | a&~b&~c&d | a&~b&c&~d | a&~b&c&d | a&b&~c&~d | a&b&c&~d | a&b&c&d')
    
    # example from Wikipedia Petrick's_method
    parsed = parse('~a&~b&~c | ~a&~b&c | ~a&b&~c | ~a&~b&c | a&b&~c | a&b&c')
    
    print(parsed)
    gv = SimplificationTable.for_expr(parsed)
    
    gv.fill_stages()
    
    for r in gv.results():
        print(r)
    
    print()
    
    minimal = ' | '.join([r._reduced.to_conj() for r in gv.minimal_results()])
    print(minimal if minimal != '' else '0')


if __name__ == '__main__':
    main()

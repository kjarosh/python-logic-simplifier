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
    
    def next_stage(self):
        """Processes the last stage.
        
        If any new reduced permutations are available, it appends the
        new stage and returns 'True'. Otherwise it returns 'False'.
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
        "Processes stages until no more reductions may be made."
        
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
        """
        
        ret = set()  # returned value
        
        def handler(perm):
            if not hasattr(perm, 'processed'):
                ret.add(perm)
        
        self.each_permutation(handler);
        
        return ret
    
    def grouped_results(self):
        """Return grouped results.
        
        They are grouped by permutations. Dictionary in the
        following form is returned:
        
            { permutation: set of reduced permutations, ... }
        
        """
        
        grouped = defaultdict(lambda: set())
        for reduced in self.results():
            for f in reduced._perms:
                grouped[f].add(reduced)
        
        return grouped
    
    def essential_results(self):
        ret = set()
        grouped = self.grouped_results()
        
        while True:
            minterm = None
            minlen = 0
            
            for _, reduced in grouped.items():
                if len(reduced) != 0 and (len(reduced) < minlen or minlen == 0):
                    minlen = len(reduced)
                    minterm = reduced.pop()
            
            if minterm == None: break;
            
            ret.add(minterm)
            for _, reduced in grouped.items():
                reduced.discard(minterm)
        
        # check if any left
        # for _, reduced in grouped.items():
        #    if len(reduced) != 0: raise NotImplementedError()
        
        return ret
    
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
    parsed = parse('~a&b&~c&~d | a&~b&~c&~d | a&~b&~c&d | a&~b&c&~d | a&~b&c&d | a&b&~c&~d | a&b&c&~d | a&b&c&d')
    print(parsed)
    gv = SimplificationTable.for_expr(parsed)
    
    gv.fill_stages()
    
    for r in gv.results():
        print(r.get_reduced())
    
    return
    
    print(gv.essential_results())
    for reduced in gv.essential_results():
        print(reduced._reduced)


if __name__ == '__main__':
    main()

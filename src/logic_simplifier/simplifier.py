from collections import defaultdict
from logic_simplifier.parser import parse


class PermutationTable(object):
    # _stages - list of grouped permutations
    #             [ {0: set(perms), 1: set(perms)}, ... ]
    
    def __init__(self, grouped):
        self._stages = [grouped]
    
    def next_stage(self):
        # get last stage
        group = self._stages[-1]
        newgroup = defaultdict(lambda: set())
        
        # gid = no of 1s
        for gid, perms in group.items():
            if not (gid + 1) in group: continue
            for perm in perms:
                for perm2 in group[gid + 1]:
                    reduced = perm.reduce(perm2)
                    if reduced != None:
                        # can reduce
                        newgroup[gid].add(reduced)
                        perm.processed = True
                        perm2.processed = True
        
        if newgroup:
            print(newgroup)
            self._stages.append(newgroup)
            return True
        
        return False
    
    def fill_stages(self):
        while self.next_stage():
            continue
    
    def results(self):
        ret = set()
        for group in self._stages:
            for _, perms in group.items():
                for perm in perms:
                    if not hasattr(perm, 'processed'):
                        ret.add(perm)
        return ret
    
    def grouped_results(self):
        """grouped by ReducedPermutation.from"""
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
        ret = 'PermutationTable(\n'
        for stage in self._stages:
            ret += '== Stage\n'
            for gid, perms in stage.items():
                ret += str(gid) + ': ' + repr(perms) + '\n'
        ret += ')'
        return ret
    
    @classmethod
    def for_expr(cls, expr):
        positives = Permutation.generate_positives(expr)
        return cls.group_values(positives)
    
    @staticmethod
    def group_values(values):
        ret = defaultdict(lambda: [])
        for val in values:
            reduced = ReducedPermutation.from_permutation(val)
            ret[val.count_positives()].append(reduced)
        return PermutationTable(ret)


class ReducedPermutation(object):
    # _perms -- set of reduced permutations
    # _reduced -- the reduced form
    
    def __init__(self, perms, reduced):
        self._perms = perms
        self._reduced = reduced
        
        if not isinstance(reduced, Permutation):
            raise ValueError()
    
    def reduce(self, p):
        keys = set().union(p._reduced._val.keys(), self._reduced._val.keys())
        ret = dict()
        reduced = False
        
        for key in keys:
            val1 = p._reduced._val[key]
            val2 = self._reduced._val[key]
            
            if val1 == val2:
                ret[key] = val1
            elif reduced:
                # already reduced once
                return None
            else:
                reduced = True
                ret[key] = None
        
        return ReducedPermutation(self._perms.union(p._perms), Permutation(ret))
    
    def __str__(self):
        return repr(self)
    
    def __repr__(self):
        return 'ReducedPermutation(from=' + str(self._perms) + ', to=' + str(self._reduced) + ')'
    
    def __eq__(self, p):
        return isinstance(p, ReducedPermutation) \
            and self._perms == p._perms \
            and self._reduced == p._reduced
    
    def __hash__(self):
        return hash(frozenset(self._perms)) ^ hash(self._reduced)
    
    @staticmethod
    def from_permutation(perm):
        return ReducedPermutation(set([ perm ]), perm)


class Permutation(object):
    # _val - dictionary variable: value
    #          True  - 1
    #          False - 0
    #          None  - don't care
    
    def __init__(self, val):
        self._val = val
    
    def prepend(self, val):
        return Permutation({**val, **self._val})
    
    def count_positives(self):
        positives = 0
        for _, v in self._val.items():
            if v: positives += 1
        return positives
    
    def __str__(self):
        return 'Permutation(' + str(self._val) + ')'
    
    def __repr__(self):
        return 'Permutation(' + repr(self._val) + ')'
    
    def __eq__(self, p):
        return isinstance(p, Permutation) and self._val == p._val
    
    def __hash__(self):
        return hash(frozenset(self._val.items()))
    
    @staticmethod
    def empty():
        return Permutation({})
    
    @classmethod
    def generate_values(cls, varlist):
        if len(varlist) == 0:
            yield cls.empty()
        else:
            for p in cls.generate_values(varlist[1:]):
                yield p.prepend({ varlist[0]: True  })
                yield p.prepend({ varlist[0]: False })
    
    @classmethod
    def generate_positives(cls, expr):
        varlist = list(expr.extract_vars())
        for p in cls.generate_values(varlist):
            if expr.eval(p._val):
                yield p


def main():
    # parsed = parse('~a&b&~c&~d | a&~b&~c&d | a&~b&~c&~d')
    parsed = parse('~a&b&~c&~d | a&~b&~c&~d | a&~b&~c&d | a&~b&c&~d | a&~b&c&d | a&b&~c&~d | a&b&c&~d | a&b&c&d')
    print(parsed)
    gv = PermutationTable.for_expr(parsed)
    
    gv.fill_stages()
    
    print(gv)
    print(gv.essential_results())
    for reduced in gv.essential_results():
        print(reduced._reduced)


if __name__ == '__main__':
    main()

"""
This file contains classes responsible for describing
various permutations.

@author: Kamil Jarosz
"""


class Permutation(object):
    "An immutable class representing a permutation."
    
    def __init__(self, val):
        self._val = val.copy()
        """Permutation value stored as a dictionary.
        
        It has the following structure:
        
            { var: val, ... }
        
        where 'var' is the name of the variable and 'val' is
        its value with the following possibilities:
          * True  -- this variable is 1
          * False -- this variable is 0
          * None  -- don't care
        """
    
    def append(self, val):
        """Appends the given variable values and returns a new permutation.
        
        @param val: a dictionary in the form described in __init__
        """
        
        return Permutation({ **self._val, **val })
    
    def count_positives(self):
        "Count variables with the value equal to 1."
        
        count = 0
        for _, v in self._val.items():
            if v: count += 1
        return count
    
    def values(self):
        "Returns a mapping var -> val described in __init__."
        
        return self._val.copy()
    
    def __str__(self):
        return 'Permutation(' + str(self._val) + ')'
    
    def __repr__(self):
        return 'Permutation(' + repr(self._val) + ')'
    
    def __eq__(self, p):
        try:
            return self._val == p._val
        except AttributeError:
            return False
    
    def __hash__(self):
        if not hasattr(self, '_computed_hash'):
            self._computed_hash = \
                hash(frozenset(self._val.items()))
        
        return self._computed_hash
    
    @staticmethod
    def empty():
        """Returns an empty permutation.
        
        It may be populated further by using 'append'.
        """
        
        return Permutation({})
    
    @classmethod
    def generate_values(cls, varlist):
        if len(varlist) == 0:
            yield cls.empty()
        else:
            for p in cls.generate_values(varlist[1:]):
                yield p.append({ varlist[0]: True  })
                yield p.append({ varlist[0]: False })
    
    @classmethod
    def generate_positives(cls, expr):
        varlist = list(expr.extract_vars())
        for p in cls.generate_values(varlist):
            if expr.eval(p.values()):
                yield p


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


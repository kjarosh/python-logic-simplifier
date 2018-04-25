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
    
    def keys(self):
        "Returns a set of variable names."
        
        return self._val.keys()
    
    def values(self):
        "Returns a mapping var -> val described in __init__."
        
        return self._val.copy()
    
    def value(self, key):
        "Returns a value held by a variable with the given name."
        
        return self._val[key]
    
    def to_conj(self):
        ret = ''
        for k in sorted(self._val.keys()):
            v = self._val[k];
            if v == True: ret += ' & ' + k
            if v == False: ret += ' & ~' + k
        return '1' if ret == '' else ret[3:]
    
    def __str__(self):
        ret = ''
        for k in sorted(self._val.keys()):
            v = self._val[k];
            if v == True: ret += k
            if v == False: ret += '!' + k
        return ret
    
    def __repr__(self):
        return str(self)
    
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
        """Generate all possible values for a list of variables.
        
        Example: for ['a', 'b'], we'll get
         * Permutation({ 'a': False, 'b': False })
         * Permutation({ 'a': False, 'b': True  })
         * Permutation({ 'a': True,  'b': False })
         * Permutation({ 'a': True,  'b': True  })
        """
        
        if len(varlist) == 0:
            # the only possibility is an empty
            #   permutation
            yield cls.empty()
        else:
            for p in cls.generate_values(varlist[1:]):
                yield p.append({ varlist[0]: True  })
                yield p.append({ varlist[0]: False })


class ReducedPermutation(object):
    """This class describes a reduced permutation.
    
    It contains information about the reduced form as well
    as the permutations which the form was reduced from.
    """
    
    def __init__(self, perms, reduced):
        self._perms = perms
        "A set of initial permutations."
        self._reduced = reduced
        "The reduced form."
        
        if not isinstance(reduced, Permutation):
            raise ValueError()
    
    def get_reduced(self):
        return self._reduced
    
    def reduce(self, p):
        """Reduce this permutation with p.
        
        @return: the reduced permutation, or None when
                 reduction is impossible
        """
        
        self_keys = self._reduced.keys()
        p_keys = p._reduced.keys()
        
        keys = set().union(self_keys, p_keys)
        ret = dict()
        reduced = False
        
        for key in keys:
            val1 = p._reduced.value(key)
            val2 = self._reduced.value(key)
            
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
        return 'ReducedPermutation(from=' + str(self._perms) + ', to=' + str(self._reduced) + ')'
    
    def __repr__(self):
        return str(self)
    
    def __eq__(self, p):
        return isinstance(p, ReducedPermutation) \
            and self._perms == p._perms \
            and self._reduced == p._reduced
    
    def __hash__(self):
        return hash(frozenset(self._perms)) ^ hash(self._reduced)
    
    @staticmethod
    def from_permutation(perm):
        return ReducedPermutation(set([ perm ]), perm)


def _test():
    # permutations of a,b,c,d
    for val in Permutation.generate_values(['a', 'b', 'c', 'd']):
        print(val)
    
    # reducing
    a = ReducedPermutation.from_permutation(Permutation({ 'a': True, 'b': False }))
    b = ReducedPermutation.from_permutation(Permutation({ 'a': False, 'b': False }))
    print(a.reduce(b))
    a = ReducedPermutation.from_permutation(Permutation({ 'a': True, 'b': False }))
    b = ReducedPermutation.from_permutation(Permutation({ 'a': False, 'b': True }))
    print(a.reduce(b))
    a = ReducedPermutation.from_permutation(Permutation({ 'a': True, 'b': None }))
    b = ReducedPermutation.from_permutation(Permutation({ 'a': False, 'b': None }))
    print(a.reduce(b))
    a = ReducedPermutation.from_permutation(Permutation({ 'a': True, 'b': False }))
    b = ReducedPermutation.from_permutation(Permutation({ 'a': True, 'b': None }))
    print(a.reduce(b))


if __name__ == '__main__':
    _test();

"""
This file provides a Parser class, used to parse a string
into an expression tree, defined in 'logic_simplifier.expr'.
"""

from logic_simplifier.expr import Operator, Negation, FalseVal, TrueVal, Variable


class ParseException(Exception):
    pass


class Parser(object):
    _ops = [
        { '=' },  # lowest priority
        { '>' },
        { '|' },
        { '^' },
        { '&' },  # highest priority
    ]
    """List of sets of operators with given priorities.
    
    The n-th element of this list holds a set of operators
    with their priority equal to n.
    
    Elements with lower index have lower priority.
    All operators are left-associative.
    """
    
    def __init__(self, data):
        self._data = data
        "String to parse"
        self._pos = 0
        "Actual position"
    
    def parse(self):
        parsed = self._parseexpr()
        
        if self._pos != len(self._data):
            # not everything has been parsed
            raise ParseException('unexpected ' + self._data[self._pos])
        
        return parsed
    
    def _parseexpr(self):
        return self._parsepri(0)

    def _parsepri(self, pri):
        if len(self._ops) <= pri:
            return self._parseneg()
        
        expr = self._parsepri(pri + 1)
        
        while not self._end():
            if not (self._look() in self._ops[pri]):
                # it's not this operator
                break
            
            op = self._next()
            self._skips()
            
            right = self._parsepri(pri + 1)
            expr = Operator(expr, op, pri, right)
        
        return expr
    
    def _parseneg(self):
        if self._look() == '~':
            self._next()
            self._skips()
            return Negation(self._parseterm());
        else:
            return self._parseterm()
        
    def _parseterm(self):
        lk = self._look()
        if lk == '(':
            self._next()
            expr = self._parseexpr()
            
            if self._next() != ')':
                raise ParseException('expected )')
            
            self._skips()
            
            return expr
        elif lk == '0':
            self._next()
            self._skips()
            return FalseVal()
        elif lk == '1':
            self._next()
            self._skips()
            return TrueVal()
        else:
            var = ''
            while not self._end() and self._look().isalpha():
                var += self._next()
                
            self._skips()
            
            if len(var) == 0:
                raise ParseException('expected variable name')
            
            return Variable(var)
    
    def _look(self):
        "Returns value at the current position."
        
        return self._data[self._pos]
    
    def _next(self):
        "Moves to the next position and returns value at the old position."
        
        ret = self._data[self._pos]
        self._pos += 1
        return ret
    
    def _end(self):
        "Check whether end has been reached."
        
        return self._pos >= len(self._data)
    
    def _skips(self):
        "Skip space."
        
        while not self._end() and self._look() == ' ':
            self._pos += 1


def parse(data):
    "Parses the given string into an expression tree."
    return Parser(data).parse()


def _test_parse(expr):
    try:
        print(str(expr).ljust(16) + '  ->  ' + str(parse(expr)))
    except:
        print(str(expr).ljust(16) + '  ->  ' + 'Invalid syntax')


def _test():
    _test_parse('a&b')
    _test_parse('a|~b')
    _test_parse('(~a & b) |c')
    _test_parse('(a & (b) |c)')
    _test_parse('a & (b |c)')
    _test_parse('a & (~b |c')
    _test_parse('a) & (b |c')
    _test_parse('(a > b) |c')
    _test_parse('a > (b |~c)')
    _test_parse('abc & def')
    _test_parse('abc & def *')
    
    print()
    
    expr = parse('a & (b) & 1')
    print(expr)
    print(expr.extract_vars())
    print(expr.eval({
        'a': True,
        'b': False
    }))


if __name__ == '__main__':
    _test()

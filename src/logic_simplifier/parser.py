from logic_simplifier.expr import Operator, Negation, FalseVal, TrueVal, Variable


class Parser(object):
    # all operators ale left-associative
    # negation has the highest priority
    _ops = [
        { '=' },  # lowest priority
        { '>' },
        { '|' },
        { '^' },
        { '&' }
    ]
    
    # _data
    # _pos
    
    def __init__(self, data):
        self._data = data
        self._pos = 0
    
    def parse(self):
        parsed = self._parseexpr()
        if self._pos != len(self._data):
            raise RuntimeError('unexpected ' + self._data[self._pos])
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
                raise RuntimeError('expected )')
            
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
            return Variable(var)
    
    def _look(self):
        return self._data[self._pos]
    
    def _next(self):
        ret = self._data[self._pos]
        self._pos += 1
        return ret
    
    def _end(self):
        return self._pos >= len(self._data)
    
    def _skips(self):
        while not self._end() and self._look() == ' ':
            self._pos += 1


def parse(data):
    return Parser(data).parse()


def _test_parse(expr):
    try:
        print(str(expr) + '  ->  ' + str(parse(expr)))
    except:
        print(str(expr) + '  ->  ' + 'Invalid syntax')


if __name__ == '__main__':
    _test_parse('a&b')
    _test_parse('a|~b')
    _test_parse('(~a & b) |c')
    _test_parse('(a & (b) |c)')
    _test_parse('a & (b |c)')
    _test_parse('a & (~b |c')
    _test_parse('a) & (b |c')
    _test_parse('(a > b) |c')
    _test_parse('a > (b |~c)')
    
    expr = parse('a & (b) & 1')
    print(expr)
    print(expr.extract_vars())
    print(expr.eval({
        'a': True,
        'b': False
    }))



class InvalidOperatorException(Exception):
    pass


class VariableNotFoundException(Exception):
    pass


class Expression(object):

    def eval(self, varmap):
        raise NotImplementedError
    
    def extract_vars(self):
        return set()


class Negation(Expression):
    # expr
    
    def __init__(self, expr):
        self.expr = expr
    
    def eval(self, varmap):
        return not self.expr.eval(varmap)
    
    def extract_vars(self):
        return self.expr.extract_vars()
    
    def __str__(self):
        return '~' + str(self.expr)


class Operator(Expression):
    # left
    # op
    # pri
    # right
    
    def __init__(self, left, op, pri, right):
        self.left = left
        self.op = op
        self.pri = pri
        self.right = right
    
    def eval(self, varmap):
        p = lambda: self.left.eval(varmap)
        q = lambda: self.right.eval(varmap)
        
        if   self.op == '>': return not (p() and not q())
        elif self.op == '&': return p() and q()
        elif self.op == '|': return p() or q()
        elif self.op == '^': return p() != q()
        elif self.op == '=': return p() == q()
        else:
            raise InvalidOperatorException(self.op)
    
    def extract_vars(self):
        return self.left.extract_vars().union(self.right.extract_vars())
    
    def __str__(self):
        ret = ''
        
        # if priority is lower, we need to use parentheses
        
        if hasattr(self.left, 'pri') and self.left.pri < self.pri:
            ret += '(' + str(self.left) + ')'
        else:
            ret += str(self.left)
            
        ret += ' ' + self.op + ' '
        
        if hasattr(self.right, 'pri') and self.right.pri < self.pri:
            ret += '(' + str(self.right) + ')'
        else:
            ret += str(self.right)
        
        return ret


class Variable(Expression):
    # name
    
    def __init__(self, name):
        self.name = name
    
    def eval(self, varmap):
        if self.name in varmap:
            return varmap[self.name]
        
        raise VariableNotFoundException(self.name)
    
    def extract_vars(self):
        return { self.name }
    
    def __str__(self):
        return self.name


class FalseVal(Expression):

    def eval(self, _):
        return False
    
    def extract_vars(self):
        return set()
    
    def __str__(self):
        return '0'


class TrueVal(Expression):

    def eval(self, _):
        return True
    
    def extract_vars(self):
        return set()
    
    def __str__(self):
        return '1'


from __future__ import division
from __future__ import unicode_literals
from past.utils import old_div
__docformat__ = 'restructuredtext'

from fipy.variables.cellToFaceVariable import _CellToFaceVariable
from fipy.tools.numerix import exp, take, where

__all__ = ["ScharfetterGummelFaceVariable"]

class ScharfetterGummelFaceVariable(_CellToFaceVariable):
    def __init__(self, var, boundaryConditions=()):
        _CellToFaceVariable.__init__(self, var)
        self.bcs = boundaryConditions
        
    def _calcValue_(self, alpha, id1, id2):
        cell1 = take(self.var,id1)
        cell2 = take(self.var,id2)
        delta = cell1 - cell2
        
        eps = 1e-14
        value = where(abs(delta) < eps, old_div(1., exp(delta)), 0.)
        delta = where(abs(delta) < eps, eps, delta) 
        value = where((abs(delta) > eps) & (delta < 100), 
                      old_div(delta, (exp(delta) - 1)), value)
                            
        value *= exp(cell1) 
        
        for bc in self.bcs:
            if isinstance(bc, FixedValue):
                value[bc.faces.value] = bc._value
        
        return value

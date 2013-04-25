from SymbolTable import *
SYMBOL_TABLE = SymbolTable()

VM_OPERATORS = {'+':'add', '-':'sub', '*':'call Math.multiply 2', '/':'call Math.divide 2', '|':'or', '&':'and', '<':'lt', '>':'gt', '=':'eq', }
UNARY_OPERATORS = {'~':'not', '-':'neg'}
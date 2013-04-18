from JackTokenizer import *
from SymbolTable import *

class CompilationEngine:
  def __init__(self, tokens, outfile):
    self.tokens = tokens
    self.i = 0
    self.out = outfile
    self.indent = 0
    self.compileClass()
    self.linenumber

  def fail(self, message):
    print ">>>>>>>>>>>>>>>>>>>>", message, self.linenumber

  def assertEnd(self):
    if self.i != len(self.tokens):
      self.fail('Expected end-of-file after class definition')

  def nextToken(self):
    if self.i >= len(self.tokens):
      self.fail('Unexpected end of file')
    token = self.tokens[self.i]
    self.i += 1
    self.linenumber = token[2]
    return token

  def peek(self):
    token = self.nextToken()
    self.i -= 1
    return token

  def keyword(self, kw):
    token = self.nextToken()
    if token[0] != KEYWORD or token[1] != kw:
      self.fail('Expected keyword: %s' % kw)
    print >>self.out, ' '*self.indent + '<keyword> %s </keyword>' % token[1]
    return token[1]

  def identifier(self):
    token = self.nextToken()
    if token[0] != IDENTIFIER:
      self.fail('Expected identifier')
    print >>self.out, ' '*self.indent + '<identifier> %s </identifier>' % \
        token[1]
    return token[1]

  def symbol(self, s):
    token = self.nextToken()
    if token[0] != SYMBOL or token[1] != s:
      self.fail('Expected symbol: %s' % repr(s))
    if s == '<': s = '&lt;'
    if s == '>': s = '&gt;'
    if s == '&': s = '&amp;'
    print >>self.out, ' '*self.indent + '<symbol> %s </symbol>' % s
    return token[1]

  def expectType(self):
    token = self.peek()
    if token[0] == KEYWORD and token[1] in ['int', 'char', 'boolean']:
      return self.keyword(token[1])
    return self.identifier()

  def compileClass(self):
    self.symbol_table = SymbolTable()
    print >>self.out, ' '*self.indent + '<class>'
    self.indent += 2
    self.keyword('class')
    name = self.identifier()
    self.symbol('{')
    while True:
      token = self.peek()
      if token[0] != KEYWORD or token[1] not in ['static', 'field']:
        break
      self.compileClassVarDec()
    while True:
      token = self.peek()
      if token[0] != KEYWORD or token[1] not in ['constructor', 'function', 'method']:
        break
      self.compileSubroutine()
    self.symbol('}')
    self.indent -= 2
    print >>self.out, ' '*self.indent + '</class>'
    print self.symbol_table

  def expectVariables(self):
    variables = []
    variables.append(self.expectType())
    while True:
      variables.append(self.identifier())
      if self.peek()[1] == ',':
        self.symbol(',')
      else:
        break
    return variables

  def compileClassVarDec(self):
    print >>self.out, ' '*self.indent + '<classVarDec>'
    self.indent += 2
    token = self.peek()
    kind = self.keyword(token[1])
    variables = self.expectVariables()
    _type = variables[0]
    names = variables[1:]
    for name in names:
      self.symbol_table.define(name, _type, kind)
    self.symbol(';')
    self.indent -= 2
    print >>self.out, ' '*self.indent + '</classVarDec>'

  def compileVarDec(self):
    print >>self.out, ' '*self.indent + '<varDec>'
    self.indent += 2
    self.keyword('var')
    variables = self.expectVariables()
    self.symbol(';')
    self.indent -= 2
    print >>self.out, ' '*self.indent + '</varDec>'
    return variables

  def expectParams(self):
    params = []
    types = []
    names = []
    print >>self.out, ' '*self.indent + '<parameterList>'
    self.indent += 2
    while True:
      if self.peek()[1] == ')':
        break
      types.append(self.expectType())
      names.append(self.identifier())
      if self.peek()[1] == ',':
        self.symbol(',')
    self.indent -= 2
    print >>self.out, ' '*self.indent + '</parameterList>'
    params.append(types)
    params.append(names)
    return params

  def compileSubroutine(self):
    self.symbol_table.startSubroutine()
    print >>self.out, ' '*self.indent + '<subroutineDec>'
    self.indent += 2
    token = self.peek()
    self.keyword(token[1])
    self.keyword('void') if self.peek()[1] == 'void' else self.expectType()
    self.identifier()
    self.symbol('(')
    params = self.expectParams()
    types = params[0]
    names = params[1]
    for i in range(len(types)):
      self.symbol_table.define(names[i], types[i], 'arg')
    self.symbol(')')
    self.compileSubroutineBody()
    self.indent -= 2
    print >>self.out, ' '*self.indent + '</subroutineDec>'

  def compileSubroutineBody(self):
    print >>self.out, ' '*self.indent + '<subroutineBody>'
    self.indent += 2
    self.symbol('{')
    while self.peek()[1] != '}':
      token = self.peek()
      if token[1] == 'var':
        variables = self.compileVarDec()
        _type = variables[0]
        names = variables[1:]
        for name in names:
          self.symbol_table.define(name, _type, 'var')
      else:
        self.expectStatements()
    self.symbol('}')
    self.indent -= 2
    print >>self.out, ' '*self.indent + '</subroutineBody>'

  def expectStatement(self):
    statement = self.peek()[1]
    print >>self.out, ' '*self.indent + '<%sStatement>' % statement
    self.indent += 2

    if self.peek()[1] == 'let':
      self.keyword('let')
      self.identifier()
      if self.peek()[1] == '[':
        self.symbol('[')
        self.expectExpression()
        self.symbol(']')
      self.symbol('=')
      self.expectExpression()
      self.symbol(';')
    elif self.peek()[1] == 'if':
      self.keyword('if')
      self.symbol('(')
      self.expectExpression()
      self.symbol(')')
      self.symbol('{')
      self.expectStatements()
      self.symbol('}')
      if self.peek()[1] == 'else':
        self.keyword('else')
        self.symbol('{')
        self.expectStatements()
        self.symbol('}')
    elif self.peek()[1] == 'while':
      self.keyword('while')
      self.symbol('(')
      self.expectExpression()
      self.symbol(')')
      self.symbol('{')
      self.expectStatements()
      self.symbol('}')
    elif self.peek()[1] == 'do':
      self.keyword('do')
      self.expectSubroutineCall()
      self.symbol(';')
    elif self.peek()[1] == 'return':
      self.keyword('return')
      if self.peek()[1] != ';':
        self.expectExpression()
      self.symbol(';')
    else:
      self.fail("Expected statement")

    self.indent -= 2
    print >>self.out, ' '*self.indent + "</%sStatement>" % statement

  def expectStatements(self):
    print >>self.out, ' '*self.indent + "<statements>"
    self.indent += 2

    next = self.peek()[1]
    while next in ['let', 'if', 'while', 'do', 'return']:

      self.expectStatement()
      next = self.peek()[1]

    self.indent -=2
    print >>self.out, ' '*self.indent + "</statements>"

  def constant(self):
    token = self.nextToken()
    if "Constant" not in token[0]:
      fail("Expected constant.")
    print >>self.out, ' '*self.indent + "<%s> %s </%s>" % (token[0], token[1], token[0])

  def expectTerm(self):
    print >>self.out, ' '*self.indent + "<term>"
    self.indent += 2

    token = self.peek()
    if "Constant" in token[0]:
      self.constant()
    elif token[1] in ['true', 'false', 'null', 'this']:
      self.keyword(token[1])
    elif token[0] == IDENTIFIER:
      self.identifier()
      if self.peek()[1] == '.':
          self.expectSubroutineCall()
      if self.peek()[1] == "[":
        self.symbol('[')
        self.expectExpression()
        self.symbol(']')
    elif token[1] == '(':
      self.symbol('(')
      self.expectExpression()
      self.symbol(')')
    else:
      if token[1] in "-~":
        self.symbol(token[1])
        self.expectTerm()
      else:
        self.fail("Expected term.")

    self.indent -= 2
    print >>self.out, ' '*self.indent + "</term>"

  def expectOp(self):
    self.symbol(self.peek()[1]) if self.peek()[1] in OPERATORS else self.fail("Expected operator")

  def expectExpression(self):
    print >>self.out, ' '*self.indent + '<expression>'
    self.indent += 2
    self.expectTerm()
    while self.peek()[1] in OPERATORS:
      self.expectOp()
      self.expectTerm()
    self.indent -= 2
    print >>self.out, ' '*self.indent + '</expression>'

  def expectExpressionList(self):
    print >>self.out, ' '*self.indent + '<expressionList>'
    self.indent += 2
    if self.peek()[1] != ')':
      self.expectExpression()
      while self.peek()[1] == ',':
        self.symbol(',')
        self.expectExpression()
    self.indent -= 2
    print >>self.out, ' '*self.indent + '</expressionList>'


  def expectSubroutineCall(self):
    self.identifier()
    if self.peek()[1] == '.':
      self.symbol('.')
      self.identifier()
    self.symbol('(')
    self.expectExpressionList()
    self.symbol(')')

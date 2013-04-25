from JackTokenizer import *
from constants import *
from VmWriter import *

class CompilationEngine:
  def __init__(self, tokens, outfile):
    self.writer = VmWriter('myMain.vm')
    self.tokens = tokens
    self.i = 0
    self.out = outfile
    self.indent = 0
    self.linenumber = 0
    self.labelNum = 0
    self.numLocalVariables = 0
    self.compileClass()
    self.writer.close()

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
    print >>self.out, ' '*self.indent + '<identifier> %s </identifier>' % token[1]
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
    self.fieldCount = 0;
    print >>self.out, ' '*self.indent + '<class>'
    self.indent += 2
    self.keyword('class')
    self.className = self.identifier()
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
    print SYMBOL_TABLE

  def expectVariables(self):
    variables = []
    variables.append(self.expectType())
    while True:
      variables.append(self.identifier())
      if self.peek()[1] == ',':
        self.symbol(',')
      else:
        return variables

  def compileClassVarDec(self):
    print >>self.out, ' '*self.indent + '<classVarDec>'
    self.indent += 2
    token = self.peek()
    kind = self.keyword(token[1])
    if kind == 'field':
      self.fieldCount += 1
    variables = self.expectVariables()
    _type = variables[0]
    names = variables[1:]
    for name in names:
      SYMBOL_TABLE.define(name, _type, kind)
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
    SYMBOL_TABLE.startSubroutine()
    print >>self.out, ' '*self.indent + '<subroutineDec>'
    self.indent += 2
    self.isMethod = False
    self.isConstructor = False
    token = self.peek()
    if token[1] == 'constructor':
      self.isConstructor = True
    elif token[1] == 'method':
      self.isMethod = True
    self.keyword(token[1])
    self.keyword('void') if self.peek()[1] == 'void' else self.expectType()
    self.subName = self.peek()[1]
    self.identifier()
    self.symbol('(')
    params = self.expectParams()
    types = params[0]
    names = params[1]
    for i in range(len(types)):
      SYMBOL_TABLE.define(names[i], types[i], 'arg')
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
      while token[1] == 'var':
        variables = self.compileVarDec()
        self.numLocalVariables = len(variables[1:])
        _type = variables[0]
        names = variables[1:]
        for name in names:
          SYMBOL_TABLE.define(name, _type, 'var')
        token = self.peek()
      # write function/method/constructor vm code
      self.writer.writeFunction(self.className + '.' + self.subName, self.numLocalVariables)
      if self.isConstructor:
        self.writer.writePush("constant", self.fieldCount)
        self.writer.writeCall("Memory.alloc", 1) #allocate space for this object
        self.writer.writePop("pointer", 0) #assign object to 'this'
      elif self.isMethod:
        self.writer.writePush(SYMBOL_TABLE.ARG, 0)
        self.writer.writePop("pointer", self.writer.THIS_POINTER)

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
      var = self.identifier()
      containsList = False
      if self.peek()[1] == '[':
        containsList = True
        self.symbol('[')
        self.expectExpression()
        self.writer.writePush(SYMBOL_TABLE.kindOf(var), SYMBOL_TABLE.getOffset(var))
        self.writer.writeArithmetic('add')
        self.symbol(']')
      self.symbol('=')
      self.expectExpression()
      if containsList:
        self.writer.writePop('temp', 0)
        self.writer.writePop('pointer', 1)
        self.writer.writePush('temp', 0)
        self.writer.writePop('that', 0)
      else:
        kind = SYMBOL_TABLE.kindOf(var)
        offset = SYMBOL_TABLE.getOffset(var)
        self.writer.writePop(kind, offset)
      self.symbol(';')
    elif self.peek()[1] == 'if':
      trueLabel = "IF_TRUE" + str(self.labelNum)
      falseLabel = "IF_FALSE" + str(self.labelNum)
      endLabel = "IF_END" + str(self.labelNum)
      self.labelNum += 1

      self.keyword('if')
      self.symbol('(')
      self.expectExpression()

      # write vm if without else
      self.writer.writeIf(trueLabel)
      self.writer.writeGoto(falseLabel)
      self.writer.writeLabel(trueLabel)

      self.symbol(')')
      self.symbol('{')
      self.expectStatements()
      self.symbol('}')
      if self.peek()[1] == 'else':

        #write vm without else
        self.writer.writeGoto(endLabel)
        self.writer.writeLabel(falseLabel)
        self.keyword('else')
        self.symbol('{')
        self.expectStatements()
        self.writer.writeLabel(endLabel)
        self.symbol('}')
      else:
        self.writer.writeLabel(falseLabel)

    # do while
    elif self.peek()[1] == 'while':
      self.keyword('while')
      self.symbol('(')
      self.writer.writeLabel('WHILE_EXP0')
      self.expectExpression()
      self.writer.writeArithmetic('not')
      self.symbol(')')
      self.writer.writeIf('WHILE_END0')
      self.symbol('{')
      self.expectStatements()
      self.writer.writeGoto('WHILE_EXP0')
      self.writer.writeLabel('WHILE_END0')
      self.symbol('}')

    # do do
    elif self.peek()[1] == 'do':
      self.keyword('do')
      self.expectSubroutineCall()
      self.writer.writePop('temp', 0) # pops and ignores return value
      self.symbol(';')
    elif self.peek()[1] == 'return':
      self.keyword('return')
      self.writer.writeReturn()
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
      if token[0] == 'integerConstant':
        self.writer.writePush('constant', token[1])
      elif token[0] == 'String Constant':
        self.writer.writePush('constant', len(token[1]))
        self.writer.writeCall('String.new', 1)
        for i in range(len(token[1])):
          self.writer.writePush('constant', ord(token[1][i]))
          self.writer.writeCall('String.appendChar', 2)

    elif token[1] in ['true', 'false', 'null', 'this']:
      self.keyword(token[1])
      if token[1] == 'false':
        self.writer.writePush('constant', 1)
      elif token[1] == 'true':
        self.writer.writePush('constant', 0)
        self.writer.writeArithmetic('not')
    elif token[0] == IDENTIFIER:
      identifier = self.identifier()
      if self.peek()[1] == '.':
          self.expectSubroutineCall(identifier)
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
        self.writer.writeArithmetic(UNARY_OPERATORS[token[1]])
      else:
        self.fail("Expected term.")

    self.indent -= 2
    print >>self.out, ' '*self.indent + "</term>"

  def expectOp(self):
    op = self.peek()[1]
    self.symbol(self.peek()[1]) if self.peek()[1] in OPERATORS else self.fail("Expected operator")
    return op

  def expectExpression(self):
    print >>self.out, ' '*self.indent + '<expression>'
    self.indent += 2
    self.expectTerm()
    while self.peek()[1] in OPERATORS:
      op = self.expectOp()
      self.expectTerm()
      self.writer.writeArithmetic(VM_OPERATORS[op])
    self.indent -= 2
    print >>self.out, ' '*self.indent + '</expression>'

  def expectExpressionList(self):
    self.numExpressions = 0
    print >>self.out, ' '*self.indent + '<expressionList>'
    self.indent += 2
    if self.peek()[1] != ')':
      self.expectExpression()
      self.numExpressions += 1
      while self.peek()[1] == ',':
        self.symbol(',')
        self.expectExpression()
        self.numExpressions += 1
    self.indent -= 2
    print >>self.out, ' '*self.indent + '</expressionList>'


  def expectSubroutineCall(self, first_identifier=''):
    self.numExpressions = 0
    if first_identifier:
      first_identifier = first_identifier
    else:
      first_identifier = self.identifier()
    sub_identifier = ''
    isObjorClass = False
    if self.peek()[1] == '.':
      isObjorClass = True
      self.symbol('.')
      sub_identifier = self.identifier() # method or function name
    self.symbol('(')
    self.expectExpressionList()
    self.symbol(')')

    if isObjorClass:
      # if sub_identifier is a method, push its class onto stack
      if SYMBOL_TABLE.isDefined(first_identifier):
        self.writer.writePush(SYMBOL_TABLE.kindOf(first_identifier), SYMBOL_TABLE.indexOf(first_identifier))
        callName = SYMBOL_TABLE.typeOf(first_identifier) + "." + sub_identifier
        self.numExpressions += 1
      else:
        callName = first_identifier + "." + sub_identifier
      self.writer.writeCall(callName, self.numExpressions)
    # if there is only 1 identifer and it is a method,
    # push it on to the stack first as first param
    else:
      if SYMBOL_TABLE.isDefined(first_identifier):
        self.writer.writePush(SYMBOL_TABLE.kindOf(first_identifier), SYMBOL_TABLE.indexOf(first_identifier))
      else:
        self.writer.writePush('pointer', 0)


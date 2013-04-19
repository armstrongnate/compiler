class SymbolTable:

  NONE = 0
  STATIC = "static"
  FIELD = "this"
  ARG = "argument"
  VAR = "local"

  def __init__(self):
    self.arg = {}
    self.var = {}
    self.field = {}
    self.static = {}

  def startSubroutine(self):
    self.arg = {}
    self.var = {}

  def define(self, name, var_type, kind):
    if kind == 'arg':
      if name in self.arg:
        fail('variable already defined: %s' % name)
      self.arg[name] = (var_type, len(self.arg))

    if kind == 'var':
      if name in self.var:
        fail('variable already defined: %s' % name)
      self.var[name] = (var_type, len(self.var))

    if kind == 'static':
      if name in self.static:
        fail('variable already defined: %s' % name)
      self.static[name] = (var_type, len(self.static))

    if kind == 'field':
      if name in self.field:
        fail('variable already defined: %s' % name)
      self.field[name] = (var_type, len(self.field))

  def kindOf(self, name):
    if name in self.arg:
      return 'arg'
    elif name in self.var:
      return 'var'
    elif name in self.static:
      return 'static'
    elif name in self.field:
      return 'field'

  def indexOf(self, name):
    if name in self.arg:
      return self.arg[name][1]
    elif name in self.var:
      return self.var[name][1]
    elif name in self.static:
      return self.static[name][1]
    elif name in self.field:
      return self.field[name][1]
    else:
      raise Exception(name + " not found in symbol table")

  def isDefined(self, name):
    if name in self.arg or name in self.var or name in self.static or name in self.field:
      return True
    return False

  def __str__(self):
    out = "+++++++++++ Static ++++++++++++\n %s \n" % self.static
    out += "+++++++++++ Field ++++++++++++\n %s \n" % self.field
    out += "+++++++++++ Arg ++++++++++++\n %s \n" % self.arg
    out += "+++++++++++ Var ++++++++++++\n %s \n" % self.var
    return out
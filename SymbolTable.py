class SymbolTable:
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

  def __str__(self):
    out = "+++++++++++ Static ++++++++++++\n %s \n" % self.static
    out += "+++++++++++ Field ++++++++++++\n %s \n" % self.field
    out += "+++++++++++ Arg ++++++++++++\n %s \n" % self.arg
    out += "+++++++++++ Var ++++++++++++\n %s \n" % self.var
    return out
from constants import *

class VmWriter:
  def __init__(self, fout):
    self.out = open(fout, 'w')
    self.THIS_POINTER = 0

  def writePush(self, segment, index):
    # possible segments: const, arg, local, static, this, that, pointer, temp
    print >>self.out, "push " + segment + " " + str(index)

  def writePop(self, segment, index):
    print >>self.out, "pop " + segment + " " + str(index)

  def writeArithmetic(self, command):
    # possible commands: add, sub, neg, eq, gt, lt, and, or, not
    print >>self.out, command

  def writeLabel(self, label):
    print >>self.out, "label " + label

  def writeGoto(self, label):
    print >>self.out, "goto " + label

  def writeIf(self, label):
    print >>self.out, "if-goto " + label

  def writeCall(self, name, nArgs):
    print >>self.out, "call " + name + " " + str(nArgs)

  def writeFunction(self, name, nLocals):
    print >>self.out, "function " + name + " " + str(nLocals)

  def writeReturn(self):
    print >>self.out, "push constant 0\nreturn"

  def close(self):
    self.out.close()
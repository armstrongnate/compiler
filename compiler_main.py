from CompilationEngine import *

def print_xml_test(tokens, xout):
  print >>xout, '<tokens>'
  for token in tokens:
    if token[0] == 'Symbol':
      symbol = token[1]
      if symbol == '<':
        symbol = '&lt;'
      elif symbol == '>':
        symbol = '&gt;'
      print >>xout, '<symbol> %s </symbol>' % symbol
    elif token[0] == 'Keyword':
      print >>xout, '<keyword> %s </keyword>' % token[1]
    elif token[0] == 'Identifier':
      print >>xout, '<identifier> %s </identifier>' % token[1]
    elif token[0] == 'int':
      print >>xout, '<integerConstant> %s </integerConstant>' % token[1]
    else:
      print >>xout, '<stringConstant> %s </stringConstant>' % token[1]
  print >>xout, '</tokens>'

  xout.close()

def main():
  fin = open('Square.jack', 'r')
  xout = open('test_out.xml', 'w')

  j = JackTokenizer(fin)
  tokens = j.getTokens()
  CompilationEngine(tokens, xout)
  fin.close()

if __name__ == '__main__':
  main()
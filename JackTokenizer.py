symbolList = ['{','}','(',')','[',']','.',',',';','+','-','*','/','&','|','<','>','=','~']
keywordList = ['class','constructor','function','method','field','static',
'var','int','char','boolean','void','true','false','null','this',
'let','do','if','else','while','return']
OPERATORS = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
UNARY_OPERATORS = ['-', '~']
KEYWORD = 'Keyword'
SYMBOL = 'Symbol'
IDENTIFIER = 'Identifier'
STRING_CONSTANT = 'String Constant'
INTEGER = 'integerConstant'
LINENUMBER = 0

class JackTokenizer:
  def __init__(self, fp):
    self.f = fp.read().replace('\r\n', '\n').replace('\r', '\n')
    #self.f += '\n' if self.f[-1:] != '\n' else None
    self.tokens = self.getTokens()

  def getTokens(self):
    tokenlist = []
    end = False
    f = self.f
    i = 0
    linecount = 0
    while end == False:
      i = 0
      if len(f) <= 0:
        break
      spacecount = 0
      #check for white space
      if f[i].isspace():
        if f[i] == '\n':
          linecount += 1
        f = f[i+1:]
        i = 0
        continue
      #check for // comments
      if f[:2] == '//':
        f = f[f.find('\n')+1:]
        continue

      #check for /* comments
      if f[:2] == '/*':
        f = f[2:]
        ec = f.find('*/')
        for j in range(ec+2):
          if f[j] == '\n':
            linecount+=1
        f = f[ec+2:]
        continue

      #find symbols
      if f[i] in symbolList:
        symbol = f[i]
        f = f[i+1:]
        tokenlist.append(('Symbol', symbol, linecount+1))
        continue

      #find digits
      if f[i].isdigit():
        num = ''
        while f[i].isdigit():
          num+=(f[i])
          i+=1
        f = f[i:]
        if int(num) <= 32767:
          tokenlist.append(('integerConstant', num, linecount+1))
        else:
          print "That number on line", linecount+1, "is too large."
        i = 0
        continue

      #find string constants
      if f[i] == '"':
        f = f[i+1:]
        eq = f.find('"')
        for j in range(i,eq):
          if f[j] == '\n':
            return "ERROR: You must close the quotes on line",linecount+1,"."
        stringconst = f[i:eq]
        f = f[eq+1:]
        tokenlist.append(('String Constant', stringconst, linecount+1))
        continue

      #find keywords and identifiers
      string = ''
      if f[i].isalnum() or f[i] == '_':
        while f[i].isalnum() or f[i] == '_':
          string+=(f[i])
          i+=1
        f = f[i:]
        if string in keywordList:
          tokenlist.append(('Keyword', string, linecount+1))
        else:
          tokenlist.append(('Identifier', string, linecount+1))
        i = 0
        continue

      else:
        print "syntax error on line", linecount+1,"."

    fin = open('tokens.txt', 'w')
    for token in tokenlist:
      print >>fin, token
    fin.close()
    return tokenlist

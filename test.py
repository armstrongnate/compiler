word = '\nNate\nArmstrong'

for i in range(len(word)):
  if word[:i].isspace():
    print "found space"
    word = word[i:]
  if word[i:i+1].isspace():
    before = word[:i]
    after = word[i+1:]
print word, before, after
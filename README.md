This compiler is one of the assignments in the textbook, _Elements of Computing Systems: Building a Modern Computer from First Principles_. It compiles Jack code into VM code.

## How to Use
Specify the .jack file you wish to parse in compiler_main.py. Eventually, maybe, I'll have it read a directory specified from the terminal but for now it reads one file and in writes one file out. You can specify the name of the .vm file it will write to on the first line of the CompilationEngine.py constructor.

Run compiler_main.py from the command line once you've specified the names of the file you wish to read in and write to.

  python compiler_main.py

## Test Files

There are several files that get written to in the process of compiling the jack code.

The first is tokens.txt. This is just a list of all the tokens the JackTokenizer class finds. In short, the Jack Tokenizer runs through the input file and organizes each word, operator, etc as a token and specifies its type, and what line number it occurres at.

The next is test_out.xml. As the CompilationEngine parses over the tokens list, it writes each token it finds as an xml element. This was just one of the building blocks to getting the compiler to understand the jack language.

The final output is, as it stands, Main.vm.

The constants.py keeps track of several variables that are the same between the classes; the most important being the SYMBOL_TABLE.

If you're working through the Elements of Computing Systems textbook, congrats on getting this far and good luck with the rest!

Email me with any questions. natearmstrong2@gmail.com
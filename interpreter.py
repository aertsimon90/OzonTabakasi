import sys
import time
import os
import shutil

class Interpreter:
	def __init__(self):
		self.vars = {}
	def repr(self, value, listn=0, dictn=0):
		t = str(type(value)).split("<class '")[1].split("'>")[0]
		if t == "int":
			return "int;/"+repr(value)
		elif t == "float":
			return "flt;/"+repr(value)
		elif t == "str":
			return "str;/"+value
		elif t == "list":
			new = []
			for h in value:
				new.append(self.repr(h, listn=listn+1, dictn=dictn))
			return "ls;/"+(f"!,{listn}/".join(new))
		elif t == "dict":
			new = []
			for name, h in value.items():
				name = self.repr(name, listn=listn, dictn=dictn+1)
				h = self.repr(h, listn=listn, dictn=dictn+1)
				new.append(name+f"!:{dictn}:/"+h)
			return "dict;/"+(f"!.{dictn}/".join(new))
		elif t == "NoneType":
			return "nan;/nan"
		elif t == "bool":
			if value == True:
				return "bool;/1"
			else:
				return "bool;/0"
		else:
			return "nan;/nan"
	def seperator(self, seed, value, listn, dictn, mathn):
		splitter = f"!c{seed}/"
		new = []
		for h in value.split(splitter):
			h = self.execute(h, listn=listn, dictn=dictn, mathn=mathn, seed=seed+1)
			new.append(h)
		return new
	def execute(self, value, listn=0, dictn=0, mathn=0, seed=0):
		if "str" not in str(type(value)):
			return
		if f"\n/ot{seed}/new;/\n" in value:
			for hh in value.split(f"\n/ot{seed}/new;/\n"):
				self.execute(hh, listn, dictn, mathn, seed)
			return
		if "#//>>" in value:
			value = value[:value.find("#//>>")]
		value = value.lstrip()
		runner = value[:value.find(";/")]
		value = value[value.find(";/")+2:]
		if runner == "int":
			return int(value)
		elif runner == "flt":
			return float(value)
		elif runner == "str":
			return value
		elif runner == "len":
			return len(self.execute(value, listn=listn, dictn=dictn, mathn=mathn, seed=seed))
		elif runner == "ls":
			new = []
			for h in value.split(f"!,{listn}/"):
				if len(h) != 0:
					new.append(self.execute(h, listn=listn+1, dictn=dictn, mathn=mathn, seed=seed))
			return new
		elif runner == "dict":
			new = {}
			for h in value.split(f"!.{dictn}/"):
				if len(h) != 0:
					name = h[:h.find(f"!:{dictn}:/")]
					h = h[h.find(f"!:{dictn}:/")+4+len(str(dictn)):]
					new[self.execute(name, listn=listn, dictn=dictn+1, mathn=mathn)] = self.execute(h, listn=listn, dictn=dictn+1, mathn=mathn, seed=seed)
			return new
		elif runner == "bool":
			if value == "0":
				return False
			elif value == "1":
				return True
			else:
				raise ValueError("bool type object value can be 0 or 1. (0=false) (1=true)")
		elif runner == "nan":
			if value == "nan":
				return None
			else:
				raise ValueError("nan type object value is can be nan")
		elif runner == "math":
			new = None
			for h in value.split(f"!m{mathn}/"):
				if len(h) != 0:
					h = h.lstrip()
					method = h[:h.find(":")]
					h = self.execute(h[h.find(":")+1:], listn=listn, dictn=dictn, mathn=mathn+1, seed=seed)
					if new == None:
						t = str(type(h))
						if "int" in t or "float" in t:
							new = 0
						elif "list" in t:
							new = []
						elif "NoneType" in t:
							raise ValueError("nan type object can't use in math.")
						else:
							new = ""
					if method == "+":
						new += h
					elif method == "-":
						new -= h
					elif method == "*":
						new *= h
					elif method == "/":
						new /= h
					elif method == "**":
						new **= h
					elif method == "%":
						new %= h
					elif method == "//":
						new //= h
			return new
		elif runner == "syseval":
			value = self.execute(value, listn, dictn, mathn, seed)
			result = eval(value, self.vars, self.vars)
			self.vars = dict(self.vars)
			return result
		elif runner == "sysexec":
			value = self.execute(value, listn, dictn, mathn, seed)
			exec(value, self.vars, self.vars)
			self.vars = dict(self.vars)
		elif runner == "select":
			values = self.seperator(seed, value, listn, dictn, mathn)
			if len(values) == 0:
				raise ValueError("no inputs on select command")
			elif len(values) == 1:
				raise ValueError("no target index on select command")
			elif len(values) == 2:
				return values[0][values[1]]
			elif len(values) == 3:
				return values[0][values[1]:values[2]]
			else:
				return values[0][values[1]:values[2]:values[3]]
		elif runner == "for":
			values = self.seperator(seed, value, listn, dictn, mathn)
			if len(values) == 0:
				raise ValueError("no inputs on for command")
			elif len(values) == 1:
				raise ValueError("no variable on for command")
			elif len(values) == 2:
				raise ValueError("no code on for command")
			else:
				targetvalue = values[0]
				variable = values[1]
				code = values[2]
				for h in targetvalue:
					self.vars[variable] = h
					self.execute(code, listn=listn, dictn=dictn, mathn=mathn, seed=seed+1)
		elif runner == "if":
			values = self.seperator(seed, value, listn, dictn, mathn)
			if len(values) == 0:
				raise ValueError("no inputs on if command")
			elif len(values) == 1:
				raise ValueError("no code on if command")
			elif len(values) == 2:
				target = values[0]
				code = values[1]
				if target:
					self.execute(code, listn=listn, dictn=dictn, mathn=mathn, seed=seed)
			else:
				target = values[0]
				code = values[1]
				elsecode = values[2]
				if target:
					self.execute(code, listn=listn, dictn=dictn, mathn=mathn, seed=seed+1)
				else:
					self.execute(elsecode, listn=listn, dictn=dictn, mathn=mathn, seed=seed+1)
		elif runner == "var":
			values = self.seperator(seed, value, listn, dictn, mathn)
			if len(values) < 2:
				raise SystemError("no inputs on var command")
			self.vars[values[0]] = values[1]
		elif runner == "varvalue":
			return self.vars[self.execute(value, listn=listn, dictn=dictn, mathn=mathn, seed=seed)]
		elif runner == "stdout-write":
			value = self.execute(value, listn, dictn, mathn, seed)
			sys.stdout.write(value)
		elif runner == "stdout-flush":
			sys.stdout.flush()
		elif runner == "stderr-write":
			value = self.execute(value, listn, dictn, mathn, seed)
			sys.stderr.write(value)
		elif runner == "stderr-flush":
			sys.stderr.flush()
		elif runner == "stdin-readline":
			return sys.stdin.readline()
		elif runner == "nowtime":
			return time.time()
		elif runner == "sleep":
			value = self.execute(value, listn, dictn, mathn, seed)
			time.sleep(value)
		elif runner == "==":
			values = self.seperator(seed, value, listn, dictn, mathn)
			return values[0] == values[1]
		elif runner == ">=":
			values = self.seperator(seed, value, listn, dictn, mathn)
			return values[0] >= values[1]
		elif runner == "<=":
			values = self.seperator(seed, value, listn, dictn, mathn)
			return values[0] <= values[1]
		elif runner == ">":
			values = self.seperator(seed, value, listn, dictn, mathn)
			return values[0] > values[1]
		elif runner == "<":
			values = self.seperator(seed, value, listn, dictn, mathn)
			return values[0] < values[1]
		elif runner == "!=":
			values = self.seperator(seed, value, listn, dictn, mathn)
			return values[0] != values[1]
		elif runner == "exec":
			value = self.execute(value, listn, dictn, mathn, seed)
			self.execute(value, listn, dictn, mathn, seed)
		elif runner == "eval":
			value = self.execute(value, listn, dictn, mathn, seed)
			return self.execute(value, listn, dictn, mathn, seed)
		elif runner == "repr":
			value = self.execute(value, listn, dictn, mathn, seed)
			return self.repr(value)
		elif runner == "fstr":
			for n, v in self.vars.items():
				t = str(type(v))
				if "str" not in t and "int" not in t and "float" not in t:
					value = value.replace(f"<${n}>", self.repr(v))
				else:
					value = value.replace(f"<${n}>", str(v))
			return value
		elif runner == "strip":
			value = self.execute(value, listn, dictn, mathn, seed)
			return value.strip()
		elif runner == "stripwith":
			value = self.seperator(seed, value, listn, dictn, mathn)
			stripper = value[0]
			value = value[1]
			return value.strip(stripper)
		elif runner == "split":
			value = self.execute(value, listn, dictn, mathn, seed)
			return value.split()
		elif runner == "splitwith":
			value = self.seperator(seed, value, listn, dictn, mathn)
			splitter = value[0]
			value = value[1]
			return value.split(splitter)
		elif runner == "join":
			value = self.seperator(seed, value, listn, dictn, mathn)
			joiner = value[0]
			value = value[1]
			return joiner.join(value)
		elif runner == "range":
			value = self.seperator(seed, value, listn, dictn, mathn)
			min = value[0]
			max = value[1]
			return list(range(min, max))
		elif runner == "loop":
			value = self.seperator(seed, value, listn, dictn, mathn)
			count = value[0]
			code = value[1]
			for _ in range(count):
				self.execute(code, listn, dictn, mathn, seed+1)
		elif runner == "while":
			value = self.seperator(seed, value, listn, dictn, mathn)
			stat = value[0]
			code = value[1]
			while self.execute(stat, listn, dictn, mathn, seed+1):
				self.execute(code, listn, dictn, mathn, seed+1)
		elif runner == "argv":
			return sys.argv
		elif runner == "environ":
			return dict(os.environ)
		elif runner == "exit":
			sys.exit()
		else:
			return None

def to_python(file):
	import requests
	print("Converting to python...")
	content = requests.get("https://raw.githubusercontent.com/aertsimon90/OzonTabakasi/refs/heads/main/interpreter.py", timeout=10).text
	content = content[:content.find("""# start
# <MAIN FUNCTION SEPERATOR>
# <MAIN FUNCTION SEPERATOR>
# <MAIN FUNCTION """+"""SEPERATOR>
# <MAIN FUNCTION SEPERATOR>
# <MAIN FUNCTION SEPERATOR>
# stop""")]
	with open(file, "rb") as f:
		code = f.read().decode("utf-8", errors="ignore")
	addcode = f"Interpreter().execute({repr(code)})"
	content = content+addcode
	with open("ot_output", "w", encoding="utf-8") as f:
		f.write(content)
	print("YOUR PYTHON CODE IN 'ot_output' FILE!")
def to_c(file):
	to_python(file)
	print("Importing Cython...")
	from Cython.Build import cythonize
	print("Importing SetupTools...")
	from setuptools import setup
	print("ot_output to ot_output.py...")
	os.rename("ot_output", "ot_output.py")
	print("creating ot_output.c...")
	setup(ext_modules=cythonize(["ot_output.py"], language_level="3"), script_args=["build_ext", "--inplace"])
	print("renaming ot_output.c to ot_output...")
	os.rename("ot_output.c", "ot_output")
	print("removing ot_output.py")
	os.remove("ot_output.py")
	print("YOUR C CODE IN 'ot_output' FILE!")
def to_program(file):
	print("Converting to C File...")
	to_c(file)
	print("Updating GCC...")
	if os.name == "nt":
		os.system("winget install GCC")
	else:
		os.system("pkg install gcc -y")
		os.system("sudo apt install gcc -y")
		os.system("sudo pacman -S gcc")
		os.system("sudo dnf install gcc")
		os.system("sudo zypper install gcc")
		os.system("sudo apk add gcc")
		os.system("sudo emerge --ask sys-devel/gcc")
	print("C file to executable file...")
	os.system("gcc ot_output -o ot_output")
	print("YOUR EXECUTABLE PROGRAM CODE IN 'ot_output' FILE!")
def to_program_pyinstaller(file):
	to_python(file)
	print("Updating PyInstaller...")
	os.system("python -m pip install pyinstaller")
	print()
	print("--- WHAT DO YOU WANT ? ---")
	print()
	args = ["--onefile"]
	if os.name == "nt":
		nooutput = input("Hide terminal/console screen? (Y/n): ").lower()
		if nooutput.startswith("y"):
			args.append("--no-console")
	icon = input("Want program icon? (Y/n): ").lower()
	if icon.startswith("y"):
		iconfile = input("Icon file name or path (just use .ico): ")
		args.append("-i "+iconfile)
	command = "python -m PyInstaller ot_output "+(" ".join(args))
	print(f"My Command: {command}")
	os.system(command)
	if "dist" in os.listdir():
		if os.name == "nt":
			shutil.copy("dist/ot_output.exe", "ot_output")
		else:
			shutil.copy("dist/ot_output", "ot_output")
	print("YOUR EXECUTABLE PROGRAM CODE IN 'ot_output' FILE!")

# start
# <MAIN FUNCTION SEPERATOR>
# <MAIN FUNCTION SEPERATOR>
# <MAIN FUNCTION SEPERATOR>
# <MAIN FUNCTION SEPERATOR>
# <MAIN FUNCTION SEPERATOR>
# stop

if __name__ == "__main__":
	argvs = sys.argv.copy()
	if len(argvs) == 0:
		raise SystemError("Error: System Arguments not found.")
	elif len(argvs) == 1:
		print("Running on Command Line mode.\nOZONTABAKASI v1.0.0 (Low Level Programming Language) (by aertsimon90 visit on github)\nNOTE: This programming language tests and challenges your ordinary programming skills. Difficult to use but easy to learn, this programming language is written by a highly optimized interpreter.\nIf you don't know what to do, we have prepared a simple text that makes learning easier, so don't worry, we support you in these matters. To reach the text, just type 'help'.\nIf you want to test the speed of the current programming language interpreter, just type 'speedtest' and you can see if it is really optimized enough.\nThe current interpreter appears to be based on the 'PYTHON' language. To see the interpreter arguments, restart the program and add only the '--help' argument. (You can use arguments for compile the OzonTabakasi language to binary or exe program)\n")
		interpreter = Interpreter()
		while True:
			i = input(">>> ")
			if i == "speedtest":
				print("Testing speed of: Screen Write.")
				start = time.time()
				interpreter.execute("stdout-write;/str;/Hello, World!\n")
				end = time.time()
				otsw = end-start
				print(f"Result Time on OzonTabakasi (seconds): {otsw:.15f}")
				start = time.time()
				print("Hello, World!")
				end = time.time()
				pysw = end-start
				print(f"Result Time on PYTHON (seconds): {pysw:.15f}")

				print("Testing speed of: Basic Calculation.")
				start = time.time()
				interpreter.execute("var;/str;/testr123!c0/math;/+:int;/150!m0/*:int;/100")
				end = time.time()
				otsw = end-start
				print(f"Result Time on OzonTabakasi (seconds): {otsw:.15f}")
				start = time.time()
				testr123 = 150*100
				end = time.time()
				pysw = end-start
				print(f"Result Time on PYTHON (seconds): {pysw:.15f}")
				
				print("Testing speed of: Big Calculation.")
				start = time.time()
				interpreter.execute("var;/str;/testr123!c0/math;/+:int;/150!m0/*:int;/100!m0//:flt;/283.382627281729284828!m0/*:flt;/8272827273728817227372.2836272736")
				end = time.time()
				otsw = end-start
				print(f"Result Time on OzonTabakasi (seconds): {otsw:.15f}")
				start = time.time()
				testr123 = ((150*100)/283.382627281729284828)*8272827273728817227372.2836272736
				end = time.time()
				pysw = end-start
				print(f"Result Time on PYTHON (seconds): {pysw:.15f}")
			elif i == "help":
				print("""Syntax Rules of OzonTabakasi

Every OzonTabakasi code consists of several key values: listn, dictn, mathn, and seed.
Each of these values represents different depths in various structures:

listn represents the depth of a list element.

dictn represents the depth of a dictionary structure.

mathn represents the depth of a mathematical operation.


When using these values in commands, automatic separators are applied when the code runs.
For example, when you first enter a list value, its depth is 0. If you want to nest another list inside it, the new list's separator should use 1 as the depth.
If there's another list inside that one, its depth should be 2, and so on. This depth can increase indefinitely.

List Syntax

In lists, separators are structured as !,{listn}/.
When entering list elements, you need to separate them with this separator.

Example:
If we assume the current list depth is 0, a simple list structure would be:

ls;/str;/Hello!,0/str;/Hello 2

At first glance, this may seem like a list containing "Hello!" and "Hello 2", but that's not entirely correct.
The ! symbol marks the beginning of the separator. Remember that the separator for lists is !,{listn}/.
Since this list's depth is 0, the actual separator used here is !,0/.
If we were to nest another list inside, the separator would become !,1/.

Thus, the actual list content is:

["Hello", "Hello 2"]

Another important syntax rule is the command separator, written as ;/.
Command separators divide the runner (command name) from its value.

For example, in the code:

hello;/world

hello is the runner (command).

world is the value.


In the case of lists:

ls;/str;/Hello!,0/str;/Hello 2

ls (short for "list") is the runner that defines a list.

The list elements are str;/Hello and str;/Hello 2, meaning each element is defined with a string runner (str).


A more complex nested list example:

ls;/str;/Hello!,0/ls;/str;/Hello 1!,1/str;/Hello 2

Here, we see two ls runners, each with a different depth.
This represents a nested list, equivalent to the following JSON:

["Hello", ["Hello 1", "Hello 2"]]

Dictionary Syntax

Dictionaries use a different type of separator, structured as !.{dictn}/.
Like lists, these separators indicate depth levels and separate dictionary keys and values.

Example dictionary syntax:

dict;/str;/Name!:0:/str;/Simon Scap!.0/str;/Age!:0:/int;/20

Here, we see two types of separators:

1. !.0/ - Separates dictionary elements.


2. !:0:/ - Separates keys and values, similar to the : symbol in JSON.



The equivalent JSON structure of the above example would be:

{"Name": "Simon Scap", "Age": 20}

Mathematical Operations Syntax

Mathematical syntax in OzonTabakasi is unique and differs from conventional mathematical notation.

Example:

math;/+:int;/1!m0/+:int;/2

Like lists and dictionaries, mathematical expressions use a depth separator, written as !m{mathn}/.
The depth starts at 0, just like in other structures.

Breaking down the code:

+:int;/1 → The first element sets the base value to 0 and adds 1 to it.

+:int;/2 → The second element adds 2 to the current value.


So, step by step:

0 + 1 = 1  
1 + 2 = 3

Final result: 3.

A more complex example:

math;/+:int;/150!m0/*:int;/2!m0/-:int;/5

Here, we see addition (+), multiplication (*), and subtraction (-).
However, OzonTabakasi math does not follow standard order of operations. Instead, operations are performed in sequence.

Step-by-step calculation:

(150 * 2) - 5  
= 300 - 5  
= 295

So, the final result is 295.

Seed Syntax

The seed is one of the most critical elements in OzonTabakasi.
It is used to separate code blocks or arguments within commands.

Separating Code Blocks

When writing OzonTabakasi code, you can separate lines of code using the seed separator:

/ot{seed}/new;/

This is similar to a newline character (\n) in other programming languages.

Example:

stdout-write;/str;/Hello, World!
/ot0/new;/
stdout-flush;/

Here, /ot0/new;/ separates two different commands:

1. Writes "Hello, World!" to the output.


2. Flushes the output to ensure it is displayed correctly.



Separating Arguments in a Command

Some commands require multiple values, which can be separated using !c{seed}/.

Example:

runner;/value1!c0/value2

This is similar to separating arguments in a function.

Whitespace and Formatting

OzonTabakasi allows flexible formatting. You can add tabs or spaces before commands for better readability.

Both of the following are valid:

math;/
  +:int;/159!m0/
  *:int;/2

  math;/
+:int;/159!m0/
*:int;/2

      math;/
   +:int;/159!m0/
  *:int;/2

This makes it easier to write clean and readable code.

Conclusion

These are the fundamental syntax rules of OzonTabakasi.
Understanding list, dictionary, math, and seed structures is crucial for writing proper code.

With this syntax, OzonTabakasi offers a structured, powerful, and customizable way to process data efficiently.

Data Types in OzonTabakası

The OzonTabakası programming language supports various data types that are used to represent different kinds of values. These data types enable structured data manipulation within the language, including numbers, strings, lists, dictionaries, boolean values, and more. Below is a detailed explanation of each data type and its usage.

1. Integer (int;/value)

An integer represents a whole number, which can be positive or negative. It does not include any fractional or decimal part. In OzonTabakası, an integer is declared using the prefix int;/.

Example Usage:

int;/12345

This represents the integer 12345.

2. Floating-point Number (flt;/value)

A floating-point number, or float, represents a number that has a fractional part, usually separated by a decimal point. It allows for more precision than integers and is typically used for calculations requiring decimals.

Example Usage:

flt;/3.14159

This represents the floating-point number 3.14159, a common approximation of Pi.

3. String (str;/value)

A string represents a sequence of characters. Strings are commonly used to store text and can include letters, numbers, spaces, punctuation, and special characters. In OzonTabakası, a string is denoted with the prefix str;/.

Example Usage:

str;/Hello, World!

This represents the string "Hello, World!".

---

4. Formatted String (fstr;/value)

A formatted string is a type of string that allows embedding of variables directly into the string. Unlike regular strings, fstr strings in OzonTabakası only allow embedding variables and do not provide additional functionality. It is used when you want to include the value of a variable within a string.

Example Usage:

fstr;/Hello, <@name>!

Here, the string contains a placeholder <@name>, which can be replaced with the actual value of the name variable during runtime.

Example with Variable:

var;/str;/name!c0/stdin-readline;/
/ot0/new;/
stdout-write;/fstr;/Hello, <@name>!

In this example:

The name variable is populated by reading a line from user input (stdin-readline).

The program then outputs a personalized greeting using the fstr;/ format.


However, it is important to note that fstr does not perform any other operations like calculations or formatting beyond embedding variables into the string. It is specifically for variable interpolation.


5. List (ls;/value!,{listn}/value!,{listn}/...)

A list is an ordered collection of items, which can be of various data types such as integers, strings, floats, and even other lists. Lists in OzonTabakası are defined with the prefix ls;/ and allow multiple items separated by the delimiter !,{listn}/.

Example Usage:

ls;/int;/12345!,0/str;/Hello!!,0/str;/Test 123!,0/flt;/4.567!,0/ls;/str;/Hello!,1/str;/Hello2

This defines a list containing several elements of various data types (integers, strings, floats, and even another list). The result would be:

[12345, "Hello!", "Test 123", 4.567, ["Hello", "Hello2"]]

Explanation:

The numbers 12345 and 4.567 are integers and floats.

The strings "Hello!" and "Test 123" are standard strings.

The list ["Hello", "Hello2"] is nested inside the main list.


6. Dictionary (dict;/key!:{dictn}:/value!.0/key!:{dictn}:/value!.0/...)

A dictionary, or map, is a collection of key-value pairs where each key is unique, and each key maps to a value. In OzonTabakası, dictionaries are defined with the prefix dict;/, and each key-value pair is separated by the !:{dictn}:/ delimiter.

Example Usage:

dict;/str;/Name!:0:/str;/Simon!.0/str;/Surname!:0:/str;/Scap!.0/str;/Age!:0:/int;/20!.0/str;/Money!:0:/flt;/15000.5!.0/str;/City!:0:/str;/Erzincan!.0/str;/Messages!:0:/dict;/str;/1!:1:/str;/Hello!!.1/str;/2!:1:/str;/My name is Simon

This defines a dictionary with several key-value pairs, including nested dictionaries. The result would be:

{
  "Name": "Simon",
  "Surname": "Scap",
  "Age": 20,
  "Money": 15000.50,
  "City": "Erzincan",
  "Messages": {
    "1": "Hello!",
    "2": "My name is Simon"
  }
}

Explanation:

The dictionary contains basic information such as Name, Surname, Age, Money, and City.

The Messages key maps to another dictionary, which includes two messages.


7. Boolean (bool;/1 or 0)

A boolean value represents a true or false state. It can be either 1 (True) or 0 (False). This data type is commonly used for conditional checks and logical operations.

Example Usage:

bool;/1

This represents the boolean value True.

bool;/0

This represents the boolean value False.

8. Not a Number (NaN, nan;/nan)

The NaN value, which stands for Not a Number, is used to represent undefined or unrepresentable values, such as the result of dividing zero by zero. In OzonTabakası, nan;/ is used to denote this special value.

Example Usage:

nan;/nan

This represents the None or NaN value, which indicates that a value is undefined or not applicable.


---

Summary

int;/value: Represents integer values (whole numbers).

flt;/value: Represents floating-point numbers (decimal values).

str;/value: Represents string values (sequences of characters).

fstr;/value: Represents formatted strings that allow dynamic embedding of variables.

ls;/value: Represents a list (ordered collection of items).

dict;/key: Represents a dictionary (collection of key-value pairs).

bool;/1 or 0: Represents boolean values (True or False).

nan;/nan: Represents undefined or NaN values (None).


These data types, combined with OzonTabakası's syntax, allow for the creation of complex, structured data and operations, enabling powerful manipulation of variables, user input, and data structures in programs written in OzonTabakası.""")
			else:
				interpreter.execute(i)
	elif len(argvs) >= 2:
		if argvs[1].startswith("-"):
			if argvs[1] == "--help":
				print("OZONTABAKASI INTERPRETER & COMPILER")
				print("--help = Show Arguments")
				print("--to-python <file> = Convert OzonTabakasi to Python Code")
				print("--to-c <file>= Convert OzonTabakasi to Python and Convert to C Code File with using Cython.")
				print("--to-program <file> = OzonTabakasi to Python and Convert to C Code File with using Cython and Convert C Code File to Executable System Program using GCC (For Linux=Binary, For Windows=EXE)")
				print("--to-program-pyinstaller <file> = OzonTabakasi to Python and Convert Binary/EXE with PyInstaller (Faster and Encrypted)")
				print("All Output Files are named one name, its 'ot_output' (if you converted a ozontabakasi code to python/c/binary/exe all data are saving on ot_output file)")
			elif argvs[1] == "--to-python":
				file = argvs[2]
				to_python(file)
			elif argvs[1] == "--to-c":
				file = argvs[2]
				to_c(file)
			elif argvs[1] == "--to-program":
				file = argvs[2]
				to_program(file)
			elif argvs[1] == "--to-program-pyinstaller":
				file = argvs[2]
				to_program_pyinstaller(file)
			else:
				with open(argvs[1], "r", encoding="utf-8") as f:
					content = f.read()
				Interpreter().execute(content)
		else:
			with open(argvs[1], "r", encoding="utf-8") as f:
				content = f.read()
			Interpreter().execute(content)
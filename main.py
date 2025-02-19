
import os, json
from pathlib import Path

config_path = str(Path.home() / ".config/project-manager/config.json")

try :
	with open(config_path) as f :
		config = json.load(f)
	print("Loaded config")
except FileNotFoundError :
	print("No config file found, creating")
	try :
		os.mkdir(config_path[:config_path.rfind("/")])
	except : ...
	with open(config_path, "w") as f :
		json.dump({
			"langs": [],
			"rm-misplaced": None,
			"packages": {},
			"editor": "",
			"ideas": []
		}, f)
	with open(config_path) as f :
		config = json.load(f)
	print("Created & loaded config file")

def saveConfig() :
	with open(config_path, "w") as f :
		json.dump(config, f)

def setConfig(key: str, val) :
	config[key] = val
	saveConfig()

def getConfig(key: str, default) :
	return config[key] if key in config else default

editor = getConfig("editor", "")
ideas = getConfig("ideas", [])

if editor == "" :
	print("Looks like you haven't configured an editor")
	ide = input("With what command should I open the directory $x: ")

	setConfig("editor", ide)

langs = getConfig("langs", [])

if not langs :
	toadd = []
	print("You can change alnguage folders later but it requires a restart to get configured properly")
	select = input("There are no language files in the config, would you like to autoselect them? (y/n) ").lower()[0] == "y"
	homedirs = [str(Path.home() / x) for x in os.listdir(Path.home()) if os.path.isdir(Path.home() / x) and x[0] != "."]

	if select :
		toadd = [x for x in homedirs if len(x[len(str(Path.home())):]) < 5]
	else :
		ins = input("Directories to add: ").strip().split()
		toadd = [x if x.startswith("/") else str(Path.home() / x) for x in ins]

	while True :
		print("Folders that will be added:")
		for i in toadd :
			print(" -", i)
		correct = input("Is this correct? (y/n) ").lower()[0] == "y"

		if correct :
			langs = toadd
			setConfig("langs", toadd)
			break
		else :
			rm = input("Files to remove: ").strip().split()
			ad = input("Files to add: ").strip().split()

			rm = [x if x[0] == "/" else str(Path.home() / x) for x in rm]
			ad = [x if x[0] == "/" else str(Path.home() / x) for x in ad]

			for i in rm :
				if i in toadd :
					toadd.pop(toadd.index(i))

			toadd.extend(ad)

print("Loaded langs:")
for i in langs :
	print(" -", i)

print("Checking langs")

packs = getConfig("packages", {})
runs = getConfig("run-scripts", {})
extensions = getConfig("extensions", {})

for i in langs :
	l = i[i.rfind("/")+1:]

	print(f"Checking '{l}'")

	if not l in extensions :
		ex = input("File extension fo lang: ")

		extensions[l] = ex
		setConfig("extensions", extensions)

	if not l in runs :
		rn = input("Command to run the project: ")
		runs[l] = rn

		setConfig("run-scripts", runs)

	if not l in packs :
		print(f"Lang '{l}' does not have a package manager defined")
		packs[l] = {}

	if not "add" in packs[l] :
		packs[l]["add"] = input("Command to install library $x: ")

	if not "rm" in packs[l] :
		packs[l]["rm"] = input("Command to remove a library $x: ")

	if not "search" in packs[l] :
		packs[l]["search"] = input("Command to search for a library $x: ")

	if not "list" in packs[l] :
		packs[l]["list"] = input("Command to list installed packages: ")

	print(f"Lang '{l}' ok")

	setConfig("packages", packs)

rm_misplaced = getConfig("rm-misplaced", None)
misplaced = []
no_project_file = []

meta_structure = {
	"main": "",
	"last-modified": -1.0,
	"revision": 0,
	"name": "<not set>",
	"desc": "<not set>",
	"commits": [],
	"todos": [],
	"points": 0
}

print("Checking project files")
for i in langs :
	for f in os.listdir(i) :
		path = i + "/" + f
		if os.path.isfile(path) :
			misplaced.append(path)
		else :
			if not os.path.isfile(path + "/project.json") :
				no_project_file.append(path)
			else :
				with open(path + "/project.json") as f :
					proj = json.load(f)

				changed = False
				for m in meta_structure :
					if not m in proj :
						proj[m] = meta_structure[m]
						changed = True

				if changed :
					with open(path + "/project.json", "w") as f :
						json.dump(proj, f)

if rm_misplaced == None :
	print("These files seem to be misplaced:")
	for i in misplaced :
		print(" -", i)
	rm = input("Do you want to remove them? (y/n) ").lower()[0] == "y"
else :
	rm = rm_misplaced

setConfig("rm-misplaced", rm)
if rm :
	for i in misplaced :
		os.remove(i)

indent = "  "
def printJsonPritty(obj, depth = 0) :
	string = ""

	if type(obj) is dict :
		string += indent * depth + "{\n"
		for n,i in enumerate(obj) :
			string += indent * (depth + 1) + printJsonPritty(i, 0) + ": " + printJsonPritty(obj[i], depth + 1).lstrip() + ("," if n < len(obj) - 1 else "") + "\n"
		string += indent * depth + "}"

	if type(obj) is list :
		string += indent * depth + "[\n"
		for n,i in enumerate(obj) :
			string += printJsonPritty(i, depth + 1) + ("," if n < len(obj) - 1 else "") + "\n"
		string += indent * depth + "]"

	if type(obj) is str :
		return indent * depth + f"\033[92m'{obj}'\033[00m"

	if type(obj) is None :
		return indent * depth + "null"

	if type(obj) is int :
		return indent * depth + f"\033[96m{obj}\033[00m"

	if type(obj) is float :
		return indent * depth + f"\033[96m{obj}\033[00m"

	if type(obj) is bool :
		return indent * depth + f"\033[94m{"true" if obj else "false"}\033[00m"

	return string

if no_project_file :
	print("These files don't have a project file:")
	for i in no_project_file :
		print(" -", i)
	create = input("Do you want to create them? (y/n) ").lower()[0] == "y"

	if create :
		for i in no_project_file :
			print(i + "/project.json")
			meta = {
				"name": i[i.rfind("/")+1:],
				"desc": "<not set>",
				"revision": 0,
				"last-modified": os.stat(i).st_mtime,
				"main": ""
			}
			print(printJsonPritty(meta))
			with open(i + "/project.json", "w") as f :
				json.dump(meta, f)

def formatText(string: str) :
	new = string.replace("-", " ")
	new = "".join([x.upper() if n == 0 or new[n-1] == " " else x for n,x in enumerate(new)])
	return new

def getMetadata(path: str) :
	with open(path + "/project.json") as f :
		return json.load(f)

def showMetadata(path: str) :
	project_info = getMetadata(path)

	print("Project metadata:")
	print(printJsonPritty(project_info))

def setMetadata(path: str, key: str, value) :
	meta = getMetadata(path)

	meta[key] = value

	with open(path + "/project.json", "w") as f :
		f.write(json.dumps(meta))

def metaCmd(path: str) :
	showMetadata(path)

	return 1

def openCmd(path: str) -> int :

	print("Opening project")
	ide = getConfig("editor", "")

	os.popen(f"{ide.replace("$x", path)} &")

	return 1

def packCmd(path: str) -> int :
	lang = path[len(str(Path.home()))+1:path.rfind("/")]

	commands = getConfig("packages", {})[lang]

	print("Possible subcommands: add, rm, search, list")
	cmd = input(">>> ").strip().lower()

	if cmd == "add" :
		lib = input("Library to add: ").strip()
		cmd = f"cd {path} && {commands["add"].replace("$x", lib)}"
		print(f"Running {cmd}")
		os.system(cmd)
	elif cmd == "rm" :
		lib = input("Library to remove: ").strip()
		cmd = f"cd {path} && {commands["rm"].replace("$x", lib)}"
		print(f"Running {cmd}")
		os.system(cmd)
	elif cmd == "search" :
		lib = input("Keywords to search: ").strip()
		cmd = f"cd {path} && {commands["search"].replace("$x", lib)}"
		print(f"Running {cmd}")
		os.system(cmd)
	elif cmd == "list" :
		cmd = f"cd {path} && {commands["list"]}"
		print(f"Running {cmd}")
		os.system(cmd)

	return 1

def runCmd(path: str) :
	lang = path[len(str(Path.home()))+1:path.rfind("/")]

	script = getConfig("run-scripts", {})[lang]
	main = getMetadata(path)["main"]

	if main == "" :
		print("Main entry point not definde, use meta > set > main")
		return

	cmd = f"cd {path} && {script.replace("$x", main)}"

	os.system(cmd)

import time

def gitCmd(path: str) :
	print("Possible subommands: link, commit, pull")
	cmd = input(">>> ").strip()

	if cmd == "link" :
		link = input("Repository https/ssh: ")

		ret = os.system(f"cd {path} && git remote add origin {link} && git branch -M main && git add . && git commit -m \"First Commit\" && git push --set-upstream origin main")

		if ret == 0 :
			print("Linked github repo successfully!")

			meta = getMetadata(path)
			meta["commits"].append({
				"message": "First Commit",
				"time": time.time()
			})
			setMetadata(path, "commits", meta["commits"])

	elif cmd == "commit" :
		msg = input("Commit message: ")

		ret = os.system(f"cd {path} && git add . && git commit -m \"{msg}\" && git push")

		if ret == 0 :
			print("Commit pushed successfully!")
			cm = getMetadata(path)["commits"]
			cm.append(msg)
			setMetadata(path, "commits", cm)

			meta = getMetadata(path)
			meta["commits"].append({
				"message": msg,
				"time": time.time()
			})
			setMetadata(path, "commits", meta["commits"])
	elif cmd == "pull" :
		ret = os.system(f"cd {path} && git pull")
		if ret == 0 : print("Commit pulled successfully!")

def todoCmd(path: str) :
	print("Possible subcommands: exit, show, add, mark")
	cmd = input(">>> ")
	todo = getMetadata(path)["todos"]
	points = getMetadata(path)["points"]

	if cmd == "exit" :
		return 1
	elif cmd == "show" :
		print("This projects todos:")
		for i in todo :
			print(" " + ("x" if i["completed"] else "-"), i["label"], f"({i["points"]} points)" if not i["completed"] else "(completed)")
		print("Total points:", points)
	elif cmd == "add" :
		label = input("This todo's label: ")
		p = input("Amount of points to reward: ")
		if not p.isdecimal() :
			print(p, "is not a number")
			return 0

		points = int(p)

		todo.append({
			"label": label,
			"points": points,
			"completed": False
		})

		setMetadata(path, "todos", todo)
	elif cmd == "mark" :
		label = input("This todo's label: ")

		for i in todo :
			if i["label"] == label and not i["completed"] :
				i["completed"] = True
				p = getMetadata(path)["points"] + i["points"]
				setMetadata(path, "points", p)
				setMetadata(path, "todos", todo)
				return 0

		print("No uncompleted todo named:", label)

	return 0

def projectMode(path: str) :
	cmds = {
		"meta": metaCmd,
		"open": openCmd,
		"pack": packCmd,
		"run": runCmd,
		"git": gitCmd,
		"todo": todoCmd
	}

	while True :
		print("Availible commands: meta, open, exit, pack, run, git, todo")
		cmd = input(">>> ").strip()

		if cmd == "exit": return

		ex = 0
		while ex == 0 :
			ex = cmds[cmd](path)

def projectLoadMode() :
	print("(exit to abort) Select a project: [lang]/[name]")
	ins = input(">>> ")
	if ins == "exit" : return 1

	lang, name = map(str.strip, ins.split("/")) if "/" in ins else (ins, "")

	if name == "" :
		projects = [x for x in os.listdir(Path.home() / lang) if os.path.isfile(Path.home() / lang / x / "project.json")]
		projects.sort()
		print("Availible projects:")
		for i in projects :
			print(" -", i)
		name = input("Project name: ").strip()

	path = Path.home() / lang / name

	if not os.path.isdir(path) :
		print(f"'{path}' is not a project!")
		return 0

	last_update = os.stat(path).st_mtime
	meta = getMetadata(str(path))

	if last_update > meta["last-modified"] :
		setMetadata(str(path), "last-modified", last_update)
		setMetadata(str(path), "revision", meta["revision"] + 1)

	showMetadata(str(path))

	return projectMode(str(path))

def folderEditMode() :
	while True :
		print("Possible subcommands: exit, add, rm, list")
		cmd = input(">>> ")

		if cmd == "exit" :
			return

		if cmd == "list" :
			print("Language folders:")
			for i in langs :
				inside = os.listdir(i)

				projects = len([x for x in inside if os.path.isdir(i+"/"+x)])
				files = len([x for x in inside if os.path.isfile(i+"/"+x)])

				info = [x for x in [f"{projects} projects" if projects > 0 else "", f"{files} files" if files > 0 else ""] if x]

				print(" -", i, ("(" + ", ".join(info) + ")") if info else "")
		elif cmd == "add" :
			while True :
				add = input("Directories to add: ").strip().split()

				add = [x if x[0] == "/" else str(Path.home() / x) for x in add]

				print("These dirs will be added:")
				for i in add :
					print(" -", i)

				correct = input("Is this correct? (y/n) ").lower()[0] == "y"
				if correct :
					langs.extend(add)
					setConfig("langs", langs)
					break
		elif cmd == "rm" :
			while True :
				add = input("Directories to remove: ").strip().split()

				add = [x if x[0] == "/" else str(Path.home() / x) for x in add]

				print("These dirs will be removed:")
				for i in add :
					print(" -", i)

				correct = input("Is this correct? (y/n) ").lower()[0] == "y"
				if correct :
					for i in add :
						if i in langs :
							langs.pop(langs.index(i))
					setConfig("langs", langs)
					break

def configEditMode() :
	cfg = printJsonPritty(config)
	print(cfg)
	print(f"Config stored in '{config_path}'")

def escapeText(string: str) :
	return string.lower().replace(" ", "_")

def createMode() :
	while True :
		print("Possible language folders:")
		for i in langs :
			print(" -", i)
		lang = input("Project language: ").strip()
		lang = lang if lang.startswith("/") else str(Path.home() / lang)

		if not lang in langs :
			print(f"'{lang}' is not a registered language folder, please register it as such before continuing")
			return

		name = input("Project name: ").strip()
		name_esc = escapeText(name)
		print(f"Escaped name: {name_esc}")

		desc = input("Project decsription: ").strip()
		desc = desc if desc != "" else "<not set>"

		path = lang + "/" + name_esc

		ex = extensions[lang[lang.rfind("/")+1:]]

		main = input(f"Main project entry point (default: {name_esc}.{ex}): ")
		main = main if main != "" else name_esc + "." + ex

		meta = {
			"name": name,
			"desc": desc,
			"revision": 0,
			"last-modified": -1,
			"main": main
		}
		mt = printJsonPritty(meta)
		print("Meta file created:")
		print(mt)
		correct = input("Is this correct? (y/n) ").lower()[0] == "y"
		if correct :
			break

	os.mkdir(path)

	os.system(f"cd {path} && git init")

	with open(path + "/" + main, "w") as f :
		pass

	with open(path + "/project.json", "w") as f :
		json.dump(meta, f)

	last_update = os.stat(path).st_mtime
	meta = getMetadata(str(path))

	if last_update > meta["last-modified"] :
		setMetadata(str(path), "last-modified", last_update)
		setMetadata(str(path), "revision", meta["revision"] + 1)

	return projectMode(str(path))

def ideaMode() :

	while True :

		print("Possible subcommands: exit, make, show, rm")
		cmd = input(">>> ")

		if cmd == "exit" :
			break
		elif cmd == "show" :
			print("Saved project ideas:")
			for i in ideas :
				print(" -", i["name"])
				print(" ", " ", i["desc"])
		elif cmd == "make" :
			name = input("Idea name: ")
			desc = input("Idea description: ")

			ideas.append({
				"name": name,
				"desc": desc
			})

			setConfig("ideas", ideas)
		elif cmd == "rm" :
			id = input("Id to remove: ")
			if not id.isdecimal() :
				print(id, "is not a number")
				continue

			id = int(id)

			ideas.pop(id)

			setConfig("ideas", ideas)

def interactiveMode() :
	print("(exit to close) Select a mode, possible modes: langs, project, config, create, ideas")
	mode = input(">>> ")

	if mode == "exit": exit()

	func = None
	if mode == "project" :
		func = projectLoadMode
	elif mode == "langs" :
		func = folderEditMode
	elif mode == "config" :
		func = configEditMode
	elif mode == "create" :
		func = createMode
	elif mode == "ideas" :
		func = ideaMode

	if func :
		func()

while True :
	interactiveMode()

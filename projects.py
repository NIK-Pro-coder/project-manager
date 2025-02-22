#!/usr/bin/env python

import os, json
from pathlib import Path
from typing import Any

def green(text: str) -> str : return f"\033[92m{text}\033[00m"
def aquamarine(text: str) -> str : return f"\033[96m'{text}'\033[00m"
def blue(text: str) -> str : return f"\033[94m'{text}'\033[00m"

indent = "  "
def printJsonPritty(obj: Any, depth: int = 0) -> str :
	string: str = ""

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
		string = indent * depth + green(f"'{obj}'")

	if obj == None :
		string = indent * depth + "null"

	if type(obj) is int :
		string = indent * depth + aquamarine(str(obj))

	if type(obj) is float :
		string = indent * depth + aquamarine(str(obj))

	if type(obj) is bool :
		string = indent * depth + blue("true" if obj else "false")

	return string

config_path = str(Path.home() / ".config/project-manager/config.json")

def autocomplete(query: str, possiblilities: list[str]) -> str :
	got: str = input(query).strip()
	fil: list[str] = [x for x in possiblilities if x.startswith(got)]
	fil = list(set(fil))

	if len(fil) == 0 or got == "" :
		print("Nothing matched, possible values:", ", ".join(possiblilities))
		return autocomplete(query, possiblilities)
	elif len(fil) > 1 :
		print("Possibilities:", ", ".join(fil))
		return autocomplete(query, fil)
	else :
		print(f"\033[F{query}{fil[0]}")
		return fil[0]

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
			"ideas": [],
			"create-backup": None,
			"templates": {}
		}, f)
	with open(config_path) as f :
		config = json.load(f)
	print("Created & loaded config file")

def saveConfig() :
	with open(config_path, "w") as f :
		json.dump(config, f)

def setConfig(key: str, val: Any) :
	config[key] = val
	saveConfig()

def getConfig(key: str, default: Any) :
	return config[key] if key in config else default

oncreate = getConfig("on-create", {})
onload = getConfig("on-load", {})

templates: dict = getConfig("templates", {})
editor = getConfig("editor", "")
ideas = getConfig("ideas", [])

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

langs = [x for x in langs if x.startswith("/")]
setConfig("langs", langs)

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
		ex = input(f"File extension for lang (default = .{l}): ").removeprefix(".")

		extensions[l] = ex
		setConfig("extensions", extensions)

	print(f"Lang '{l}' ok")

rm_misplaced: bool | None = getConfig("rm-misplaced", None)
misplaced: list[str] = []
no_project_file: list[str] = []

meta_structure: dict[str, str | float | int | list[dict[str, int | str | bool]]] = {
	"main": "",
	"last-modified": -1.0,
	"revision": 0,
	"name": "<not set>",
	"desc": "<not set>",
	"commits": [],
	"todos": [],
	"points": 0
}

create_backup: bool | None = getConfig("create-backups", None)
if create_backup == None :
	print("This program creates a file called project.json for every project file you have")
	create_backup = input("Would you like to skip this step for filders that have 'backup' in their name? (y/n) ").lower()[0] == "y"

	setConfig("create-backups", create_backup)

projects_in_folder: bool | None = getConfig("projects-in-folder", None)
if projects_in_folder == None :
	projects_in_folder = input("Would you like to move project files all to a signle folder? (y/n) ").lower()[0] == "y"

	setConfig("projects-in-folder", projects_in_folder)

if projects_in_folder and not os.path.isdir(Path.home() / ".config/project-manager/projects") :
	os.mkdir(Path.home() / ".config/project-manager/projects")

def makeCompisitePath(path: str) :

	p = path.split("/")[1:]
	s = ""

	for i in p :
		s += "/" + i
		if not os.path.isdir(s) :
			os.mkdir(s)

def dirTree(start_from: str) -> list[str] :
	inside = os.listdir(start_from)

	ret = []

	for i in inside :
		if os.path.isdir(start_from + "/" + i) :
			ret.extend(dirTree(start_from + "/" + i))
		else :
			ret.append(start_from + "/" + i)

	return ret

if projects_in_folder :
	for i in langs :
		print(i)
		if not os.path.isdir(Path.home() / (".config/project-manager/projects/" + i)) :
			makeCompisitePath(str(Path.home() / (".config/project-manager/projects/" + i)))

	for i in langs :
		for f in os.listdir(i) :
			path: str = i + "/" + f
			if os.path.isfile(path + "/project.json") :
				with open(Path.home() / (".config/project-manager/projects" + path + ".json"), "w") as f :
					with open(path + "/project.json") as r :
						f.write(r.read())
				os.remove(path + "/project.json")
else :
	files = dirTree(str(Path.home() / ".config/project-manager/projects"))
	files_stripped = [x.removeprefix(str(Path.home() / ".config/project-manager/projects")) for x in files]

	for i in files_stripped :
		makeCompisitePath(i[:i.rfind("/")])

		with open(i[:i.rfind(".")] + "/project.json", "w") as w :
			with open(str(Path.home() / ".config/project-manager/projects") + i) as r :
				w.write(r.read())

print("Checking project files")
for i in langs :
	for f in os.listdir(i) :
		path: str = i + "/" + f
		if os.path.isfile(path) :
			misplaced.append(path)
		else :
			if projects_in_folder :
				if not os.path.isfile(Path.home() / (".config/project-manager/projects" + path + ".json")) :
					if not "backup" in f or not create_backup :
						no_project_file.append(path)
				else :
					with open(Path.home() / (".config/project-manager/projects" + path + ".json")) as f :
						proj = json.load(f)

					proj["commits"] = [x for x in proj["commits"] if type(x) is dict]

					for m in meta_structure :
						if not m in proj :
							proj[m] = meta_structure[m]

					with open(Path.home() / (".config/project-manager/projects" + path + ".json"), "w") as f :
						json.dump(proj, f)
			else :
				if not os.path.isfile(path + "/project.json") :
					if not("backup" in f) or not(create_backup) :
						no_project_file.append(path)
				else :
					with open(path + "/project.json") as f :
						proj = json.load(f)

					proj["commits"] = [x for x in proj["commits"] if type(x) is dict]

					for m in meta_structure :
						if not m in proj :
							proj[m] = meta_structure[m]

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


if no_project_file :
	print("These files don't have a project file:")
	for i in no_project_file :
		print(" -", i)
	create = input("Do you want to create them? (y/n) ").lower()[0] == "y"

	if create :
		for i in no_project_file :
			meta = meta_structure.copy()
			meta["name"] = i[i.rfind("/")+1:]

			print(printJsonPritty(meta))
			if projects_in_folder :
				with open(Path.home() / ".config/project-manager/projects" / (i + ".json"), "w") as f :
					json.dump(meta, f)
			else :
				with open(i + "/project.json", "w") as f :
					json.dump(meta, f)

def formatText(string: str) :
	new = string.replace("-", " ")
	new = "".join([x.upper() if n == 0 or new[n-1] == " " else x for n,x in enumerate(new)])
	return new

def getMetadata(path: str) :
	if projects_in_folder :
		with open(Path.home() / (".config/project-manager/projects" + path + ".json")) as f :
			return json.load(f)
	else :
		with open(path + "/project.json") as f :
			return json.load(f)

def showMetadata(path: str) :
	project_info = getMetadata(path)

	print("Project metadata:")
	print(printJsonPritty(project_info))
	if projects_in_folder :
		print(f"Metadata stored in: {Path.home()}.config/project-manager/projects{path}.json")
	else :
		print(f"Metadata stored in: {path}/project.json")

def setMetadata(path: str, key: str, value: Any) :
	meta = getMetadata(path)

	meta[key] = value

	if projects_in_folder :
		with open(Path.home() / (".config/project-manager/projects" + path + ".json"), "w") as f :
			f.write(json.dumps(meta))
	else :
		with open(i + "/project.json", "w") as f :
			f.write(json.dumps(meta))

def metaCmd(path: str) :
	showMetadata(path)

	return 1

def openCmd(path: str) -> int :

	if editor == "" :
		print("Looks like you haven't configured an editor")
		ide = input("Command to open the project: (use $x for project dir) ")

		setConfig("editor", ide)

	print("Opening project")
	ide = getConfig("editor", "")

	os.popen(f"{ide.replace("$x", path)} &")

	return 1

def packCmd(path: str) -> int :
	lang = path[len(str(Path.home()))+1:path.rfind("/")]

	if not lang in packs :
		packs[lang] = {}
		setConfig("packages", packs)

	commands = packs[lang]

	print("Possible subcommands: add, rm, search, list")
	cmd = autocomplete(f"/project{path[len(str(Path.home())):]}/pack >>> ", ["add", "rm", "list"]).strip().lower()

	if cmd == "add" :
		if not "add" in packs[lang] :
			packs[lang]["add"] = input("Command to install library: (use $x for library name and $t for target dir) ")
			setConfig("packages", packs)

		lib = input(f"/project{path[len(str(Path.home())):]}/pack/add | Library to add: ").strip()
		if lib == "" : return 0
		cmd_run = f"cd {path} && {commands["add"].replace("$x", lib).replace("$t", path)}"
	elif cmd == "rm" :
		if not "rm" in packs[lang] :
			packs[lang]["rm"] = input("Command to remove a library: (use $x for library name and $t for target dir) ")
			setConfig("packages", packs)

		lib = input(f"/project{path[len(str(Path.home())):]}/pack/rm | Library to remove: ").strip()
		if lib == "" : return 0
		cmd_run = f"cd {path} && {commands["rm"].replace("$x", lib).replace("$t", path)}"
	elif cmd == "search" :
		if not "search" in packs[lang] :
			packs[lang]["search"] = input("Command to search for a library: (use $x for library name and $t for target dir) ")
			setConfig("packages", packs)

		lib = input(f"/project{path[len(str(Path.home())):]}/pack/search | Keywords to search: ").strip()
		if lib == "" : return 0
		cmd_run = f"cd {path} && {commands["search"].replace("$x", lib).replace("$t", path)}"
	elif cmd == "list" :
		if not "list" in packs[lang] :
			packs[lang]["list"] = input("Command to list installed packages: (use $t for project dir) ")
			setConfig("packages", packs)

		cmd_run = f"cd {path} && {commands["list"]}"

	print(f"Running {cmd_run}")
	os.system(cmd_run)

	return 1

def runCmd(path: str) :
	lang = path[len(str(Path.home()))+1:path.rfind("/")]

	if not lang in runs :
		rn = input("Command to run this project: (use $x for main entry point) ")
		runs[lang] = rn

		setConfig("run-scripts", runs)

	script = runs[lang]
	main = getMetadata(path)["main"]

	if main == "" :
		print("Main entry point not definde, edit the project.json file")
		return

	cmd = f"cd {path} && {script.replace("$x", main)}"

	os.system(cmd)

import time

def gitCmd(path: str) :
	print("Possible subommands: link, commit, pull, exit")
	cmd = autocomplete(f"/project{path[len(str(Path.home())):]}/git >>> ", ["link", "commit", "pull", "exit"]).strip()

	if cmd == "exit" :
		return
	if cmd == "link" :
		link = input(f"/project{path[len(str(Path.home())):]}/git/link | Repository https/ssh: ")

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
		msg = input(f"/project{path[len(str(Path.home())):]}/git/commit | Commit message: ")

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

def showTodo(path: str) :
	todo = getMetadata(path)["todos"]
	points = getMetadata(path)["points"]

	print("This projects todos:")
	for i in todo :
		print(" -", i["label"], f"({i["points"]} points)", "\033[92m(completed)\033[00m" if i["completed"] else "")
	p_norm = points%30
	print("Points:", p_norm, "[" + "#" * p_norm + "-" * (30 - p_norm) + "]", end = " ")
	print("Level:", int(points / 30))

def todoCmd(path: str) :
	print("Possible subcommands: exit, show, add, mark")
	cmd = autocomplete(f"/project{path[len(str(Path.home())):]}/todo >>> ", ["exit", "show", "add", "mark"])
	todo = getMetadata(path)["todos"]
	points = getMetadata(path)["points"]

	if cmd == "exit" :
		return 1
	elif cmd == "show" :
		showTodo(path)
	elif cmd == "add" :
		label = input(f"/project{path[len(str(Path.home())):]}/todo/add | This todo's label: ")
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
		p_label = [x["label"] for x in todo if not x["completed"]]
		label = autocomplete(f"/project{path[len(str(Path.home())):]}/todo/mark | This todo's label: ", p_label)

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

	lang = path[:path.rfind("/")]

	if not lang in onload :
		onload[lang] = ""
		create = input(f"Lang '{lang}' has not onload command set, would you like ot do it now? (y/n) ").lower()[0] == "y"

		if create :
			cmd = input("Onload command: (use $t for project path) ")
			onload[lang] = cmd

		setConfig("on-load", onload)

	if onload[lang] != "" :
		cmd = f"cd {path} && {onload[lang].replace("$t", path)}"
		print(f"Running onload command: '{cmd}'")
		os.system(cmd)

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
		cmd = autocomplete(f"/project{path[len(str(Path.home())):]} >>> ", ["meta", "open", "exit", "pack", "run", "git", "todo"]).strip()

		if cmd == "exit": return

		ex = 0
		while ex == 0 :
			ex = cmds[cmd](path)

def projectLoadMode() :
	print("(exit to abort) Select a project: [lang]/[name]")

	p_langs = [x[x.rfind("/")+1:] for x in langs]
	p_langs.append("exit")

	ins = autocomplete("/project >>> ", p_langs)
	if ins == "exit" : return 1

	lang, name = map(str.strip, ins.split("/")) if "/" in ins else (ins, "")

	if name == "" :
		projects = [x for x in os.listdir(Path.home() / lang) if os.path.isdir(Path.home() / lang / x)]
		projects.sort()
		print("Availible projects:")
		for i in projects :
			print(" -", i)
		p_projects = projects
		p_projects.extend([x[x.rfind("/")+1:] for x in projects])
		name = autocomplete(f"/project/{lang} | Project name: ", p_projects).strip()

	path = Path.home() / lang / name

	if not os.path.isdir(path) :
		print(f"'{path}' is not a project!")
		return 0

	last_update = os.stat(path).st_mtime
	meta = getMetadata(str(path))

	if last_update > meta["last-modified"] :
		setMetadata(str(path), "last-modified", last_update)
		setMetadata(str(path), "revision", meta["revision"] + 1)

	showTodo(str(path))

	return projectMode(str(path))

def folderEditMode() :
	while True :
		print("Possible subcommands: exit, add, rm, list")
		cmd = autocomplete("/langs >>> ", ["exit", "add", "rm", "list"])

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
				add = input("/langs/add | Directories to add: ").strip().split()

				add = [x if x[0] == "/" else str(Path.home() / x) for x in add]

				print("These dirs will be added:")
				for i in add :
					print(" -", i)

				correct = input("/langs/add | Is this correct? (y/n) ").lower()[0] == "y"
				if correct :
					langs.extend(add)
					setConfig("langs", langs)
					break
		elif cmd == "rm" :
			while True :
				add = input("/langs/rm | Directories to remove: ").strip().split()

				add = [x if x[0] == "/" else str(Path.home() / x) for x in add]

				print("These dirs will be removed:")
				for i in add :
					print(" -", i)

				correct = input("/langs/rm | Is this correct? (y/n) ").lower()[0] == "y"
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

def createModeNoTempl() :
	while True :
		print("Possible language folders:")
		for i in langs :
			print(" -", i)

		p_langs = langs
		p_langs.extend([x[x.rfind("/")+1:] for x in langs])

		lang = autocomplete("/create | Project language: ", p_langs).strip()
		lang = lang if lang.startswith("/") else str(Path.home() / lang)

		if not lang in langs :
			print(f"'{lang}' is not a registered language folder, please register it as such before continuing")
			return -1

		name = input("/create | Project name: ").strip()
		name_esc = escapeText(name)
		print(f"Escaped name: {name_esc}")

		desc = input("/create | Project decsription: ").strip()
		desc = desc if desc != "" else "<not set>"

		path = lang + "/" + name_esc

		ex = extensions[lang[lang.rfind("/")+1:]]

		main = input(f"/create | Main project entry point (default: {name_esc}.{ex}): ")
		main = main if main != "" else name_esc + "." + ex

		meta = meta_structure.copy()
		meta["name"] = name
		meta["desc"] = desc
		meta["main"] = main

		mt = printJsonPritty(meta)
		print("Meta file created:")
		print(mt)
		correct = input("/create | Is this correct? (y/n) ").lower()[0] == "y"
		if correct :
			break

	os.mkdir(path)

	os.system(f"cd {path} && git init")

	with open(path + "/" + main, "w") as f :
		pass

	if projects_in_folder :
		with open(Path.home() / (".config/project-manager/projects" + path + ".json"), "w") as f :
			json.dump(meta, f)
	else :
		with open(path + "/project.json", "w") as f :
			json.dump(meta, f)

def copyDir(path: str, to: str) :
	inside = [x for x in os.listdir(path)]

	files = [x for x in inside if os.path.isfile(path + "/" + x) and not os.path.islink(path + "/" + x)]
	dirs = [x for x in inside if os.path.isdir(path + "/" + x) and not os.path.islink(path + "/" + x)]

	for i in files :
		with open(to + "/" + i, "w") as f :
			with open(path + "/" + i) as r :
				f.write(r.read())

	for i in dirs :
		os.mkdir(to + "/" + i)
		copyDir(path + "/" + i, to + "/" + i)

def createModeTempl() :
	while True :
		tm = autocomplete("/create | Name of template to use: ", list(templates.keys()))

		templ = templates[tm]

		name = input("/create | Project name: ").strip()
		name_esc = escapeText(name)
		print(f"/create | Escaped name: {name_esc}")

		desc = input("/create | Project description: ").strip()
		desc = desc if desc else "<not set>"

		path = templ["lang"] + "/" + name_esc

		meta = meta_structure.copy()
		meta["name"] = name
		meta["desc"] = desc
		meta["main"] = templ["main"]

		mt = printJsonPritty(meta)
		print("Meta file created:")
		print(mt)
		correct = input("/create | Is this correct? (y/n) ").lower()[0] == "y"
		if correct :
			break

	os.mkdir(path)

	print(f"Copying {templ["dir"]} -> {path}")

	copyDir(templ["dir"], path)

	os.system(f"cd {path} && git init")

	if projects_in_folder :
		with open(Path.home() / (".config/project-manager/projects" + path + ".json"), "w") as f :
			json.dump(meta, f)
	else :
		with open(path + "/project.json", "w") as f :
			json.dump(meta, f)

	print("Running pre-package command:", templ["cmd"].replace("$t", path))
	os.system(f"cd {path} && " + templ["cmd"].replace("$t", path))

	ln = path[len(str(Path.home()))+1:path.rfind("/")]
	add = getConfig("packages", {})[ln]["add"]

	print("Getting libraries")

	for i in templ["pack"] :
		cmd = f"cd {path} && {add.replace("$x", i).replace("$t", path)}"
		print(f"Running {cmd}")
		os.system(cmd)

	return path

def createMode() :
	if len(templates) > 0 :
		temp = input("/create | Would you like to use a template? (y/n) ").strip().lower()[0] == "y"
	else :
		temp = False

	if temp :
		path = createModeTempl()
	else :
		path = createModeNoTempl()
		if path == -1 :
			return


	lang = path[:path.rfind("/")]

	if not lang in oncreate :
		oncreate[lang] = ""
		create = input(f"Lang '{lang}' has not oncreate command set, would you like ot do it now? (y/n) ").lower()[0] == "y"

		if create :
			cmd = input("Oncreate command: (use $t for project path) ")
			oncreate[lang] = cmd

		setConfig("on-create", oncreate)

	if oncreate[lang] != "" :
		cmd = f"cd {path} && {oncreate[lang].replace("$t", path)}"
		print(f"Running oncreate command: '{cmd}'")
		os.system(cmd)

	return projectMode(str(path))

def ideaMode() :

	while True :

		print("Possible subcommands: exit, make, show, rm")
		cmd = autocomplete("/ideas >>> ", ["exit", "make", "show", "rm"])

		if cmd == "exit" :
			break
		elif cmd == "show" :
			print("Saved project ideas:")
			for i in ideas :
				print(" -", i["name"])
				print(" ", " ", i["desc"])
		elif cmd == "make" :
			name = input("/ideas/add | Idea name: ")
			desc = input("/ideas/add | Idea description: ")

			ideas.append({
				"name": name,
				"desc": desc
			})

			setConfig("ideas", ideas)
		elif cmd == "rm" :
			possible = [x["name"] for x in ideas]
			id = autocomplete("/ideas/rn | Name if idea to remove: ", possible)

			for n,i in enumerate(ideas) :
				if i["name"] == id :
					ideas.pop(n)

			setConfig("ideas", ideas)

def templateMode() :
	while True :
		print("Possible subcommands: exit, show, add, rm")
		cmd = autocomplete("/tmpl >>> ", ["exit", "show", "add", "rm"])

		if cmd == "exit" :
			return
		elif cmd == "show" :
			pritty = printJsonPritty(templates)
			print("Templates:")
			print(pritty)
		elif cmd == "add" :
			while True :
				name = escapeText(input("/tmpl/add | Template Name: "))
				print(f"/tmpl/add | Name set as '{name}'")

				p_langs = langs
				p_langs.extend([x[x.rfind("/")+1:] for x in langs])

				base_lang = autocomplete("/tmpl/add | Template base language: ", p_langs)
				base_lang = base_lang if base_lang.startswith("/") else str(Path.home() / base_lang)

				dir = input("/tmpl/add | Template directory: ").strip()
				dir = dir if dir.startswith("/") else str(Path.home() / dir)

				entry = input(f"/tmpl/add | Main entry point (default: main.{extensions[base_lang[base_lang.rfind("/")+1:]]}): ")
				entry = entry if entry else f"main.{extensions[base_lang[base_lang.rfind("/")+1:]]}"

				cmd = input("/tmpl/add | OnCreate command: ").strip()
				packages = input("/tmpl/add | Packages to install automatically: ").strip().split()

				temp = {
					"lang": base_lang,
					"dir": dir,
					"main": entry,
					"cmd": cmd,
					"pack": packages
				}

				mt = printJsonPritty(temp)
				print("Template file created: ")
				print(green(f"'{name}'") + ":", mt)
				correct = input("/tmpl/add | Is this correct? (y/n) ").lower()[0] == "y"
				if correct :
					templates[name] = temp
					setConfig("templates", templates)
					break
		elif cmd == "rm" :
			name = autocomplete("/tmpl/rm | Template to remove: ", list(templates.keys()))
			templates.pop(name)
			setConfig("templates", templates)

def interactiveMode() :
	print("(exit to close) Select a mode, possible modes: langs, project, config, create, ideas, templ")
	mode = autocomplete("/ >>> ", ["exit", "langs", "project", "config", "create", "ideas", "templ"])

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
	elif mode == "templ" :
		func = templateMode

	if func :
		func()

while True :
	interactiveMode()

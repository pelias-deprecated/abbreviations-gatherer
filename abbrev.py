import BeautifulSoup
import urllib2
import json
import sys
import os

def getParsedSite():
	try:
		rawdata = urllib2.urlopen("http://wiki.openstreetmap.org/wiki/Name_finder:Abbreviations")
		parsed = BeautifulSoup.BeautifulSoup(rawdata)
		return parsed
	except:
		print "Couldn't reach server. Check your internet connection"
		sys.exit()

def getLanguageTable(index):
	return parsedSite.findAll("table")[index]

def getLanguageList():
	print "Loading abbreviations data"
	i = 0
	languageList = []
	for header in parsedSite.findAll("h2"):
		if header.span and header.span.string != "Template for another language":
			span = header.span
			languageList.append(str(i) + "-" + span.string)
			i += 1
	return languageList


def parseLanguage(languageTable):
	abbreviationList = {}
	for abbreviationElement in languageTable.findAll("tr")[1:]:
		row = parseRow(abbreviationElement)
		if row[0] not in abbreviationList:
			abbreviationList[row[0]] = row[1]
		else:
			abbreviationList[row[0]]["abbreviations"] += row[1]["abbreviations"]
	langDict = {"language": "", "abbreviationlist": abbreviationList}
	return langDict


def parseRow(rowElement):
	assert len(rowElement.findAll("td")) == 6
	keys = ["abbreviation", "concatenated", "separable", "implemented", "notes"]
	rowDic = dict.fromkeys(keys)
	tds = rowElement.findAll("td")
	rowDic["abbreviations"] = [tds[1].text]
	rowDic["concatenated"] = True if tds[2].text != 'no' else False
	rowDic["separable"] = tds[3].text
	rowDic["implemented"] = True if tds[2].text != 'no' else False
	rowDic["notes"] = tds[5].text
	return (tds[0].text, rowDic)

def getAllLangs():
	for index in range(len(getLanguageList())-1):
		ex(index)

def toJSON(dict):
	return json.dumps(dict)

def export(jsonData):
	if not os.path.exists("out"):
		os.makedirs("out")
	path = "out/" + json.loads(jsonData)["language"][:3].lower()+".json"
	file = open(path, "w")
	file.write(jsonData)
	print "Data written in " + path

def ex(index):
	languageTable = getLanguageTable(index)
	languageData = parseLanguage(languageTable)
	languageList = getLanguageList()
	languageData["language"] = languageList[int(index)][languageList[int(index)].find("-")+1:]
	jsonData = toJSON(languageData)
	export(jsonData)

def getOverlapping(index):
	languageTable = getLanguageTable(index)
	languageData = parseLanguage(languageTable)
	invertedIndex = {}
	for key in languageData["abbreviationlist"]:
		if key["abbreviation"] not in invertedIndex:
			invertedIndex[key["abbreviation"]] = [key["fullword"]]
		else:
			invertedIndex[key["abbreviation"]].append(key["fullword"])
	overlaps = {}
	for abbreviation in invertedIndex:
		if len(invertedIndex[abbreviation]) > 1:
			overlaps[abbreviation] = invertedIndex[abbreviation]
	if not os.path.exists("overlaps"):
		os.makedirs("overlaps")
	languageList = getLanguageList()
	path = "overlaps/" + languageList[int(index)][languageList[int(index)].find("-")+1:] + ".json"
	file = open(path, "w")
	file.write(json.dumps(overlaps))


parsedSite = getParsedSite()

if "-l" in sys.argv:
	for lan in getLanguageList():
		print lan

if "-o" in sys.argv:
	index = int(sys.argv[sys.argv.index("-o")+1])
	conflicts = getOverlapping(index)

elif "-g" in sys.argv:
	index = int(sys.argv[sys.argv.index("-g")+1])
	
	if sys.argv[index].isdigit():
		ex(int(sys.argv[index]))

	else:
		print "You need to specify one of the following indices or add --all"
		listLanguages()

elif "--all" in sys.argv:
	getAllLangs()

else:
	print ""
	print "Use -g [language index] to generate abbreviations data for a language"
	print "Use --all to generate all files"
	print "Use -l to list available languages"
	print ""

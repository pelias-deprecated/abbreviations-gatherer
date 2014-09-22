import BeautifulSoup
import urllib2
import json
import sys
import os

print "Loading abbvreviations data"

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
	i = 0
	languageList = []
	for header in parsedSite.findAll("h2"):
		if header.span and header.span.string != "Template for another language":
			span = header.span
			languageList.append(str(i) + "-" + span.string)
			i += 1
	return languageList


def parseLanguage(languageTable):
	abbreviationList = []
	for abbreviationElement in languageTable.findAll("tr")[1:]:
		abbreviationList.append(parseRow(abbreviationElement))
	print len(abbreviationList), "values written in JSON file"
	langDict = {"language": "", "abbreviationlist":abbreviationList}
	return langDict


def parseRow(rowElement):
	assert len(rowElement.findAll("td")) == 6
	keys = ["fullword", "abbreviation", "concatenated", "separable", "implemented", "notes"]
	rowDic = dict.fromkeys(keys)
	tds = rowElement.findAll("td")
	rowDic["fullword"] = tds[0].text
	rowDic["abbreviation"] = tds[1].text
	rowDic["concatenated"] = True if tds[2].text != 'no' else False
	rowDic["separable"] = tds[3].text
	rowDic["implemented"] = True if tds[2].text != 'no' else False
	rowDic["notes"] = tds[5].text
	return rowDic

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

parsedSite = getParsedSite()

if "-l" in sys.argv:
	for lan in languageList:
		print lan

elif "-g" in sys.argv:
	index = sys.argv.index("-g")+1
	
	if sys.argv[index].isdigit():
		ex(index)

	elif sys.argv[index] == "-all":
		pass

	else:
		print "You need to specify one of the following indices or add --all"
		listLanguages()

else:
	print "You need to specify an option"

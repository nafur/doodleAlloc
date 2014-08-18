
import urllib
import re
import json
import bs4

# Basic skeleton
def load_data(url, analyzer):
	html = urllib.urlopen(url).read()
	if len(html) == 0:
		return { "status": ["No HTML source could be loaded."] }
	
	return analyzer(html)

# load from doodle.com
def load_doodle(url):
	dataRE = re.compile("doodleJS.data.poll = ([^\n]*);")
	
	def analyzer(html):
		m = dataRE.search(html)
		if m == None:
			return { "status": "No json data was found in HTML source." }
	
		j = json.loads(m.group(1))
	
		return {
			"status": ["Loaded json data from <a href=\"" + url + "\">" + url + "</a>"],
			"tasks": j["optionsText"],
			"persons": map(lambda p: (p["name"], p["preferences"]), j["participants"])
		}
	
	return load_data(url, analyzer)

# load from terminplaner2.dfn.de
def load_dfn(url):
	def loadTasks(thead):
		tr = thead.tr
		if "rowspan" in tr.th.attrs and tr.th["rowspan"] == "2":
			cats = map(lambda x: (x.string, int(x["colspan"])), tr.find_all("th")[2:-1])
			ths = tr.next_sibling.find_all("th")
			res = []
			cc = cats.pop(0)
			for t in ths:
				if cc[1] == 0: cc = cats.pop(0)
				res.append(cc[0] + " " + t.string)
				cc = (cc[0], cc[1]-1)
			return res
		else:
			return map(lambda x: x.string, tr.find_all("th")[2:-1])

	def loadPersons(tbody):
		persons = []
		prefmap = {"Yes": "y", "Maybe": "m", "No": "n"}
		for p in tbody.find_all("tr"):
			if p.td.string != " ": continue # only person rows start with a td containing a space.
			tds = p.find_all("td")[1:-1]
			name = tds.pop(0).abbr.string
			pref = ""
			for t in tds:
				pref += prefmap[t.img["alt"]]
			persons.append( (name, pref) )
		return persons

	def analyzer(html):
		s = bs4.BeautifulSoup(html)
		try:
			tbl = s.find(id="responses").form.table
			return {
				"status": ["Parsed HTML from <a href=\"" + url + "\">" + url + "</a>"],
				"tasks": loadTasks(tbl.thead),
				"persons": loadPersons(tbl.tbody)
			}
		except KeyboardInterrupt:
			return { "status": ["An error occurred while parsing HTML from <a href=\"" + url + "\">" + url + "</a>. Chances are, that the URL is wrong."] }
		
	return load_data(url, analyzer)	

urls = {
	"doodle.com": (re.compile("http://doodle.com/[a-z0-9]+(/admin)?"), load_doodle),
	"dfn.de": (re.compile("https://terminplaner2.dfn.de/foodle/[a-zA-Z0-9\-]+"), load_dfn),
}

def load_auto(url):
	for page in urls:
		urlRE, f = urls[page]
		m = urlRE.search(url)
		if m != None:
			return f(m.group(0))
	status = ["No valid pattern for url <a href=\"" + url + "\">" + url + "</a> was found. Valid patterns are:"]
	for page in urls:
		status.append(page + ": <code>" + str(urls[page][0].pattern) + "</code>")
	return { "status": status }

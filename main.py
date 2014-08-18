from flask import Flask, render_template, request
app = Flask(__name__)

import loader
import assignment	


@app.route('/', methods=['GET','POST'])
def index():
	options = {}
	if request.method == 'POST':
		options["status"] = []
		options["url"] = request.form['url']

		data = loader.load_auto(options["url"])
		options["status"].extend(data["status"])

		if "persons" in data:
			solution = assignment.assign(data["persons"], data["tasks"])
			if solution[0] == 1:
				options["status"].append("Computed an assignment.")
			else:
				options["status"].append("Could not compute an assignment.")
			options["data"] = data
			options["solution"] = solution

	return render_template('index.html', **options)

if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0')

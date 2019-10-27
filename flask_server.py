from Instastories import scrape_from_web, logToHTML
from flask import Flask, render_template, request
app = Flask(__name__)

@app.route("/")
def index():
    render_log = logToHTML()
    return render_template("index.html", count_i = 0, count_v = 0, rendered_log = render_log)

	
@app.route("/scrape/", methods=['POST'])

def scrape():
    if request.method == "POST":
        amountScraped = int(request.form["amountToScrape"])
        count_i, count_v = scrape_from_web(amountScraped)

        rendered_log = logToHTML()
        return render_template('index.html', count_i = count_i, count_v = count_v, rendered_log = rendered_log)


	



if __name__ == "__main__":
    app.run()
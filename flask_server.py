from Instastories import *
from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
def index():
	return render_template('index.html')
	
	
@app.route("/scrape/", methods=['POST'])
def scrape():
	numberOfScraped = startScraping()
	return render_template('index.html', variable= numberOfScraped)
	



if __name__ == "__main__":
    app.run()
from Instastories import scrape_from_web
from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
def index():
	return render_template('index.html')
	
	
@app.route("/scrape/", methods=['POST'])
def scrape():
	scrape_from_web()
	return render_template('index.html')
	



if __name__ == "__main__":
    app.run()
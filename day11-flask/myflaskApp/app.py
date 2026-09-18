from flask import Flask,render_template

app = Flask(__name__)

@app.route("/")
def home():
    # return "Home Page!"
    # return "<h1> Home Page </h1> <p> this is paragraph ! </p>"
    return render_template('index.html')

@app.route("/about")
def about():
    return "About Page!"

@app.route("/login")
def login():
    return "Login Page!"

if __name__ == "__main__":
    app.run(debug=True)

# debug=True -> server will reload automatically whenever we do any changes.
# stop server -> ctrl + c



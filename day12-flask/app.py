from flask import Flask,render_template

app = Flask(__name__)


@app.route("/")
def home():
    name = "Deepak"
    person ={
        "age":30,
        "city":"New Delhi",
        "Phone" : 8984736434,
        "email" : "deepak@gmail.com"
    }

    context={
        "person":person,
        "name":name
    }
    return render_template("index.html",**context)


# dynamic routing
@app.route("/user/<int:userId>")
def user(userId):
    print("UserId : ",type(userId))
    return f"My userId is : {userId}"


@app.route("/user/<string:name>")
def profile(name):
    print("UserId : ",type(name))
    return f"My Name Is : {name}"


if __name__ == "__main__":
    app.run(debug=True)
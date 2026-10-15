from flask import Flask, make_response,request,session


app = Flask(__name__)
# please don't share this secret key with anyone.
app.secret_key = "lF97p8tZX|8(rjcO"

@app.route("/")
def home():
    return "Cookies and Session"


@app.route("/set-cookie")
def setCookie():
    response = make_response("Cookie Created")
    response.set_cookie("full_name", "Deepak Kumar", max_age=60)
    return response


@app.route("/get-cookie")
def getCookie():
    username = request.cookies.get("full_name")

    if username:
        return f"Welcome {username}"
    else:
        return f"Cookies Not Set"



@app.route("/delete-cookie")
def deleteCookie():
    response = make_response("Cookie Deleted")
    response.delete_cookie("full_name")
    return response


# Create session
@app.route("/set-session")
def set_session():
    session["username"] = "Deepak"
    session["email"] = "deepak@gmail.com"
    session["role"] = "Trainer"
    return "Session Created"


# Get Session
@app.route("/get-session")
def get_session():
    username = session.get("username")
    email = session.get("email")
    if username or email:
       return f"Welcome {username} , Email : {email}"

    return "Session Not Found"


@app.route("/clear-session")
def clear_session():
    session.clear()
    return "Session Cleared"




if __name__ == "__main__":
    app.run(debug=True)
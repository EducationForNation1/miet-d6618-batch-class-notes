from flask import Flask,render_template,request,flash,redirect
from db.contact import create_table
import sqlite3

app = Flask(__name__)
app.secret_key = 'thisismysecretkey' 
create_table()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact", methods=['GET','POST'])
def contact():
    if request.method == 'POST':
        # print("POST Request")
        full_name = request.form['full_name'].strip()
        email = request.form['email'].strip()
        phone = request.form['phone'].strip()
        message = request.form['msg'].strip()



        if full_name == "":
            flash("Name Field Can't be Empty ", "danger")
            return redirect("/contact")

        if email == "":
            flash("Email field is required", "danger")
            return redirect("/contact")


        if len(phone) != 10 or not phone.isdigit():
            flash("Enter Valid 10 digit Phone Number", "danger")
            return redirect("/contact")

        if len(message) < 10:
            flash("Message should be more than 10 characters", "danger")
            return redirect('/contact')


        # step-1 make connection
        con = sqlite3.connect('students.db') 

        # step-2 insert query
        con.execute(
             'INSERT INTO contact(full_name,email,phone,message) VALUES(?,?,?,?)', (full_name, email, phone,message) 
        )
        #  step-3 data ko permanent save krne ke liye
        con.commit() 

        # step-4 connection close
        con.close()

        # step-5 show custom message
        flash("Thank You, Our Team will Contact You", "success")
        return redirect("/contact")

        
    else:
        print("GET Request")
    return render_template("contact.html")

# entery point
if __name__ == "__main__":
    app.run(debug=True)


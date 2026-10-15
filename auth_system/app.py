from datetime import datetime
from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///auth.db"
db = SQLAlchemy(app)  #using 'db' we can create CRUD

# table - we create model for table
class User(db.Model):
    id=db.Column(
        db.Integer,
        primary_key =True
    )

    full_name = db.Column(
        db.String(100),
        nullable=False
    )

    username = db.Column(
        db.String(50),
        unique = True,
        nullable=False
    )

    email = db.Column(
        db.String(255),
        unique = True,
        nullable = False
    )

    phone = db.Column(
        db.String(15)
    )

    password = db.Column(
        db.String(255),
        nullable = False
    )

    role = db.Column(
        db.String(20),
        default = 'user'
    )

    is_varified = db.Column(
        db.Boolean,
        default = False
    )

    is_active = db.Column(
        db.Boolean,
        default = True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

@app.route("/")
def home():
    return render_template("index.html")

# run only one time,  it will create all tables into database.
# with app.app_context():
#     db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
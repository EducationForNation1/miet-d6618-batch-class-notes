from flask import Flask,jsonify,request
import mysql.connector

app = Flask(__name__)

db = mysql.connector.connect(
 host="localhost",
 user="root",
 password="root",
 database="flaskcrud"
)

if db:
    print("Database Connected")
else:
    print("Database connection failed")

@app.route('/')
def home():
    return jsonify({
        "message":"This is My First API Using Flask"
    })

@app.route("/get-records", methods=["GET"])
def getRecords():
    cursor = db.cursor(dictionary=True) #dictionary=True
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    cursor.close()

    return jsonify({
        "message":"Get All Students Records",
        "students" :students
    })

@app.route("/get-single-record/<int:id>", methods=["GET"])
def retSingleStudent(id):
    cursor = db.cursor(dictionary=True)
    cursor.execute(
    "SELECT * FROM students WHERE id = %s", (id,)
    )
    student = cursor.fetchone()
    cursor.close()
    if student:
        return jsonify({
            "Student Id": id,
            "message" : "Get Single Student Record",
            "student":student
        })
    return jsonify({
        "Student Id": id,
        "message": "Student Not Found"
    })


@app.route("/create", methods=['POST'])
def create():
    data = request.get_json()
    if not data:
        return jsonify({
        "message": "JSON data is required"
        }), 400

    required_fields = [
        "name",
        "age",
        "course",
        ]

    for field in required_fields:
        if field not in data:
            return jsonify({
            "message": f"{field} is required"
            }), 400

    cursor = db.cursor(dictionary=True)
    query = '''
            INSERT INTO students
            (name, age, course)
            VALUES (%s, %s, %s)
            '''
    values = (
        data["name"],
        data["age"],
        data["course"]
        )

    
    cursor.execute(query, values)
    db.commit()
    cursor.close()
    return jsonify({
        "message":"New Account Created"
    }),201



@app.route("/delete/<int:id>", methods=["GET"])
def delete(id):
    cursor = db.cursor()
    cursor.execute(
    "DELETE FROM students WHERE id = %s", (id,)
    )
    db.commit()
    return jsonify({
        "Id ":id,
        "message":f"{id} Record Deleted!"
    })


if __name__ == "__main__":
    app.run(debug=True)

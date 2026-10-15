from flask import Flask, jsonify,request
from database.db import connectDB

app = Flask(__name__)

# get All todos 
@app.route("/api/todos", methods=["GET"])
def todos():
    conn = connectDB()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM todos"
        )

    todos = cursor.fetchall()
    conn.close()
    return jsonify({
        "message":"Here todos list",
        "all_todos" :todos
    }),200



# Get Single Todo by Id
@app.route("/api/todos/<int:id>", methods=["GET"])
def get_todos(id):
    conn = connectDB()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM todos WHERE id = %s",(id,)
    )
    todo = cursor.fetchone()
    conn.close()
    return jsonify({
        "todo" : todo,
        "message":f"Todo Id {id} , data Found"
    })


# Create Todo 
@app.route("/api/todos", methods=["POST"])
def create_todo():
    data = request.get_json()
    name = data.get("name")
    title = data.get("title")
    description = data.get("description")

    conn = connectDB()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        '''
            INSERT INTO todos(name,title,description) VALUES(%s,%s,%s)
        ''',(name,title,description)
    )
    conn.commit()

    conn.close()
    return jsonify({
        "message":"Todo Created Successfully"
    })

if __name__ == "__main__":
    app.run(debug=True)



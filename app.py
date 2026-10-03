from flask import Flask, request, redirect, render_template_string
import sqlite3
import os

app = Flask(__name__)

DATABASE = "complaints.db"


def create_table():
    conn = sqlite3.connect(DATABASE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            classroom TEXT NOT NULL,
            problem TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'Pending'
        )
    """)
    conn.commit()
    conn.close()


create_table()


HOME_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Classroom Maintenance System</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: Arial;
            background: #eef2f7;
            padding: 20px;
        }
        .box {
            max-width: 500px;
            margin: auto;
            background: white;
            padding: 25px;
            border-radius: 12px;
        }
        h2 {
            text-align: center;
            color: #174ea6;
        }
        input, textarea, select {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            box-sizing: border-box;
        }
        button {
            width: 100%;
            padding: 12px;
            background: #174ea6;
            color: white;
            border: none;
            border-radius: 5px;
        }
        a {
            display: block;
            text-align: center;
            margin-top: 20px;
        }
    </style>
</head>
<body>
<div class="box">
    <h2>Classroom Maintenance System</h2>
    <form action="/submit" method="POST">
        <input type="text" name="name"
        placeholder="Student Name" required>

        <input type="text" name="classroom"
        placeholder="Classroom Number" required>

        <select name="problem" required>
            <option value="">Select Problem</option>
            <option>Fan Problem</option>
            <option>Light Problem</option>
            <option>Bench Problem</option>
            <option>Projector Problem</option>
            <option>Door Problem</option>
            <option>Other</option>
        </select>

        <textarea name="description"
        placeholder="Describe the problem"></textarea>

        <button type="submit">Submit Complaint</button>
    </form>
    <a href="/admin">Admin Dashboard</a>
</div>
</body>
</html>
"""


ADMIN_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Admin Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: Arial;
            background: #eef2f7;
            padding: 15px;
        }
        .box {
            background: white;
            padding: 15px;
            border-radius: 10px;
            overflow-x: auto;
        }
        h2 {
            color: #174ea6;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            min-width: 650px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 10px;
            text-align: left;
        }
        th {
            background: #174ea6;
            color: white;
        }
        select, button {
            padding: 8px;
        }
        button {
            background: #174ea6;
            color: white;
            border: none;
        }
        a {
            display: block;
            margin-top: 20px;
        }
    </style>
</head>
<body>
<div class="box">
    <h2>Admin Complaint Dashboard</h2>

    <h3>Summary</h3>
    <p>Total: {{ total }} |
       Pending: {{ pending }} |
       In Progress: {{ progress }} |
       Fixed: {{ fixed }}</p>

    <table>
        <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Classroom</th>
            <th>Problem</th>
            <th>Description</th>
            <th>Status</th>
            <th>Update</th>
        </tr>

        {% for item in data %}
        <tr>
            <td>{{ item[0] }}</td>
            <td>{{ item[1] }}</td>
            <td>{{ item[2] }}</td>
            <td>{{ item[3] }}</td>
            <td>{{ item[4] }}</td>
            <td>{{ item[5] }}</td>
            <td>
                <form method="POST" action="/update">
                    <input type="hidden" name="id"
                    value="{{ item[0] }}">

                    <select name="status">
                        <option>Pending</option>
                        <option>In Progress</option>
                        <option>Fixed</option>
                    </select>

                    <button type="submit">Update</button>
                </form>
            </td>
        </tr>
        {% endfor %}
    </table>

    <a href="/">Back to Complaint Form</a>
</div>
</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HOME_PAGE)


@app.route("/submit", methods=["POST"])
def submit():
    name = request.form["name"]
    classroom = request.form["classroom"]
    problem = request.form["problem"]
    description = request.form.get("description", "")

    conn = sqlite3.connect(DATABASE)
    conn.execute(
        "INSERT INTO complaints "
        "(name, classroom, problem, description, status) "
        "VALUES (?, ?, ?, ?, ?)",
        (name, classroom, problem, description, "Pending")
    )
    conn.commit()
    conn.close()

    return """
    <h2>Complaint submitted successfully!</h2>
    <a href="/">Go Back</a>
    """


@app.route("/admin")
def admin():
    conn = sqlite3.connect(DATABASE)

    data = conn.execute(
        "SELECT id, name, classroom, problem, "
        "description, status FROM complaints ORDER BY id DESC"
    ).fetchall()

    conn.close()

    total = len(data)
    pending = sum(1 for item in data if item[5] == "Pending")
    progress = sum(1 for item in data if item[5] == "In Progress")
    fixed = sum(1 for item in data if item[5] == "Fixed")

    return render_template_string(
        ADMIN_PAGE,
        data=data,
        total=total,
        pending=pending,
        progress=progress,
        fixed=fixed
    )


@app.route("/update", methods=["POST"])
def update():
    complaint_id = request.form["id"]
    status = request.form["status"]

    if status not in ["Pending", "In Progress", "Fixed"]:
        return "Invalid status", 400

    conn = sqlite3.connect(DATABASE)
    conn.execute(
        "UPDATE complaints SET status=? WHERE id=?",
        (status, complaint_id)
    )
    conn.commit()
    conn.close()

    return redirect("/admin")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

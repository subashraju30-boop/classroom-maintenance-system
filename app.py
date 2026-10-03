from flask import Flask, request, redirect
import sqlite3

app = Flask(__name__)

def setup():
    con = sqlite3.connect("complaints.db")
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            classroom TEXT,
            problem TEXT,
            description TEXT
        )
    """)

    columns = [row[1] for row in cur.execute("PRAGMA table_info(complaints)")]

    if "status" not in columns:
        cur.execute("ALTER TABLE complaints ADD COLUMN status TEXT DEFAULT 'Pending'")

    con.commit()
    con.close()

setup()

@app.route("/", methods=["GET", "POST"])
def home():
    message = ""

    if request.method == "POST":
        name = request.form["name"]
        classroom = request.form["classroom"]
        problem = request.form["problem"]
        description = request.form["description"]

        con = sqlite3.connect("complaints.db")
        con.execute(
            "INSERT INTO complaints (name, classroom, problem, description, status) VALUES (?, ?, ?, ?, ?)",
            (name, classroom, problem, description, "Pending")
        )
        con.commit()
        con.close()

        message = "Complaint submitted successfully!"

    return """
    <html>
    <body style="font-family:Arial;max-width:600px;margin:40px auto">
        <h1>Classroom Maintenance</h1>

        <p style="color:green">""" + message + """</p>

        <form method="POST">
            <p>Student Name</p>
            <input name="name" required>

            <p>Classroom Number</p>
            <input name="classroom" required>

            <p>Problem Type</p>
            <select name="problem" required>
                <option>Fan</option>
                <option>Light</option>
                <option>Projector</option>
                <option>Bench</option>
                <option>Door</option>
                <option>Computer</option>
                <option>Other</option>
            </select>

            <p>Description</p>
            <textarea name="description" required></textarea>

            <br><br>
            <button type="submit">Submit Complaint</button>
        </form>

        <br>
        <a href="/admin">Open Admin Dashboard</a>
    </body>
    </html>
    """

@app.route("/admin")
def admin():
    con = sqlite3.connect("complaints.db")
    data = con.execute(
        "SELECT id, name, classroom, problem, description, status FROM complaints ORDER BY id DESC"
    ).fetchall()
    con.close()
total = len(data)
pending = sum(1 for item in data if item[5] == "Pending")
progress = sum(1 for item in data if item[5] == "In Progress")
fixed = sum(1 for item in data if item[5] == "Fixed")
summary = f"""
<h2>Summary</h2>
<p>Total: {total} | Pending: {pending} | In Progress: {progress} | Fixed: {fixed}</p>
"""

rows = ""

    for item in data:
        rows += f"""
        <tr>
            <td>{item[0]}</td>
            <td>{item[1]}</td>
            <td>{item[2]}</td>
            <td>{item[3]}</td>
            <td>{item[4]}</td>
            <td>{item[5]}</td>
            <td>
                <form method="POST" action="/update">
                    <input type="hidden" name="id" value="{item[0]}">

                    <select name="status">
                        <option>Pending</option>
                        <option>In Progress</option>
                        <option>Fixed</option>
                    </select>

                    <button type="submit">Update</button>
                </form>
            </td>
        </tr>
        """

    return """
    <html>
    <body style="font-family:Arial;margin:30px">

        <h1>Admin Complaint Dashboard</h1>

        <table border="1" cellpadding="10">
            <tr>
                <th>ID</th>
                <th>Student</th>
                <th>Classroom</th>
                <th>Problem</th>
                <th>Description</th>
                <th>Status</th>
                <th>Update</th>
            </tr>
    """ + rows + """
        </table>

        <br>
        <a href="/">Back to Complaint Form</a>

    </body>
    </html>
    """

@app.route("/update", methods=["POST"])
def update():
    complaint_id = request.form["id"]
    status = request.form["status"]

    con = sqlite3.connect("complaints.db")
    con.execute(
        "UPDATE complaints SET status = ? WHERE id = ?",
        (status, complaint_id)
    )
    con.commit()
    con.close()

    return redirect("/admin")

if __name__ == "__main__":
    app.run(debug=True)

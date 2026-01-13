from flask import Flask, render_template, request, session,redirect
import mysql.connector
import bcrypt
from datetime import date

app = Flask(__name__)
app.secret_key = "admin_secret_key" 
conn = mysql.connector.connect(
    host = "localhost",
    user = "worker",
    password = "atul@123",
    database = "attendance_db",
    # ssl_disabled=True
)

cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS admin(id INT AUTO_INCREMENT PRIMARY KEY,
username VARCHAR(20) UNIQUE,
phone_number VARCHAR(20) UNIQUE,
password VARCHAR(250),
name VARCHAR(50),
company_name VARCHAR(50),
GST_number VARCHAR(20)
)
""")

cur.execute(""" CREATE TABLE IF NOT EXISTS attendance (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(20),
        mobile_number VARCHAR(10),
        job_title VARCHAR(20),
        employee_id INT,
        date DATE,
        status VARCHAR(10),
        FOREIGN KEY (employee_id) REFERENCES employee(id)
    )""")

@app.route("/")
def login_page():
    return render_template("login.html")

@app.route("/login", methods=["POST", "GET"])
def login_submit():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        cur.execute("SELECT password FROM admin WHERE username = %s",(username,))
        admin = cur.fetchone()
        if not admin:
            return "user not found"
        stored_password = admin[0]
        if isinstance(stored_password, str):
            stored_password = stored_password.encode("utf-8")
            if bcrypt.checkpw(password.encode("utf-8"), stored_password):
                session["admin_user"] = username
    return render_template("employee_details.html")

        
@app.route("/register")
def register_page():
    return render_template("register.html")

@app.route("/register", methods=["POST", "GET"])
def register_home():
    if request.method == "POST":
        username = request.form.get("username")
        phone_number = request.form.get("phone_number")
        password = request.form.get("password")
        password1 = request.form.get("confirm_password")
        session["username"] = username
        if password == password1:
            hashed = bcrypt.hashpw(password.encode("utf-8"),bcrypt.gensalt())
            cur.execute("INSERT INTO admin(username,phone_number,password) VALUES (%s,%s,%s)",(username,phone_number,hashed))
            conn.commit()
        else:
            return "password dose not match"
    return render_template("form.html")
        
@app.route("/form")
def form_page():
    return render_template("form.html")

@app.route("/form" ,methods = ["POST","GET"])
def form_details():
    if request.method == "POST":
        name = request.form.get("name")
        company_name = request.form.get("company_name")
        gst_number = request.form.get("GST_number")
        username = session.get("username")
        cur.execute("UPDATE admin  SET name = %s," "company_name = %s," "GST_number = %s  WHERE username = %s",(name,company_name,gst_number,username))
        conn.commit()
    return render_template("login.html")

@app.route("/search_employee", methods=["GET", "POST"])
def search_employee_page():
    employee = None
    if request.method == "GET":
        name = request.args.get("name")
        if name:
            cur.execute("""
                SELECT name, mobile_number, addhar_number, account_number, ifsc_code, upi_id, job_title
                FROM employee WHERE name = %s
            """, (name,))
            employee = cur.fetchone()
    return render_template("search_employee.html", employee=employee)

@app.route("/all_employees" , methods = ["GET","POST"])
def all_employees():
    if request.method == "GET":
        cur.execute("SELECT id, name, mobile_number, addhar_number, account_number, ifsc_code, upi_id, job_title FROM employee")
        employees = cur.fetchall()
    return render_template("all_employees.html", employees=employees)



@app.route("/mark_attendance", methods=["POST","GET"])
def mark_attendance():
    if request.method == "POST":
        cur.execute("SELECT id, name,mobile_number,job_title FROM employee")
        employees = cur.fetchall()
        today = date.today()

        for emp in employees:
            emp_id = emp[0]
            emp_name = emp[1]
            emp_mobile = emp[2]
            emp_job = emp[3]
            
            
            status = request.form.get(f"attendance_{emp_id}")
            if status:
            # insert attendance record
                cur.execute("""
                            INSERT INTO attendance (employee_id,name,mobile_number,job_title, date, status)
                            VALUES (%s, %s, %s,%s,%s,%s)
                            """, (emp_id,emp_name,emp_mobile,emp_job, today, status))
                conn.commit()
        return render_template("mark_attendance.html", employees=employees)
                # return redirect("/all_employee")
    else:
        # GET request ke liye bhi kuch return hona chahiye
        cur.execute("SELECT id, name, mobile_number, job_title FROM employee")
        employees = cur.fetchall()
        return render_template("mark_attendance.html", employees=employees)
        









if __name__ == "__main__":
    app.run(debug=True)
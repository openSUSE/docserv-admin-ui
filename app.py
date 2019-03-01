from flask import Flask

# creating the app handler
app = Flask(__name__)

# basic routes
@app.route("/")
def startpage():
    return "This is the startpage of the DocServ Admin UI!"

@app.route("/server_config")
def server_config_page():
    return "This is the page for the server configuration."

@app.route("/documentation_config")
def doc_config_page():
    return "This is the page for the documentation config."

# let the app run when app.py is executed
if __name__ == "__main__":
    app.run()

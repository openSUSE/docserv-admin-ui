from flask import Flask
import ini_parse
import xmlconfig_algo

# creating the app handler
app = Flask(__name__)
# basic routes
@app.route("/")
def startpage():
    return "This is the startpage of the DocServ Admin UI!"

@app.route("/server_config")
def server_config_page():
    return str(ini_parse.get_docserv_config())
    return "This is the page for the server configuration."

@app.route("/documentation_config")
def doc_config_page():
    tree = xmlconfig_algo.get_tree()
    return str(xmlconfig_algo.get_xml_conf_dict(tree))
    return "This is the page for the documentation config."

# let the app run when app.py is executed
if __name__ == "__main__":
    app.run()

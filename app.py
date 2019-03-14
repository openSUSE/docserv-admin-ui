from flask import Flask, render_template
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
    docserv_config_dict = ini_parse.get_docserv_config()
    return render_template("buildserver_config.html", docserv_conf_dict=docserv_config_dict)

@app.route("/documentation_config")
def doc_config_page():
    tree = xmlconfig_algo.get_tree()
    return str(xmlconfig_algo.get_xml_conf_dict(tree))
    return "This is the page for the documentation config."

# let the app run when app.py is executed
if __name__ == "__main__":
    app.run()

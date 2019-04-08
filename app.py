from flask import Flask, render_template
import ini_parse
import xmlconfig_algo
import os
from lxml import etree

# creating the app handler
app = Flask(__name__)

# get the product names for every documentation
product_names = []
doc_config_dir = "docserv-config/config.d/"
for file in os.listdir(doc_config_dir):
    # parse the xml_file and get the actual shortname of the product
    try:
        file_tree = etree.parse(doc_config_dir+file)
        shortname = file_tree.xpath("./shortname")[0].text
        # add the product shortname to the list of productnames
        product_names.append(file_tree.xpath("./shortname")[0].text)
    except etree.XMLSyntaxError:
        print(f'{file} is no valid XML file.')

# basic routes
@app.route("/")
def startpage():
    buildserver_config_dict = ini_parse.get_docserv_config()
    return render_template("start_page.html", products=product_names, buildserver_config=buildserver_config_dict)

@app.route("/server_config")
def server_config_page():
    docserv_config_dict = ini_parse.get_docserv_config()
    return render_template("buildserver_config.html", docserv_conf_dict=docserv_config_dict)

@app.route("/documentation_config")
def doc_config_page():
    tree = xmlconfig_algo.get_tree()
    dict = xmlconfig_algo.get_xml_conf_dict(tree)
    return render_template("documentation_config.html", doc_dict=dict)

# route for every product
@app.route('/<name>')
def shortname_page(name):
        if name.upper() in product_names:
            return 'Hello, this is a page for {}'.format(name)
        else:
            return "No page for product {} found.".format(name)


# let the app run when app.py is executed
if __name__ == "__main__":
    app.run()

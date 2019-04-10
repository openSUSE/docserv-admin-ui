from flask import Flask, render_template
import ini_parse
import xmlconfig_algo
import os
from lxml import etree
import sys
import config

# creating the app handler
app = Flask(__name__)

# get the product names for every documentation
product_names = []
for file in os.listdir(config.product_xml_dir):
    # parse the xml_file and get the actual shortname of the product
    try:
        file_tree = etree.parse(config.product_xml_dir+file)
        shortname = file_tree.xpath("./shortname")[0].text #remove './'
        # add the product shortname to the list of productnames
        product_names.append(file_tree.xpath("./shortname")[0].text.lower())
    except etree.XMLSyntaxError:
        print(f'{file} is no valid XML file.')

# basic routes
@app.route("/")
def startpage():
    buildserver_config_dict = ini_parse.get_docserv_config()
    return render_template("start_page.html", products=product_names, buildserver_config=buildserver_config_dict)

@app.route("/documentation_config")
def doc_config_page():
    tree = xmlconfig_algo.get_tree()
    dict = xmlconfig_algo.get_xml_conf_dict(tree)
    return render_template("documentation_config.html", doc_dict=dict, products=product_names)

# route for every product
@app.route('/<name>')
def shortname_page(name):
        if name.lower() in product_names:
            product_tree = xmlconfig_algo.get_tree(name)
            product_dict = xmlconfig_algo.get_xml_conf_dict(product_tree)
            return render_template("documentation_config.html", doc_dict=product_dict, products=product_names)
        else:
            return render_template("error_message.html", products=product_names, product_name=name)

@app.route('/<name>-<version>')
def shortname_version_page(name, version):
   product_tree = xmlconfig_algo.get_tree(name)
   product_dict = xmlconfig_algo.get_xml_conf_dict(product_tree)
   return "hello world!"

# let the app run when app.py is executed
if __name__ == "__main__":
    app.run()

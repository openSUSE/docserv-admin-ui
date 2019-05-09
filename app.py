from flask import Flask, render_template, redirect, url_for
import ini_parse
import xmlconfig_algo
import os
from lxml import etree
import sys
import config
from pprint import *
import pycurl
import json
import time
import requests


# creating the app handler
app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.do')

# get the product names for every documentation
product_names = []
for file in os.listdir(config.product_xml_dir):
    # parse the xml_file and get the actual shortname of the product
    if file.endswith('.xml'):
        try:
            file_tree = etree.parse(config.product_xml_dir+file)
            shortname = file_tree.xpath("./shortname")[0].text #remove './'
            # add the product shortname to the list of productnames
            product_names.append(file_tree.xpath("./shortname")[0].text.lower())
        except etree.XMLSyntaxError:
            print(f'{file} is no valid XML file.')
    else:
        continue

# basic routes
@app.route("/")
def startpage():
    buildserver_config_dict = ini_parse.get_docserv_config()
    return render_template("start_page.html", products=product_names, buildserver_config=buildserver_config_dict)

@app.route("/documentation_config")
def doc_config_page():
    tree = xmlconfig_algo.get_tree()
    xml_dict = xmlconfig_algo.get_xml_conf_dict(tree)
    prname = xml_dict['productname']
    maintainers = xml_dict['maintainers']
    for version in doc_dict['docsets']:
        version_list.append(version)

    return render_template(
        "documentation_config.html",
        productname=prname,
        maint_list=maintainers,
        doc_dict=xml_dict,
        products=product_names,
        ver_list = version_list)

# route for every product
@app.route('/<name>')
def shortname_page(name):
        if name.lower() in product_names:
            try:
                product_tree = xmlconfig_algo.get_tree(name)
                xml_dict = xmlconfig_algo.get_xml_conf_dict(product_tree)
                version_list = []
                for version in xml_dict['docsets']:
                    version_list.append(version)
                return render_template(
                    "documentation_config.html",
                    doc_dict=xml_dict,
                    products=product_names,
                    prname = xml_dict['productname'],
                    maint_list = xml_dict['maintainers'],
                    ver_list = version_list,
                    shortname = xml_dict['shortname'])
            except FileNotFoundError:
                return render_template("error_message.html", products=product_names, product_name=name)

@app.route('/<name>-<major_version>')
def shortname_major_version_page(name, major_version):
    product_tree = xmlconfig_algo.get_tree(name)
    product_dict = xmlconfig_algo.get_xml_conf_dict(product_tree)
    for version in product_dict['docsets']:
        if major_version in product_dict['docsets'][version]['major_version']:
            return render_template(
                "major_version.html",
                products=product_names,
                doc_dict=product_dict,
                mv=major_version,
                shortname=product_dict['shortname'].lower())

@app.route('/<name>-<major_version>-<minor_version>')
def shortname_major_minor_version_page(name, major_version, minor_version):
   product_tree = xmlconfig_algo.get_tree(name)
   product_dict = xmlconfig_algo.get_xml_conf_dict(product_tree)
   for version in product_dict['docsets']:
        if major_version in product_dict['docsets'][version]['major_version']:
            if minor_version in product_dict['docsets'][version]['minor_version']:
                return render_template(
                "major_minor_version.html",
                doc_dict=product_dict,
                products=product_names,
                product_name=product_dict['productname'],
                git_url=product_dict['docsets'][version]['git_url'],
                lifecycle=product_dict['docsets'][version]['lifecycle'],
                product_version=version,
                shortname=product_dict['shortname'],
                docset=product_dict['docsets'][version],
                major=major_version,
                minor=minor_version)

# send the curl command to build the documentation
@app.route('/build_docset/<name>/<major>/<minor>/<lang>')
def build_docset(name, major, minor, lang):
    product_tree = xmlconfig_algo.get_tree(name)
    product_dict = xmlconfig_algo.get_xml_conf_dict(product_tree)
    for version in product_dict['docsets']:
        if major in product_dict['docsets'][version]['major_version']:
            if minor in product_dict['docsets'][version]['minor_version']:

                # build docset dictionary for building
                docset_dict = {}
                docset_dict["lang"] = lang
                docset_dict["product"] = product_dict['shortname'].lower()
                docset_dict["target"] = "test"
                docset_dict["docset"] = product_dict['docsets'][version]['setid']
                docset_list = [docset_dict]
                new_docset_list = str(docset_list).replace("'", "\"")

                # create curl command and try to send it to DocServ
                try:
                    c = pycurl.Curl()
                    c.setopt(pycurl.URL, config.docserv_instance_adress)
                    c.setopt(pycurl.HTTPHEADER, ['Accept: application/json'])
                    c.setopt(pycurl.POSTFIELDS, new_docset_list)
                    c.setopt(pycurl.POST, 1)
                    c.setopt(pycurl.VERBOSE, 1)
                    c.perform()
                    print(pycurl.RESPONSE_CODE)
                    c.close()
                except pycurl.error as err:
                    return f"POST Request failed. {err}"
                return redirect(url_for('show_queue'))

@app.route('/queue')
def show_queue():
    building = []
    fail = []
    success = []
    try:
        while(True):
            # fetch the JSON data from DocServ
            r = requests.get(config.docserv_instance_adress)
            data = r.json()

            # fill the status lists
            for x in data[0]['deliverables']:
                if data[0]['deliverables'][x]['status'] == 'building':
                    building.append({
                        'dc': data[0]['deliverables'][x]['dc'],
                        'status': data[0]['deliverables'][x]['status'],
                        'format': data[0]['deliverables'][x]['build_format'],
                        'title': data[0]['deliverables'][x]['title']})
                if data[0]['deliverables'][x]['status'] == 'fail':
                    fail.append({
                        'dc': data[0]['deliverables'][x]['dc'],
                        'status': data[0]['deliverables'][x]['status'],
                        'format': data[0]['deliverables'][x]['build_format'],
                        'title': data[0]['deliverables'][x]['title']})
                if data[0]['deliverables'][x]['status'] == 'success':
                    success.append({
                        'dc': data[0]['deliverables'][x]['dc'],
                        'status': data[0]['deliverables'][x]['status'],
                        'format': data[0]['deliverables'][x]['build_format'],
                        'title': data[0]['deliverables'][x]['title']})

            # render the queue page with the status data
            return render_template(
                "/build_queue.html",
                building=building,
                fail=fail,
                success=success,
                products=product_names)

            time.sleep(30)
    except requests.ConnectionError:
        return "No JSON file from DocServ available. Make sure that DocServ is running.."

# let the app run when app.py is executed
if __name__ == "__main__":
    app.run()

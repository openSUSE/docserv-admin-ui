from lxml import etree
import config

# open XML file and get the tree
def get_tree(name):
    name = name.lower()
    xml_file = open(config.product_xml_dir + f'{name}.xml', 'r')
    config_tree = etree.parse(xml_file)
    return config_tree

def get_xml_conf_dict(tree):
    xml_conf_dict = {}

    #get shortname
    xml_conf_dict['shortname'] = tree.xpath('/product/shortname')[0].text

    # get product name
    xml_conf_dict['productname'] = tree.xpath('/product/name')[0].text

    # get maintainer(s)
    maintainers_list = []
    for person in tree.xpath('/product/maintainers/contact'):
        maintainers_list.append(person.text)
    xml_conf_dict['maintainers'] = maintainers_list

    # get descriptions
    desc_dict = {}
    for description in tree.xpath('/product/desc'):
        lang_text = description.attrib['lang']
        desc_dict[lang_text] = {}
        desc_dict[lang_text]['desc_text'] = description.xpath('./p')[0].text
        # check if language is the default language
        if 'default' in description.attrib:
            desc_dict[lang_text]['default'] = True
    xml_conf_dict['descriptions'] = desc_dict

    # get docsets
    docset_dict = {}
    for docset in tree.xpath('/product/docset'):
        # get version
        version = docset[0].text
        docset_dict[version] = {}


        # get major version
        major_version = docset[0].text[:2]
        docset_dict[version]['major_version'] = major_version

        # get minor version
        minor_version = docset[0].text.replace(' ','')[2:]
        docset_dict[version]['minor_version'] = minor_version

        # get lifecycle
        docset_dict[version]['lifecycle'] = docset.attrib['lifecycle']

        # get setid
        docset_dict[version]['setid'] = docset.attrib['setid']

        # get git remote url
        git_obj = docset.xpath('./builddocs/git')[0]
        git_url = git_obj.attrib['remote']
        docset_dict[version]['git_url'] = git_url

        # get docset languages
        docset_lang_dict = {}
        for lang in docset.xpath('./builddocs/language'):
            lang_string = lang.attrib['lang']
            docset_lang_dict[lang_string] = {}

            # get the branch
            docset_lang_dict[lang_string]['branch'] = lang.xpath('./branch')[0].text

            # create a dictionary for the deliverables:
            deliv_dict = {}
            for deliv in lang.xpath('./deliverable'):
                dc_name = deliv.xpath('./dc')[0].text
                deliv_dict[dc_name] = {}

                # get all available formats for the deliverable
                format_list = []
                for format in deliv.xpath('./format')[0].attrib:
                    if deliv.xpath('./format')[0].attrib[format] == '1':
                        format_list.append(format)
                deliv_dict[dc_name]['formats'] = format_list

                # get all subdeliverables
                subdeliv_list = []
                for child_elem in deliv:
                    if child_elem.tag == 'subdeliverable':
                        subdeliv_list.append(child_elem.text)
                    deliv_dict[dc_name]['subdeliverables'] = subdeliv_list

            # put the deliverable dictionary into the docset language dictionary
            docset_lang_dict[lang_string]['deliverable'] = deliv_dict

        docset_dict[version]['language'] = docset_lang_dict

    # put the docset dictionary in the xml config dictionary
    xml_conf_dict['docsets'] = docset_dict

    # return the xml config dictionary
    return xml_conf_dict


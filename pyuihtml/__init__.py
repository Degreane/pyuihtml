import logging
from lxml import etree, html
import sys


class pyuixml(object):
    '''
    pyuixml:
        Base class to manipulate xml-ui file

    params:
        InUiFile  : Input ui-xml file to read data from
        OutUiFile : Output Html file to write to
        LogFile   : Log file to stash debug/info/warning/and errors to

    '''

    def __init__(self, InUiFile: str, OutUiFile: str, LogFile: logging.Logger):
        super(pyuixml, self).__init__()
        self.InUiFile = InUiFile
        self.OutHtmlFile = OutUiFile

        self.Logger = LogFile
        self.__initialize_html()
        self.tagWorker = {
            'ui': self.__parse_ui,
            'class': self.__parse_class,
            'widget': self.__parse_widget,
            'property': self.__parse_pass,
            'x': self.__parse_pass,
            'y': self.__parse_pass,
            'rect': self.__parse_pass,
            'width': self.__parse_pass,
            'height': self.__parse_pass,
            'size': self.__parse_pass,
            'string': self.__parse_pass,
            'spacer': self.__parse_pass,
            'layout': self.__parse_layout,
            'item': self.__parse_item
        }

        self.__read_uiFile()
        self.__loop_over_xml_data(self.xmltree)
        self.Logger.info('[0] {0}'.format(html.tostring(self.__html)))

    def __parse_pass(self, xmlObj):
        pass

    def __parse_layout(self, xmlObj):
        '''

        Logger [9]
        - get the parent
        - get the parent id
        - get the html_document with the parent_id
        - get max rows
        - get max cols
        - create element of class xmlObj.get('class')
        - set element id of xmlObj.get('name')
        - set element x-data-maxcols=max_cols
        - set element x-data-maxrows=max_rows
        - loop over from 0 to maxrow +1
            - loop over from 0 to maxcol +1
                add element of type div with id of objXml.get('name')_row{x}_col{y}
                class item empty-item
        - add element to its parent

        '''
        element_parent = xmlObj.getparent()
        if etree.iselement(element_parent):
            element_parent_id = element_parent.get('name')
            html_doc_fragment = self.__html.xpath('//*[@id="{0}"]'.format(element_parent_id))
            if len(html_doc_fragment) > 0:
                html_doc_fragment = html_doc_fragment[0]
                max_rows = 0
                max_cols = 0
                for item in xmlObj.findall('item'):
                    row = int(item.get('row'))
                    col = int(item.get('column'))
                    if col > max_cols:
                        max_cols = col
                    if row > max_rows:
                        max_rows = row
                html_element = html.Element('div')
                html_element.set('class', xmlObj.get('class'))
                html_element.set('id', xmlObj.get('name'))
                html_element.set('x-data-name', xmlObj.get('name'))
                html_element.set('x-data-maxcols', str(max_cols))
                html_element.set('x-data-maxrows', str(max_rows))
                for row in range(max_rows + 1):
                    for col in range(max_cols + 1):
                        item_element = html.Element('div')
                        item_element.set('id', "{0}_row{1}_col{2}".format(xmlObj.get('name'), row, col))
                        item_element.set('class', 'item item-empty')
                        html_element.append(item_element)
                        print(row, 'x', col)
                print(html.tostring(html_element))
                html_doc_fragment.append(html_element)
                self.Logger.info('[9] Added Layout {0}'.format(html.tostring(html_element)))

    def __parse_item(self, xmlObj):
        """
        Logger [10]
        - get parent
        - get parent name (the id in the html version)
        - get html_doc_fragment corresponding to id of parent_name
        - get item attribs xmlObj.attrib {}
        - extract row/column/rowspan from xmlObj.attrib
        """
        element_parent = xmlObj.getparent()
        if etree.iselement(element_parent):
            element_parent_name = element_parent.get('name')
            print(element_parent, element_parent_name)
            html_doc_fragment = self.__html.xpath('//*[@id="{0}"]'.format(element_parent_name))
            print('HTML DOC FRAGMENT ', html_doc_fragment)

            item_elem_id = [element_parent_name]
            if len(html_doc_fragment) > 0:
                html_doc_fragment = html_doc_fragment[0]
                element_attribs = xmlObj.attrib
                if 'row' in element_attribs:
                    item_elem_id.append('row{0}'.format(xmlObj.get('row')))
                if 'column' in element_attribs:
                    item_elem_id.append('col{0}'.format(xmlObj.get('column')))
                element_name = '_'.join(item_elem_id)
                print('item name is ', element_name)
                html_element = html_doc_fragment.find('div[@id="{0}"]'.format(element_name))
                print('html element is ', html_element)
                if etree.iselement(html_element):
                    if 'colspan' in element_attribs:
                        html_element.set('colspan', xmlObj.get('colspan'))
                    if 'rowspan' in element_attribs:
                        html_element.set('rowspan', xmlObj.get('rowspan'))
                    xmlObj.set('name', element_name)
                    html_element.set('id', element_name)
                    html_element.set('x-data-name', element_name)
                    html_element.set('class', 'item')
                    # html_doc_fragment.append(html_element)
                    self.Logger.info('[10] Parsed Item {0}'.format(html.tostring(html_element)))

    def __parse_ui(self, uiObj):
        '''
        :param uiObj:
        :return:
        :description:
        With UI we have version
        so its a Meta Tag
        Logger [6]
        '''
        version = uiObj.get('version')
        theHead = self.__html.find('head')
        theMeta = html.Element('meta')
        theMeta.set('name', 'version')
        theMeta.set('content', "{}".format(version))
        theHead.append(theMeta)
        self.Logger.info('[6] parsed Meta Tag {0} with {1}'.format(uiObj.tag, html.tostring(theMeta, encoding="utf-8")))
        # self.Logger.debug(html.tostring(self.__html, encoding="utf-8"))

    def __parse_class(self, xmlObj):
        '''
        Here we work with the class
        1- get the parent
        2- if parent.tag is ui then we add class of xmlObj.text to the body
        :param xmlObj:
        :return:
        Logger [7]
        '''
        xmlObjParent = xmlObj.getparent()
        if etree.iselement(xmlObjParent) and xmlObjParent.tag == 'ui':
            theBody = self.__html.find('body')
            if etree.iselement(theBody):
                theBody.set('class', xmlObj.text)
                self.Logger.info("[7] parsed body class {0}".format(html.tostring(theBody, encoding="utf-8")))

    def __parse_widget(self, xmlObj):
        '''
        Logger [8]

        :param xmlObj:
        :return:
        '''
        widgetClass = xmlObj.get('class')
        widgetparent = xmlObj.getparent()
        if widgetClass == 'QMainWindow':
            '''
            1- get the class of the widget
            2- check if  widget class is QMainWindow
            3- get the parent of the widget
            4- check if parent.tag is ui
                if all above meets the criteria then
                check <property name="windowTitle"> and get child[0].text
                set the page title to child[0].text
            '''
            if etree.iselement(widgetparent):
                if widgetparent.tag == "ui":
                    title = xmlObj.find('property[@name="windowTitle"]')
                    if etree.iselement(title):
                        content = str(title[0].text)
                        # print("content is {0}".format(content))
                        # help(self.__html)
                        the_title = self.__html.xpath("//title")[0]
                        if etree.iselement(the_title):
                            the_title.text = content
                            self.Logger.info("[8] parsed Title  {0}".format(html.tostring(the_title, encoding="utf-8")))
        elif widgetClass == 'QWidget':
            '''
            - get the parent of the widget
            - get parent name (should be the id of the parent)
            - get parent class
            - if parent.widgetClass == QMainWindow then we append to the body of the Html
            - get the body tag of the document
            - create element of type div
            - set the element.class to QWidget
            - set the element.id to xmlObj.get('name')
            - set the element.x-data-name to xmlObj.get('name')
            - append element to html_doc
            '''
            element_parent = xmlObj.getparent()
            if etree.iselement(element_parent):
                # element_parent_name = element_parent.get('name')
                element_parent_class = element_parent.get('class')
                if element_parent_class == 'QMainWindow':
                    html_doc_fragment = self.__html.xpath('//body')
                    if len(html_doc_fragment) > 0:
                        html_doc_fragment = html_doc_fragment[0]
                        html_element = html.Element('div')
                        html_element.set('class', 'QWidget')
                        html_element.set('id', xmlObj.get('name'))
                        html_element.set('x-data-name', xmlObj.get('name'))
                        html_doc_fragment.append(html_element)
                        self.Logger.info('[8] parsed body div {0}'.format(html.tostring(html_element)))

    def __read_uiFile(self):
        with open(self.InUiFile, mode='r') as fd:
            data = fd.read()
            data = data.encode(encoding='utf-8')
            self.xml = data
            self.Logger.info("[2] XML Data Read Successfully")
            try:
                self.xmltree = etree.fromstring(self.xml)
                self.Logger.info("[2] XML Data parsed OK")
            except Exception as Ex:
                self.Logger.error(
                    "[2] Error Encountered Parsing xml Data \n\t\t{0}".format(Ex))
                sys.exit(1)

    def __loop_over_xml_data(self, XmlObj: etree):
        '''
        :param XmlObj: Object of type lxml.etree to iterate over if it has children
        :return:
        Logger [3]
        '''
        # self.Logger.debug("[3] {0}".format(XmlObj.tag))
        self.__parse_current_obj(XmlObj)
        for tag in XmlObj:
            self.__loop_over_xml_data(tag)

    def __initialize_html(self):
        '''
        Initialize Empty Html Template

        Logger [4]
        :return:
        '''

        empty_html_template = '''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/><meta name="language" content="english"/><meta http-equiv="content-type" content="text/html"/><meta name="author" content="Faysal Al-Banna"/><meta name="designer" content="Faysal Al-Banna"/><meta name="publisher" content="Faysal Al-Banna"/><meta name="viewport" content="width=device-width, initial-scale=1.0"/><meta http-equiv="X-UA-Compatible" content="chrome=1"/><meta http-equiv="content-type" content="text/html;charset=UTF-8" /><meta http-equiv="content-language" content="en-us" /><meta http-equiv="cache-control" content="no-cache" /><meta http-equiv="pragma" content="no-cache" /><title></title></head><body></body></html>'''
        self.__html = html.fromstring(empty_html_template)
        self.Logger.info("[4] Initialized Empty HTML Template OK")

    def __parse_current_obj(self, tag):
        '''
        Logger [5]
        Check the current obj tag and parse accordingly
        :param tag: tag object to be inspected.
        :return:
        '''
        # print(tag.tag)
        if tag.tag in self.tagWorker:
            self.Logger.info('[5] Parsing Tag {0}'.format(tag.tag))
            self.tagWorker[tag.tag](tag)
        else:
            self.Logger.warning('[5] Unknown Tag {0}'.format(tag.tag))

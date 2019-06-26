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
            'class':self.__parse_class,
            'widget':self.__parse_widget
        }


        self.__read_uiFile()
        self.__loop_over_xml_data(self.xmltree)
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
        self.Logger.info('[6] parsed Meta Tag {0} with {1}'.format(uiObj.tag,html.tostring(theMeta,encoding="utf-8")))
        # self.Logger.debug(html.tostring(self.__html, encoding="utf-8"))

    def __parse_class(self,xmlObj):
        '''
        Here we work with the class
        1- get the parent
        2- if parent.tag is ui then we add class of xmlObj.text to the body
        :param xmlObj:
        :return:
        Logger [7]
        '''
        xmlObjParent=xmlObj.getparent()
        if etree.iselement(xmlObjParent) and xmlObjParent.tag == 'ui':
            theBody=self.__html.find('body')
            if etree.iselement(theBody):
                theBody.set('class',xmlObj.text)
                self.Logger.info("[7] parsed body class {0}".format(html.tostring(theBody,encoding="utf-8")))
    def __parse_widget(self,xmlObj):
        '''
        Logger [8]

        :param xmlObj:
        :return:
        '''
        widgetClass=xmlObj.get('class')
        widgetparent=xmlObj.getparent()
        if widgetClass=='QMainWindow':
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
                    title=xmlObj.find('property[@name="windowTitle"]')
                    if etree.iselement(title):
                        content=str(title[0].text)
                        # print("content is {0}".format(content))
                        # help(self.__html)
                        the_title=self.__html.xpath("//title")[0]
                        if etree.iselement(the_title):
                            the_title.text=content
                            self.Logger.info("[8] parsed Title  {0}".format(html.tostring(the_title, encoding="utf-8")))
        elif widgetClass == 'QWidget':
            '''
            1- get the parent of the widget 
            2- if parent.widgetClass == QMainWindow then we append to the body of the Html 
            
            '''
            pass
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

        empty_html_template = '''
           <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="utf-8"/>
                <meta name="language" content="english"/> 
                <meta http-equiv="content-type" content="text/html"/>
                <meta name="author" content="Faysal Al-Banna"/>
                <meta name="designer" content="Faysal Al-Banna"/>
                <meta name="publisher" content="Faysal Al-Banna"/>
                <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
                <meta http-equiv="X-UA-Compatible" content="chrome=1"/>
                <meta http-equiv="content-type" content="text/html;charset=UTF-8" />
                <meta http-equiv="content-language" content="en-us" />
                <meta http-equiv="cache-control" content="no-cache" />
                <meta http-equiv="pragma" content="no-cache" />
                <title></title>
            </head>
            <body>
            </body>
            </html>        
        '''
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

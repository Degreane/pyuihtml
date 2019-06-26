'''
PyUiHtml
========

Description:
------------

Python package to read ui-xml files generated with QtDesigner/QtCreator
and transfers it to HTML mostly compatible with ie7+
trying to bring the fun of python programming to real live visual sense ;)

Author:
-------

Faysal AL-Banna
Chief Section for ground observation
Lebanese Meteorological Department
degreane@gmail.com
00961-03-258043

Usage:
-----

python3 -m pyuihtml -IF=<InputFile .ui> [-OF=<OutputFile.html>]



'''

import argparse
import sys
import logging


def setup_logger(logfile):
    with open(logfile,mode="a+") as fd:
        fd.write("\n")
    logger = logging.getLogger('pyuihtml')
    logger.setLevel(logging.DEBUG)
    logHandler=logging.FileHandler(logfile,mode='a')
    formatter=logging.Formatter('%(asctime)s ~ %(levelname)s ~ %(message)s')
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
    return logger
def parse_cl():
    parser=argparse.ArgumentParser('pyuihtml')
    parser.add_argument('IF',type=str,help="Input File EX: -IF=Page1.ui.xml")
    parser.add_argument('OF',type=str,help="Output File [Optional] Ex: -OF=Page1.html",nargs="?",default=sys.stdout)
    parsed_args=parser.parse_args()
    if parsed_args is not None:
        InputFile=str(parsed_args.IF).split('=')[1]
        OutputFile=parsed_args.OF
        if(type(OutputFile) == type(sys.stdout)):
            return (InputFile,OutputFile)
        else:
            return (InputFile,OutputFile.split('=')[1])
    else:
        return None


InOutFiles=parse_cl()
if InOutFiles is not None:
    InFile=InOutFiles[0]
    OutFile=InOutFiles[1]
    logger=setup_logger('{0}.log'.format(InFile))
    logger.info("[1] PyUiHtml started ")
    import os
    if os.path.exists(InFile):
        import pyuihtml
        html=pyuihtml.pyuixml(InFile,OutFile,logger)
    else:
        raise Exception("File Does Not Exist")


#!/usr/bin/python
#
# MIT License
# 
# Copyright (c) 2017 Diogo Montagner
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Version........: 1.0
# Platform.......: agnostic
# Description....: Simple example of configuration collection and parsing
#


import logging
import sys
import datetime
import pprint
import json
from jnpr.junos import Device
from lxml import etree
from collections import defaultdict
from netaddr import *


# setting logging capabilities
log = logging.getLogger() # 'root' Logger
console = logging.StreamHandler()
format_str = '%(asctime)s\t%(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s'
console.setFormatter(logging.Formatter(format_str))
log.addHandler(console) # prints to console.

# set the log level here
#log.setLevel(logging.WARN)
log.setLevel(logging.ERROR)


#
# This method collects the configuration from the router
#
# Returns the the filename where the configuration was stored
#
def getConfigurationFromRouter(dev, rtName, format):

    log.debug("entered getConfigurationFromRouter")
    cnf = None
    FileName = None

    if dev is None:
        return None

    try:
        log.debug("collecting the router configuration")

        now = datetime.datetime.now()
        datets = str(now.year) + str(now.month) + str(now.day) + "_" + str(now.hour) + str(now.minute) + str(now.second)
        log.debug("timestamp set to " + str(datets))

        if (format == "cnf"):
            cnf = dev.cli("show configuration", warning=False)
            FileName = rtName + "." + datets + ".cnf"
            log.debug("The configuration will be stored in filename as %s", FileName)

            # saving the configuration into a CNF file
            f = open(FileName, 'w+')
            f.write(cnf)
            f.close
            return FileName

        elif (format == "set"):
            cnf = dev.cli("show configuration | display set", warning=False)
            FileName = rtName + "." + datets + ".set"
            log.debug("The configuration will be stored in filename as %s", FileName)
            # saving the configuration into a SET file
            f = open(FileName, 'w+')
            f.write(cnf)
            f.close
            return FileName

        else: # defaults to XML
            cnf = dev.rpc.get_config()
            FileName = rtName + "." + datets + ".xml"
            log.warn("The configuration will be stored in filename as %s", FileName)

            # saving the configuration into a XML file
            f = open(FileName, 'w+')
            f.write(etree.tostring(cnf))
            f.close
            return FileName

    except Exception as e:
        log.error("could not collect the router configuration via RPC")
        log.error(e.message)
        return None


    # if the execution gets here, the return will be None
    return FileName


def main():

    routers = {'PE0':'10.1.1.0', 'PE1':'10.1.1.1', 'PE2':'10.1.1.2', 'PE3':'10.1.1.3', 'P0':'10.1.0.0', 'P1':'10.1.0.1', 'P2':'10.1.0.2', 'P3':'10.1.0.3', 'P4':'10.1.0.4', 'P5':'10.1.0.5'}

    #
    rtUser = "root"
    rtPassword = "root123"

    print("")
    print("")

    # iterating through all routers
    for rtName in routers:
        rtIP = routers[rtName]
        print "Connecting to router " + rtName + " ( " + rtIP + " )"

        try:
            dev = Device(host=rtIP, user=rtUser, password=rtPassword, gather_facts=False)
            dev.open()
            print "    - connected to router " + rtName + " ( " + rtIP + " )"

        except Exception as e:
            log.error("could not connect to the router %s", rtName)
            log.error(e.message)
            exit(-1)

        # collects the configuration in XML format
        print "    - collecting configuration in XML format from router " + rtName
        xmlConfig = getConfigurationFromRouter(dev, rtName, "xml")
        if xmlConfig is not None:
            print "    - configuration has been stored on file " + xmlConfig

        # collects the configuration in SET format
        print "    - collecting configuration in SET format from router " + rtName
        setConfig = getConfigurationFromRouter(dev, rtName, "set")
        if setConfig is not None:
            print "    - configuration has been stored on file " + setConfig

        # collects the configuration in CNF format
        print "    - collecting configuration in CNF format from router " + rtName
        cnfConfig = getConfigurationFromRouter(dev, rtName, "cnf")
        if cnfConfig is not None:
            print "    - configuration has been stored on file " + cnfConfig

        try:
            # closing the router connection
            print "    - closing connection with router " + rtName
            dev.close()

        except Exception as e:
            log.error("could not close the connection with router " + rtName)
            log.error(e.message)


if __name__ == '__main__':
    main()

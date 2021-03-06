import subprocess
import xml.etree.ElementTree as ET
from shutil import copyfile
import os.path
from os.path import isfile, join
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import Files_and_Constants as fc



def create_xml_config_file(config_folder, params, numThreads, config_sample_folder):
    '''
    This function creates mqpar.xml file so the MaxQuant program can get all the params it needs
    '''

    sample_config = os.path.join(config_sample_folder , 'mqpar_template.xml')
    config_file = os.path.join(config_folder , 'mqpar.xml')

    tree = ET.parse(sample_config)
    root = tree.getroot()

    # raw files
    rawFilesobj = root.find('filePaths')
    rawFilesobj2 = rawFilesobj.findall('string')
    experiments = root.find('experiments')
    experiments2 = experiments.findall('string')
    for file_name, exp_name, i in zip([params[0], params[1], params[2]], ['a', 'b', 'c'], [0, 1, 2]):
         create_raw_file(file_name, rawFilesobj2, exp_name, experiments2, i)

    #db files
    fasta_db = root.find('fastaFiles')
    db_files = [join(params[3], file) for file in os.listdir(params[3])]
    for file in db_files:
        create_fasta_db_file(file, fasta_db)
    indent(fasta_db)

    #directories for output
    create_directories(params[5], root)

    #Label-free quantification params
    root.find('parameterGroups/parameterGroup/lfqMode').text = '1'
    root.find('parameterGroups/parameterGroup/fastLfq').text = 'False'
    root.find('parameterGroups/parameterGroup/lfqMinRatioCount').text = '2'

    #other params:
    root.find('parameterGroups/parameterGroup/enzymes/string').text = params[4]
    root.find('numThreads').text = str(numThreads)
    root.find('maxQuantVersion').text = fc.maxquant_version

    root.find('matchBetweenRuns').text = 'True'
    root.find('matchBetweenRunsFdr').text = 'False'
    root.find('matchingTimeWindow').text = '0.7'
    root.find('alignmentTimeWindow').text = '0'


    tree.write(config_file)


def create_raw_file(file_name, rawFilesobj, exp_name, experiments, i):
        rawFilesobj[i].text = file_name
        experiments[i].text = exp_name


def create_fasta_db_file(fasta_file, fasta_db):
    fastaFileInfo = ET.SubElement(fasta_db, "FastaFileInfo")
    d1 = ET.SubElement(fastaFileInfo, "fastaFilePath")
    d1.text = fasta_file
    d2 = ET.SubElement(fastaFileInfo, "identifierParseRule")
    d2.text = '([^\s]*)'
    d3 = ET.SubElement(fastaFileInfo, "descriptionParseRule")
    d3.text = "(.*)"
    d4 = ET.SubElement(fastaFileInfo, "taxonomyParseRule")
    d4.text = ""
    d5 = ET.SubElement(fastaFileInfo, "variationParseRule")
    d5.text = ""
    d6 = ET.SubElement(fastaFileInfo, "modificationParseRule")
    d6.text = ""
    d7 = ET.SubElement(fastaFileInfo, "taxonomyId")
    d7.text = ""
    ET.dump(fasta_db)


def create_directories(directory, root):
    root.find('fixedCombinedFolder').text = directory


def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def running_maxquant_through_cmd (config_path):
    config_file = os.path.join(config_path , 'mqpar.xml')
    subprocess.run(['mono', fc.maxquant_exe_path, config_file])



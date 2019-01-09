import logging
import argparse
import FilterExcelFile as fe
import DB_analysis as dbf
import Statistics_and_Plots as sp
import pickle
import os
import MaxQuantRun as mq
from Files_and_Contants import *
import Utilities as util
import html_editor as he
import sys
sys.path.append('cgi/')
sys.path.append('/bioseq/PASA/cgi/')
sys.path.append('/bioseq/bioSequence_scripts_and_constants/')
import WEBSERVER_CONSTANTS as CONSTS

try:
    file = open(logs + 'main.log', 'r')
except IOError:
    file = open(logs + 'main.log', 'w')
logging.basicConfig(filename=logs + 'main.log',level=logging.DEBUG)
logging.debug('This message should go to the log file')


if __name__ == '__main__':

    html_path =  os.path.join(wd, 'output.html')
    run_number = wd.split('/')[-2]



    try:
        print("running maxquant (elution)\n")
        logging.info("running maxquant (elution)")
        params_e = [raw_files_e_1,raw_files_e_2, raw_files_e_3, db_folder, enzyme, path_input_e]
        mq.create_xml_config_file(config_folder_e, params_e, numThreads, config_sample_folder)
        mq.running_maxquant_through_cmd(config_folder_e)

        print("running maxquant (flowthrough)\n")
        logging.info("running maxquant (flowthrough)")
        params_f = [raw_files_f_1,raw_files_f_2, raw_files_f_3, db_folder, enzyme, path_input_f]
        mq.create_xml_config_file(config_folder_f, params_f, numThreads, config_sample_folder)
        mq.running_maxquant_through_cmd(config_folder_f)

        print("loading and parsing day0 (elution)\n")
        logging.info("loading and parsing day0 (elution)")
        days0, peptides_dict_0 = util.read_or_new_pickle (IsDebug, path = pickle_file_e, default = fe.pre_process_on_file(day0_file))


        print("loading and parsing day10 (flowthrough)\n")
        logging.info("loading and parsing day10 (flowthrough)")
        days10, peptides_dict_10 = util.read_or_new_pickle(IsDebug, path = pickle_file_f, default= fe.pre_process_on_file(day10_file))


        print("check if peptid appears in flowthrow and not elution \n")
        logging.info("check if peptid appears in flowthrow and not elution")
        peptides_list = util.read_or_new_pickle(IsDebug, path = pickle_file_p,\
                                                default= fe.check_if_appears_in_flow_through(peptides_dict_0, peptides_dict_10, Y))


        print("create filtered peptid file\n")
        logging.info("create filtered peptid file")
        fe.create_new_filtered_file(peptides_list, output)


        print("loading and parsing DB\n")
        logging.info("loading and parsing DB")
        db = util.read_or_new_pickle(IsDebug, path=pickle_file_db, default= dbf.load_db(db_folder))



        print("create filtered peptides files according to cdr3\n")
        logging.info("create filtered peptides files according to cdr3")
        if IsDebug == True:
            try:
                non_info = pickle.load(open(pickle_file_non_info, 'rb'))
                info = pickle.load(open(pickle_file_info, 'rb'))
                CDR3_info = pickle.load(open(pickle_file_cdr3, 'rb'))
                db_peptides = pickle.load(open(pickle_file_db_peptides, 'rb'))
            except (OSError, IOError, EOFError):
                non_info, info, CDR3_info, db_peptides = dbf.create_filtered_peptides_files_according_to_cdr3(output_files + 'non_informative_peptides.tsv',\
                                                                output_files + 'informative_peptides.tsv',\
                                                                output_files + 'informative_CDR3_peptides.tsv',\
                                                                 db, peptides_list)

                pickle._dump(non_info , open(pickle_file_non_info, 'wb'))
                pickle._dump(info , open(pickle_file_info, 'wb'))
                pickle._dump(CDR3_info , open(pickle_file_cdr3, 'wb'))
                pickle._dump(db_peptides , open(pickle_file_db_peptides, 'wb'))

        else:
            non_info, info, CDR3_info, db_peptides = dbf.create_filtered_peptides_files_according_to_cdr3(output_files + 'non_informative_peptides.tsv',\
                                                                output_files + 'informative_peptides.tsv',\
                                                                output_files + 'informative_CDR3_peptides.tsv',\
                                                                 db, peptides_list)


        print("create cdr3 analysis\n")
        logging.info("create cdr3 analysis")
        sp.analyze_cdr3(CDR3_info, pictures_folder)

        print("create peptid plot\n")
        logging.info("create peptid plot")
        sp.plot_peptid_records(peptides_list, peptides_dict_0, db_peptides, pictures_folder+ 'proteomics_vs_genetics.png')

        status = 'is done'



    except Exception:

        status = 'was failed'
        msg = 'PASA failed :( '
        he.edit_failure_html(html_path, run_number, msg, CONSTS)


    msg = f'PASA pipeline {status}'

    file_names = ['filtered_peptides.txt', 'informative_CDR3_peptides.tsv',
                  'informative_peptides.tsv', 'non_informative_peptides.tsv',
                  'cdr3_length_distributions.png', 'IGH_D_counts.png',
                  'IGH_V_counts.png', 'IGH_J_counts.png',
                  'IGH_VD_counts.png', 'IGH_VJ_counts.png',
                  'IGH_DJ_counts.png', 'IGH_VDJ_counts.png',
                  'proteomics_vs_genetics.png']

    strs_to_show_on_html = ['List of curated peptides', 'List of informative CDR3 peptides',
                            'List of informative NON-CDR3 peptides', 'List of NON informative peptides',
                            'CDR3 length distribution', 'V family subgroup distribution',
                            'D family subgroup distribution', 'J family subgroup distribution',
                            'VD family subgroup distribution', 'VJ family subgroup distribution',
                            'DJ family subgroup distribution', 'VDJ family subgroup distribution',
                            'Proteomics VS Genetics']

    he.edit_success_html(html_path, output_files, run_number, CONSTS, file_names,
                         strs_to_show_on_html)
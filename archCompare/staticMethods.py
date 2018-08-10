import sys
import os
import tarfile
from subprocess import Popen, PIPE, STDOUT
import logging
from beautifultable import BeautifulTable

log = logging.getLogger(__name__)


class StaticMthods(object):
    """ Static methosds for sommon tasks """

    def __init__(self):
        super().__init__()

    def input_checker(infile):
        """
          checks user input file and returns it's type
        """
        try:
            if tarfile.is_tarfile(infile):
                log.info(("input is an archive:", infile))
                return 'tar'
            else:
                log.info(("input is a file:", infile))
                return 'file'
        except IsADirectoryError:
            return 'dir'
        except IOError as ioe:
            sys.exit('Error in reading input file:{}'.format(ioe.args[0]))

    def process_list_to_dict(path_list, prefix):
        """
          creates dictionary of paths [relative path] in an archive
          where filename prefix replaced to create keys that are identical in two dictionaries
          path_list = [file_path, name, ext]
        """
        path_dict = {}
        for meta_list in path_list:
            meta_list[0] = os.path.realpath(meta_list[0])
            path_dict[meta_list[1].replace(prefix, '', 1)] = meta_list
        return path_dict

    def run_command(cmd):
        """ runs command in a shell, returns stdout and exit code"""
        if not len(cmd):
            raise ValueError("Must supply at least one argument")
        try:
            # To capture standard error in the result, use stderr=subprocess.STDOUT:
            cmd_obj = Popen(cmd, stdin=None, stdout=PIPE, stderr=PIPE,
                            shell=True, universal_newlines=True, bufsize=-1,
                            close_fds=True, executable='/bin/bash')
            log.info(("running command", cmd))
            (out, error) = cmd_obj.communicate()
            return out, error, cmd_obj.returncode
        except OSError as oe:
            log.error("Unable to run command:{} Error:{}".format(cmd, oe.args[0]))
            sys.exit("Unable to run command:{} Error:{}".format(cmd, oe.args[0]))

    @staticmethod
    def format_results(results, dicta, dictb, outfile, verbose=None):
        """
          formats output results as tab separated file and commandline output
        """
        const_header = ['#Filea', 'Fileb']
        (columns, file_key) = ([] for i in range(2))

        failed_flag = None

        for comp_n_file, result in results.items():
            columns.append(comp_n_file[0])
            file_key.append(comp_n_file[1])

        comp_type = sorted(set(columns))
        const_header.extend(comp_type)
        table = BeautifulTable(max_width=125)
        table.column_headers = const_header

        if outfile:
            try:
                f = open(outfile, 'w')
                f.write('\t'.join(const_header) + '\n')
            except IOError as ioe:
                sys.exit('Can not create outfile:{}'.format(ioe.args[0]))

        for file_key_val in sorted(set(file_key)):
            row_data = [dicta.get(file_key_val, ['NA'])[0], dictb.get(file_key_val, ['NA'])[0]]
            for cmp in comp_type:
                res = results.get((cmp, file_key_val), 'NA')
                row_data.extend([res])
            table.append_row(row_data)

            if outfile:
                f.write('\t'.join(row_data) + '\n')
            if 'FAIL' in row_data:
                failed_flag = 1

        if verbose and outfile is None:
            table.sort(1)
            table.auto_calculate_width()
            print(table)

        if failed_flag:
            sys.exit(1)

        try:
            f.close()
        except UnboundLocalError:
            pass
        finally:
            sys.exit()

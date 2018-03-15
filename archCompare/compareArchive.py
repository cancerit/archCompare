import json
import tarfile
import os
import sys
import tempfile
import re
import logging.config
from sys import stderr
from archCompare.abstractArchive import AbstractCompare
from archCompare.staticMethods import StaticMthods as sm

configdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config/')
log_config = configdir + 'logging.conf'
json_config = configdir + 'fileTypes.json'
logging.config.fileConfig(log_config)

log = logging.getLogger('compareArchive')

'''
Compare file, folder or archived data in .tar, .gz, .bz2 format
input any of the above
output -- list of items that are common in two compared archives
based on the MD5sum and/or data contents
'''


class ArchCompare(AbstractCompare):
    """
      Main class implements abstract class and
      its methods to check the inputype of a given file and loads parameters from user config
      file required in json format
    """

    def check_input(self):
        """ check input type of user supplied
          input filea and fileb keyword arguments
          and returns tupule of input file type
        """
        super().check_input()
        input_type = []
        for infile in (self.file_a, self.file_b):
            input_type.append(sm.input_checker(infile))
        return tuple(input_type)

    def get_config(self):
        """
          load parameters from json config file, if comparison type is not defined on command line
          uses default fron config file
        """
        super().get_config()
        try:
            if self.json_file is None:
                self.json_file = json_config
            with open(self.json_file, 'r') as cfgfile:
                self.cfg = json.load(cfgfile)
                self.ignore_prefix = self.cfg['globals']['ignore_prefix_for_ext']
                if self.cmp_type is None:
                    self.cmp_type = self.cfg['globals']['default_comparison']
                log.info('Performing comaparison type:{}'.format(self.cmp_type))
        except json.JSONDecodeError as jde:
            sys.exit('json error:{}'.format(jde.args[0]))
        except FileNotFoundError as fne:
            sys.exit('Can not find json file:{}'.format(fne.args[0]))

    def _format_input(self, ftype, file_path):
        """
          accessory method to call other input formatting methods
        """
        if ftype == 'file':
            return self._format_file_input(file_path)
        elif ftype == 'tar':
            return self._format_tar_input(file_path)
        elif ftype == 'dir':
            return self._format_dir_input(file_path)
        else:
            log.erro('Undefined file format')
            return

    def _format_tar_input(self, file_path):
        """
          creates a diretory object of key = file name and values = [file paths, name, extensions]
          if requested comparison type is data then directory extracted to temp folder and
          input is then formatted
          by calling  _format_dir_input method
        """
        path_list = []
        list_for_prefix = []
        with tarfile.open(file_path, 'r') as tar:
            log.info('Processing tar file')
            if self.cmp_type in ['data', 'checksum']:
                log.info('Extracting tar file for data comparison, this might take a while ....')
                tmp_path = tempfile.mkdtemp(dir=".")
                tar.extractall(path=tmp_path)
                log.info(('Archive extraction completed at:', file_path))
                return self._format_dir_input(tmp_path)
            elif self.cmp_type == 'name':
                for tarinfo in tar:
                    if tarinfo.isreg():
                        name, ext = self._get_file_metadata(tarinfo.name)
                        path_list.append([tarinfo.name, name, ext])
                        if ext in self.ignore_prefix:
                            list_for_prefix.append(name)
                prefix = os.path.commonprefix(list_for_prefix)
                path_dict=sm.process_list_to_dict(path_list, prefix)
                return path_dict

    def _format_dir_input(self, file_path):
        """
          creates a diretory object of key = file name and values = [file paths, name, extension]
        """
        path_list = []
        list_for_prefix = []
        log.info('Processing directory:{}'.format(file_path))
        for dirpath, _, files in os.walk(file_path):
            for filename in files:
                fullpath = os.path.join(dirpath, filename)
                name, ext = self._get_file_metadata(fullpath)
                path_list.append([fullpath, name, ext])
                if ext in self.ignore_prefix:
                    list_for_prefix.append(name)
        prefix = os.path.commonprefix(list_for_prefix)
        path_dict=sm.process_list_to_dict(path_list, prefix)
        return path_dict

    def _format_file_input(self, file_path):
        """
          creates a diretory object of key = file name and values = [file paths, name, extensions]
        """
        log.info('Processing file :{}'.format(file_path))
        name, ext = self._get_file_metadata(file_path)
        path_dict=sm.process_list_to_dict([[file_path, name, ext]], '')
        return path_dict

    def _get_file_metadata(self,full_file_name):
        """
          takes file path as input and gives its path and processed extension
          #  If there are two extensions adds second extensions as prefix
        """
        (_, name) = os.path.split(full_file_name)
        (name_no_ext, first_ext) = os.path.splitext(name)
        (_, second_ext) = os.path.splitext(name_no_ext)
        first_ext = second_ext + first_ext
        return name, first_ext

    def _get_sets_to_compare(self, dictA, dictB):
        """
          peforms intersection and difference of diretory keys
          and outputs comparison of resulting sets as requested by user
          returns resuts dictionary containing filekey, comparison status and results if any
        """
        results_dict = {}
        common_files = list(set(dictA.keys()) & set(dictB.keys()))
        only_in_archiveA = list(set(dictA.keys()) - set(dictB.keys()))
        only_in_archiveB = list(set(dictB.keys()) - set(dictA.keys()))
        results_dict = self._do_comparison(dictA, dictB, common_files)
        for file_key in only_in_archiveA:
            results_dict[file_key] = ['skipped', 'onlyInA']
        for file_key in only_in_archiveB:
            results_dict[file_key] = ['skipped', 'onlyInB']
        return results_dict

    def _do_comparison(self, dictA, dictB, common_files):
        """
          loops through dictionary and call explicit comaprsion methods as requested
          returns results dictionary containing filekey, comparison status and results if any
        """
        print(common_files)
        results_dict = {}
        preprocessors_dict = self.cfg['preprocessors']
        json_data = self.cfg['diffs']
        checksum_type = self.cfg['globals']['checksum_tool']
        tmp_dir = tempfile.mkdtemp(dir=".")
        for file_key in common_files:
            filea, _, ext_filea = (dictA[file_key])
            fileb, _, _ = (dictB[file_key])
            ext_dict = json_data.get(ext_filea, None)
            preprocess_dict=preprocessors_dict.get(ext_filea,None)
            # retrieve json command for given extension
            if filea == fileb:
                log.info("Files have identical paths, skipping comaprison filea:{}fileb:{}".format(filea, fileb))
                results_dict[file_key] = ['skipped', 'IdenticalPath']
            elif self.cmp_type == 'name':
                results_dict[file_key] = ['compared', 'name']
            elif self.cmp_type == 'checksum':
                log.info("performig checksum")
                (out,error,exitcode) = sm.do_checksum_comaprison(checksum_type, filea=filea, fileb=fileb)
                if not error and exitcode==0:
                    results_dict[file_key] = ['compared', out]
                else:
                    results_dict[file_key] = ['compared', "Exitcode:{}, Error:{}".format(exitcode,error)]
            elif ext_dict is None and preprocess_dict is None:
                results_dict[file_key] = ['skipped', 'NoExtInJson']
            elif self.cmp_type == 'data':
                log.info("performig Data comparison")
                # check if extension type needs preprocessing of files e.g., vcf.gz
                if preprocess_dict is not None:
                    preprocess_cmd=preprocess_dict.get('preprocess',None)
                    filea=self._preprocess_file(preprocess_cmd,file=filea,
                                        tmp=self._get_tmp_file(dir_name=tmp_dir))
                    fileb=self._preprocess_file(preprocess_cmd,file=fileb,
                                        tmp=self._get_tmp_file(dir_name=tmp_dir))
                    # find out what to run next on these files....
                    ext_filea=preprocess_dict.get('then')
                    ext_dict = json_data.get(ext_filea, None)
                    (out,error,exitcode) = self._run_diff(ext_dict, filea=filea, fileb=fileb)
                    results_dict[file_key] = ['compared', result]
                else:
                    (out,error,exitcode) = self._run_diff(ext_dict, filea=filea, fileb=fileb)
                    results_dict[file_key] = ['compared', result]
            else:
                sys.exit('Unknown comparison type requested')
        return results_dict

    def _preprocess_file(self,cmd,**kwargs):
        sm.run_command(cmd.format(**kwargs))
        return kwargs.get('tmp')

    def _get_tmp_file(self,dir_name="."):
        return tempfile.NamedTemporaryFile(suffix='.txt',
                               prefix='archComp',
                               dir=tmp_dir,
                               ).name

    def _run_diff(self, ext_dict, **kwargs):
        """ run comparison for given set of extension ,
            additional methods could be added for different extension types
            returns data [identical file content] or None [differences in file]
        """
        err_msg='check_type not in Json config file'

        cmd = ext_dict.get('cmd')
        check_type = ext_dict.get('check', None)
        good_re = ext_dict.get('good_re', None)
        bad_re = ext_dict.get('good_re', None)

        (out,error,exitcode) = sm.run_command(cmd.format(**kwargs))
        if check_type == 'stderr':

        if good_re and check_type == 'stdout':
                for pattern in good_re:

        if check_type == 'exit-code':

        else:
            return err_msg,err_msg,err_msg


    def call_quiet(*args):
        """Safely run a command and get stdout; print stderr if there's an error.
        Like subprocess.check_output, but silent in the normal case where the
        command logs unimportant stuff to stderr. If there is an error, then the
        full error message(s) is shown in the exception message.
        """
        # args = map(str, args)
        if not len(args):
            raise ValueError("Must supply at least one argument (the command name)")
        try:
            proc = subprocess.Popen(args, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
        except OSError as exc:
            raise RuntimeError("Could not find the executable %r" % args[0]
                               + " -- is it installed correctly?"
                               + "\n(Original error: %s)" % exc)
        out, err = proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError("Subprocess command failed:\n$ %s\n\n%s"
                               % (' '.join(args), err))
        return out





    def run_comparison(self):
        """
          method to run the complete comparison
        """
        (typea, typeb) = self.check_input()
        dicta = self._format_input(typea, self.file_a)
        dictb = self._format_input(typeb, self.file_b)
        results = self._get_sets_to_compare(dicta, dictb)
        sm.format_results(results, dicta, dictb, self.outfile)

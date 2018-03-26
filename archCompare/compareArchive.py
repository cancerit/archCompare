import json
import tarfile
import os
import sys
import tempfile
import re
import logging.config
import shutil
from sys import stderr
from archCompare.abstractArchive import AbstractCompare
from archCompare.staticMethods import StaticMthods as sm

configdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config/')
log_config = configdir + 'logging.conf'
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
                sys.exit('Json configuration file must be provided')
            with open(self.json_file, 'r') as cfgfile:
                self.cfg = json.load(cfgfile)
                self.ignore_prefix = self.cfg['globals']['ignore_prefix_for_ext']
                self.debug = self.cfg['globals']['debug']
                self.checksum_type = self.cfg['globals']['checksum_tool']
                self.exiton = self.cfg['globals']['exitOn']
                if self.cmp_type is None:
                    self.cmp_type = self.cfg['globals']['reportOn']
                log.info('Performing comaparison type On:{}'.format(self.cmp_type))
        except json.JSONDecodeError as jde:
            sys.exit('json error:{}'.format(jde.args[0]))
        except FileNotFoundError as fne:
            sys.exit('Can not find json file:{}'.format(fne.args[0]))
        self.cleanup = []

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
            log.erro('Undefined file format:{}'.format(ftype))
            sys.exit('Undefined file format:{}'.format(ftype))
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
            if len(set(self.cmp_type) & set(['diffs', 'checksum'])) > 0:
                log.info('Extracting tar file for data comparison, this might take a while ....')
                tmp_path = tempfile.mkdtemp(dir=".")
                self.cleanup.append(tmp_path)
                tar.extractall(path=tmp_path)
                log.info(('Archive extraction completed at:', file_path))
                return self._format_dir_input(tmp_path)
            elif len(set(self.cmp_type) & set(['name', 'size'])) > 0:
                for tarinfo in tar:
                    if tarinfo.isreg():
                        name, ext, size = self._get_file_metadata(tarinfo.name, file_size=tarinfo.size)
                        path_list.append([tarinfo.name, name, ext, size])
                        if ext in self.ignore_prefix:
                            list_for_prefix.append(name)
                prefix = os.path.commonprefix(list_for_prefix)
                path_dict = sm.process_list_to_dict(path_list, prefix)
                return path_dict
            else:
                log.error('Unknown comparison type:{}'.format(self.cmp_type))
                sys.exit('Unknown comparison type:{}'.format(self.cmp_type))

    def _format_dir_input(self, file_path):
        """
          creates a diretory object of key = file name and
          values = [file paths, name, extension, size]
        """
        path_list = []
        list_for_prefix = []
        for dirpath, _, files in os.walk(file_path):
            for filename in files:
                fullpath = os.path.join(dirpath, filename)
                name, ext, size = self._get_file_metadata(fullpath)
                path_list.append([fullpath, name, ext, size])
                if ext in self.ignore_prefix:
                    list_for_prefix.append(name)
        prefix = os.path.commonprefix(list_for_prefix)
        path_dict = sm.process_list_to_dict(path_list, prefix)
        return path_dict

    def _format_file_input(self, file_path):
        """
          creates a diretory object of key = file name and values = [file paths, name, extensions]
        """
        log.info('Processing file :{}'.format(file_path))
        name, ext, size = self._get_file_metadata(file_path)
        path_dict = sm.process_list_to_dict([[file_path, name, ext, size]], '')
        return path_dict

    def _get_file_metadata(self, full_file_name, file_size=None):
        """
          takes file path as input and gives its path and processed extension
          #  If there are two extensions adds second extensions as prefix
        """
        (_, name) = os.path.split(full_file_name)
        (name_no_ext, first_ext) = os.path.splitext(name)
        (_, second_ext) = os.path.splitext(name_no_ext)
        first_ext = second_ext + first_ext
        if file_size is None:
            file_size = os.stat(full_file_name).st_size
        return name, first_ext, file_size

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
            results_dict['skipped', file_key] = 'onlyInA'
        for file_key in only_in_archiveB:
            results_dict['skipped', file_key] = 'onlyInB'
        return results_dict

    def _do_comparison(self, dictA, dictB, common_files):
        """
          loops through dictionary and call explicit comaprsion methods as requested
          returns results dictionary containing filekey, comparison status and results if any
        """
        if dictA is None or dictB is None:
            sys.exit('No data for comparsion archiveA:{} and archiveB:{}'.format(dictA, dictB))
        results_dict = {}
        preprocessors_dict = self.cfg['preprocessors']
        json_data = self.cfg['diffs']
        tmp_dir = tempfile.mkdtemp(dir=".")
        self.cleanup.append(tmp_dir)
        for file_key in common_files:
            filea, _, ext_filea, sizea = (dictA[file_key])
            fileb, _, _, sizeb = (dictB[file_key])
            ext_dict = json_data.get(ext_filea, None)
            ext_preprocess_dict = preprocessors_dict.get(ext_filea, None)
            if filea == fileb:
                log.info("Files have identical paths, skipping comaprison filea:{}fileb:{}".format(filea, fileb))
                results_dict['skipped', file_key] = 'IdenticalPath'
                continue
            if 'name' in self.cmp_type:
                results_dict['name', file_key] = 'PASS'
            if 'size' in self.cmp_type:
                if sizea == sizeb:
                    results_dict['size', file_key] = 'PASS'
                else:
                    results_dict['size', file_key] = 'FAIL'
            if 'checksum' in self.cmp_type:
                log.info("performig checksum comparison")
                results_dict['checksum', file_key] = self._do_checksum(filea, fileb)
                if 'checksum' in self.exiton:
                    continue
            if 'diffs' in self.cmp_type and ext_dict is None and ext_preprocess_dict is None:
                results_dict['diffs', file_key] = 'NoExtInJson'
                continue
            elif 'diffs' in self.cmp_type:
                log.info("performig Data comparison for ext:{}".format(ext_filea))
                results_dict['diffs', file_key] = self._process_diff(ext_preprocess_dict, ext_dict,
                                                                     json_data, tmp_dir,
                                                                     filea, fileb)

        return results_dict

    def _do_checksum(self, filea, fileb):
        cmd = r'{checksum} {file}'
        kwargs = {'checksum': self.checksum_type, 'file': filea}
        (outa, errora, exitcodea) = sm.run_command(cmd.format(**kwargs))
        kwargs['file'] = fileb
        (outb, errorb, exitcodeb) = sm.run_command(cmd.format(**kwargs))
        if exitcodeb != 0 or exitcodea != 0:
            log.error("outa:{},Errora:{},exitcodea:{}".format(outa, errora, exitcodea))
            log.error("outb:{},Errorb:{},exitcodeb:{}".format(outa, errora, exitcodea))
            return 'FAIL'
        elif outa == outb:
            return 'PASS'
        else:
            return 'FAIL'

    def _process_diff(self, ext_preprocess_dict, ext_dict, json_data, tmp_dir, filea, fileb):
        # check if extension type needs preprocessing of files e.g., vcf.gz
        """

        :rtype: object
        """
        if ext_preprocess_dict is not None:
            preprocess_cmd = ext_preprocess_dict.get('preprocess', None)
            filea = self._preprocess_file(preprocess_cmd, file=filea,
                                          tmp=self._get_tmp_file(dir_name=tmp_dir))
            fileb = self._preprocess_file(preprocess_cmd, file=fileb,
                                          tmp=self._get_tmp_file(dir_name=tmp_dir))
            # find out what to run next on these files....
            ext_filea = ext_preprocess_dict.get('then')
            ext_dict = json_data.get(ext_filea, None)
            if ext_dict is None:
                return 'NoExtInJson'
        (out, error, exitcode) = self._run_diff(ext_dict, filea=filea, fileb=fileb)
        if out == 'data':
            return 'PASS'
        else:
            log.error("out:{},Error:{},exitcode:{}".format(out, error, exitcode))
            return 'FAIL'

    def _preprocess_file(self, cmd, **kwargs):
        sm.run_command(cmd.format(**kwargs))
        return kwargs.get('tmp')

    def _get_tmp_file(self, dir_name="."):
        return tempfile.NamedTemporaryFile(suffix='.txt',
                                           prefix='archComp',
                                           dir=dir_name,
                                           ).name

    def _run_diff(self, ext_dict, **kwargs):
        """ run comparison for given set of extension ,
            additional methods could be added for different extension types
            returns data [identical file content] or None [differences in file]
        """
        err_msg = 'check_type not in Json config file'
        cmd = ext_dict.get('cmd')
        check_type = ext_dict.get('check', None)
        good_re = ext_dict.get('good_re', None)
        bad_re = ext_dict.get('bad_re', None)
        # format regex
        if bad_re:
            bad_re = '(' + ('|'.join(bad_re)) + ')'
        if good_re:
            good_re = '(' + ('|'.join(good_re)) + ')'

        (out, error, exitcode) = sm.run_command(cmd.format(**kwargs))
        if good_re and check_type == 'stdout':
            outlist = out.split("\n")
            goodregex = re.compile(good_re).search
            matches = self._findmatch(outlist, goodregex)
            if self.debug:
                print("Matches with good_re:{}".format(matches))
                print("out:{} error:{} exitcode:{}".format(out, error, exitcode))
            if (len(matches) > 0):
                return 'data', error, exitcode
        elif bad_re and check_type == 'stderr':
            errlist = error.split("\n")
            badregex = re.compile(bad_re).search
            matches = self._findmatch(errlist, badregex)
            if self.debug:
                print("Matches with bad_re:{}".format(matches))
                print("out:{} error:{} exitcode:{}".format(out, error, exitcode))
            if (len(matches) > 0):
                return out, error, exitcode
            else:
                return 'data', error, exitcode
        elif check_type == 'exit-code':
            if exitcode == 0:
                if self.debug:
                    print("out:{} error:{} exitcode:{}".format(out, error, exitcode))
                return 'data', error, exitcode
            else:
                return out, error, exitcode
        else:
            return out, error, exitcode

    def _findmatch(self, outlist, lookupval):
        """
            lookup a complied regular expression in the output list generated
            from stderr or stdout
        """
        return [(l, m.group(1)) for l in outlist for m in (lookupval(l),) if m]

    def cleantemp(self):
        """
            clean temporary generated paths at the end
            make sure . and .. is not included
        """
        if self.remove_tmp.lower() == 'y' or self.remove_tmp.lower() == 'yes':
            for tmp_f in self.cleanup:
                if tmp_f in ['.', '..', '/']:
                    continue
                if os.path.exists(tmp_f):
                    shutil.rmtree(tmp_f)
                    log.info('removed tmp folder:{}'.format(tmp_f))
                else:
                    log.error("file doesn't exists for cleanup:{}".format(tmp_f))
        else:
            log.info("clean up flag false, tmporary data not cleaned")

    def run_comparison(self):
        """
          method to run the complete comparison
        """
        (typea, typeb) = self.check_input()
        dicta = self._format_input(typea, self.file_a)
        dictb = self._format_input(typeb, self.file_b)
        results = self._get_sets_to_compare(dicta, dictb)
        sm.format_results(results, dicta, dictb, self.outfile)
        self.cleantemp()

import json
import tarfile
import os
import sys
import tempfile
import re
from subprocess import Popen, PIPE, STDOUT
import shlex
import logging.config
import argparse
from sys import stderr
from archCompare.abstractArchive import AbstractCompare


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


def _input_checker(infile):
	"""
		checks user input file and returns it's type
	"""
	try:
		if tarfile.is_tarfile(infile):
			print("input is an archive:", infile)
			return 'tar'
		else:
			print("input is a file:", infile)
			return 'file'
	except IsADirectoryError:
		return 'dir'
	except IOError as ioe:
		print('Error in reading input file: ', ioe.args)
		sys.exit(1)


def _process_list_to_dict(path_list, prefix):
	"""
		creates dictionary of paths in an archive
		where filename prefix replaced to create keys taht are identical in two dictionaries
	"""
	path_dict = {}
	for meta_list in path_list:
			path_dict[meta_list[1].replace(prefix, '', 1)] = meta_list
	return path_dict


def _run_command(cmd):
	""" runs command in a shell, returns stdout and exit code"""
	args = shlex.split(cmd)
	try:
		cmd_obj = Popen(args, stdin=None, stdout=PIPE, stderr=STDOUT, shell=False, universal_newlines=True, bufsize=1)
		(stdout, stderr) = cmd_obj.communicate()
		return stdout, cmd_obj.returncode
	except OSError as oe:
		log.error(("Unable to run command", cmd, oe.args))
		return 'Error', 'Error'


def _format_results(results, dicta, dictb):
	"""
		formats output results as tab separated files
	"""
	with open('results.tsv', 'w') as f:
		print('FileKey\tStatus\tResults')
		f.write('Filea\tFileb\tStatus\tResults\n')
		for key, value in results.items():
			if value[1] is None:
				value[1] = 'differ'
			print(key, '\t', '\t'.join(value))
			f.write("{}\t{}\t{}\t{}\n".format(dicta.get(key, ['NA'])[0], dictb.get(key, ['NA'])[0], value[0], value[1]))


def _do_checksum_comaprison(prog, **kwargs):
	"""
		peforms checksum comparison and
		returns checksum [identical] or None [different checksum values]
	"""
	cmd = r'{checksum} {filea} {fileb}'
	kwargs['checksum'] = prog
	(stdout, stderr) = _run_command(cmd.format(**kwargs))
	if stdout == 'Error':
		return 'Error'
	out_msg = re.split('\n|\s', stdout)
	if stderr is not None:
		return
	elif out_msg[0] == out_msg[3]:
		return 'checksum'
	else:
		return


def _get_vcf_diff(stdout, exp_out):
	"""
		compres two vcf file and returns
		data [identical file content] or None [differences in file]
	"""
	out_msg = stdout.split("\n")
	for line in out_msg:
		if not line:  # skip empty lines
			continue
		try:
			match = re.search(exp_out, line)
			if match is None:  # if match not found return true
				return 'data'
			elif match[0] == '##contig=':  # matches only when contigs are different in two vcf files
				return
		except re.error:
			log.debug('Error in regular expression')
	return 'data'


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
			input_type.append(_input_checker(infile))
		return tuple(input_type)

	def get_config(self):
		"""
			load parameters from json config file, if comparison type is not defined on command line
			uses default fron config file
		"""
		super().get_config()
		try:
			with open(self.json_file, 'r') as cfgfile:
				self.cfg = json.load(cfgfile)
				self.prefix_ext = self.cfg['other_prm']['prefix_extension']
				if self.cmp_type is None:
					self.cmp_type = ''.join(key for key, val in self.cfg['cmp_type'].items() if val.upper() == 'Y')
					log.info('Using comaparison type from json config')
		except json.JSONDecodeError as jde:
			print('json error', jde.args[0])
			sys.exit(1)
		except FileNotFoundError as fne:
			print('Can not find json file', fne.args)
			sys.exit(1)

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
			if self.cmp_type == 'data':
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
						if ext in self.prefix_ext:
							list_for_prefix.append(name)
				prefix = os.path.commonprefix(list_for_prefix)
				return _process_list_to_dict(path_list, prefix)

	def _format_dir_input(self, file_path):
		"""
			creates a diretory object of key = file name and values = [file paths, name, extensions]
		"""
		path_list = []
		list_for_prefix = []
		print('Processing directory:', file_path)
		for dirpath, _, files in os.walk(file_path):
			for filename in files:
				fullpath = os.path.join(dirpath, filename)
				name, ext = self._get_file_metadata(fullpath)
				path_list.append([fullpath, name, ext])
				if ext in self.prefix_ext:
					list_for_prefix.append(name)
		prefix = os.path.commonprefix(list_for_prefix)
		return _process_list_to_dict(path_list, prefix)

	def _format_file_input(self, file_path):
		"""
			creates a diretory object of key = file name and values = [file paths, name, extensions]
		"""
		print('Processing file:', file_path)
		name, ext = self._get_file_metadata(file_path)
		return _process_list_to_dict([[file_path, name, ext]], '')

	def _get_file_metadata(self, full_file_name):
		"""
			takes file path as input and gives its path and processed extension
			# check second extension before .gz to determine file type [ e.g., .vcf.gz ]
		"""
		(_, name) = os.path.split(full_file_name)
		(name_no_ext, first_ext) = os.path.splitext(name)
		if first_ext == '.gz':
			(_, second_ext) = os.path.splitext(name_no_ext)
			if second_ext in self.prefix_ext:
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
		if self.cmp_type == 'name':
			for file_key in common_files:
				results_dict[file_key] = ['compared', 'name']
		else:
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
		results_dict = {}
		json_data = self.cfg['extensions']
		checksum_type = self.cfg['other_prm']['checksum_type']
		for file_key in common_files:
			filea, _, ext_filea = (dictA[file_key])
			fileb, _, _ = (dictB[file_key])
			# retrieve json command for given extension
			ext_dict = json_data.get(ext_filea, None)
			if ext_dict is None:
				results_dict[file_key] = ['skipped', 'NoExtInJson']
			elif self.cmp_type == 'checksum':
				print("performig checksum")
				result = _do_checksum_comaprison(checksum_type, filea=filea, fileb=fileb)
				results_dict[file_key] = ['compared', result]
			elif self.cmp_type == 'data':
				print("performig Data comparison")
				result = self._run_diff(ext_dict, ext_filea, filea=filea, fileb=fileb)
				results_dict[file_key] = ['compared', result]
			else:
				log.error('Unknown comparison type requested')
		return results_dict

	def _run_diff(self, ext_dict, ext, **kwargs):
		""" run comparison for given set of extension , additional methods could be added for different extension
			returns data [identical file content] or None [differences in file]
		"""
		additional_prm = ext_dict.get('prm', None)
		cmd = ext_dict.get('cmd')
		exp_out = ext_dict.get('exp_out', None)
		log.info(("requested comparison type:", self.cmp_type))
		# add additional parametes
		if additional_prm is not None:
			for prm, val in additional_prm.items():
				kwargs[prm] = val
		(stdout, stderr) = _run_command(cmd.format(**kwargs))
		if stdout == 'Error':
			return 'Error'
		log.info(('ARGS:', kwargs, 'ERR:', stderr, 'OUT:', stdout))
		if re.search('^.vcf|^.vcf.gz', ext):
			return _get_vcf_diff(stdout, exp_out[0])
		else:
			if stderr:
				return
		return 'data'

	def run_comparison(self):
		"""
			method to run the complete comparison
		"""
		(typea, typeb) = self.check_input()
		dicta = self._format_input(typea, self.file_a)
		dictb = self._format_input(typeb, self.file_b)
		results = self._get_sets_to_compare(dicta, dictb)
		_format_results(results, dicta, dictb)

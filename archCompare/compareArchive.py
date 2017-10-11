import json
import tarfile
import os,sys
import tempfile
import re
from subprocess import Popen, PIPE, STDOUT
import shlex
import logging.config
import argparse
from sys import stderr
from  archCompare.abstractArchive import AbstractCompare


configdir = os.path.join(os.path.dirname(os.path.realpath(__file__)),'config/') 
log_config=configdir+'logging.conf'
logging.config.fileConfig(log_config)

log = logging.getLogger('compareArchive')

''' 
Compare file,folder or archived data in .tar, .gz, .bz2 format
input any of the above
output -- list of items that are common in two compared archives based on the MD5sum and/or data contents
'''

class ArchCompare(AbstractCompare):
        
    def check_input(self):
        super().check_input()
        input_type=[]
        for infile in (self.file_a,self.file_b):
            input_type.append(self._input_checker(infile))
        return tuple(input_type)
    
    def _input_checker(self,infile):
        try:
            if tarfile.is_tarfile(infile):
                log.info(("input is an archive:",infile))
                return 'tar'
            else:
                log.info(("input is a file:",infile))
                return 'file'
        except IsADirectoryError:
            log.info(("input is directory:",infile))
            return 'dir'
        except IOError as ioe: 
            log.debug(('Error in reading input file: ',ioe.args))
            sys.exit(ioe)
        else:
            print("Unknown file type")
            return None

    def get_config(self):
        super().get_config()
        try:
            with open(self.json_file, 'r') as cfgfile:
                self.cfg = json.load(cfgfile)
                self.prefix_ext=self.cfg['other_prm']['prefix_extension']
                if self.cmp_type == None:
                    self.cmp_type=''.join(key for key,val in self.cfg['cmp_type'].items() if val.upper() == 'Y')
                    log.info('Using comaprison type from json config')
        except json.JSONDecodeError as jde:
            log.debug(('json error',jde.args[0]))
            sys.exit(1)
        except FileNotFoundError as fne:
            log.debug(('Can not find json file',fne.args))
            sys.exit(1)
            
    def _format_input(self,ftype,file_path):
        if(ftype == 'file'):
            return self._format_file_input(file_path)
        elif(ftype == 'tar'):
            return self._format_tar_input(file_path)
        elif(ftype=='dir'):
            return self._format_dir_input(file_path)
        else:
            log.erro('Undefined file format')
            return
           
    def _format_tar_input(self,file_path):
        path_list=[]
        list_for_prefix=[]
        with tarfile.open(file_path,'r') as tar:
            log.info('Processing tar file')
            if self.cmp_type == 'data':
                log.info('Extracting tar file for data comparison, this might take a while ....')
                tmp_path= tempfile.mkdtemp(dir=".")
                tar.extractall(path=tmp_path)
                log.info(('Archive extraction completed at:',file_path))
                return self.format_dir_input(tmp_path)
            elif self.cmp_type == 'name':
                for tarinfo in tar:           
                    if tarinfo.isreg():        
                        name,ext=self._get_file_metadata(tarinfo.name)
                        path_list.append([tarinfo.name,name,ext])
                        if(ext in self.prefix_ext):
                            list_for_prefix.append(name)           
                prefix=os.path.commonprefix(list_for_prefix)
                return self._process_list_to_dict(path_list,prefix)
        
    def _format_dir_input(self,file_path):
        path_list=[]
        list_for_prefix=[]
        
        log.info(('Processing directory:',file_path))
        
        for dirpath,_,files in os.walk(file_path):
            for filename in files:
                fullpath=os.path.join(dirpath,filename)
                name,ext=self._get_file_metadata(fullpath)
                path_list.append([fullpath,name,ext])
                
                if(ext in self.prefix_ext):
                    list_for_prefix.append(name)
                    
        prefix=os.path.commonprefix(list_for_prefix)     
        return self._process_list_to_dict(path_list,prefix)

     
    def _format_file_input(self,file_path):
        log.info(('Processing file:',file_path))
        name,ext=self._get_file_metadata(file_path)
        return self._process_list_to_dict([[file_path,name,ext]],'')
      
    def _get_file_metadata(self,full_file_name):
        ''' takes file path as input and gives its path and processed extension '''
        (_,name)=os.path.split(full_file_name)
        (name_no_ext,first_ext)=os.path.splitext(name)             
        if(first_ext == '.gz'): # check second extension before .gz to determine file type [ e.g., .vcf.gz ]
            (_,second_ext)=os.path.splitext(name_no_ext)
            if(second_ext in self.prefix_ext):
                first_ext=second_ext+first_ext
        return name,first_ext   
 
    def _process_list_to_dict(self,path_list,prefix):
        ''' creates dictionary of paths in an archive 
        where filename prefix replaced to create keys taht are identical in two dictionaries'''
        path_dict={}
        for meta_list in path_list:
                path_dict[meta_list[1].replace(prefix,'',1)]=meta_list
        return path_dict
    
    def _get_sets_to_compare(self,dictA,dictB):      
        # getcommon files
        results_dict={}
        common_files=list(set(dictA.keys()) & set(dictB.keys()))
        only_in_archiveA=list(set(dictA.keys()) - set(dictB.keys()))
        only_in_archiveB=list(set(dictB.keys()) - set(dictA.keys()))  
        if(self.cmp_type == 'name'):
            for file_key in common_files:
                results_dict[file_key]=['compared','name']
        else: 
            results_dict=self._do_comparison(dictA,dictB,common_files)
        for file_key in only_in_archiveA:
            results_dict[file_key]=['skipped','onlyInA']
        for file_key in only_in_archiveB:
            results_dict[file_key]=['skipped','onlyInB']                           
        return results_dict
        
    def _do_comparison(self,dictA,dictB,common_files):
        results_dict={}
        json_data=self.cfg['extensions']
        checksum_type=self.cfg['other_prm']['checksum_type']
        for file_key in common_files:
            filea,_,ext_filea=(dictA[file_key])
            fileb,_,_=(dictB[file_key])
            # retrieve json command for given extension
            ext_dict=json_data.get(ext_filea,None)
            if ext_dict==None:
                results_dict[file_key]=['skipped','NoExtInJson']
            elif self.cmp_type == 'checksum':
                print("performig checksum")
                result=self._do_checksum_comaprison(checksum_type,filea=filea,fileb=fileb)
                results_dict[file_key]=['compared',result]
            elif self.cmp_type == 'data':
                print("performig Data comparison")
                result=self._run_diff(ext_dict,ext_filea,filea=filea,fileb=fileb)
                results_dict[file_key]=['compared',result]
            else:
                log.error('Unknown comparison type requested')
        return results_dict   
      
    def _do_checksum_comaprison(self,prog,**kwargs):
        cmd=r'{chksum} {filea} {fileb}'
        kwargs['chksum']=prog
        (stdout,stderr)=self._run_command(cmd.format(**kwargs)) 
        out_msg=re.split('\n|\s',stdout)
        if stderr != None:
            return
        elif out_msg[0] == out_msg[3]:
            return 'chksum'
        else:
            return

    def _run_diff(self,ext_dict,ext,**kwargs):
        ''' run comparsion for give set of extensions , additional methods could be added for different extension
         types otherwise else should return None if stderror from command is non zero'''
        additional_prm=ext_dict.get('prm',None)
        cmd=ext_dict.get('cmd')
        exp_out=ext_dict.get('exp_out',None)
        log.info(("requested comparison type:",self.cmp_type))
        # add additional parametes
        if additional_prm != None:
            for prm,val in additional_prm.items():
                kwargs[prm]=val      
        (stdout,stderr)=self._run_command(cmd.format(**kwargs))  
        log.info(('ARGS:',kwargs,'ERR:',stderr,'OUT:',stdout))       
        if (re.search('^.vcf|^.vcf.gz',ext)):
            return self._get_vcf_diff(stdout,exp_out[0])
        else:
            if stderr:
                return
        return 'data'
    
    def _get_vcf_diff(self,stdout,exp_out):
        log.info(("requested comparison type:",self.cmp_type))
        out_msg=stdout.split("\n")
        for line in out_msg:
            if not line: # skip empty lines
                continue
            try:
                match=re.search(exp_out,line)
                if match == None: # if match not found return true
                    return 'data'
                elif match[0] == '##contig=': # matches only when contigs are different in two vcf files 
                    return
            except re.error:
                log.debug('Error in regular expression')
        return 'data'
    
    def _run_command(self,cmd):
        args=shlex.split(cmd)
        try:
            cmdobj=Popen(args,stdin=None, stdout=PIPE, stderr=STDOUT, shell=False, universal_newlines=True, bufsize=1)
            (stdout, stderr) = cmdobj.communicate()
            return stdout, cmdobj.returncode
        except OSError as oe:
            log.error(("Unable to run command",cmd,oe.args))
            
    def run_comparison(self):
        (typea,typeb)=self.check_input()
        dicta=self._format_input(typea,self.file_a)
        dictb=self._format_input(typeb, self.file_b)
        results=self._get_sets_to_compare(dicta,dictb)
        self._format_results(results)
    
    def _format_results(self,results):
        print('FileKey\tStatus\tResults')
        for key,value in results.items():
            if value[1] == None:
        		    value[1]='differ'
            print(key,'\t','\t'.join(value))  
def main():
     print("Running module as main not allowed")
if __name__ == '__main__':
  main()



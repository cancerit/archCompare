import archCompare.compareArchive as fc
import archCompare.staticMethods as sm
import pytest
import os

'''
written test to check codebase integrity
of archCompare
'''

class TestClass():
    testdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data/')
    t_foldera=testdir+'testA'
    t_folderb=testdir+'testB'
    t_filea=testdir+'samplea.caveman_c.annot.vcf.gz'
    t_fileb=testdir+'testB.txt'
    t_tara=testdir+'testA.tar'
    t_tarb=testdir+'testB.tar'

    t_dirbamA=testdir+'testBamA'
    t_dirbamB=testdir+'testBamB'
    cwdpath=os.getcwd()
    configdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config/')
    t_json = configdir + 'test.json'
    cmp_type=['data']
    tar_cmp_type=['name']
    file_dict={'samplea.caveman_c.annot.vcf.gz':[t_filea,
                                                'samplea.caveman_c.annot.vcf.gz',
                                                '.vcf.gz',2055]
                                                }
    format_tar_dictA={
                      'samplea.bam': [cwdpath+'/testA/samplea.bam', 'samplea.bam', '.bam',73060],
                      'samplea.bam.bai': [cwdpath+'/testA/samplea.bam.bai', 'samplea.bam.bai', '.bam.bai',8536],
                      'onlyinA.txt': [cwdpath+'/testA/onlyinA.txt', 'onlyinA.txt', '.txt',0],
                      'no_ext_file': [cwdpath + '/testA/no_ext_file', 'no_ext_file', '', 42],
                      'samplea.caveman_c.annot.vcf.gz': [cwdpath+'/testA/vcf_data/samplea.caveman_c.annot.vcf.gz',
                       'samplea.caveman_c.annot.vcf.gz', '.vcf.gz',2060]}

    format_tar_dictB={
                      'samplea.bam': [cwdpath+'/testB/samplea.bam', 'samplea.bam', '.bam',73060],
                      'samplea.caveman_c.annot.vcf.gz': [cwdpath+'/testB/vcf_data/samplea.caveman_c.annot.vcf.gz',
                       'samplea.caveman_c.annot.vcf.gz', '.vcf.gz',2055],
                      'samplea.bam.bai': [cwdpath+'/testB/samplea.bam.bai', 'samplea.bam.bai', '.bam.bai',8536],
                      'no_ext_file': [cwdpath + '/testB/no_ext_file', 'no_ext_file', '', 42],
                      'onlyinB.txt': [cwdpath+'/testB/onlyinB.txt', 'onlyinB.txt', '.txt',0]}

    format_dir_dictA={
                      'samplea.bam': [t_foldera+'/samplea.bam', 'samplea.bam', '.bam',73060],
                      'samplea.bam.bai': [t_foldera+'/samplea.bam.bai', 'samplea.bam.bai', '.bam.bai',8536],
                      'onlyinA.txt': [t_foldera+'/onlyinA.txt', 'onlyinA.txt', '.txt',0],
                      'no_ext_file': [t_foldera + '/no_ext_file', 'no_ext_file', '', 42],
                      'samplea.caveman_c.annot.vcf.gz': [t_foldera+'/vcf_data/samplea.caveman_c.annot.vcf.gz',
                       'samplea.caveman_c.annot.vcf.gz', '.vcf.gz',2060]}

    format_dir_dictB={
                      'samplea.bam': [t_folderb+'/samplea.bam', 'samplea.bam', '.bam',73060],
                      'samplea.caveman_c.annot.vcf.gz': [t_folderb+'/vcf_data/samplea.caveman_c.annot.vcf.gz',
                      'samplea.caveman_c.annot.vcf.gz', '.vcf.gz',2055],
                      'samplea.bam.bai': [t_folderb+'/samplea.bam.bai', 'samplea.bam.bai', '.bai',8536],
                      'no_ext_file': [t_folderb + '/no_ext_file', 'no_ext_file', '', 42],
                      'onlyinB.txt': [t_folderb+'/onlyinB.txt', 'onlyinB.txt', '.txt',0]}

    common_inAB=['samplea.bam', 'samplea.bam.bai', 'samplea.caveman_c.annot.vcf.gz']

    def test_format_file_input(self):
        my_dir_file=fc.ArchCompare(archive_a=self.t_foldera,archive_b=self.t_filea,json_config=self.t_json,cmp_type=self.cmp_type)
        assert self.file_dict == my_dir_file._format_file_input(self.t_filea),'test_format_file_input OK'

    def test_format_dir_input(self):
        self.maxDiff = None
        my_dir_file=fc.ArchCompare(archive_a=self.t_foldera,archive_b=self.t_filea,json_config=self.t_json,cmp_type=self.cmp_type)
        assert self.format_dir_dictA == my_dir_file._format_dir_input(self.t_foldera),'test_format_dir_input OK'

    def test_format_tar_input(self):
        self.maxDiff = None
        my_tar_tar=fc.ArchCompare(archive_a=self.t_tara,archive_b=self.t_tarb,json_config=self.t_json,cmp_type=self.tar_cmp_type)
        assert self.format_tar_dictA == my_tar_tar._format_tar_input(self.t_tara),'test_format_tar_inputA OK'
        assert self.format_tar_dictB == my_tar_tar._format_tar_input(self.t_tarb),'test_format_tar_inputB OK'

if __name__ == '__main__':
  mytests=TestClass()
  mytests()

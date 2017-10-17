import archCompare.compareArchive as fc
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
    
    configdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config/') 
    t_json=configdir+'fileTypes.json'
    cmp_type='data'
    file_dict={'samplea.caveman_c.annot.vcf.gz':[t_filea,'samplea.caveman_c.annot.vcf.gz','.vcf.gz']}
    
    format_dir_bamdiffA={'samplea.bam': [t_dirbamA+'/samplea.bam', 'samplea.bam', '.bam']}
    format_dir_bamdiffB={'samplea.bam': [t_dirbamB+'/samplea.bam', 'samplea.bam', '.bam']}
    common_files_bamdiff=['samplea.bam']   
    bamdiff_result={'samplea.bam': ['compared', None]}                  
    
   
    format_tar_dictA={
                      'bam': ['testA/samplea.bam', 'samplea.bam', '.bam'], 
                      'bam.bai': ['testA/samplea.bam.bai', 'samplea.bam.bai', '.bai'], 
                      'onlyinA.txt': ['testA/onlyinA.txt', 'onlyinA.txt', '.txt'], 
                      'caveman_c.annot.vcf.gz': ['testA/vcf_data/samplea.caveman_c.annot.vcf.gz', 'samplea.caveman_c.annot.vcf.gz', '.vcf.gz']}
    
    
    format_tar_dictB={
                      'bam': ['testB/samplea.bam', 'samplea.bam', '.bam'],
                      'caveman_c.annot.vcf.gz': ['testB/vcf_data/samplea.caveman_c.annot.vcf.gz', 'samplea.caveman_c.annot.vcf.gz', '.vcf.gz'], 
                      'bam.bai': ['testB/samplea.bam.bai', 'samplea.bam.bai', '.bai'], 
                      'onlyinB.txt': ['testB/onlyinB.txt', 'onlyinB.txt', '.txt']}


 
    format_dir_dictA={
                      'bam': [t_foldera+'/samplea.bam', 'samplea.bam', '.bam'], 
                      'bam.bai': [t_foldera+'/samplea.bam.bai', 'samplea.bam.bai', '.bai'], 
                      'onlyinA.txt': [t_foldera+'/onlyinA.txt', 'onlyinA.txt', '.txt'], 
                      'caveman_c.annot.vcf.gz': [t_foldera+'/vcf_data/samplea.caveman_c.annot.vcf.gz', 'samplea.caveman_c.annot.vcf.gz', '.vcf.gz']}
    
    
    format_dir_dictB={
                      'bam': [t_folderb+'/samplea.bam', 'samplea.bam', '.bam'],
                      'caveman_c.annot.vcf.gz': [t_folderb+'/vcf_data/samplea.caveman_c.annot.vcf.gz', 'samplea.caveman_c.annot.vcf.gz', '.vcf.gz'], 
                      'bam.bai': [t_folderb+'/samplea.bam.bai', 'samplea.bam.bai', '.bai'], 
                      'onlyinB.txt': [t_folderb+'/onlyinB.txt', 'onlyinB.txt', '.txt']}
    
    common_inAB=['samplea.bam', 'samplea.bam.bai', 'samplea.caveman_c.annot.vcf.gz']
    only_inA=['onlyinA.txt']
    only_inB=['onlyinB.txt']
    
    common_files=['bam', 'bam.bai', 'caveman_c.annot.vcf.gz']
    
    name_cmp_dict={'bam.bai': ['compared', 'name'], 'caveman_c.annot.vcf.gz': ['compared', 'name'], 'bam': ['compared', 'name'], 'onlyinA.txt': ['skipped', 'onlyInA'], 'onlyinB.txt': ['skipped', 'onlyInB']}
    
    data_cmp_dict={'bam': ['compared', 'data'], 'bam.bai': ['skipped', 'NoExtInJson'], 'caveman_c.annot.vcf.gz': ['compared', None]}
    checksum_cmp_dict={'bam': ['compared', None], 'bam.bai': ['skipped', 'NoExtInJson'], 'caveman_c.annot.vcf.gz': ['compared', None]}
    
    def test_dir_file_type(self):
        # check input type function 
        my_dir_file=fc.ArchCompare(archive_a=self.t_foldera,archive_b=self.t_filea,json_config=self.t_json,cmp_type=self.cmp_type)
        assert my_dir_file.check_input() == ('dir','file') , 'Directory n file test OK'
        my_dir_tar=fc.ArchCompare(archive_a=self.t_foldera,archive_b=self.t_tara,json_config=self.t_json,cmp_type=self.cmp_type)
        assert ('dir','tar')== my_dir_tar.check_input(),'directory n tar test OK'
        my_tar_tar=fc.ArchCompare(archive_a=self.t_tarb,archive_b=self.t_tara,json_config=self.t_json,cmp_type=self.cmp_type)
        assert ('tar','tar') == my_tar_tar.check_input(),'tar n tar test OK'
        my_dir_dir=fc.ArchCompare(archive_a=self.t_foldera,archive_b=self.t_folderb,json_config=self.t_json,cmp_type=self.cmp_type)
        assert ('dir','dir')== my_dir_dir.check_input(),'directory n directory test OK'
        my_file_file=fc.ArchCompare(archive_a=self.t_filea,archive_b=self.t_fileb,json_config=self.t_json,cmp_type=self.cmp_type)
        assert ('file','file') == my_file_file.check_input(),'file n file test OK'
        
    def test_get_file_metadata(self):
        # test if file paths sub 
        my_dir_file=fc.ArchCompare(archive_a=self.t_foldera,archive_b=self.t_filea,json_config=self.t_json,cmp_type=self.cmp_type)
        assert ('samplea.caveman_c.annot.vcf.gz','.vcf.gz') == my_dir_file._get_file_metadata(self.t_filea),'file metadata test ok'

    def test_format_file_input(self):
        my_dir_file=fc.ArchCompare(archive_a=self.t_foldera,archive_b=self.t_filea,json_config=self.t_json,cmp_type=self.cmp_type)
        assert self.file_dict == my_dir_file._format_file_input(self.t_filea),'test_format_file_input OK'
    
    def test_format_dir_input(self):
        self.maxDiff = None
        my_dir_file=fc.ArchCompare(archive_a=self.t_foldera,archive_b=self.t_filea,json_config=self.t_json,cmp_type=self.cmp_type)
        assert self.format_dir_dictA == my_dir_file._format_dir_input(self.t_foldera),'test_format_dir_input OK'
        
    def test_format_tar_input(self):
        self.maxDiff = None
        my_tar_tar=fc.ArchCompare(archive_a=self.t_tara,archive_b=self.t_tarb,json_config=self.t_json,cmp_type='name')
        assert self.format_tar_dictA == my_tar_tar._format_tar_input(self.t_tara),'test_format_tar_inputA OK'
        assert self.format_tar_dictB == my_tar_tar._format_tar_input(self.t_tarb),'test_format_tar_inputB OK'
        
    def test_get_sets(self):
        my_tar_file=fc.ArchCompare(archive_a=self.t_tara,archive_b=self.t_filea,json_config=self.t_json,cmp_type='name')
        assert self.name_cmp_dict == my_tar_file._get_sets_to_compare(self.format_dir_dictA,self.format_dir_dictB),'test_get_sets OK'
        
    #def test_do_comparison(self):
    #    self.maxDiff = None
    #    my_tar_tar_cmp=fc.ArchCompare(archive_a=self.t_tara,archive_b=self.t_tarb,json_config=self.t_json,cmp_type='data')
    #    assert self.data_cmp_dict == my_tar_tar_cmp._do_comparison(self.format_dir_dictA,self.format_dir_dictB,self.common_files),'test_do_comparison OK'
    
    #def test_bamdiff(self):
    #    self.maxDiff = None
    #    my_dir_dir_bam=fc.ArchCompare(archive_a=self.t_dirbamA,archive_b=self.t_dirbamB,json_config=self.t_json,cmp_type='data')
    #    assert self.bamdiff_result == my_dir_dir_bam._do_comparison(self.format_dir_bamdiffA,self.format_dir_bamdiffB,self.common_files_bamdiff),'test_do_BamComparison OK'
    def test_checksum(self):
        self.maxDiff = None
        my_dir_dir_checksum=fc.ArchCompare(archive_a=self.t_foldera,archive_b=self.t_folderb,json_config=self.t_json,cmp_type='checksum')
        assert self.checksum_cmp_dict == my_dir_dir_checksum._do_comparison(self.format_dir_dictA,self.format_dir_dictB,self.common_files),'test_do_BamComparison OK'

if __name__ == '__main__':
  mytests=TestClass()
  mytests()



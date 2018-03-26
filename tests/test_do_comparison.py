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

    format_dir_dictA={
                  'samplea.bam': [t_foldera+'/samplea.bam', 'samplea.bam', '.bam',73060],
                  'samplea.bam.bai': [t_foldera+'/samplea.bam.bai', 'samplea.bam.bai', '.bam.bai',8536],
                  'onlyinA.txt': [t_foldera+'/onlyinA.txt', 'onlyinA.txt', '.txt',0],
                  'samplea.caveman_c.annot.vcf.gz': [t_foldera+'/vcf_data/samplea.caveman_c.annot.vcf.gz',
                   'samplea.caveman_c.annot.vcf.gz', '.vcf.gz',2060]}

    format_dir_dictB={
                  'samplea.bam': [t_folderb+'/samplea.bam', 'samplea.bam', '.bam',73060],
                  'samplea.caveman_c.annot.vcf.gz': [t_folderb+'/vcf_data/samplea.caveman_c.annot.vcf.gz',
                  'samplea.caveman_c.annot.vcf.gz', '.vcf.gz',2055],
                  'samplea.bam.bai': [t_folderb+'/samplea.bam.bai', 'samplea.bam.bai', '.bai',8536],
                  'onlyinB.txt': [t_folderb+'/onlyinB.txt', 'onlyinB.txt', '.txt',0]}

    common_files=['samplea.bam', 'samplea.bam.bai', 'samplea.caveman_c.annot.vcf.gz']

    name_cmp_dict={('name','samplea.bam.bai'): 'PASS',
                    ('name','samplea.caveman_c.annot.vcf.gz'): 'PASS',
                    ('name','samplea.bam'): 'PASS'
                    }
    checksum_cmp_dict={('checksum','samplea.bam.bai'): 'FAIL',
                ('checksum','samplea.caveman_c.annot.vcf.gz'): 'FAIL',
                ('checksum','samplea.bam'): 'FAIL'
                    }
    size_cmp_dict={('size','samplea.bam.bai'): 'PASS',
                ('size','samplea.caveman_c.annot.vcf.gz'): 'FAIL',
                ('size','samplea.bam'): 'PASS'
                    }



    def test_checksum(self):
        self.maxDiff = None
        my_tar_tar_cmp=fc.ArchCompare(archive_a=self.t_tara,archive_b=self.t_tarb,json_config=self.t_json,cmp_type=['name'])
        assert self.name_cmp_dict == my_tar_tar_cmp._do_comparison(self.format_dir_dictA,self.format_dir_dictB,self.common_files),'test_do_nameComparison OK'

    def test_checksum(self):
        self.maxDiff = None
        my_dir_dir_checksum=fc.ArchCompare(archive_a=self.t_foldera,archive_b=self.t_folderb,json_config=self.t_json,cmp_type=['checksum'])
        assert self.checksum_cmp_dict == my_dir_dir_checksum._do_comparison(self.format_dir_dictA,self.format_dir_dictB,self.common_files),'test_do_checksumComparison OK'

    def test_size(self):
        self.maxDiff = None
        my_dir_dir_size=fc.ArchCompare(archive_a=self.t_foldera,archive_b=self.t_folderb,json_config=self.t_json,cmp_type=['size'])
        assert self.size_cmp_dict == my_dir_dir_size._do_comparison(self.format_dir_dictA,self.format_dir_dictB,self.common_files),'test_do_sizeComparison OK'


if __name__ == '__main__':
  mytests=TestClass()
  mytests()

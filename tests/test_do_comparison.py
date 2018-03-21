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
    configdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../archCompare/config/')
    t_json=configdir+'compareMethods.json'
    cmp_type=['data']

    format_dir_bamdiffA={'samplea.bam': [t_dirbamA+'/samplea.bam', 'samplea.bam', '.bam',73060]}
    format_dir_bamdiffB={'samplea.bam': [t_dirbamB+'/samplea.bam', 'samplea.bam', '.bam',73060]}
    common_files_bamdiff=['samplea.bam']
    bamdiff_result={('diffs','samplea.bam'): 'N'}

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

    name_cmp_dict={('name','samplea.bam.bai'): 'Y',
                    ('name','samplea.caveman_c.annot.vcf.gz'): 'Y',
                    ('name','samplea.bam'): 'Y'
                    }
    data_cmp_dict={('diffs','samplea.bam.bai'): 'NoExtInJson',
                ('diffs','samplea.caveman_c.annot.vcf.gz'): 'Y',
                ('diffs','samplea.bam'): 'Y',
                ('skipped','onlyinA.txt'): 'onlyInA',
                ('skipped','onlyinB.txt'): 'onlyInB'}
    checksum_cmp_dict={('checksum','samplea.bam.bai'): 'N',
                ('checksum','samplea.caveman_c.annot.vcf.gz'): 'N',
                ('checksum','samplea.bam'): 'N'
                    }
    size_cmp_dict={('size','samplea.bam.bai'): 'Y',
                ('size','samplea.caveman_c.annot.vcf.gz'): 'N',
                ('size','samplea.bam'): 'Y'
                    }



    @pytest.mark.skipif("TRAVIS" in os.environ and os.environ["TRAVIS"] == "true", reason="Skipping this test on Travis CI.")
    def test_do_comparison(self):
        self.maxDiff = None
        my_tar_tar_cmp=fc.ArchCompare(archive_a=self.t_tara,archive_b=self.t_tarb,json_config=self.t_json,cmp_type=['name'])
        assert self.name_cmp_dict == my_tar_tar_cmp._do_comparison(self.format_dir_dictA,self.format_dir_dictB,self.common_files),'test_do_nameComparison OK'

    @pytest.mark.skipif("TRAVIS" in os.environ and os.environ["TRAVIS"] == "true", reason="Skipping this test on Travis CI.")
    def test_bamdiff(self):
        self.maxDiff = None
        my_dir_dir_bam=fc.ArchCompare(archive_a=self.t_dirbamA,archive_b=self.t_dirbamB,json_config=self.t_json,cmp_type=['diffs'])
        assert self.bamdiff_result == my_dir_dir_bam._do_comparison(self.format_dir_bamdiffA,self.format_dir_bamdiffB,self.common_files_bamdiff),'test_do_BamComparison OK'

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

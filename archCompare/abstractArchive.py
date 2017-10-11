from abc import ABC, abstractmethod

class AbstractCompare(ABC):
    def __init__(self,**kwargs):
        self.file_a    =kwargs['archive_a']
        self.file_b    = kwargs['archive_b']
        self.json_file = kwargs['json_config']
        self.cmp_type  = kwargs.get('cmp_type',None)
        self.get_config()
        super().__init__()
    
    @abstractmethod
    def check_input(self):
        pass
        
    @abstractmethod
    def get_config(self):
        pass
    
    if __name__ == '__main__':
        print ('Running as python script')
    




import fsspec
import os
from ipfsspec.asyn import AsyncIPFSFileSystem
from fsspec import register_implementation
import asyncio
import json
import pickle
import io
from transformers import AutoModel, AutoTokenizer
from datasets import load_dataset, Dataset
import os, sys
sys.path.append(os.getenv('PWD'))

from algocean.client.local import LocalModule


# register_implementation(IPFSFileSystem.protocol, IPFSFileSystem)
# register_implementation(AsyncIPFSFileSystem.protocol, AsyncIPFSFileSystem)

# with fsspec.open("ipfs://QmZ4tDuvesekSs4qM5ZBKpXiZGun7S2CYtEZRB3DYXkjGx", "r") as f:
#     print(f.read())

class ClientModule:
    def __init__(self):
        self.local = fsspec.filesystem("file")
        self.fs = AsyncIPFSFileSystem()
    
register_implementation(AsyncIPFSFileSystem.protocol, AsyncIPFSFileSystem)

    
    
class IPFSModule(AsyncIPFSFileSystem):
    
    def __init__(self, config={}):
        AsyncIPFSFileSystem.__init__(self)
        self.local =  LocalModule()

    @property
    def tmp_root_path(self):
        return f'/tmp/algocean/{self.id}'
    
    def get_temp_path(self, path):
        tmp_path = os.path.join(self.tmp_root_path, path)
        if not os.path.exists(self.tmp_root_path):
            self.local.makedirs(os.path.dirname(path), exist_ok=True)
        
        return tmp_path
    
    
    def save_model(self, model, path:str):

        
        # self.mkdir(path, create_parents=True)
        
        tmp_path = self.get_temp_path(path=path)
        model.save_pretrained(tmp_path)
        self.mkdirs(path)
        
        cid = self.force_put(lpath=tmp_path, rpath=path, max_trials=10)
        self.local.rm(tmp_path,  recursive=True)
        
        return cid

    def save_tokenizer(self, tokenizer, path:str):

        
        # self.mkdir(path, create_parents=True)
        
        tmp_path = self.get_temp_path(path=path)
        tokenizer.save_pretrained(tmp_path)
        self.mkdirs(path)
        
        cid = self.force_put(lpath=tmp_path, rpath=path, max_trials=10)
        self.local.rm(tmp_path,  recursive=True)
        
        return cid

    

    def load_tokenizer(self,  path:str):
        tmp_path = self.get_temp_path(path=path)
        self.get(lpath=tmp_path, rpath=path )
        model = AutoTokenizer.from_pretrained(tmp_path)
        self.local.rm(tmp_path,  recursive=True)
        return model


    
    def load_model(self,  path:str):
        tmp_path = self.get_temp_path(path=path)
        self.get(lpath=tmp_path, rpath=path )
        model = AutoModel.from_pretrained(tmp_path)
        # self.fs.local.rm(tmp_path,  recursive=True)
        return model


    def load_dataset(self, path):
        tmp_path = self.get_temp_path(path=path)
        self.get(lpath=tmp_path, rpath=path )
        dataset = Dataset.load_from_disk(tmp_path)
        # self.fs.local.rm(tmp_path,  recursive=True)
        
        return dataset


    def save_dataset(self, dataset, path:str):
        tmp_path = self.get_temp_path(path=path)
        dataset = dataset.save_to_disk(tmp_path)
        cid = self.force_put(lpath=tmp_path, rpath=path, max_trials=10)
        # self.fs.local.rm(tmp_path,  recursive=True)
        return cid



    
    def put_json(self, data, path='json_placeholder.pkl'):
        tmp_path = self.get_temp_path(path=path)
        self.local.put_json(path=tmp_path, data=data)
        cid = self.force_put(lpath=tmp_path, rpath=path, max_trials=10)
        self.local.rm(tmp_path)
        return cid

    def put_pickle(self, data, path='/pickle_placeholder.pkl'):
        tmp_path = self.get_temp_path(path=path)
        self.local.put_pickle(path=tmp_path, data=data)
        cid = self.force_put(lpath=tmp_path, rpath=path, max_trials=10)
        self.local.rm(tmp_path)
        return cid
    def get_pickle(self, path):
        return pickle.loads(self.cat(path))

    def get_json(self, path):
        return json.loads(self.cat(path))

          
    def force_put(self, lpath, rpath, max_trials=10):
        trial_count = 0
        cid = None
        while trial_count<max_trials:
            try:
                cid= self.put(lpath=lpath, rpath=rpath, recursive=True)
                break
            except fsspec.exceptions.FSTimeoutError:
                trial_count += 1
                print(f'Failed {trial_count}/{max_trials}')
                
        return cid

    @property
    def id(self):
        return type(self).__name__ +':'+ str(hash(self))

    @property
    def name(self):
        return self.id


if __name__ == '__main__':
    import ipfspy
    import streamlit as st

    
    module = IPFSModule()
    st.write(module.name)


    import torch


    dataset = load_dataset('glue', 'mnli', split='train')
    st.write(module.save_dataset(dataset=dataset,path= '/dog'))
    # cid = module.put_pickle(path='/bro/test.json', data={'yo':'fam'})
    # st.write(module.get_pickle(cid))

    st.write(module.ls('/dog'))
    # st.write(module.ls('/'))
    # st.write(module..get_object('/tmp/test.jsonjw4ij6u'))





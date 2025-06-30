import os
from pyodm import Node
import glob
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

class Node_processing:

    def __init__(self,image_dir):
        self.start_api = Node('nodeodm', 3000)#
        self.task = self.create_node_task(image_folder=image_dir)
        uuid = self.task.uuid
        
    
    def create_node_task(self,image_folder):
        task = self.start_api.create_task(glob.glob(f"{image_folder}/*.JPG"), {'dsm': True,'dtm':True,'odm':True})
        return task
    
    def download_task(self,path):
        self.task.wait_for_completion()
        self.task.download_assets(path) 
        
               
    def get_uuid(self):
        return self.task.uuid
    
    def get_tasks(self,api):
        return self.start_api.get_task(api)
    
    def task_info(self):
        info = self.start_api.info()
        #api_version = info.version
        #queue_count = info.task_queue_count
        #max_images = info.max_images
        #engine_version = info.engine_version
        #engine = info.engine
        
        return info
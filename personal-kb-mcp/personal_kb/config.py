import os  
import pathlib  
from typing import Optional  

class Config:  
    def __init__(self):  
        # 数据存储的基本目录  
        self.data_dir = pathlib.Path.home() / ".personal_kb"  
        self.data_dir.mkdir(exist_ok=True)  
        
        # 数据库路径  
        self.db_path = self.data_dir / "knowledge_base.db"  
        
        # 服务器配置  
        self.server_name = "Personal Knowledge Base"  
        self.server_version = "0.1.0"  
        
        # 智谱API配置  
        self.zhipu_api_key = os.environ.get("ZHIPU_API_KEY", "")  
        self.zhipu_model = os.environ.get("ZHIPU_MODEL", "glm-4")  
        
        # 如果环境变量存在则加载  
        if os.environ.get("PERSONALKB_DB_PATH"):  
            self.db_path = pathlib.Path(os.environ.get("PERSONALKB_DB_PATH"))  

config = Config()  
import os  
import pathlib  
from typing import Optional  

class Config:  
    def __init__(self):  
        
        self.current_file_path = os.path.abspath(__file__)
        print(f"当前配置文件路径: {self.current_file_path}")
        # 数据存储的基本目录  
            # 确保主目录是 /path/to/personal-kb-mcp
        # 原代码存在问题，`os.path.abspath(__file__)` 返回的是字符串，没有 `parent()` 方法。
        # 应该先将其转换为 `pathlib.Path` 对象，再调用 `parent` 属性。
        self.current_file_path = pathlib.Path(self.current_file_path)
        self.project_dir = self.current_file_path.parent.parent
        print(f"项目目录: {self.project_dir}")
        self.data_dir = self.project_dir / "data"
        self.data_dir.mkdir(exist_ok=True)  
        
        # 数据库路径  
        self.db_path = self.data_dir / "knowledge_base.db"  
        
        print(f"数据库路径: {self.db_path}")
        
        # 服务器配置  
        self.server_name = "Personal Knowledge Base"  
        self.server_version = "0.1.0"  
        
        # 智谱API配置  
        self.zhipu_api_key = os.environ.get("ZHIPU_API_KEY", "")  
        self.zhipu_model = os.environ.get("ZHIPU_MODEL", "glm-4-flash")  
        
        # 如果环境变量存在则加载  
        if os.environ.get("PERSONALKB_DB_PATH"):  
            self.db_path = pathlib.Path(os.environ.get("PERSONALKB_DB_PATH"))  

config = Config()  
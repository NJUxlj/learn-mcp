"""  
数据模型定义模块。  
使用Pydantic模型定义数据结构，用于输入验证和输出格式化。  
"""  

from pydantic import BaseModel, Field  
from typing import List, Optional  
from datetime import datetime  

# 输入模型  
class CreateNoteInput(BaseModel):  
    """创建笔记的输入模型"""  
    title: str = Field(..., description="笔记标题")  
    content: str = Field(..., description="笔记内容")  
    tags: Optional[List[str]] = Field(None, description="可选的要与笔记关联的标签列表")  

class UpdateNoteInput(BaseModel):  
    """更新笔记的输入模型"""  
    note_id: int = Field(..., description="要更新的笔记ID")  
    title: Optional[str] = Field(None, description="笔记的新标题")  
    content: Optional[str] = Field(None, description="笔记的新内容")  
    tags: Optional[List[str]] = Field(None, description="要与笔记关联的新标签列表")  

class DeleteNoteInput(BaseModel):  
    """删除笔记的输入模型"""  
    note_id: int = Field(..., description="要删除的笔记ID")  

class GetNoteInput(BaseModel):  
    """获取笔记的输入模型"""  
    note_id: int = Field(..., description="要检索的笔记ID")  

class ListNotesInput(BaseModel):  
    """列出笔记的输入模型"""  
    limit: Optional[int] = Field(10, description="要返回的最大笔记数")  
    offset: Optional[int] = Field(0, description="要跳过的笔记数")  

class SearchNotesInput(BaseModel):  
    """搜索笔记的输入模型"""  
    query: str = Field(..., description="搜索查询")  
    limit: Optional[int] = Field(10, description="要返回的最大结果数")  

class GetNotesByTagInput(BaseModel):  
    """按标签获取笔记的输入模型"""  
    tag_name: str = Field(..., description="要筛选的标签名称")  
    limit: Optional[int] = Field(10, description="要返回的最大笔记数")  
    offset: Optional[int] = Field(0, description="要跳过的笔记数")  

class RenameTagInput(BaseModel):  
    """重命名标签的输入模型"""  
    old_name: str = Field(..., description="当前标签名称")  
    new_name: str = Field(..., description="新标签名称")  

class DeleteTagInput(BaseModel):  
    """删除标签的输入模型"""  
    tag_name: str = Field(..., description="要删除的标签名称")  

# 输出模型  
class NoteOutput(BaseModel):  
    """笔记输出模型"""  
    id: int  
    title: str  
    content: str  
    created_at: str  
    updated_at: str  
    tags: List[str]  

class TagOutput(BaseModel):  
    """标签输出模型"""  
    id: int  
    name: str  
    note_count: int  

class ListNotesOutput(BaseModel):  
    """笔记列表输出模型"""  
    notes: List[NoteOutput]  

class ListTagsOutput(BaseModel):  
    """标签列表输出模型"""  
    tags: List[TagOutput]  

class SuccessOutput(BaseModel):  
    """成功操作输出模型"""  
    success: bool  
    message: str  

class DatabaseStatsOutput(BaseModel):  
    """数据库统计输出模型"""  
    note_count: int  
    tag_count: int  
    latest_notes: List[dict]  
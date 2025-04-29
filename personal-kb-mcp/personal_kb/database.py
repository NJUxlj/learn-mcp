"""  
数据库操作模块。  
提供知识库的存储、检索、修改和删除功能。  
"""  

from sqlalchemy import Column, Integer, String, Text, DateTime, Table, ForeignKey, create_engine, func  
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import relationship, sessionmaker, Session  
import datetime  
import os  
import pathlib  
from typing import List, Dict, Any, Optional  

from .config import config

Base = declarative_base()  

# 笔记和标签的多对多关联表  
note_tag_association = Table(  
    'note_tag_association',  
    Base.metadata,  
    Column('note_id', Integer, ForeignKey('notes.id')),  
    Column('tag_id', Integer, ForeignKey('tags.id'))  
)  

class Note(Base):  
    """笔记模型"""  
    __tablename__ = 'notes'  
    
    id = Column(Integer, primary_key=True)  
    title = Column(String(255), nullable=False)  
    content = Column(Text, nullable=False)  
    created_at = Column(DateTime, default=datetime.datetime.utcnow)  
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)  
    
    # 与Tag的关系（通过关联表）  
    tags = relationship("Tag", secondary=note_tag_association, back_populates="notes")  
    
    def __repr__(self):  
        return f"<Note(id={self.id}, title='{self.title}')>"  

    def to_dict(self):  
        """将笔记转换为字典表示"""  
        return {  
            "id": self.id,  
            "title": self.title,  
            "content": self.content,  
            "created_at": self.created_at.isoformat(),  
            "updated_at": self.updated_at.isoformat(),  
            "tags": [tag.name for tag in self.tags]  
        }  

class Tag(Base):  
    """标签模型"""  
    __tablename__ = 'tags'  
    
    id = Column(Integer, primary_key=True)  
    name = Column(String(50), nullable=False, unique=True)  
    
    # 与Note的关系（通过关联表）  
    notes = relationship("Note", secondary=note_tag_association, back_populates="tags")  
    
    def __repr__(self):  
        return f"<Tag(id={self.id}, name='{self.name}')>"  

    def to_dict(self):  
        """将标签转换为字典表示"""  
        return {  
            "id": self.id,  
            "name": self.name,  
            "note_count": len(self.notes)  
        }  

class Database:  
    """数据库操作类"""  
    def __init__(self, db_path=None):  
        """  
        初始化数据库连接  
        
        Args:  
            db_path: SQLite数据库文件路径，如果为None则使用默认路径  
        """  
        if db_path is None:  
            # 在用户主目录中使用默认路径  
            data_dir = config.project_dir / ".personal_kb"  
            data_dir.mkdir(exist_ok=True)  
            db_path = data_dir / "knowledge_base.db"  
        
        self.db_path = db_path  
        self.engine = create_engine(f"sqlite:///{db_path}")  
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)  
        
        # 如果表不存在则创建  
        Base.metadata.create_all(self.engine)  
    
    def get_session(self) -> Session:  
        """获取新的数据库会话"""  
        return self.SessionLocal()  
    
    # 笔记操作  
    def create_note(self, title: str, content: str, tags: Optional[List[str]] = None) -> Dict[str, Any]:  
        """  
        创建新笔记，可选择添加标签  
        
        Args:  
            title: 笔记标题  
            content: 笔记内容  
            tags: 可选的标签列表  
            
        Returns:  
            创建的笔记信息  
        """  
        with self.get_session() as session:  
            # 创建新笔记  
            note = Note(title=title, content=content)  
            
            # 处理标签  
            if tags:  
                for tag_name in tags:  
                    # 检查标签是否存在  
                    tag = session.query(Tag).filter(Tag.name == tag_name).first()  
                    if not tag:  
                        # 如果标签不存在则创建  
                        tag = Tag(name=tag_name)  
                        session.add(tag)  
                    note.tags.append(tag)  
            
            session.add(note)  
            session.commit()  
            session.refresh(note)  
            return note.to_dict()  
    
    def get_note(self, note_id: int) -> Optional[Dict[str, Any]]:  
        """  
        通过ID获取笔记  
        
        Args:  
            note_id: 笔记ID  
            
        Returns:  
            笔记信息或None（如果不存在）  
        """  
        with self.get_session() as session:  
            note = session.query(Note).filter(Note.id == note_id).first()  
            if note:  
                return note.to_dict()  
            return None  
    
    def update_note(self, note_id: int, title: Optional[str] = None,   
                   content: Optional[str] = None, tags: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:  
        """  
        更新笔记  
        
        Args:  
            note_id: 要更新的笔记ID  
            title: 可选的新标题  
            content: 可选的新内容  
            tags: 可选的新标签列表  
            
        Returns:  
            更新后的笔记信息或None（如果不存在）  
        """  
        with self.get_session() as session:  
            note = session.query(Note).filter(Note.id == note_id).first()  
            if not note:  
                return None  
            
            if title is not None:  
                note.title = title  
            if content is not None:  
                note.content = content  
            
            # 如果提供了标签则更新  
            if tags is not None:  
                # 清除所有现有标签  
                note.tags.clear()  
                
                # 添加新标签  
                for tag_name in tags:  
                    # 检查标签是否存在  
                    tag = session.query(Tag).filter(Tag.name == tag_name).first()  
                    if not tag:  
                        # 如果标签不存在则创建  
                        tag = Tag(name=tag_name)  
                        session.add(tag)  
                    note.tags.append(tag)  
            
            note.updated_at = datetime.datetime.utcnow()  
            session.commit()  
            session.refresh(note)  
            return note.to_dict()  
    
    def delete_note(self, note_id: int) -> bool:  
        """  
        通过ID删除笔记  
        
        Args:  
            note_id: 要删除的笔记ID  
            
        Returns:  
            是否成功删除  
        """  
        with self.get_session() as session:  
            note = session.query(Note).filter(Note.id == note_id).first()  
            if not note:  
                return False  
            session.delete(note)  
            session.commit()  
            return True  
    
    def list_notes(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:  
        """  
        列出笔记（分页）  
        
        Args:  
            limit: 最大返回数量  
            offset: 跳过数量  
            
        Returns:  
            笔记列表  
        """  
        with self.get_session() as session:  
            notes = session.query(Note).order_by(Note.updated_at.desc()).limit(limit).offset(offset).all()  
            return [note.to_dict() for note in notes]  
    
    def search_notes(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:  
        """  
        通过标题或内容搜索笔记  
        
        Args:  
            query: 搜索词  
            limit: 最大返回结果数  
            
        Returns:  
            匹配的笔记列表  
        """  
        with self.get_session() as session:  
            # 使用LIKE运算符的简单搜索实现  
            search_term = f"%{query}%"  
            notes = session.query(Note).filter(  
                (Note.title.like(search_term)) | (Note.content.like(search_term))  
            ).order_by(Note.updated_at.desc()).limit(limit).all()  
            return [note.to_dict() for note in notes]  
    
    # 标签操作  
    def list_tags(self) -> List[Dict[str, Any]]:  
        """  
        列出所有标签  
        
        Returns:  
            标签列表  
        """  
        with self.get_session() as session:  
            tags = session.query(Tag).order_by(Tag.name).all()  
            return [tag.to_dict() for tag in tags]  
    
    def get_notes_by_tag(self, tag_name: str, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:  
        """  
        获取具有特定标签的笔记  
        
        Args:  
            tag_name: 要筛选的标签  
            limit: 最大返回笔记数  
            offset: 跳过数量  
            
        Returns:  
            带有指定标签的笔记列表  
        """  
        with self.get_session() as session:  
            tag = session.query(Tag).filter(Tag.name == tag_name).first()  
            if not tag:  
                return []  
            
            # 获取分页笔记  
            notes = tag.notes[offset:offset+limit]  
            return [note.to_dict() for note in notes]  
    
    def rename_tag(self, old_name: str, new_name: str) -> bool:  
        """  
        重命名标签  
        
        Args:  
            old_name: 当前标签名称  
            new_name: 新标签名称  
            
        Returns:  
            是否成功重命名  
        """  
        with self.get_session() as session:  
            # 检查旧标签是否存在  
            old_tag = session.query(Tag).filter(Tag.name == old_name).first()  
            if not old_tag:  
                return False  
            
            # 检查新标签名称是否已存在  
            existing_tag = session.query(Tag).filter(Tag.name == new_name).first()  
            if existing_tag:  
                # 合并标签 - 将旧标签的所有笔记分配给新标签  
                for note in old_tag.notes:  
                    if note not in existing_tag.notes:  
                        existing_tag.notes.append(note)  
                session.delete(old_tag)  
            else:  
                # 简单重命名  
                old_tag.name = new_name  
            
            session.commit()  
            return True  
    
    def delete_tag(self, tag_name: str) -> bool:  
        """  
        删除标签  
        
        Args:  
            tag_name: 要删除的标签名称  
            
        Returns:  
            是否成功删除  
        """  
        with self.get_session() as session:  
            tag = session.query(Tag).filter(Tag.name == tag_name).first()  
            if not tag:  
                return False  
            session.delete(tag)  
            session.commit()  
            return True  

    def get_database_stats(self) -> Dict[str, Any]:  
        """  
        获取数据库统计信息  
        
        Returns:  
            数据库统计信息  
        """  
        with self.get_session() as session:  
            note_count = session.query(func.count(Note.id)).scalar()  
            tag_count = session.query(func.count(Tag.id)).scalar()  
            latest_notes = session.query(Note).order_by(Note.created_at.desc()).limit(5).all()  
            
            return {  
                "note_count": note_count,  
                "tag_count": tag_count,  
                "latest_notes": [  
                    {"id": note.id, "title": note.title, "created_at": note.created_at.isoformat()}  
                    for note in latest_notes  
                ]  
            }  
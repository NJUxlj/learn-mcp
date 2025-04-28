"""  
工具函数模块。  
提供各种辅助函数用于解析和格式化内容。  
"""  

import re  
from typing import List, Dict, Any  
from datetime import datetime  
import json  

def extract_tags_from_content(content: str) -> List[str]:  
    """  
    从内容中提取hashtag标签  
    
    Args:  
        content: 要解析的文本内容  
        
    Returns:  
        提取的标签列表  
    """  
    # 匹配以#开头并包含字母、数字、下划线和中文字符的标签  
    hashtag_pattern = r'#([a-zA-Z0-9_\u4e00-\u9fff]+)'  
    tags = re.findall(hashtag_pattern, content)  
    return list(set(tags))  # 移除重复项  

def format_note_for_display(note: Dict[str, Any]) -> str:  
    """  
    格式化笔记以便美观显示  
    
    Args:  
        note: 笔记数据字典  
        
    Returns:  
        格式化的笔记内容（Markdown格式）  
    """  
    header = f"# {note['title']}\n\n"  
    
    # 格式化日期时间  
    created_at = parse_iso_date(note['created_at'])  
    updated_at = parse_iso_date(note['updated_at'])  
    
    created_str = created_at.strftime("%Y-%m-%d %H:%M:%S") if created_at else note['created_at'][:19]  
    updated_str = updated_at.strftime("%Y-%m-%d %H:%M:%S") if updated_at else note['updated_at'][:19]  
    
    meta = f"创建时间: {created_str} | 更新时间: {updated_str}\n"  
    
    # 格式化标签  
    tags = " ".join([f"#{tag}" for tag in note['tags']]) if note['tags'] else ""  
    if tags:  
        tags = f"\n标签: {tags}\n"  
    
    content = note['content']  
    
    # 组合所有内容  
    return f"{header}{meta}{tags}\n{content}"  

def parse_iso_date(date_string: str) -> datetime:  
    """  
    解析ISO格式的日期字符串  
    
    Args:  
        date_string: ISO格式的日期字符串  
        
    Returns:  
        datetime对象或None（如果解析失败）  
    """  
    try:  
        return datetime.fromisoformat(date_string.replace('Z', '+00:00'))  
    except (ValueError, AttributeError):  
        return None  

def summarize_content(content: str, max_length: int = 100) -> str:  
    """  
    创建内容摘要  
    
    Args:  
        content: 要摘要的内容  
        max_length: 最大长度  
        
    Returns:  
        摘要内容  
    """  
    if len(content) <= max_length:  
        return content  
    
    # 查找最后一个完整单词的位置  
    last_space = content[:max_length].rfind(' ')  
    if last_space > 0:  
        return content[:last_space] + "..."  
    return content[:max_length] + "..."  

def format_json(obj: Any) -> str:  
    """  
    格式化JSON对象  
    
    Args:  
        obj: 要格式化的对象  
        
    Returns:  
        格式化的JSON字符串  
    """  
    return json.dumps(obj, ensure_ascii=False, indent=2)  

def sanitize_tag_name(tag_name: str) -> str:  
    """  
    清理标签名称  
    
    Args:  
        tag_name: 原始标签名称  
        
    Returns:  
        清理后的标签名称  
    """  
    # 移除前导#（如果存在）  
    if tag_name.startswith('#'):  
        tag_name = tag_name[1:]  
    
    # 删除无效字符，只保留字母、数字、下划线和中文字符  
    sanitized = re.sub(r'[^\w\u4e00-\u9fff]', '', tag_name)  
    
    return sanitized  
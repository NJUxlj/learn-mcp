# MCP服务器实现
"""  
MCP服务器实现。  
提供了一个Model Context Protocol服务器，允许AI模型与知识库交互。  
"""  

import typer  
from fastmcp import FastMCP  
from rich.console import Console  
from rich import print as rprint  
import logging  
import sys  
import os  
from pathlib import Path  
import json  

from .database import Database  
from .schema import (  
    CreateNoteInput, UpdateNoteInput, DeleteNoteInput, GetNoteInput,  
    ListNotesInput, SearchNotesInput, GetNotesByTagInput, RenameTagInput,  
    DeleteTagInput  
)  
from .config import config  
from .utils import extract_tags_from_content, format_note_for_display  

# 设置命令行应用  
app = typer.Typer()  
console = Console()  

# 设置日志  
logging.basicConfig(  
    level=logging.INFO,  
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  
    handlers=[  
        logging.StreamHandler(sys.stdout)  
    ]  
)  
logger = logging.getLogger("personalkb")  

def create_mcp_server(db_path=None):  
    """  
    创建并配置MCP服务器  
    
    Args:  
        db_path: 可选的数据库路径  
        
    Returns:  
        配置好的MCP服务器  
    """  
    # 初始化数据库  
    db = Database(db_path=db_path or config.db_path)  
    
    # 创建MCP服务器  
    mcp_server = FastMCP(  
        title=config.server_name,  
        version=config.server_version,  
        description="一个支持智谱API的个人知识库"  
    )  
    
    # 定义MCP工具/函数  
    
    @mcp_server.tool()  
    def create_note(title: str, content: str, tags: list[str] = None) -> dict:  
        """  
        在知识库中创建新笔记  
        
        Args:  
            title: 笔记标题  
            content: 笔记内容  
            tags: 可选的要与笔记关联的标签列表  
                
        Returns:  
            创建的笔记信息  
        """  
        # 如果未提供标签但内容中包含标签，则自动提取标签  
        if tags is None and '#' in content:  
            tags = extract_tags_from_content(content)  
            
        note = db.create_note(title=title, content=content, tags=tags)  
        logger.info(f"创建笔记: {title} (ID: {note['id']})")  
        return note  
    
    @mcp_server.tool()  
    def get_note(note_id: int) -> dict:  
        """  
        通过ID检索笔记  
        
        Args:  
            note_id: 要检索的笔记ID  
            
        Returns:  
            笔记信息  
        """  
        note = db.get_note(note_id=note_id)  
        if not note:  
            return {"error": f"未找到ID为{note_id}的笔记"}  
        return note  
    
    @mcp_server.tool()  
    def update_note(note_id: int, title: str = None, content: str = None, tags: list[str] = None) -> dict:  
        """  
        更新现有笔记  
        
        Args:  
            note_id: 要更新的笔记ID  
            title: 笔记的可选新标题  
            content: 笔记的可选新内容  
            tags: 可选的新标签列表  
            
        Returns:  
            更新后的笔记信息  
        """  
        # 如果提供了内容但未提供标签，并且内容中包含标签，则自动提取标签  
        if content is not None and tags is None and '#' in content:  
            tags = extract_tags_from_content(content)  
            
        note = db.update_note(note_id=note_id, title=title, content=content, tags=tags)  
        if not note:  
            return {"error": f"未找到ID为{note_id}的笔记"}  
        logger.info(f"更新笔记ID: {note_id}")  
        return note  
    
    @mcp_server.tool()  
    def delete_note(note_id: int) -> dict:  
        """  
        通过ID删除笔记  
        
        Args:  
            note_id: 要删除的笔记ID  
            
        Returns:  
            成功状态  
        """  
        success = db.delete_note(note_id=note_id)  
        if not success:  
            return {"success": False, "message": f"未找到ID为{note_id}的笔记"}  
        logger.info(f"删除笔记ID: {note_id}")  
        return {"success": True, "message": f"成功删除ID为{note_id}的笔记"}  
    
    @mcp_server.tool()  
    def list_notes(limit: int = 10, offset: int = 0) -> dict:  
        """  
        列出笔记（分页）  
        
        Args:  
            limit: 要返回的最大笔记数  
            offset: 要跳过的笔记数  
            
        Returns:  
            笔记列表  
        """  
        notes = db.list_notes(limit=limit, offset=offset)  
        return {"notes": notes}  
    
    @mcp_server.tool()  
    def search_notes(query: str, limit: int = 10) -> dict:  
        """  
        通过标题或内容搜索笔记  
        
        Args:  
            query: 搜索词  
            limit: 要返回的最大结果数  
            
        Returns:  
            匹配笔记列表  
        """  
        notes = db.search_notes(query=query, limit=limit)  
        logger.info(f"搜索 '{query}'，找到 {len(notes)} 个结果")  
        return {"notes": notes}  
    
    @mcp_server.tool()  
    def list_tags() -> dict:  
        """  
        列出知识库中的所有标签  
        
        Returns:  
            标签列表  
        """  
        tags = db.list_tags()  
        return {"tags": tags}  
    
    @mcp_server.tool()  
    def get_notes_by_tag(tag_name: str, limit: int = 10, offset: int = 0) -> dict:  
        """  
        获取具有特定标签的笔记  
        
        Args:  
            tag_name: 要筛选的标签  
            limit: 要返回的最大笔记数  
            offset: 要跳过的笔记数  
            
        Returns:  
            具有指定标签的笔记列表  
        """  
        notes = db.get_notes_by_tag(tag_name=tag_name, limit=limit, offset=offset)  
        logger.info(f"检索到 {len(notes)} 个带有标签 '{tag_name}' 的笔记")  
        return {"notes": notes}  
    
    @mcp_server.tool()  
    def rename_tag(old_name: str, new_name: str) -> dict:  
        """  
        重命名标签  
        
        Args:  
            old_name: 当前标签名称  
            new_name: 新标签名称  
            
        Returns:  
            成功状态  
        """  
        success = db.rename_tag(old_name=old_name, new_name=new_name)  
        if not success:  
            return {"success": False, "message": f"未找到标签 '{old_name}'"}  
        logger.info(f"将标签 '{old_name}' 重命名为 '{new_name}'")  
        return {"success": True, "message": f"将标签 '{old_name}' 重命名为 '{new_name}'"}  
    
    @mcp_server.tool()  
    def delete_tag(tag_name: str) -> dict:  
        """  
        删除标签  
        
        Args:  
            tag_name: 要删除的标签名称  
            
        Returns:  
            成功状态  
        """  
        success = db.delete_tag(tag_name=tag_name)  
        if not success:  
            return {"success": False, "message": f"未找到标签 '{tag_name}'"}  
        logger.info(f"删除标签 '{tag_name}'")  
        return {"success": True, "message": f"成功删除标签 '{tag_name}'"}  
    
    @mcp_server.tool()  
    def get_database_stats() -> dict:  
        """  
        获取知识库统计信息  
        
        Returns:  
            数据库统计信息  
        """  
        stats = db.get_database_stats()  
        return stats  
    
    @mcp_server.tool()  
    def format_note(note_id: int) -> str:  
        """  
        格式化笔记以便美观显示  
        
        Args:  
            note_id: 要格式化的笔记ID  
            
        Returns:  
            格式化为markdown的笔记  
        """  
        note = db.get_note(note_id=note_id)  
        if not note:  
            return f"错误: 未找到ID为{note_id}的笔记"  
        return format_note_for_display(note)  
    
    return mcp_server  

@app.command()  
def run(  
    db_path: str = typer.Option(None, "--db-path", "-d", help="数据库文件路径"),  
    verbose: bool = typer.Option(False, "--verbose", "-v", help="显示详细日志")  
):  
    """运行MCP服务器"""  
    # 如果启用详细模式，设置日志级别为DEBUG  
    if verbose:  
        logger.setLevel(logging.DEBUG)  
        
    # 确定数据库路径  
    db_file = db_path or config.db_path  
    
    rprint(f"[bold green]启动PersonalKB MCP服务器[/bold green]")  
    rprint(f"[blue]数据库路径:[/blue] {db_file}")  
    
    # 创建并运行MCP服务器  
    mcp_server = create_mcp_server(db_path=db_file)  
    rprint("[bold yellow]服务器已就绪。等待连接...[/bold yellow]")  
    
    try:  
        mcp_server.run_stdio()  
    except KeyboardInterrupt:  
        rprint("[yellow]接收到中断信号，正在优雅地关闭...[/yellow]")  
    except Exception as e:  
        rprint(f"[bold red]服务器错误: {str(e)}[/bold red]")  
        raise  

@app.command()  
def init(  
    db_path: str = typer.Option(None, "--db-path", "-d", help="数据库文件路径"),  
    force: bool = typer.Option(False, "--force", "-f", help="覆盖现有数据库")  
):  
    """初始化数据库"""  
    # 确定数据库路径  
    db_file = Path(db_path) if db_path else config.db_path  
    
    # 检查文件是否存在  
    if db_file.exists() and not force:  
        rprint(f"[yellow]警告: 数据库文件 {db_file} 已存在。使用 --force 覆盖。[/yellow]")  
        return  
    
    # 如果目录不存在则创建  
    db_file.parent.mkdir(parents=True, exist_ok=True)  
    
    # 如果强制覆盖且文件存在，则删除  
    if force and db_file.exists():  
        os.remove(db_file)  
        rprint(f"[yellow]已删除现有数据库文件[/yellow]")  
    
    # 初始化数据库  
    db = Database(db_path=db_file)  
    rprint(f"[bold green]数据库已初始化于:[/bold green] {db_file}")  
    
    # 如果数据库为空，创建一些示例笔记  
    with db.get_session() as session:  
        note_count = session.query(db.Note).count()  
        if note_count == 0:  
            rprint("[yellow]创建示例笔记...[/yellow]")  
            
            # 欢迎笔记  
            db.create_note(  
                title="欢迎使用PersonalKB",   
                content="这是您的个人知识库，支持与智谱AI模型集成。您可以使用它来存储和组织笔记、想法和知识。\n\n"  
                       "试着让AI助手帮助您添加、搜索或更新笔记！\n\n"  
                       "您可以使用hashtag方式添加标签，例如 #welcome #getting-started",  
                tags=["欢迎", "入门指南"]  
            )  
            
            # Markdown支持笔记  
            db.create_note(  
                title="Markdown支持",   
                content="笔记支持Markdown格式：\n\n"  
                       "# 一级标题\n"  
                       "## 二级标题\n\n"  
                       "- 项目符号\n"  
                       "- 更多要点\n\n"  
                       "1. 有序列表\n"  
                       "2. 第二项\n\n"  
                       "```python\n"  
                       "print('也支持代码块！')\n"  
                       "```\n\n"  
                       "您还可以使用**粗体**、*斜体*和`内联代码`。\n\n"  
                       "#markdown #格式 #教程",  
                tags=["markdown", "格式", "教程"]  
            )  
            
            # 使用指南笔记  
            db.create_note(  
                title="使用指南",   
                content="## 如何有效使用此知识库\n\n"  
                       "1. **组织笔记**：使用标签对相关笔记进行分类\n"  
                       "2. **搜索功能**：使用搜索查找特定信息\n"  
                       "3. **与AI结合**：让智谱AI帮助您管理和检索知识\n\n"  
                       "### 常用命令：\n\n"  
                       "- 「帮我创建一个关于机器学习的笔记」\n"  
                       "- 「搜索关于Python的笔记」\n"  
                       "- 「列出所有标签」\n"  
                       "- 「显示数据库统计信息」\n\n"  
                       "#指南 #教程 #使用方法",  
                tags=["指南", "教程", "使用方法"]  
            )  
            
            rprint("[green]示例笔记已创建！[/green]")  

@app.command()  
def export(  
    output_file: str = typer.Option("knowledge_base_export.json", "--output", "-o", help="输出文件路径"),  
    db_path: str = typer.Option(None, "--db-path", "-d", help="数据库文件路径")  
):  
    """导出知识库内容到JSON文件"""  
    # 确定数据库路径  
    db_file = db_path or config.db_path  
    
    # 初始化数据库  
    db = Database(db_path=db_file)  
    
    # 获取所有笔记  
    notes = db.list_notes(limit=10000)  # 获取足够多的笔记  
    
    # 获取所有标签  
    tags = db.list_tags()  
    
    # 创建导出数据  
    export_data = {  
        "metadata": {  
            "exported_at": datetime.datetime.now().isoformat(),  
            "version": config.server_version,  
            "note_count": len(notes),  
            "tag_count": len(tags)  
        },  
        "notes": notes,  
        "tags": tags  
    }  
    
    # 写入文件  
    with open(output_file, 'w', encoding='utf-8') as f:  
        json.dump(export_data, f, indent=2, ensure_ascii=False)  
    
    rprint(f"[bold green]知识库已导出到[/bold green] {output_file}")  
    rprint(f"笔记: {len(notes)}, 标签: {len(tags)}")  

@app.command()  
def import_data(  
    input_file: str = typer.Argument(..., help="要导入的JSON文件"),  
    db_path: str = typer.Option(None, "--db-path", "-d", help="数据库文件路径"),  
    merge: bool = typer.Option(True, "--merge/--replace", help="合并或替换现有数据")  
):  
    """从JSON文件导入知识库内容"""  
    # 确定数据库路径  
    db_file = db_path or config.db_path  
    
    # 检查输入文件  
    if not os.path.exists(input_file):  
        rprint(f"[bold red]错误: 文件 {input_file} 不存在[/bold red]")  
        return  
    
    # 读取JSON数据  
    try:  
        with open(input_file, 'r', encoding='utf-8') as f:  
            import_data = json.load(f)  
    except Exception as e:  
        rprint(f"[bold red]读取JSON文件出错: {str(e)}[/bold red]")  
        return  
    
    # 验证导入数据  
    if not isinstance(import_data, dict) or "notes" not in import_data:  
        rprint("[bold red]无效的导入文件格式[/bold red]")  
        return  
    
    # 初始化数据库  
    db = Database(db_path=db_file)  
    
    # 如果选择替换，则清空数据库  
    if not merge:  
        rprint("[yellow]警告: 替换模式 - 将删除所有现有数据[/yellow]")  
        with db.get_session() as session:  
            # 删除所有标签和笔记  
            session.query(db.Note).delete()  
            session.query(db.Tag).delete()  
            session.commit()  
    
    # 导入笔记  
    imported_notes = 0  
    for note_data in import_data.get("notes", []):  
        try:  
            # 提取必要字段  
            title = note_data.get("title")  
            content = note_data.get("content")  
            tags = note_data.get("tags", [])  
            
            if title and content:  
                db.create_note(title=title, content=content, tags=tags)  
                imported_notes += 1  
        except Exception as e:  
            logger.error(f"导入笔记出错: {str(e)}")  
    
    rprint(f"[bold green]已成功导入 {imported_notes} 个笔记[/bold green]")  

def main():  
    app()  

if __name__ == "__main__":  
    main()  
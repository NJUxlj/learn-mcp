"""  
命令行工具应用程序，用于直接与知识库交互。  
这个脚本可以脱离AI模型直接操作知识库。  
"""  

import typer  
from rich.console import Console  
from rich.table import Table  
from rich.markdown import Markdown  
from rich.panel import Panel  
from rich import box  
import os  
from pathlib import Path  

from .database import Database  
from .config import config  
from .utils import format_note_for_display, sanitize_tag_name  

app = typer.Typer()  
console = Console()  

def get_database():  
    """获取数据库连接"""  
    return Database(db_path=config.db_path)  

@app.command()  
def add(  
    title: str = typer.Option(..., "--title", "-t", prompt=True, help="笔记标题"),  
    content: str = typer.Option(None, "--content", "-c", help="笔记内容"),  
    tags: str = typer.Option(None, "--tags", help="逗号分隔的标签列表")  
):  
    """添加新笔记"""  
    # 如果未提供内容，则启动编辑器  
    if content is None:  
        import tempfile  
        import subprocess  
        
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as temp:  
            temp_filename = temp.name  
        
        # 使用默认编辑器打开临时文件  
        editor = os.environ.get("EDITOR", "nano")  
        subprocess.call([editor, temp_filename])  
        
        # 读取编辑后的内容  
        with open(temp_filename, "r") as temp:  
            content = temp.read()  
        
        # 删除临时文件  
        os.unlink(temp_filename)  
    
    # 处理标签  
    tag_list = None  
    if tags:  
        tag_list = [sanitize_tag_name(tag.strip()) for tag in tags.split(",") if tag.strip()]  
    
    # 创建笔记  
    db = get_database()  
    note = db.create_note(title=title, content=content, tags=tag_list)  
    
    console.print(f"[green]笔记已创建，ID: {note['id']}[/green]")  
    console.print(Panel(Markdown(format_note_for_display(note)), title=f"笔记 #{note['id']}", border_style="green"))  

@app.command()  
def show(  
    id: int = typer.Argument(..., help="笔记ID")  
):  
    """显示笔记详情"""  
    db = get_database()  
    note = db.get_note(note_id=id)  
    
    if not note:  
        console.print(f"[red]未找到ID为{id}的笔记[/red]")  
        return  
    
    console.print(Panel(Markdown(format_note_for_display(note)), title=f"笔记 #{id}", border_style="blue"))  

@app.command()  
def list_notes(  
    limit: int = typer.Option(10, "--limit", "-l", help="要显示的最大笔记数"),  
    offset: int = typer.Option(0, "--offset", "-o", help="要跳过的笔记数"),  
    tag: str = typer.Option(None, "--tag", "-t", help="按标签筛选")  
):  
    """列出笔记"""  
    db = get_database()  
    
    if tag:  
        notes = db.get_notes_by_tag(tag_name=tag, limit=limit, offset=offset)  
        console.print(f"[blue]标签 '{tag}' 的笔记:[/blue]")  
    else:  
        notes = db.list_notes(limit=limit, offset=offset)  
    
    if not notes:  
        console.print("[yellow]没有找到笔记[/yellow]")  
        return  
    
    table = Table(title="笔记列表", box=box.ROUNDED)  
    table.add_column("ID", justify="right", style="cyan")  
    table.add_column("标题", style="green")  
    table.add_column("标签", style="yellow")  
    table.add_column("更新时间", style="blue")  
    
    for note in notes:  
        table.add_row(  
            str(note['id']),  
            note['title'],  
            ", ".join(note['tags']) if note['tags'] else "-",  
            note['updated_at'][:19]  # 仅显示日期部分  
        )  
    
    console.print(table)  
    
    # 显示分页信息  
    if len(notes) == limit:  
        console.print(f"[blue]显示 {offset+1}-{offset+len(notes)} 项。查看更多请使用 --offset {offset+limit}[/blue]")  

@app.command()  
def tags():  
    """列出所有标签"""  
    db = get_database()  
    tags = db.list_tags()  
    
    if not tags:  
        console.print("[yellow]没有找到标签[/yellow]")  
        return  
    
    table = Table(title="标签列表", box=box.ROUNDED)  
    table.add_column("ID", justify="right", style="cyan")  
    table.add_column("名称", style="green")  
    table.add_column("笔记数量", justify="right", style="yellow")  
    
    for tag in tags:  
        table.add_row(  
            str(tag['id']),  
            tag['name'],  
            str(tag['note_count'])  
        )  
    
    console.print(table)  

@app.command()  
def search(  
    query: str = typer.Argument(..., help="搜索查询"),  
    limit: int = typer.Option(10, "--limit", "-l", help="要显示的最大结果数")  
):  
    """搜索笔记"""  
    db = get_database()  
    results = db.search_notes(query=query, limit=limit)  
    
    if not results:  
        console.print(f"[yellow]未找到匹配 '{query}' 的结果[/yellow]")  
        return  
    
    console.print(f"[green]找到 {len(results)} 个匹配 '{query}' 的结果:[/green]")  
    
    table = Table(box=box.ROUNDED)  
    table.add_column("ID", justify="right", style="cyan")  
    table.add_column("标题", style="green")  
    table.add_column("标签", style="yellow")  
    table.add_column("更新时间", style="blue")  
    
    for note in results:  
        table.add_row(  
            str(note['id']),  
            note['title'],  
            ", ".join(note['tags']) if note['tags'] else "-",  
            note['updated_at'][:19]  # 仅显示日期部分  
        )  
    
    console.print(table)  

@app.command()  
def edit(  
    id: int = typer.Argument(..., help="要编辑的笔记ID"),  
    title: str = typer.Option(None, "--title", "-t", help="新标题"),  
    tags: str = typer.Option(None, "--tags", help="逗号分隔的新标签列表"),  
    edit_content: bool = typer.Option(False, "--edit-content", "-e", help="在编辑器中编辑内容")  
):  
    """编辑笔记"""  
    db = get_database()  
    note = db.get_note(note_id=id)  
    
    if not note:  
        console.print(f"[red]未找到ID为{id}的笔记[/red]")  
        return  
    
    # 处理内容编辑  
    content = None  
    if edit_content:  
        import tempfile  
        import subprocess  
        
        # 创建临时文件并写入现有内容  
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as temp:  
            temp.write(note['content'].encode('utf-8'))  
            temp_filename = temp.name  
        
        # 使用默认编辑器打开临时文件  
        editor = os.environ.get("EDITOR", "nano")  
        subprocess.call([editor, temp_filename])  
        
        # 读取编辑后的内容  
        with open(temp_filename, "r", encoding='utf-8') as temp:  
            content = temp.read()  
        
        # 删除临时文件  
        os.unlink(temp_filename)  
    
    # 处理标签  
    tag_list = None  
    if tags is not None:  
        tag_list = [sanitize_tag_name(tag.strip()) for tag in tags.split(",") if tag.strip()]  
    
    # 更新笔记  
    updated_note = db.update_note(note_id=id, title=title, content=content, tags=tag_list)  
    
    if updated_note:  
        console.print(f"[green]笔记ID {id} 已更新[/green]")  
        console.print(Panel(Markdown(format_note_for_display(updated_note)), title=f"已更新的笔记 #{id}", border_style="green"))  
    else:  
        console.print(f"[red]更新笔记ID {id} 失败[/red]")  

@app.command()  
def delete(  
    id: int = typer.Argument(..., help="要删除的笔记ID"),  
    force: bool = typer.Option(False, "--force", "-f", help="跳过确认提示")  
):  
    """删除笔记"""  
    db = get_database()  
    note = db.get_note(note_id=id)  
    
    if not note:  
        console.print(f"[red]未找到ID为{id}的笔记[/red]")  
        return  
    
    # 显示要删除的笔记  
    console.print(Panel(f"标题: {note['title']}\n标签: {', '.join(note['tags']) if note['tags'] else '无'}",   
                       title=f"要删除的笔记 #{id}", border_style="red"))  
    
    # 确认删除  
    if not force and not typer.confirm("确定要删除这个笔记吗?"):  
        console.print("[yellow]已取消删除[/yellow]")  
        return  
    
    success = db.delete_note(note_id=id)  
    if success:  
        console.print(f"[green]笔记ID {id} 已删除[/green]")  
    else:  
        console.print(f"[red]删除笔记ID {id} 失败[/red]")  

@app.command()  
def stats():  
    """显示知识库统计信息"""  
    db = get_database()  
    stats = db.get_database_stats()  
    
    console.print(Panel(  
        f"笔记总数: [bold green]{stats['note_count']}[/bold green]\n"  
        f"标签总数: [bold yellow]{stats['tag_count']}[/bold yellow]\n\n"  
        f"数据库路径: [blue]{db.db_path}[/blue]\n",  
        title="知识库统计信息",  
        border_style="cyan"  
    ))  
    
    if stats['latest_notes']:  
        console.print("[bold]最近添加的笔记:[/bold]")  
        table = Table(box=box.SIMPLE)  
        table.add_column("ID", style="cyan")  
        table.add_column("标题", style="green")  
        table.add_column("创建时间", style="blue")  
        
        for note in stats['latest_notes']:  
            table.add_row(  
                str(note['id']),  
                note['title'],  
                note['created_at'][:19]  
            )  
        
        console.print(table)  

def main():  
    app()  

if __name__ == "__main__":  
    main()  
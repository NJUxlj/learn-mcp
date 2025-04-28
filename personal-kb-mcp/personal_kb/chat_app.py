# 命令行聊天应用
"""  
交互式命令行聊天应用程序，使用智谱API与知识库交互。  
"""  

import os  
import sys  
import json  
import typer  
from rich.console import Console  
from rich.markdown import Markdown  
from rich.panel import Panel  
from prompt_toolkit import PromptSession  
from prompt_toolkit.history import FileHistory  
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory  
from prompt_toolkit.completion import WordCompleter  
from pathlib import Path  

from .zhipu_client import ZhipuClient  
from .config import config  

app = typer.Typer()  
console = Console()  

def display_message(role: str, content: str) -> None:  
    """显示消息，针对不同角色使用不同样式。"""  
    if role == "assistant":  
        # 渲染助手消息为Markdown  
        md = Markdown(content)  
        console.print(Panel(md, title="智谱助手", border_style="green"))  
    elif role == "user":  
        console.print(Panel(content, title="用户", border_style="blue"))  
    elif role == "system":  
        console.print(Panel(content, title="系统", border_style="yellow"))  
    else:  
        console.print(content)  

@app.command()  
def chat(  
    api_key: str = typer.Option(None, "--api-key", "-k", help="智谱API密钥"),  
    model: str = typer.Option("glm-4", "--model", "-m", help="要使用的智谱模型")  
):  
    """启动交互式聊天会话与知识库交互。"""  
    # 创建用户目录  
    config_dir = Path.home() / ".personal_kb"  
    config_dir.mkdir(exist_ok=True)  
    
    # 设置历史文件  
    history_file = config_dir / "chat_history"  
    
    # 从环境变量获取API密钥  
    api_key = api_key or os.environ.get("ZHIPU_API_KEY")  
    if not api_key:  
        console.print("[red]错误: 未提供智谱API密钥。请使用--api-key参数或设置ZHIPU_API_KEY环境变量[/red]")  
        sys.exit(1)  
    
    # 创建智谱客户端  
    client = ZhipuClient(api_key=api_key, model=model)  
    
    # 启动MCP服务器  
    try:  
        client.start_mcp_server()  
    except Exception as e:  
        console.print(f"[red]启动MCP服务器出错: {str(e)}[/red]")  
        sys.exit(1)  
    
    # 欢迎消息  
    console.print(Panel(  
        "欢迎使用智谱知识库助手!\n"  
        "您可以询问您的知识库信息，创建、搜索和管理笔记。\n"  
        "键入 'exit' 或按 Ctrl+D 退出。",   
        title="个人知识库助手",   
        border_style="cyan"  
    ))  
    
    # 系统提示信息  
    system_message = {  
        "role": "system",  
        "content": """你是一个强大的AI助手，与个人知识库系统集成。你可以使用工具来创建、搜索、更新和管理用户的笔记和标签。  
        
功能包括：  
1. 创建新笔记（create_note）  
2. 获取笔记（get_note）  
3. 更新笔记（update_note）  
4. 删除笔记（delete_note）  
5. 列出笔记（list_notes）  
6. 搜索笔记（search_notes）  
7. 列出标签（list_tags）  
8. 按标签获取笔记（get_notes_by_tag）  
9. 获取数据库统计信息（get_database_stats）  

始终使用最合适的工具来满足用户需求。在处理笔记内容时，保持原始格式。当创建或更新笔记时，确保保留用户提供的任何Markdown格式。"""  
    }  
    
    # 创建会话历史  
    messages = [system_message]  
    
    # 创建提示会话  
    completer = WordCompleter([  
        "创建笔记", "查找笔记", "搜索", "所有笔记", "所有标签",  
        "统计信息", "帮助", "退出"  
    ])  
    session = PromptSession(  
        history=FileHistory(str(history_file)),  
        auto_suggest=AutoSuggestFromHistory(),  
        completer=completer  
    )  
    
    try:  
        while True:  
            # 获取用户输入  
            try:  
                user_input = session.prompt("输入 > ")  
            except (EOFError, KeyboardInterrupt):  
                break  
                
            # 检查退出命令  
            if user_input.lower() in ("exit", "quit", "退出"):  
                break  
                
            if not user_input.strip():  
                continue  
                
            # 添加用户消息  
            user_message = {"role": "user", "content": user_input}  
            messages.append(user_message)  
            display_message("user", user_input)  
            
            # 调用API  
            with console.status("[bold green]正在思考...[/bold green]"):  
                response = client.chat(messages)  
            
            if "error" in response:  
                console.print(f"[red]错误: {response['error']}[/red]")  
                continue  
                
            # 获取回复内容  
            try:  
                assistant_message = response["choices"][0]["message"]  
                content = assistant_message["content"]  
                
                # 添加到消息历史  
                messages.append({"role": "assistant", "content": content})  
                
                # 显示回复  
                display_message("assistant", content)  
            except (KeyError, IndexError) as e:  
                console.print(f"[red]解析响应出错: {str(e)}[/red]")  
                console.print(f"[yellow]原始响应: {response}[/yellow]")  
    
    finally:  
        # 停止MCP服务器  
        client.stop_mcp_server()  
        console.print("[cyan]会话结束，谢谢使用！[/cyan]")  

def main():  
    app()  

if __name__ == "__main__":  
    main()  
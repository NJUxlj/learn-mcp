# 安装必要的包  
# pip install modelcontextprotocol fastmcp  

from mcp.server.fastmcp import FastMCP  
import math  

# 实例化MCP服务器  
mcp = FastMCP("Math Operations Server")  


# 定义工具功能  
@mcp.tool()  
def add(a: int, b: int) -> int:  
    """将两个数字相加"""  
    return int(a + b)  

@mcp.tool()  
def subtract(a: int, b: int) -> int:  
    """将两个数字相减"""  
    return int(a - b)  

@mcp.tool()  
def multiply(a: int, b: int) -> int:  
    """将两个数字相乘"""  
    return int(a * b)  

@mcp.tool()  
def divide(a: int, b: int) -> float:  
    """将两个数字相除"""  
    if b == 0:  
        raise ValueError("Cannot divide by zero")  
    return a / b  

# 启动服务器  
if __name__ == "__main__":  
    # 使用stdio传输方式启动服务器  
    mcp.run(transport='stdio')  
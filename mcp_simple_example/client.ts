//TypeScript MCP客户端示例
// npm install @anthropic-ai/sdk @modelcontextprotocol/sdk dotenv  

import { Anthropic } from '@anthropic-ai/sdk';  
import { createMcpClientForStdio } from '@modelcontextprotocol/sdk';  
import * as dotenv from 'dotenv';  

// 加载环境变量  
dotenv.config();  

// 初始化Anthropic客户端  
const anthropic = new Anthropic({  
  apiKey: process.env.ANTHROPIC_API_KEY,  
});  

async function main() {  
  // 连接到MCP服务器  
  const mcpProcess = require('child_process').spawn('node', ['path_to_your_mcp_server.js']);  
  const mcpClient = await createMcpClientForStdio({  
    input: mcpProcess.stdout,  
    output: mcpProcess.stdin,  
  });  

  // 获取可用工具  
  const tools = await mcpClient.listTools();  
  console.log('Available tools:', tools);  

  // 使用Claude调用MCP工具  
  const message = await anthropic.messages.create({  
    model: 'claude-3-opus-20240229',  
    max_tokens: 1000,  
    system: "You can use tools to help answer the user's questions.",  
    messages: [  
      {  
        role: 'user',  
        content: "Please greet me by name. My name is Alice."  
      }  
    ],  
    tools: tools,  
    tool_choice: 'auto',  
  });  

  console.log(message.content);  
}  

main().catch(console.error);  
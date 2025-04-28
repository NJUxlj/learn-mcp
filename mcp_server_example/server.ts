//使用Node.js/TypeScript实现MCP服务器
// 首先安装必要的包  
// npm install @modelcontextprotocol/sdk dotenv  

import { createServer } from '@modelcontextprotocol/sdk';  

// 创建一个MCP服务器  
const server = createServer({  
  title: "Simple MCP Server",  
  tools: [  
    {  
      name: "greet",  
      description: "Greets a person by name",  
      parameters: {  
        type: "object",  
        properties: {  
          name: {  
            type: "string",  
            description: "The name of the person to greet"  
          }  
        },  
        required: ["name"]  
      },  
      handler: async ({ name }) => {  
        return `Hello, ${name}! Welcome to the MCP server.`;  
      }  
    },  
    {  
      name: "getCurrentTime",  
      description: "Returns the current time",  
      parameters: {  
        type: "object",  
        properties: {}  
      },  
      handler: async () => {  
        return new Date().toLocaleTimeString();  
      }  
    }  
  ]  
});  

// 启动服务器（stdio模式）  
server.listen({  
  stdio: true  
});  

console.log("MCP Server is running...");  
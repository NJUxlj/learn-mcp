```
conda create -n mcp-client python=3.12 -y

conda activate mcp-client

pip install uv

uv pip install mcp
```

```
uv run --active client.py
```
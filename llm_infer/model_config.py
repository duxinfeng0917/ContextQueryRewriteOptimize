import os
from dotenv import load_dotenv

# 自动加载项目根目录或当前目录的 .env 文件
load_dotenv()

# ── API Key 从环境变量读取，禁止硬编码 ──────────────────────────────────────
# 配置方式：在项目根目录创建 .env 文件（参考 .env.example），或在系统环境中设置：
#   export AZURE_GROUP_API_KEY="your-key"
#   export AZURE_WANGMC_API_KEY="your-key"
#   export KINGSOFT_API_KEY="your-key"
_AZURE_GROUP_KEY   = os.environ.get("AZURE_GROUP_API_KEY", "")
_AZURE_WANGMC_KEY  = os.environ.get("AZURE_WANGMC_API_KEY", "")
_KINGSOFT_KEY      = os.environ.get("KINGSOFT_API_KEY", "")

azure_model_config = {
    "DeepSeek-R1-0528": {
        "base_url": "https://sfmx-ai-group-resource.services.ai.azure.com/models",
        "api_key": _AZURE_GROUP_KEY,
    },
    "DeepSeek-V3-0324": {
        "base_url": "https://sfmx-ai-group-resource.services.ai.azure.com/models",
        "api_key": _AZURE_GROUP_KEY,
    },
    "DeepSeek-V3.2": {
        "base_url": "https://sfmx-ai-wangmc-resource.services.ai.azure.com/models",
        "api_key": _AZURE_WANGMC_KEY,
    },
    "DeepSeek-V3.2-Speciale": {
        "base_url": "https://sfmx-ai-wangmc-resource.services.ai.azure.com/models",
        "api_key": _AZURE_WANGMC_KEY,
    },
    "gpt-4.1": {
        "base_url": "https://sfmx-ai-group-resource.cognitiveservices.azure.com/openai/v1/",
        "api_key": _AZURE_GROUP_KEY,
    },
    "gpt-4.1-mini": {
        "base_url": "https://sfmx-ai-group-resource.cognitiveservices.azure.com/openai/v1/",
        "api_key": _AZURE_GROUP_KEY,
    },
    "gpt-4o": {
        "base_url": "https://sfmx-ai-group-resource.cognitiveservices.azure.com/openai/v1/",
        "api_key": _AZURE_GROUP_KEY,
    },
    "gpt-4o-mini": {
        "base_url": "https://sfmx-ai-group-resource.cognitiveservices.azure.com/openai/v1/",
        "api_key": _AZURE_GROUP_KEY,
    },
    "o3": {
        "base_url": "https://sfmx-ai-group-resource.cognitiveservices.azure.com/openai/v1/",
        "api_key": _AZURE_GROUP_KEY,
    },
    "o3-pro": {  # TODO 调用会报错，原因暂时不知
        "base_url": "https://sfmx-ai-group-resource.cognitiveservices.azure.com/openai/v1/",
        "api_key": _AZURE_GROUP_KEY,
    },
    "o4-mini": {
        "base_url": "https://sfmx-ai-group-resource.cognitiveservices.azure.com/openai/v1/",
        "api_key": _AZURE_GROUP_KEY,
    },
    "gpt-5.2": {
        "base_url": "https://sfmx-ai-wangmc-resource.cognitiveservices.azure.com/openai/v1/",
        "api_key": _AZURE_WANGMC_KEY,
    },
    "gpt-5.2-chat": {
        "base_url": "https://sfmx-ai-wangmc-resource.cognitiveservices.azure.com/openai/v1/",
        "api_key": _AZURE_WANGMC_KEY,
    },
    "gpt-5.4-pro": {  # 注意：gpt-5.4-pro 不支持 chatCompletion
        "base_url": "https://sfmx-ai-wangmc-resource.cognitiveservices.azure.com/openai/v1/",
        "api_key": _AZURE_WANGMC_KEY,
    },
    "gpt-5.4": {
        "base_url": "https://sfmx-ai-wangmc-resource.cognitiveservices.azure.com/openai/v1/",
        "api_key": _AZURE_WANGMC_KEY,
    },
    "gpt-5.4-mini": {
        "base_url": "https://sfmx-ai-wangmc-resource.cognitiveservices.azure.com/openai/v1/",
        "api_key": _AZURE_WANGMC_KEY,
    },
    "gpt-5.4-nano": {
        "base_url": "https://sfmx-ai-wangmc-resource.cognitiveservices.azure.com/openai/v1/",
        "api_key": _AZURE_WANGMC_KEY,
    },
    "Kimi-K2.5": {
        "base_url": "https://sfmx-ai-wangmc-resource.services.ai.azure.com/openai/v1/",
        "api_key": _AZURE_WANGMC_KEY,
    },
}

kingsoft_model_config = {
    "deepseek-v3.2": {
        "base_url": "http://kspmas.ksyun.com/v1",
        "api_key": _KINGSOFT_KEY,
    },
    "deepseek-v3.2-speciale": {
        "base_url": "http://kspmas.ksyun.com/v1",
        "api_key": _KINGSOFT_KEY,
    },
    "kimi-k2.5": {
        "base_url": "http://kspmas.ksyun.com/v1",
        "api_key": _KINGSOFT_KEY,
    },
    "minimax-m2.7": {
        "base_url": "http://kspmas.ksyun.com/v1",
        "api_key": _KINGSOFT_KEY,
    },
    "glm-5": {
        "base_url": "http://kspmas.ksyun.com/v1",
        "api_key": _KINGSOFT_KEY,
    },
    # 下面这些暂不支持
    "qwen3.5-35b-a3b": {
        "base_url": "http://kspmas.ksyun.com/v1",
        "api_key": _KINGSOFT_KEY,
    },
    # "qwen3.5-122b-a10b": {
    #     "base_url": "http://kspmas.ksyun.com/v1",
    #     "api_key": _KINGSOFT_KEY,
    # },
    # "qwen3.5-397b-a17b": {
    #     "base_url": "http://kspmas.ksyun.com/v1",
    #     "api_key": _KINGSOFT_KEY,
    # },
}

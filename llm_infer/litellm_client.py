"""
litellm_client.py
LiteLLM 统一模型客户端

职责：
  - 从 model_config.py 读取 Azure 端点凭据
  - 通过 LiteLLM 统一管理所有模型调用
  - 对外暴露 completion() 和 make_dspy_lm() 两个接口

用法：
  from llm_infer.litellm_client import completion, make_dspy_lm

  # 直接调用
  resp = completion('gpt-5.4-nano', [{'role': 'user', 'content': '你好'}])
  print(resp.choices[0].message.content)

  # 构造 DSPy LM
  lm = make_dspy_lm('gpt-5.4-nano')
"""

import os

# 必须在 import litellm 之前设置，否则 LiteLLM 启动时就会触发远程拉取
os.environ.setdefault('LITELLM_LOCAL_MODEL_COST_MAP', 'True')

import litellm
from model_config import azure_model_config

# ── LiteLLM 全局配置 ─────────────────────────────────────────────────────────
litellm.telemetry = False        # 禁用遥测上报
litellm.suppress_debug_info = True  # 抑制多余 debug 输出


def _get_cfg(model_name: str) -> dict:
    """从 azure_model_config 取出指定模型的 base_url / api_key。"""
    if model_name not in azure_model_config:
        raise KeyError(f"模型 '{model_name}' 不在 azure_model_config 中，"
                       f"可用: {list(azure_model_config.keys())}")
    return azure_model_config[model_name]


def completion(
    model_name: str,
    messages: list[dict],
    max_tokens: int = 512,
    **kwargs,
) -> litellm.ModelResponse:
    """
    通过 LiteLLM 调用 Azure 模型。

    参数：
      model_name  : azure_model_config 中的键名，如 'gpt-5.4-nano'
      messages    : OpenAI 格式的消息列表
      max_tokens  : 最大输出 token 数
      **kwargs    : 透传给 litellm.completion 的其他参数

    返回：
      litellm.ModelResponse（与 openai.ChatCompletion 结构相同）
    """
    cfg = _get_cfg(model_name)
    return litellm.completion(
        model=f'openai/{model_name}',
        messages=messages,
        api_base=cfg['base_url'],
        api_key=cfg['api_key'],
        max_tokens=max_tokens,
        **kwargs,
    )


def make_dspy_lm(model_name: str = 'gpt-5.4-nano', max_tokens: int = 512):
    """
    构造 DSPy LM 实例（底层使用 LiteLLM）。

    参数：
      model_name : azure_model_config 中的键名，默认 'gpt-5.4-nano'
      max_tokens : 最大输出 token 数

    返回：
      dspy.LM 实例，可直接传给 dspy.configure(lm=...)
    """
    import dspy
    cfg = _get_cfg(model_name)
    return dspy.LM(
        model=f'openai/{model_name}',
        api_base=cfg['base_url'],
        api_key=cfg['api_key'],
        max_tokens=max_tokens,
    )

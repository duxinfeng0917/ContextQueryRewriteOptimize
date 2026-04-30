import time
import traceback
from loguru import logger
from typing import Dict, List
from openai import OpenAI
from model_config import azure_model_config, kingsoft_model_config


class MyModel:

    def __init__(self, model_config: dict):
        self.model_name_to_client: Dict[str, OpenAI] = self.init_model_clients(model_config)

    def init_model_clients(self, model_config: dict):
        model_name_to_client = {}
        for model_name, config in model_config.items():
            client = OpenAI(
                base_url=config["base_url"],
                api_key=config["api_key"],
            )
            model_name_to_client[model_name] = client
        return model_name_to_client

    def __call__(self, model_name, messages, *args, **kwargs):
        if model_name not in self.model_name_to_client:
            all_model_names = list(self.model_name_to_client.keys())
            raise RuntimeError(f"Invalid value '{model_name}' for parameter model_name, Valid options: {','.join(all_model_names)}")

        client = self.model_name_to_client[model_name]
        try:
            start_time = time.time()
            completion = client.chat.completions.create(model=model_name, messages=messages)
            use_time = time.time() - start_time
            return completion, use_time
        except Exception as e:
            logger.error(traceback.format_exc())
            logger.error(f"ERROR：{e}. ERRORONLINE：{e.__traceback__.tb_lineno}")
            return {}, 0.0


if __name__ == "__main__":
    messages = [
        {"role": "user", "content": "你是谁？"},
    ]

    # # azure上的模型
    # model = MyModel(azure_model_config)
    # model_names = [
    #     "gpt-4.1", "gpt-4.1-mini", "gpt-4o", "gpt-4o-mini", "o3", "o4-mini",
    #     "gpt-5.2", "gpt-5.2-chat",
    #     "gpt-5.4", "gpt-5.4-mini", "gpt-5.4-nano",
    #     "DeepSeek-R1-0528", "DeepSeek-V3-0324",
    #     "DeepSeek-V3.2", "DeepSeek-V3.2-Speciale",
    #     "Kimi-K2.5",
    # ]

    # 金山云上的模型
    model = MyModel(kingsoft_model_config)
    model_names = ["deepseek-v3.2", "kimi-k2.5", "minimax-m2.7", "glm-5", "qwen3.5-35b-a3b"]

    for model_name in model_names:
        completion, use_time = model(model_name=model_name, messages=messages)
        logger.info(model_name)
        logger.info(use_time)
        logger.info(completion)
        print("\n")

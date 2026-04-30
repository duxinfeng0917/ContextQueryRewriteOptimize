"""
run_inference.py
加载优化后的 DSPy 程序，对单条或批量 query 执行改写推理。

模型：gpt-5.4-nano（Azure OpenAI），凭据来自 llm_infer/model_config.py

用法：
  # 单条改写
  python3 run_inference.py \\
      --query "那辆车月供多少？" \\
      --history "User: Seal 落地价多少？\nAgent: 大约 12 万。" \\
      --car-series "Seal" \\
      --lang Zh

  # 批量推理（输入 JSON 文件）
  python3 run_inference.py --batch input.json --output output.json
"""

import re
import os
import sys
import json
import argparse
import dspy

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'llm_infer'))
from litellm_client import make_dspy_lm  # noqa: E402

from dspy_optimizer import (
    QueryRewriter,
    extract_history,
    extract_car_series_from_prompt,
    extract_current_query,
)


def load_program(program_path: str = '') -> QueryRewriter:
    """初始化 LM（via LiteLLM）并加载优化程序（若存在）。"""
    lm = make_dspy_lm('gpt-5.4-nano', max_tokens=512)
    dspy.configure(lm=lm)
    program = QueryRewriter()
    if program_path and os.path.exists(program_path):
        program.load(program_path)
        print(f'[Load] 已加载优化程序: {program_path}')
    else:
        print('[Load] 未找到优化程序，使用基础 DSPy 程序（未优化）')
    return program


def rewrite_query(
    program: QueryRewriter,
    current_query: str,
    dialogue_history: str = '',
    car_series: str = '',
    language_type: str = 'Zh',
) -> str:
    """单条 query 改写接口。"""
    pred = program(
        car_series=car_series,
        dialogue_history=dialogue_history,
        language_type=language_type,
        current_query=current_query,
    )
    return (pred.rewritten_query or current_query).strip()


def rewrite_from_prompt(program: QueryRewriter, full_prompt: str) -> str:
    """从完整的 rewrite_prompt 字符串中提取信息并改写（与原系统兼容）。"""
    history = extract_history(full_prompt)
    car_series = extract_car_series_from_prompt(full_prompt)
    current_query = extract_current_query(full_prompt)

    has_zh = bool(re.search(r'[一-鿿]', current_query))
    has_my = bool(re.search(r'\b(nak|boleh|berapa|harga|kereta|tak|saya)\b', current_query, re.I))
    if has_zh and not has_my:
        lang = 'Zh'
    elif not has_zh and has_my:
        lang = 'My'
    elif has_zh and has_my:
        lang = 'Mix'
    else:
        lang = 'En'

    return rewrite_query(program, current_query, history, car_series, lang)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--query', type=str, default='', help='单条待改写 query')
    parser.add_argument('--history', type=str, default='', help='对话历史')
    parser.add_argument('--car-series', type=str, default='', help='可能涉及的车系')
    parser.add_argument('--lang', type=str, default='Zh', help='语言类型 Zh/En/My/Mix')
    parser.add_argument('--batch', type=str, default='', help='批量输入 JSON 文件路径')
    parser.add_argument('--output', type=str, default='', help='批量输出 JSON 文件路径')
    parser.add_argument('--program', type=str, default='optimized_rewriter.json',
                        help='优化程序路径（默认 optimized_rewriter.json）')
    args = parser.parse_args()

    program = load_program(args.program)

    if args.batch:
        with open(args.batch, encoding='utf-8') as f:
            items = json.load(f)
        results = []
        for item in items:
            result = rewrite_query(
                program,
                current_query=item['current_query'],
                dialogue_history=item.get('dialogue_history', ''),
                car_series=item.get('car_series', ''),
                language_type=item.get('language_type', 'Zh'),
            )
            results.append({**item, 'rewritten_query': result})
        out_path = args.output or args.batch.replace('.json', '_rewritten.json')
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f'[Done] 批量改写完成，结果已保存至: {out_path}')

    elif args.query:
        result = rewrite_query(
            program,
            current_query=args.query,
            dialogue_history=args.history,
            car_series=args.car_series,
            language_type=args.lang,
        )
        print(f'原句: {args.query}')
        print(f'改写: {result}')

    else:
        parser.print_help()


if __name__ == '__main__':
    main()

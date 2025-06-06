import re

def extract_token_counts(token_usage_str):
    prompt = completion = 0
    prompt_match = re.search(r'prompt_tokens=(\d+)', token_usage_str)
    completion_match = re.search(r'completion_tokens=(\d+)', token_usage_str)
    if prompt_match:
        prompt = int(prompt_match.group(1))
    if completion_match:
        completion = int(completion_match.group(1))
    return prompt, completion

def calculate_gpt4o_mini_cost(prompt_tokens, completion_tokens):
    input_cost = (prompt_tokens / 1000) * 0.00015
    output_cost = (completion_tokens / 1000) * 0.0006
    return input_cost + output_cost

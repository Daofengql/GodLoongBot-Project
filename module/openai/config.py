from dataclasses import field as dt_field

from graia.saya import Channel

channel = Channel.current()


class OpenAIConfig:
    api_keys: list[str] = ["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","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"]
    """ OpenAI API Key """

    gpt3_cache: int = 2
    """ GPT-3 缓存对话数量 """

    gpt3_max_token: int = 2000
    """ GPT-3 最大 Token 数量 """

    gpt3_switch: bool = False
    """ GPT-3 开关 """

    dalle_switch: bool = False
    """ DallE 开关"""

    dalle_size: str = "256x256"
    """ DallE 图片大小 """

    chatgpt_switch: bool = True
    """ ChatGPT 开关 """

    chatgpt_temperature: float = 1
    """ ChatGPT Temperature """

    chatgpt_cache: int = 4
    """ ChatGPT 缓存对话数量 """

    chatgpt_max_token: int = 2000
    """ ChatGPT 最大 Token 数量 """

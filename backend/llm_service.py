import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def get_llm_client() -> OpenAI:
    api_key = os.getenv("LLM_API_KEY")

    if not api_key or api_key in {"你的API密钥", "我的密钥"}:
        raise RuntimeError("尚未配置有效的 LLM_API_KEY")

    base_url = os.getenv("LLM_BASE_URL") or None

    return OpenAI(
        api_key=api_key,
        base_url=base_url,
    )


def generate_grounded_answer(query: str, context: str) -> str:
    client = get_llm_client()
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")

    response = client.chat.completions.create(
        model=model,
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": (
                    "你是企业客服助手。只能根据提供的知识库资料回答。"
                    "资料没有覆盖的问题必须明确说不知道，不得编造。"
                ),
            },
            {
                "role": "user",
                "content": f"知识库资料：\n{context}\n\n用户问题：{query}",
            },
        ],
    )

    return response.choices[0].message.content or ""
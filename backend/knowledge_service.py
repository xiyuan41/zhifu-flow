from pathlib import Path


KNOWLEDGE_FILE = (
    Path(__file__).resolve().parent.parent / "knowledge" / "售后规则.md"
)


def search_knowledge(query: str, top_k: int = 3) -> list[dict]:
    text = KNOWLEDGE_FILE.read_text(encoding="utf-8")
    sections = [part.strip() for part in text.split("\n## ") if part.strip()]

    query_words = set(query.lower().split())
    results = []

    for section in sections:
        section_lower = section.lower()
        score = sum(1 for word in query_words if word in section_lower)

        if score > 0:
            results.append(
                {
                    "score": score,
                    "content": section,
                    "source": "售后规则.md",
                }
            )

    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:top_k]
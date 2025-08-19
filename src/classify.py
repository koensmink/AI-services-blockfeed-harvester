def classify_domain(domain: str) -> bool:
    # Heel simpele heuristiek
    keywords = ["ai", "openai", "anthropic", "copilot", "perplexity", "gemini", "huggingface"]
    return any(k in domain.lower() for k in keywords)

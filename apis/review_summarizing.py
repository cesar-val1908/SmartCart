# from .openai import summarize_reviews

# # First fetch product reviews (mocked for now) needs to be changed to web scraped reviews
# def fetch_product_reviews(product_name):
#     mock_reviews = [
#         f"I love my {product_name}, it's awesome!",
#         f"The {product_name} broke within 2 weeks.",
#         f"The price of the {product_name} was fair, but the quality could be better.",
#     ]
#     return mock_reviews

# # Second combine and summarize using OpenAI
# def get_review_summary_for_product(product_name):
#     reviews = fetch_product_reviews(product_name)
#     combined_reviews = "\n".join(reviews)
#     summary = summarize_reviews(combined_reviews)
#     return summary


from .serp_api import search_serp_products
from .openai import summarize_reviews

def fetch_product_reviews(product_name):
    data = search_serp_products(product_name)
    if not data or "shopping_results" not in data:
        return ["No reviews found."]

    snippets = []
    for result in data["shopping_results"]:
        if "snippet" in result:
            snippets.append(result["snippet"])

    return snippets if snippets else ["No reviews available."]

def get_review_summary_for_product(product_name):
    reviews = fetch_product_reviews(product_name)
    combined_reviews = "\n".join(reviews)
    return summarize_reviews(combined_reviews)

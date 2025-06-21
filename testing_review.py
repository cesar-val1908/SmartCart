from apis.review_summarizing import get_review_summary_for_product

def test_summary():
    product = "Sony WH-1000XM5 Headphones"
    summary = get_review_summary_for_product(product)
    print("GPT-3.5 Summary of Reviews:")
    print(summary)

if __name__ == "__main__":
    test_summary()

"""Test module query enhancement"""
from src.retrieval.hybrid_search import QueryProcessor

# Initialize query processor
processor = QueryProcessor()

# Test queries
test_queries = [
    "What is covered in Session 5?",
    "What's in the Session 4 module?",
    "Tell me about Week 3",
    "How do I design steel frames?",  # Non-module query
    "What sections are on the page?",  # Non-module query
]

print("=" * 80)
print("Testing Module Query Detection and Enhancement")
print("=" * 80)

for query in test_queries:
    print(f"\nQuery: '{query}'")
    print("-" * 80)
    
    # Analyze
    analysis = processor.analyze_query(query)
    print(f"Is Module Query: {analysis.get('is_module_query')}")
    print(f"Module Number: {analysis.get('module_number')}")
    print(f"Intent: {analysis.get('intent')}")
    
    # Enhance
    enhanced = processor.enhance_query(query, analysis)
    if enhanced != query:
        print(f"Enhanced Query: '{enhanced}'")
    else:
        print("No enhancement applied")

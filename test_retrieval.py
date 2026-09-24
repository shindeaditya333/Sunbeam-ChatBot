from agents.tools import create_search_tool

tool = create_search_tool(5)

result = tool.invoke({
    "query": "sunbeam contact info"
})

print("\n" + "=" * 70)
print("RETRIEVAL RESULT")
print("=" * 70)
print(result)
print("=" * 70)
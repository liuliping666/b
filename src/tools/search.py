from src.tools.web_tools.core.engines.google import Search as GoogleSearch

# init a search engine
gsearch = GoogleSearch(proxy=None)

query = "The answer to life, the universe, and everything?"

# will automatically parse Google and corresponding web pages
gresults = gsearch.search(query, cache=True, page_cache=True, topk=1, end_year=2024)

print(gresults)
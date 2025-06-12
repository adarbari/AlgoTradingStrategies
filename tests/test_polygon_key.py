from polygon import RESTClient

api_key = "rD9rEIzrzJOcVlPq1ttiAyRLyZyquFiF"
client = RESTClient(api_key)

try:
    aggs = client.list_aggs(
        ticker="AAPL",
        multiplier=1,
        timespan="day",
        from_="2024-02-15",
        to="2024-02-16",
        limit=1
    )
    print("API key works! Aggregates:", aggs)
except Exception as e:
    print("API key failed:", e) 
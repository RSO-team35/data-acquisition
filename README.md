# data-acquisition
Microsevice that acquires data for price comparison


Run server for development (reloads when code changes are saved)

```bash
python3 -m uvicorn scraper_app.main:app --reload --port 8008
```

Access OpenAPI docs at

http://127.0.0.1:8008/docs#/
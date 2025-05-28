## How to run

Installing dependencies:

```
python -m venv venv
```

```
venv/Scripts/activate
```

```
pip install -r requirements.txt
```

Run the server:

```
uvicorn api:app --reload
```

## API

**POST** request on http://127.0.0.1:8000/generate-resume/:

You can find the full example JSON data here: [resume.json](./resume.json)


**Return Response:** {"url": <url of the resume to download pdf file>}
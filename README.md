# people-match
A questions and answers based search for finding the right people according to individual criteria.

## The problem
In this "quick" modern time, search engines such as google, will supply answer most of the time.
But when it comes to finding the right person: "Your one true love", An esoteric person, a unique specialist, or any unique individual or knowledge... your search will retrieve the same "top" results.

## The solution
People.

The seeker will provide several yes/no question quiz.
The spread of the quiz sheet will be done in an intelligent propagated manner until a match will be found with the person.

## Features
- Seeded matchmaking questions focused on partner discovery (e.g., pets, long‑term plans, outdoors).
- In-memory PeopleSearch engine with support for creating users, answering questions, asking new ones, and finding best matches by yes/no criteria.
- Simple Flask UI so anyone can answer questions, introduce their own, and search for compatible people.
- Pytest suite that exercises the matching logic end-to-end.

## Getting started
### Prerequisites
- Python 3.11+
- pip

### Install dependencies
```bash
pip install -r requirements.txt
```

### Run the tests
```bash
pytest
```

### Launch the web UI
```bash
export FLASK_APP=src.app
flask run --reload
```
Then open http://127.0.0.1:5000 to answer questions, add your own, and search for people who match your criteria.

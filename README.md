# Twitter/X Search Exporter — Legacy Python Prototype

A Python command-line prototype for searching posts through the **legacy Twitter API**, cleaning returned text, and exporting results to JSON or CSV. It uses [Tweepy](https://www.tweepy.org/).

> **Compatibility warning:** The source uses `tweepy.API.search` and v1.1-style search arguments. Current Tweepy versions and Twitter/X API access levels may no longer support these methods. **This project has not been tested against a current API subscription and is not confirmed functional today.**

## Repository contents

- `scrapper.py` — actual script entrypoint
- `.env.example` — names of required credential environment variables, with placeholders only
- `.gitignore` — prevents common local credentials, CSV/JSON exports, and logs from accidental future commits
- `LICENSE` — MIT license included in this repository

## Run locally (for controlled legacy compatibility testing)

Create an isolated Python environment:

```bash
git clone https://github.com/29amank/tweet_scrapper.git
cd tweet_scrapper
python -m venv .venv
```

Activate it with `.venv\Scripts\Activate.ps1` on Windows PowerShell, or `source .venv/bin/activate` on Linux/macOS, then install the library:

```bash
python -m pip install tweepy
```

Before running, set **these environment variables** in your terminal or an approved local secret manager:

- `X_CONSUMER_KEY`
- `X_CONSUMER_SECRET`
- `X_ACCESS_TOKEN`
- `X_ACCESS_TOKEN_SECRET`

`.env.example` is a *reference template*. The current script reads **process environment variables**, and does **not** load a `.env` file automatically. Never commit genuine values to GitHub or paste them into public logs.

Run:

```bash
python scrapper.py
```

The script asks for a query, start/end dates, maximum records, and optional text cleanup. If the API call succeeds, it can export data as `tweets.csv` or `tweets.json`. These exports can contain user content, so handle and retain them responsibly.

## Known limitations

- The legacy `API.search` call and date-search parameters may fail under current Tweepy or Twitter/X APIs. Modernizing requires validating the currently permitted API endpoints, authentication and rate limits.
- The script launches only **one** search task in its thread executor; it is not a parallel scraping system despite the previous README's description.
- Output volume, historical date range, and functionality depend on the API service's access policies.
- Six offline tests have passed in GitHub Actions for credential configuration, date validation, text cleanup and synthetic CSV/JSON exports. These **do not** verify real Twitter/X API access or compatibility.
- Runtime dependency versions are not pinned. Run offline tests with `python -m unittest discover -s tests -p 'test_*.py' -v` after installing Tweepy.
- Do not bypass platform access restrictions or collect private data without appropriate authorization.

## Safety

- Credential values are read from environment variables rather than hard-coded in `scrapper.py`.
- `.gitignore` helps prevent accidental future additions, but cannot remove previously tracked data or history.
- Revoke or rotate any credential that was previously exposed.
- Review API terms, data retention, and user privacy before using exported data.

## License

[MIT License](LICENSE) — see the included license file.

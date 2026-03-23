# Tests README

## Overview

This folder contains unit tests for the backend of the Greenhouse Monitoring System.
The tests follow a Test-Driven Development (TDD) approach to verify the weather data pipeline.

## What is Tested

* `get_weather()` – API success and failure cases
* `transform_data()` – correct data formatting
* `save_data()` – database insert behavior
* `collect_data_to_db()` – full pipeline flow
* `init_db_collection()` – database connection handling

## Running Tests

Activate virtual environment:

```
.\backend\.venv\Scripts\Activate.ps1
```

Run tests:

```
python -m unittest discover -s tests
```

## Notes

* Uses `unittest` and `unittest.mock`
* No real API or database is required
* Scheduler loop is not tested (infinite loop)

## Summary

These tests ensure the backend is reliable and handles both normal and error cases correctly.

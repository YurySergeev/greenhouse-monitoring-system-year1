# Tests README

## Overview

This folder contains backend unit tests for the Greenhouse Monitoring System.
The tests verify the weather data pipeline using a Test-Driven Development (TDD) approach.

## What is Tested

* Weather API fetching (`get_weather`)
* Data transformation (`transform_data`)
* Database saving (`save_data`)
* Full pipeline flow (`collect_data_to_db`)
* Database connection (`init_db_collection`)

## Running Tests

Activate virtual environment:

```bash
.\backend\.venv\Scripts\Activate.ps1
```

Run all tests:

```bash
python -m unittest discover -s tests
```

## Notes

* Uses `unittest`
* Uses fake objects instead of real API/database
* No external services are required
* Scheduler loop is not tested

## Summary

These tests ensure the backend works correctly and handles errors safely.

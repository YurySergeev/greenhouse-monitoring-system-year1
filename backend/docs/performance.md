# Database Performance Results

## Index Added
- ts

## Purpose
The timestamp index improves performance for queries that retrieve recent sensor data and sort by time.

## Test Query
```python
list(collection.find().sort("ts", -1).limit(100))
```
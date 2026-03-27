# Greenhouse Monitoring System (GMS)
**Group Alpha**

## Overview
The Greenhouse Monitoring System (GMS) is a software-based monitoring platform designed to observe and visualize environmental conditions within a greenhouse. The system organizes the greenhouse into defined zones and provides data into  metrics that affect plant health and it can be analyzed 

GMS presents this information through a web-based dashboard, allowing users to quickly assess conditions, identify potential issues, and make informed decisions to maintain an optimal growing environment.

---

## Project Objectives
The primary objectives of the Greenhouse Monitoring System are to:

- Monitor  conditions across multiple greenhouse zone, starting with zone 1 as main goal 
- Visualize key metrics such as temperature and humidity through  dashboards
- Design a  scalable system that can integrate physical sensors using Raspberry Pi devices
- Support incremental development, allowing the system to evolve from simulated data from APIs as testing sources to real sensor based data

---

## Development Approach
During the initial development phase, the system focuses on frontend design and functionality using Python and Streamlit. Environmental data is temporarily sourced from the OpenWeather API to simulate sensor readings while hardware integration is in progress and defined by the team it's usage 

This approach enables rapid prototyping, testing, and demonstration of system functionality before transitioning to live sensor data in later phases.

---

## Quick Testing
Run the short automated test suite from the repository root:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

Current coverage includes:
- Temperature conversion utility checks
- Backend weather data transformation checks
- Backend save-path insertion behavior with a fake collection

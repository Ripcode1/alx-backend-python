# Python Generators Project

This project demonstrates advanced usage of Python generators for efficient data processing and memory management.

## Learning Objectives

- Master Python Generators using the `yield` keyword
- Handle Large Datasets with batch processing and lazy loading
- Simulate Real-world Scenarios with streaming data
- Optimize Performance with memory-efficient computations
- Apply SQL Knowledge for dynamic data fetching

## Project Structure

- `seed.py` - Database setup and data seeding
- `0-stream_users.py` - Generator for streaming database rows
- `1-batch_processing.py` - Batch processing with generators
- `2-lazy_paginate.py` - Lazy pagination implementation
- `4-stream_ages.py` - Memory-efficient age aggregation

## Requirements

- Python 3.x
- MySQL database
- mysql-connector-python package

## Setup

1. Install required packages:
```bash
pip install mysql-connector-python
```

2. Run the seed script to set up the database:
```bash
python3 seed.py
```

## Usage

Each task has a corresponding main file for testing:
- `0-main.py` - Test database setup
- `1-main.py` - Test user streaming
- `2-main.py` - Test batch processing
- `3-main.py` - Test lazy pagination
- `4-main.py` - Test age aggregation

## Author

ALX Backend Python Project

# Python Generators for Database Streaming

This project demonstrates how to use Python generators for efficient database operations, focusing on memory optimization when handling large datasets.

## Project Structure

- `seed.py`: Sets up the MySQL database and populates it with sample data
- `0-stream_users.py`: Streams database rows one by one using a generator
- `1-batch_processing.py`: Processes data in batches with generators
- `2-lazy_paginate.py`: Implements lazy loading of paginated data
- `4-stream_ages.py`: Performs memory-efficient aggregation using generators

## Setup Instructions

### Prerequisites

- Python 3.x
- MySQL Server
- `mysql-connector-python` package

Install the required package:

```bash
pip install mysql-connector-python
```

### Database Setup

1. Ensure MySQL is running on your local machine
2. Place your `user_data.csv` file in the same directory as `seed.py`
3. Run the seed script:

```bash
python3 seed.py
```

This will:
- Connect to your MySQL server (default credentials: root/root)
- Create the `ALX_prodev` database if it doesn't exist
- Create the `user_data` table with the specified schema
- Populate the table with data from `user_data.csv`

### Database Schema

The `user_data` table has the following structure:
- `user_id`: Primary Key, UUID, Indexed
- `name`: VARCHAR, NOT NULL
- `email`: VARCHAR, NOT NULL
- `age`: DECIMAL, NOT NULL

## Running the Examples

Each script can be executed independently:

```bash
python3 0-stream_users.py
python3 1-batch_processing.py
python3 2-lazy_paginate.py
python3 4-stream_ages.py
```

## Project Tasks

### 1. Stream Users One by One
- Uses a generator to fetch database rows efficiently one at a time
- Implementation in `0-stream_users.py`

### 2. Batch Processing
- Fetches and processes data in configurable batch sizes
- Filters users over the age of 25
- Implementation in `1-batch_processing.py`

### 3. Lazy Loading with Pagination
- Simulates API-style pagination but loads pages only when needed
- Implementation in `2-lazy_paginate.py`

### 4. Memory-Efficient Aggregation
- Calculates average age without loading entire dataset into memory
- Implementation in `4-stream_ages.py`

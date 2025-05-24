README.md
Advanced Python: Generators, Decorators, Context Managers, and Asynchronous Programming
This project provides a comprehensive exploration of advanced Python programming techniques, including generators, decorators, context managers, and asynchronous programming. These concepts empower developers to write efficient, readable, and maintainable code for scenarios involving large data processing, resource management, and concurrent execution.
Table of Contents
Project Overview (#project-overview)
Learning Objectives (#learning-objectives)
Key Concepts (#key-concepts)
Generators (#generators)
Decorators (#decorators)
Context Managers (#context-managers)
Asynchronous Programming (#asynchronous-programming)
Project Requirements (#project-requirements)
Tasks (#tasks)
Task 0: Getting Started with Python Generators (#task-0-getting-started-with-python-generators)
Task 1: Generator that Streams Rows from an SQL Database (#task-1-generator-that-streams-rows-from-an-sql-database)
Task 2: Batch Processing Large Data (#task-2-batch-processing-large-data)
Task 3: Lazy Loading Paginated Data (#task-3-lazy-loading-paginated-data)
Task 4: Memory-Efficient Aggregation with Generators (#task-4-memory-efficient-aggregation-with-generators)
Additional Resources (#additional-resources)
Repository (#repository)
Project Overview
This project focuses on leveraging Python's advanced features to handle large datasets, manage resources efficiently, and implement concurrent programming. By completing the tasks, you will gain hands-on experience with:
Creating memory-efficient iterators using generators.
Modifying function behavior with decorators.
Managing resources safely with context managers.
Writing non-blocking, concurrent code using asynchronous programming.
Integrating Python with SQL databases for dynamic data processing.
The tasks emphasize practical applications such as streaming data from a MySQL database, batch processing, lazy loading, and computing aggregates efficiently.
Learning Objectives
By completing this project, you will:
Master generators for memory-efficient iterative data processing.
Use decorators to modify function behavior and promote code reusability.
Implement context managers to manage resources like files and database connections.
Write asynchronous code using asyncio for concurrent execution of IO-bound tasks.
Handle large datasets efficiently using batch processing and lazy loading.
Integrate Python with SQL databases to fetch and process data dynamically.
Optimize performance by minimizing memory usage and leveraging Python’s yield keyword.
Key Concepts
Generators
Generators are iterators that yield values one at a time, enabling memory-efficient processing and lazy evaluation. They are defined using the yield keyword and are ideal for handling large datasets or streams.
Key Features:
Generator Functions: Use yield to produce values incrementally.
Generator Expressions: Similar to list comprehensions but return generator objects.
Benefits:
Memory efficiency by generating one item at a time.
Lazy evaluation for on-demand computation.
Example:
python
# Generator Function
def firstn(n):
    num = 0
    while num < n:
        yield num
        num += 1

# Generator Expression
squares = (x * x for x in range(10))
Decorators
Decorators are functions that modify the behavior of other functions or methods. They are applied using the @decorator_name syntax and are useful for adding functionality like logging or access control without altering the original code.
Key Features:
Basic Structure: Wraps a function with an inner wrapper function.
Flexible Arguments: Handles varying arguments using *args and **kwargs.
Benefits:
Code reusability across multiple functions.
Separation of concerns for cleaner code.
Example:
python
# Simple Decorator
def decorator(func):
    def wrapper():
        print("Before function call")
        func()
        print("After function call")
    return wrapper

@decorator
def say_hello():
    print("Hello!")

# Decorator with Arguments
def do_twice(func):
    def wrapper_do_twice(*args, **kwargs):
        func(*args, **kwargs)
        func(*args, **kwargs)
    return wrapper_do_twice

@do_twice
def greet(name):
    print(f"Hello {name}")
Context Managers
Context managers ensure resources are properly acquired and released, typically using the with statement. They are ideal for managing file operations, network connections, or locks.
Key Features:
Class-based Context Managers: Use __enter__ and __exit__ methods.
Contextlib-based Context Managers: Use @contextmanager decorator for simpler implementation.
Benefits:
Automatic resource management (e.g., closing files).
Cleaner, more readable code.
Example:
python
# Class-based Context Manager
class File:
    def __init__(self, filename, method):
        self.file_obj = open(filename, method)

    def __enter__(self):
        return self.file_obj

    def __exit__(self, type, value, traceback):
        self.file_obj.close()

with File('demo.txt', 'w') as f:
    f.write('Hello World!')

# Contextlib-based Context Manager
from contextlib import contextmanager

@contextmanager
def open_file(name):
    f = open(name, 'w')
    try:
        yield f
    finally:
        f.close()

with open_file('demo.txt') as f:
    f.write('Hello World!')
Asynchronous Programming
Asynchronous programming enables non-blocking code execution for concurrent tasks, using Python’s asyncio library with async and await keywords. It is ideal for IO-bound tasks like web servers and network communication.
Key Features:
Coroutines: Functions defined with async def that can pause and resume.
Event Loop: Manages execution of coroutines and asynchronous tasks.
Concurrency with asyncio: Runs multiple coroutines concurrently without multithreading.
Benefits:
Improved performance for IO-bound tasks.
Efficient concurrency without threading overhead.
Example:
python
import asyncio

# Basic Coroutine
async def greet(name):
    print(f"Hello {name}")
    await asyncio.sleep(1)
    print(f"Goodbye {name}")

asyncio.run(greet("World"))

# Running Multiple Coroutines
async def main():
    await asyncio.gather(
        greet("Alice"),
        greet("Bob"),
    )

asyncio.run(main())
Project Requirements
Proficiency in Python 3.x.
Understanding of yield and generator functions.
Familiarity with SQL and database operations (MySQL, SQLite).
Basic knowledge of database schema design and data seeding.
Ability to use Git and GitHub for version control.
Tasks
Task 0: Getting Started with Python Generators
Objective: Set up a MySQL database and create a generator to stream rows from it one by one.
Instructions:
Write a script seed.py to:
Connect to a MySQL database server (connect_db()).
Create a database ALX_prodev if it doesn’t exist (create_database()).
Connect to the ALX_prodev database (connect_to_prodev()).
Create a table user_data with fields:
user_id (UUID, Primary Key, Indexed)
name (VARCHAR, NOT NULL)
email (VARCHAR, NOT NULL)
age (DECIMAL, NOT NULL)
Populate the table with data from user_data.csv (insert_data()).
Example Output:
bash
connection successful
Table user_data created successfully
Database ALX_prodev is present
[('00234e50-34eb-4ce2-94ec-26e3fa749796', 'Dan Altenwerth Jr.', 'Molly59@gmail.com', 67), ...]
Repository:
GitHub repository: alx-backend-python
Directory: python-generators-0x00
File: seed.py
Task 1: Generator that Streams Rows from an SQL Database
Objective: Create a generator to stream rows one by one from the user_data table.
Instructions:
In 0-stream_users.py, write a function stream_users() that:
Uses a generator with yield to fetch rows one by one.
Contains no more than one loop.
Example Output:
bash
{'user_id': '00234e50-34eb-4ce2-94ec-26e3fa749796', 'name': 'Dan Altenwerth Jr.', 'email': 'Molly59@gmail.com', 'age': 67}
{'user_id': '006bfede-724d-4cdd-a2a6-59700f40d0da', 'name': 'Glenda Wisozk', 'email': 'Miriam21@gmail.com', 'age': 119}
...
Repository:
GitHub repository: alx-backend-python
Directory: python-generators-0x00
File: 0-stream_users.py
Task 2: Batch Processing Large Data
Objective: Create a generator to fetch and process data in batches from the user_data table.
Instructions:
In 1-batch_processing.py, write:
stream_users_in_batches(batch_size): Fetches rows in batches using a generator.
batch_processing(batch_size): Processes each batch to filter users over 25 years old.
Use no more than three loops.
Example Output:
bash
{'user_id': '00234e50-34eb-4ce2-94ec-26e3fa749796', 'name': 'Dan Altenwerth Jr.', 'email': 'Molly59@gmail.com', 'age': 67}
{'user_id': '006bfede-724d-4cdd-a2a6-59700f40d0da', 'name': 'Glenda Wisozk', 'email': 'Miriam21@gmail.com', 'age': 119}
...
Repository:
GitHub repository: alx-backend-python
Directory: python-generators-0x00
File: 1-batch_processing.py
Task 3: Lazy Loading Paginated Data
Objective: Simulate fetching paginated data using a generator to lazily load each page.
Instructions:
In 2-lazy_paginate.py, write:
lazy_paginate(page_size): Uses a generator to fetch pages lazily, starting at offset 0.
Include paginate_users(page_size, offset) to fetch data for a specific page.
Use only one loop.
Example Output:
bash
{'user_id': '00234e50-34eb-4ce2-94ec-26e3fa749796', 'name': 'Dan Altenwerth Jr.', 'email': 'Molly59@gmail.com', 'age': 67}
{'user_id': '006bfede-724d-4cdd-a2a6-59700f40d0da', 'name': 'Glenda Wisozk', 'email': 'Miriam21@gmail.com', 'age': 119}
...
Repository:
GitHub repository: alx-backend-python
Directory: python-generators-0x00
File: 2-lazy_paginate.py
Task 4: Memory-Efficient Aggregation with Generators
Objective: Use a generator to compute the average age of users in a memory-efficient way.
Instructions:
In 4-stream_ages.py, write:
stream_user_ages(): Yields user ages one by one.
A function to calculate the average age without loading the entire dataset into memory.
Print: Average age of users: <average_age>.
Use no more than two loops.
Do not use SQL’s AVERAGE function.
Repository:
GitHub repository: alx-backend-python
Directory: python-generators-0x00
File: 4-stream_ages.py
Additional Resources
Python Generators
How to Use Generators in Python
Python Decorators
Context Managers
Asynchronous Programming in Python
Repository
GitHub repository: alx-backend-python
Directory: python-generators-0x00
Files:
seed.py
0-stream_users.py
1-batch_processing.py
2-lazy_paginate.py
4-stream_ages.py
README.md
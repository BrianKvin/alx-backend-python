### README.md

- ### Advanced Python: Generators, Decorators, Context Managers, and Asynchronous Programming
  This project provides a comprehensive exploration of advanced Python programming techniques, including generators, decorators, context managers, and asynchronous programming. These concepts empower developers to write efficient, readable, and maintainable code for scenarios involving large data processing, resource management, and concurrent execution.

### Table of Contents

- Project Overview (#project-overview)
- Learning Objectives (#learning-objectives)
- Key Concepts (#key-concepts)
- Generators (#generators)
- Decorators (#decorators)
- Context Managers (#context-managers)
- Asynchronous Programming (#asynchronous-programming)
- Project Requirements (#project-requirements)
- Tasks (#tasks)
- Task 0: Getting Started with Python Generators (#task-0-getting-started-with-python-generators)
- Task 1: Generator that Streams Rows from an SQL Database (#task-1-generator-that-streams-rows-from-an-sql-database)
- Task 2: Batch Processing Large Data (#task-2-batch-processing-large-data)
- Task 3: Lazy Loading Paginated Data (#task-3-lazy-loading-paginated-data)
- Task 4: Memory-Efficient Aggregation with Generators (#task-4-memory-efficient-aggregation-with-generators)

### Additional Resources (#additional-resources)

### Repository (#repository)

### Project Overview

This project focuses on leveraging Python's advanced features to handle large datasets, manage resources efficiently, and implement concurrent programming. By completing the tasks, you will gain hands-on experience with:

- Creating memory-efficient iterators using generators.
- Modifying function behavior with decorators.
- Managing resources safely with context managers.
- Writing non-blocking, concurrent code using asynchronous programming.
- Integrating Python with SQL databases for dynamic data processing.
- The tasks emphasize practical applications such as streaming data from a MySQL database, batch processing, lazy loading, and computing aggregates efficiently.

### Learning Objectives

### By completing this project, you will:

- Master generators for memory-efficient iterative data processing.
- Use decorators to modify function behavior and promote code reusability.
- Implement context managers to manage resources like files and database connections.
- Write asynchronous code using asyncio for concurrent execution of IO-bound tasks.
- Handle large datasets efficiently using batch processing and lazy loading.
- Integrate Python with SQL databases to fetch and process data dynamically.
- Optimize performance by minimizing memory usage and leveraging Python’s yield keyword.

### Key Concepts

- Generators
- Generators are iterators that yield values one at a time, enabling memory-efficient processing and lazy evaluation. They are defined using the yield keyword and are ideal for handling large datasets or streams.

### Key Features:

- Generator Functions: Use yield to produce values incrementally.
- Generator Expressions: Similar to list comprehensions but return generator objects.

### Benefits:

- Memory efficiency by generating one item at a time.
- Lazy evaluation for on-demand computation.

### Example:

python

### Generator Function

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
Flexible Arguments: Handles varying arguments using *args and \*\*kwargs.
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
def wrapper_do_twice(*args, \*\*kwargs):
func(*args, **kwargs)
func(\*args, **kwargs)
return wrapper_do_twice

@do_twice
def greet(name):
print(f"Hello {name}")
Context Managers
Context managers ensure resources are properly acquired and released, typically using the with statement. They are ideal for managing file operations, network connections, or locks.
Key Features:
Class-based Context Managers: Use **enter** and **exit** methods.
Contextlib-based Context Managers: Use @contextmanager decorator for simpler implementation.
Benefits:
Automatic resource management (e.g., closing files).
Cleaner, more readable code.
Example:
python

# Class-based Context Manager

class File:
def **init**(self, filename, method):
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

### Asynchronous Programming

Asynchronous programming enables non-blocking code execution for concurrent tasks, using Python’s asyncio library with async and await keywords. It is ideal for IO-bound tasks like web servers and network communication.

### Key Features:

- Coroutines: Functions defined with async def that can pause and resume.
- Event Loop: Manages execution of coroutines and asynchronous tasks.
- Concurrency with asyncio: Runs multiple coroutines concurrently without multithreading.

### Benefits:

- Improved performance for IO-bound tasks.
- Efficient concurrency without threading overhead.

### Example:

python
import asyncio

### Basic Coroutine

async def greet(name):
print(f"Hello {name}")
await asyncio.sleep(1)
print(f"Goodbye {name}")

asyncio.run(greet("World"))

#### Running Multiple Coroutines

async def main():
await asyncio.gather(
greet("Alice"),
greet("Bob"),
)

asyncio.run(main())

# Project Requirements

- Proficiency in Python 3.x.
- Understanding of yield and generator functions.
- Familiarity with SQL and database operations (MySQL, SQLite).
- Basic knowledge of database schema design and data seeding.
- Ability to use Git and GitHub for version control.

# Tasks

Here's your content rewritten as a clean and professional `README.md` file:

---

# 📦 Task 0: Getting Started with Python Generators

## 🎯 Objective

Set up a MySQL database and use a Python generator to stream user data rows one by one.

---

## 📜 Instructions

### 🔧 1. Create `seed.py` with the following functionality:

#### ✅ Connect to MySQL Server

* **Function:** `connect_db()`
* Connects to the MySQL server.

#### ✅ Create the Database

* **Function:** `create_database()`
* Creates a database named `ALX_prodev` if it doesn’t already exist.

#### ✅ Connect to the `ALX_prodev` Database

* **Function:** `connect_to_prodev()`
* Connects specifically to the `ALX_prodev` database.

#### ✅ Create `user_data` Table

* **Function:** `create_table()`
* Table schema:

  * `user_id` – UUID, **Primary Key**, **Indexed**
  * `name` – `VARCHAR`, **NOT NULL**
  * `email` – `VARCHAR`, **NOT NULL**
  * `age` – `DECIMAL`, **NOT NULL**

#### ✅ Populate Table from CSV

* **Function:** `insert_data()`
* Populates `user_data` table with rows from `user_data.csv`.

---

## 📤 Example Output

```bash
connection successful
Table user_data created successfully
Database ALX_prodev is present
[('00234e50-34eb-4ce2-94ec-26e3fa749796', 'Dan Altenwerth Jr.', 'Molly59@gmail.com', 67), ...]
```

---

## 📂 Repository Structure

* **GitHub Repository:** `alx-backend-python`
* **Directory:** `python-generators-0x00`
* **Main Script:** `seed.py`

---

---

## 🔁 Task 1: Generator That Streams Rows from an SQL Database

### 🎯 Objective

Create a Python generator that streams rows from the `user_data` table one by one.

---

### 📜 Instructions

In the file `0-stream_users.py`, implement a function called `stream_users()` that:

* Connects to the `ALX_prodev` MySQL database.
* Fetches all rows from the `user_data` table.
* Yields each row **one at a time** using a generator.
* Contains **no more than one loop** in the function.

---

### 🧪 Example Output

```bash
{'user_id': '00234e50-34eb-4ce2-94ec-26e3fa749796', 'name': 'Dan Altenwerth Jr.', 'email': 'Molly59@gmail.com', 'age': 67}
{'user_id': '006bfede-724d-4cdd-a2a6-59700f40d0da', 'name': 'Glenda Wisozk', 'email': 'Miriam21@gmail.com', 'age': 119}
...
```

---

### 📂 Repository Structure

* **GitHub Repository:** `alx-backend-python`
* **Directory:** `python-generators-0x00`
* **File:** `0-stream_users.py`

---

---

## 📦 Task 2: Batch Processing Large Data

### 🎯 Objective

Use a generator to fetch and process data from the `user_data` table in batches.

---

### 📜 Instructions

In the file `1-batch_processing.py`, implement the following:

#### 🔁 `stream_users_in_batches(batch_size)`

* A generator function that fetches rows in batches from the database.
* Uses a database cursor and `fetchmany()` for memory-efficient streaming.

#### 🧮 `batch_processing(batch_size)`

* Iterates through each batch.
* Filters and prints users whose `age` is **greater than 25**.
* Uses **no more than three loops** in total.

---

### 🧪 Example Output

```bash
{'user_id': '00234e50-34eb-4ce2-94ec-26e3fa749796', 'name': 'Dan Altenwerth Jr.', 'email': 'Molly59@gmail.com', 'age': 67}
{'user_id': '006bfede-724d-4cdd-a2a6-59700f40d0da', 'name': 'Glenda Wisozk', 'email': 'Miriam21@gmail.com', 'age': 119}
...
```

---

### 📂 Repository Structure

* **GitHub Repository:** `alx-backend-python`
* **Directory:** `python-generators-0x00`
* **File:** `1-batch_processing.py`

---

---

## 🚀 Task 3: Lazy Loading Paginated Data

### 🎯 Objective

Simulate fetching paginated records from the `user_data` table using a generator for **lazy loading**—efficiently handling large datasets by only loading one page at a time.

---

### 📜 Instructions

In `2-lazy_paginate.py`, implement the following:

#### 📄 `paginate_users(page_size, offset)`

* Fetch a specific page of data from the table using `LIMIT` and `OFFSET`.

#### 🌀 `lazy_paginate(page_size)`

* A generator that yields each page of data.
* Starts at `offset = 0` and increases until no more results are found.
* Must use **only one loop**.

---

### 🧪 Example Output

```bash
{'user_id': '00234e50-34eb-4ce2-94ec-26e3fa749796', 'name': 'Dan Altenwerth Jr.', 'email': 'Molly59@gmail.com', 'age': 67}
{'user_id': '006bfede-724d-4cdd-a2a6-59700f40d0da', 'name': 'Glenda Wisozk', 'email': 'Miriam21@gmail.com', 'age': 119}
...
```

---

## 🧠 Task 4: Memory-Efficient Aggregation with Generators

### 🎯 Objective

Stream user ages one at a time and calculate their average without loading all records into memory.

---

### 📜 Instructions

In `4-stream_ages.py`, implement:

#### 🌀 `stream_user_ages()`

* A generator that yields each user's `age` from the `user_data` table one by one.

#### ➗ Average Age Function

* Iterate over the stream and compute the average.
* **Do not** use SQL's `AVG()` function.
* Use **no more than two loops**.

#### ✅ Output Format

```bash
Average age of users: 45.67
```

---

## 📁 Repository Structure

| File                    | Purpose                                                       |
| ----------------------- | ------------------------------------------------------------- |
| `seed.py`               | Sets up the MySQL database and populates `user_data` from CSV |
| `0-stream_users.py`     | Streams user rows one by one                                  |
| `1-batch_processing.py` | Fetches and filters users in batches                          |
| `2-lazy_paginate.py`    | Implements lazy pagination using generators                   |
| `4-stream_ages.py`      | Streams and aggregates user ages efficiently                  |
| `README.md`             | Project documentation                                         |

---


---

# 🧠 Python Quiz: Intermediate Concepts

This README documents quiz questions and answers covering intermediate Python topics such as decorators, context managers, asynchronous programming, generators, and memory optimization techniques.

---

## ✅ Quiz Completion

Congratulations! You've successfully completed the quiz. Review the questions and answers below for quick reference and revision.

---

## 📋 Quiz Questions and Options

### Question 0

**What does the `@contextmanager` decorator do in Python?**

* [ ] It creates a class-based context manager
* [ ] It provides a shortcut for defining decorators
* [ ] It converts a function into an async function
* [x] It converts a generator function into a context manager

---

### Question 1

**How can a Python decorator handle functions with different arguments?**

* [ ] Use a specific argument signature for the wrapper function
* [ ] Modify the original function to match the wrapper signature
* [x] Use `*args` and `**kwargs` in the wrapper function
* [ ] Decorators cannot handle functions with arguments

---

### Question 2

**What is the main difference between Python’s `range()` in Python 3 and `xrange()` in Python 2?**

* [ ] `range()` returns a generator while `xrange()` returns a list
* [ ] `xrange()` is only available in Python 3
* [ ] `xrange()` is slower than `range()`
* [x] `range()` returns an immutable sequence, while `xrange()` returns a generator

---

### Question 3

**In an asynchronous Python program, what does `asyncio.run()` do?**

* [x] Runs the given coroutine and blocks until it is complete
* [ ] Starts an event loop without blocking
* [ ] Converts a function into a coroutine
* [ ] Schedules a coroutine to run later

---

### Question 4

**Which method is essential for creating a context manager using a class?**

* [ ] `__call__`
* [x] `__enter__` and `__exit__`
* [ ] `__new__`
* [ ] `__del__`

---

### Question 5

**What is a key advantage of using a generator function over returning a list in Python?**

* [x] Reduces memory usage
* [ ] Ensures type safety
* [ ] Increases execution speed
* [ ] Simplifies code structure

---

### Question 6

**Which of the following best describes a Python decorator?**

* [ ] A function that replaces another function
* [ ] A method for optimizing code execution
* [x] A function that wraps another function to modify its behavior
* [ ] A way to repeat the execution of a function

---

### Question 7

**Which statement about generator expressions is true?**

* [ ] They cannot be composed with other generators
* [ ] They return lists that are lazily evaluated
* [ ] They always consume more memory than list comprehensions
* [x] They are syntactically similar to list comprehensions but use parentheses instead of square brackets

---

### Question 8

**How can you turn a list comprehension into a generator expression?**

* [ ] Use curly braces `{}` instead of square brackets
* [ ] Add a `yield` statement inside the comprehension
* [ ] Use double square brackets `[[ ]]`
* [x] Use parentheses `()` instead of square brackets

---

### Question 9

**What happens if the `__exit__` method of a context manager returns `True` after an exception is raised?**

* [ ] The exception is re-raised
* [ ] The context manager is reset to its initial state
* [ ] The program terminates
* [x] The exception is suppressed

---

## 📚 Topics Covered

* Context Managers
* Decorators
* Asynchronous Programming
* Generator Functions and Expressions
* Memory Efficiency
* Python 2 vs 3 Differences

---

## 📚 Additional Resources

* [Python Generators – Real Python](https://realpython.com/introduction-to-python-generators/)
* [Python Decorators](https://realpython.com/primer-on-python-decorators/)
* [Context Managers](https://docs.python.org/3/library/contextlib.html)
* [Asynchronous Programming](https://docs.python.org/3/library/asyncio.html)

---


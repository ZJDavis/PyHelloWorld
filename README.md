# Python Program Menu Project
## (Formerly Python "Hello World" Project)

A modular Python project that provides a menu-driven interface for running multiple standalone Python programs. Each program is implemented as its own class, stored in a separate file, and automatically discovered at runtime.

This repository is designed to be **extensible**, **educational**, and **easy to grow** as new programs are added.

---

## 📌 Project Goals

* Demonstrate clean Python architecture using classes and packages
* Allow new programs to be added without modifying menu code
* Provide a simple command-line user experience
* Serve as a learning sandbox for experimenting with Python programs

---

## 🗂️ Project Structure

```
project_root/
│
├── main.py                 # Application entry point
├── PyProgramBase.py        # Base class for all programs
├── README.md               # Project documentation
│
└── programs/               # Individual program implementations
    ├── __init__.py
    ├── PyHelloWorld.py
    ├── PyMathProgram.py
    ├── PyRecamansSequence.py
```

---

## ▶️ How to Run

Make sure you have Python 3.9+ installed.

From the project root directory:

```bash
python main.py
```

You will be presented with a numbered menu. Enter a number to execute the corresponding program.

---

## 🧠 How It Works

* `main.py` automatically discovers program classes in the `programs/` folder
* Only files starting with `Py` are loaded
* Each program must:

  * Be defined in its own file
  * Inherit from `ProgramBase`
  * Implement a `run()` method

No manual registration is required — new programs appear automatically in the menu.

---

## 🧩 Adding a New Program

1. Create a new file in the `programs/` directory:

```
programs/PyMyNewProgram.py
```

2. Use the following template:

```python
from PyProgramBase import ProgramBase

class MyNewProgram(ProgramBase):
    def run(self):
        print("My new program is running!")
```

3. Run `main.py` — your program will appear in the menu automatically.

---

## 📦 Included Programs

### Hello World

Basic example program used to verify the menu and discovery system.

### Math Program

Simple arithmetic demonstration.

### Recamán’s Sequence

A persistent implementation of Recamán’s sequence that:

* Stores the entire sequence across runs
* Prevents duplicates
* Appends 100 new values per execution
* Monitors storage file size and prompts for reset if it exceeds 10 MB

The sequence is stored locally in `recaman_sequence.json`.

---

## 🔄 Resetting Stored Data

Some programs (such as Recamán’s Sequence) persist data to disk.

To reset stored data manually, delete the associated `.json` file from the project root.

---

## 🛠️ Future Ideas

This README is intentionally designed to grow. Possible future additions:

* Program categories
* Configuration file support
* Logging and diagnostics
* Unit tests
* Plugin-style enable/disable flags

---

## 📖 Markdown Notes (for Editing This File)

* `#` = Main heading
* `##` = Section heading
* `###` = Subsection heading
* Triple backticks (```) create code blocks
* Blank lines improve readability

Markdown is designed to be readable as plain text — keep it simple.

---

## 📄 License

This project is for personal and educational use. Add a license here if you plan to distribute it.

# Truth Table Generator Plus

A Tkinter-based GUI application for generating and analyzing propositional logic formulas. Features include:

- Full truth table generation
- Tautology and contradiction checks
- Disjunctive Normal Form (DNF) and Conjunctive Normal Form (CNF) construction
- Karnaugh maps for 2-variable functions

## Author

Yathin Vemula

## Date

April 22, 2025

## Requirements

- Python 3.6 or higher
- Tkinter (usually included with Python)
- Standard Python libraries: `itertools`, `re`, `sys`

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/truth-table-generator-plus.git
   cd truth-table-generator-plus
   ```

2. (Optional) Create and activate a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. Ensure Python and Tkinter are installed on your system.

## Usage

Run the application with:

```bash
python3 truth_table_generator_plus.py
```

On Windows:

```bash
python truth_table_generator_plus.py
```

- Enter a propositional logic formula (e.g., `A AND B -> C`) in the input field.
- Click **Generate** to produce the truth table.
- Use toolbar buttons to check for tautologies, contradictions, display DNF, CNF, or show the K-Map (for 2-variable formulas).

Enjoy exploring propositional logic!


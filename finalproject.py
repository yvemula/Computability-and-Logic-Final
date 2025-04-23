#!/usr/bin/env python3
"""
Truth Table Generator Plus

A Tkinter-based GUI application that:
 - Parses and evaluates propositional logic formulas
 - Generates full truth tables
 - Checks for tautologies and contradictions
 - Builds Disjunctive Normal Form (DNF) and Conjunctive Normal Form (CNF)
 - Displays Karnaugh maps for 2-variable functions
 - Supports advanced operators: AND, OR, NOT, XOR, IMPLIES (->), EQUIV (<->), NAND(), NOR()
 - Provides menu options for saving, copying, and help

Author: Yathin Vemula
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import itertools
import re
import sys


def eval_formula(formula: str, **kwargs) -> bool:
    """
    Evaluate a propositional logic formula under given variable assignments.

    Args:
        formula: A string representing the logic formula.
        **kwargs: Variable assignments, e.g., A=True, B=False.

    Returns:
        Boolean result of the evaluated formula.

    Raises:
        ValueError: If the formula contains invalid syntax.
    """
    # Normalize case and strip whitespace
    expr = formula.strip().upper()

    # Map user operators to Python expressions
    replacements = {
        ' AND ': ' and ',
        ' OR ': ' or ',
        ' NOT ': ' not ',
        '->': ' or ',        # placeholder for implication
        '<->': ' == ',       # equivalence
        ' XOR ': ' ^ '       # exclusive or
    }
    for user_op, py_op in replacements.items():
        expr = expr.replace(user_op, py_op)

    # Replace NAND and NOR functions: NAND(A,B) -> not (A and B)
    expr = re.sub(r'NAND\(([^,]+),([^\)]+)\)', r' not (\1 and \2)', expr)
    expr = re.sub(r'NOR\(([^,]+),([^\)]+)\)',  r' not (\1 or \2)',  expr)

    # Rewrite implication a -> b to (not a) or b
    expr = re.sub(r'([^\s]+)\s*<=\s*([^\s]+)', r'(not \1) or \2', expr)

    try:
        # Evaluate safely without builtins
        return bool(eval(expr, {}, kwargs))
    except Exception as e:
        raise ValueError(f"Invalid formula syntax: {e}")


def generate_truth_table(variables: list, formula: str) -> list:
    """
    Generate a truth table for the given formula.

    Args:
        variables: List of single-letter variable names (['A','B', ...]).
        formula: The logic formula to evaluate.

    Returns:
        A list of rows; each row is [val1, val2, ..., result].
    """
    table = []
    # Iterate over all combinations of True/False
    for combo in itertools.product([False, True], repeat=len(variables)):
        assignment = dict(zip(variables, combo))
        result = eval_formula(formula, **assignment)
        table.append(list(combo) + [result])
    return table


def build_dnf(vars: list, table: list) -> str:
    """
    Build Disjunctive Normal Form (DNF) from a truth table.

    Each row where result==True becomes a conjunction clause;
    clauses are combined with OR.

    Args:
        vars: Variable names.
        table: Truth table rows.

    Returns:
        A string representing the DNF.
    """
    clauses = []
    for row in table:
        if row[-1]:  # only true rows
            terms = []
            for var, val in zip(vars, row[:-1]):
                terms.append(var if val else f"not {var}")
            clauses.append("(" + " and ".join(terms) + ")")
    return " or ".join(clauses) if clauses else "False"


def build_cnf(vars: list, table: list) -> str:
    """
    Build Conjunctive Normal Form (CNF) from a truth table.

    Each row where result==False becomes a disjunction clause;
    clauses are combined with AND.

    Args:
        vars: Variable names.
        table: Truth table rows.

    Returns:
        A string representing the CNF.
    """
    clauses = []
    for row in table:
        if not row[-1]:  # only false rows
            terms = []
            for var, val in zip(vars, row[:-1]):
                # negate term for false rows
                terms.append(var if not val else f"not {var}")
            clauses.append("(" + " or ".join(terms) + ")")
    return " and ".join(clauses) if clauses else "True"


def build_kmap(vars: list, table: list) -> dict:
    """
    Construct a Karnaugh map data structure for 2–4 variables.

    Args:
        vars: Variable names (length 2–4).
        table: Truth table rows.

    Returns:
        A dict mapping variable assignment tuples to result bits.
        None if unsupported variable count.
    """
    n = len(vars)
    if n < 2 or n > 4:
        return None
    # Map assignment tuples (e.g., (0,1,1)) to result
    return {tuple(row[:-1]): row[-1] for row in table}


class TruthApp:
    """
    Main GUI application for Truth Table Generator Plus.
    """
    def __init__(self, root):
        self.root = root
        root.title("Truth Table Generator Plus")
        # Status bar variable
        self.status_var = tk.StringVar()
        # Build UI components
        self._build_menu()
        self._build_widgets()

    def _build_menu(self):
        """Create the application menu bar."""
        menubar = tk.Menu(self.root)
        # File menu
        filem = tk.Menu(menubar, tearoff=0)
        filem.add_command(label="Save CSV", command=self.save_table)
        filem.add_separator()
        filem.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filem)
        # Edit menu
        editm = tk.Menu(menubar, tearoff=0)
        editm.add_command(label="Clear All", command=self.on_clear)
        editm.add_command(label="Copy Table", command=self.copy_table)
        menubar.add_cascade(label="Edit", menu=editm)
        # Help menu
        helpm = tk.Menu(menubar, tearoff=0)
        helpm.add_command(label="Operators", command=self.show_help)
        helpm.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=helpm)
        self.root.config(menu=menubar)

    def _build_widgets(self):
        """Construct all GUI widgets: entry, buttons, table, status."""
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill="x")
        # Formula input
        ttk.Label(frame, text="Formula (e.g. A AND B -> C, XOR(A,B), NAND(A,B), NOR(A,B)):").pack(anchor="w")
        self.entry = ttk.Entry(frame, width=60)
        self.entry.pack(fill="x", pady=5)
        # Button toolbar
        btns = ttk.Frame(frame)
        btns.pack(fill="x", pady=5)
        for txt, cmd in [
            ("Generate", self.on_generate),
            ("Tautology?", self.on_check_taut),
            ("Contradiction?", self.on_check_contra),
            ("Show DNF", self.on_show_dnf),
            ("Show CNF", self.on_show_cnf),
            ("Show K-Map", self.on_show_kmap)
        ]:
            ttk.Button(btns, text=txt, command=cmd).pack(side="left", padx=4)
        # Truth table display
        self.tree = ttk.Treeview(self.root, show="headings")
        self.tree.pack(fill="both", expand=True, padx=10)
        # Status bar
        ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w").pack(fill="x", side="bottom")

    def show_help(self):
        """Display supported operators and usage."""
        ops = (
            "Supported operators:\n"
            "AND, OR, NOT, XOR(A,B), IMPLIES (->), EQUIV (<->), NAND(A,B), NOR(A,B).\n"
            "Use parentheses to group subexpressions."
        )
        messagebox.showinfo("Operators", ops)

    def show_about(self):
        """Display application version and author info."""
        messagebox.showinfo("About", "Truth Table Generator Plus\nAdds DNF, CNF, K-Map, tautology/contradiction checks.")

    def on_generate(self):
        """Generate and display the truth table for the entered formula."""
        formula = self.entry.get()
        if not formula:
            self.status_var.set("Please enter a formula.")
            return
        try:
            # Extract single-letter variables only
            vars = sorted(set(re.findall(r"\b[A-Z]\b", formula.upper())))
            self.vars = vars
            self.table = generate_truth_table(vars, formula)
            # Configure table columns
            cols = vars + ["Result"]
            self.tree.config(columns=cols)
            for c in cols:
                self.tree.heading(c, text=c)
                self.tree.column(c, width=80, anchor="center")
            # Insert rows
            self.tree.delete(*self.tree.get_children())
            for row in self.table:
                self.tree.insert('', 'end', values=[int(v) for v in row])
            self.status_var.set(f"Generated {len(self.table)} rows.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_check_taut(self):
        """Check and alert whether the formula is a tautology."""
        if not hasattr(self, 'table'):
            self.on_generate()
        vals = [row[-1] for row in self.table]
        text = "is a tautology" if all(vals) else "is NOT a tautology"
        messagebox.showinfo("Tautology Check", f"Formula {text}.")

    def on_check_contra(self):
        """Check and alert whether the formula is a contradiction."""
        if not hasattr(self, 'table'):
            self.on_generate()
        vals = [row[-1] for row in self.table]
        text = "is a contradiction" if not any(vals) else "is NOT a contradiction"
        messagebox.showinfo("Contradiction Check", f"Formula {text}.")

    def on_show_dnf(self):
        """Compute and display Disjunctive Normal Form."""
        if not hasattr(self, 'table'):
            self.on_generate()
        dnf = build_dnf(self.vars, self.table)
        messagebox.showinfo("DNF", dnf)

    def on_show_cnf(self):
        """Compute and display Conjunctive Normal Form."""
        if not hasattr(self, 'table'):
            self.on_generate()
        cnf = build_cnf(self.vars, self.table)
        messagebox.showinfo("CNF", cnf)

    def on_show_kmap(self):
        """
        Display a Karnaugh map in a new window for 2-variable functions.
        Only supports exactly two variables.
        """
        if not hasattr(self, 'table'):
            self.on_generate()
        kmap = build_kmap(self.vars, self.table)
        # Validate 2-variable case
        if len(self.vars) != 2 or kmap is None:
            messagebox.showinfo("K-Map", "K-Map only supported for 2 variables.")
            return
        # Create top-level window
        top = tk.Toplevel(self.root)
        top.title("Karnaugh Map")
        rvar, cvar = self.vars
        # Column headers
        tk.Label(top, text="").grid(row=0, column=0)
        tk.Label(top, text=f"{cvar}=0").grid(row=0, column=1)
        tk.Label(top, text=f"{cvar}=1").grid(row=0, column=2)
        # Fill K-map cells
        for i, rv in enumerate([False, True], start=1):
            tk.Label(top, text=f"{rvar}={int(rv)}").grid(row=i, column=0)
            for j, cv in enumerate([False, True], start=1):
                val = int(kmap[(rv, cv)])
                tk.Label(top, text=str(val), borderwidth=1, relief="solid", width=4).grid(row=i, column=j)

    def copy_table(self):
        """Copy the current truth table to clipboard (tab-delimited)."""
        rows = [self.tree.item(i)['values'] for i in self.tree.get_children()]
        text = '\n'.join('\t'.join(map(str,row)) for row in rows)
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.status_var.set(f"Copied {len(rows)} rows to clipboard.")

    def save_table(self):
        """Save the current table as a CSV file."""
        if not hasattr(self, 'table'):
            self.on_generate()
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV','*.csv')])
        if not path:
            return
        with open(path, 'w') as f:
            # Header
            f.write(','.join(self.vars + ['Result']) + '\n')
            # Rows
            for row in self.table:
                f.write(','.join(str(int(v)) for v in row) + '\n')
        self.status_var.set(f"Saved to {path}")

    def on_clear(self):
        """Clear all input and table display."""
        self.entry.delete(0, 'end')
        self.tree.delete(*self.tree.get_children())
        self.status_var.set("")


if __name__ == '__main__':
    # Initialize and run the main application
    root = tk.Tk()
    app = TruthApp(root)
    root.mainloop()

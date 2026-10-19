"""bank_app.py - Tkinter GUI for the C++ Bank backend (COP 4020 Project 1, Part 2).

Python handles presentation only. All banking rules (search, duplicate
detection, balance checks) live in the C++ backend.
"""

import ctypes
import os
import re
import sys
import tkinter as tk
from ctypes import POINTER, c_char_p, c_double, c_int, c_void_p, create_string_buffer
from tkinter import filedialog, messagebox, ttk

ERR_SIZE = 256
NAME_SIZE = 128
SSN_SIZE = 64


def load_bank_library():
    """Load the platform-appropriate shared library from this file's folder."""
    if sys.platform.startswith("win"):
        lib_name = "bank.dll"
    elif sys.platform == "darwin":
        lib_name = "libbank.dylib"
    else:
        lib_name = "libbank.so"

    folder = os.path.dirname(os.path.abspath(__file__))
    lib_path = os.path.join(folder, lib_name)
    if not os.path.exists(lib_path):
        raise FileNotFoundError(
            f"Shared library not found: {lib_path}\n"
            "Compile the C++ code first (see README.md)."
        )
    if sys.platform.startswith("win") and hasattr(os, "add_dll_directory"):
        os.add_dll_directory(folder)
    return ctypes.CDLL(lib_path)


def decode(buf):
    """Decode a ctypes string buffer safely."""
    return buf.value.decode("utf-8", errors="replace")


class BankApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bank Management System")
        self.root.geometry("900x650")
        self.root.minsize(720, 560)
        self.root.configure(background="#F3F6F3")

        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background="#F3F6F3")
        style.configure("TLabel", background="#F3F6F3", foreground="#20352D", font=("Segoe UI", 10))
        style.configure(
            "PageHeading.TLabel",
            background="#F3F6F3",
            foreground="#174F3D",
            font=("Segoe UI", 15, "bold"),
        )
        style.configure(
            "TLabelFrame",
            background="#F3F6F3",
            bordercolor="#CFDAD2",
            relief="solid",
            padding=12,
        )
        style.configure(
            "TLabelFrame.Label",
            background="#F3F6F3",
            foreground="#315A49",
            font=("Segoe UI", 9, "bold"),
        )
        style.configure(
            "TNotebook",
            background="#F3F6F3",
            borderwidth=0,
            tabmargins=(0, 4, 0, 0),
        )
        style.configure(
            "TNotebook.Tab",
            background="#E2EAE4",
            foreground="#42594D",
            padding=(14, 9),
            font=("Segoe UI", 9, "bold"),
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", "#FFFFFF"), ("active", "#D5E2D9")],
            foreground=[("selected", "#174F3D")],
        )
        style.configure(
            "TButton",
            background="#176B50",
            foreground="#FFFFFF",
            bordercolor="#176B50",
            padding=(14, 8),
            font=("Segoe UI", 10, "bold"),
        )
        style.map(
            "TButton",
            background=[("pressed", "#104B39"), ("active", "#248363")],
            bordercolor=[("active", "#248363")],
        )
        style.configure(
            "TEntry",
            fieldbackground="#FFFFFF",
            foreground="#20352D",
            bordercolor="#C5D2C9",
            padding=7,
        )
        style.configure(
            "Status.TLabel",
            background="#E3EBE5",
            foreground="#40574B",
            padding=(10, 7),
            font=("Segoe UI", 9),
        )

        self.lib = load_bank_library()
        self._setup_ctypes()

        # Launch with an empty bank (no client file loaded yet).
        err = create_string_buffer(ERR_SIZE)
        self.bank_ptr = self.lib.bank_create(b"", err, ERR_SIZE)
        if not self.bank_ptr:
            raise RuntimeError(f"Failed to initialize the Bank backend: {decode(err)}")

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self._create_widgets()

    # ------------------------------------------------------------------
    # ctypes declarations
    # ------------------------------------------------------------------
    def _setup_ctypes(self):
        lib = self.lib

        lib.bank_create.argtypes = [c_char_p, c_char_p, c_int]
        lib.bank_create.restype = c_void_p

        lib.bank_destroy.argtypes = [c_void_p]
        lib.bank_destroy.restype = None

        lib.bank_save_file.argtypes = [c_void_p, c_char_p, c_char_p, c_int]
        lib.bank_save_file.restype = c_int

        lib.bank_find_client.argtypes = [
            c_void_p, c_char_p,
            c_char_p, c_int,
            c_char_p, c_int,
            POINTER(c_double),
            c_char_p, c_int,
        ]
        lib.bank_find_client.restype = c_int

        lib.bank_deposit.argtypes = [c_void_p, c_char_p, c_double, POINTER(c_double), c_char_p, c_int]
        lib.bank_deposit.restype = c_int

        lib.bank_withdraw.argtypes = [c_void_p, c_char_p, c_double, POINTER(c_double), c_char_p, c_int]
        lib.bank_withdraw.restype = c_int

        lib.bank_add_client.argtypes = [c_void_p, c_char_p, c_char_p, c_char_p, c_double, c_char_p, c_int]
        lib.bank_add_client.restype = c_int

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def _create_widgets(self):
        # Pack the status bar FIRST so the notebook cannot squeeze it out.
        self.status_var = tk.StringVar(value="Ready. No client file loaded.")
        ttk.Label(
            self.root, textvariable=self.status_var,
            style="Status.TLabel", anchor="w",
        ).pack(side="bottom", fill="x")

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        self.notebook = notebook
        self.tab_frames = {}

        tabs = [
            (" File ", self._build_file_tab),
            (" Find Client ", self._build_search_tab),
            (" Deposit / Withdraw ", self._build_transaction_tab),
            (" Add Client ", self._build_add_client_tab),
            (" Help Chat ", self._build_help_chat_tab),
        ]
        for title, builder in tabs:
            frame = ttk.Frame(notebook, padding=10)
            notebook.add(frame, text=title)
            self.tab_frames[title.strip()] = frame
            builder(frame)

    def _build_file_tab(self, parent):
        ttk.Label(parent, text="File Operations", style="PageHeading.TLabel").pack(pady=(10, 15))
        ttk.Button(parent, text="Load Client File...", command=self.load_file).pack(pady=8, ipadx=12)
        ttk.Button(parent, text="Save Data To File...", command=self.save_file).pack(pady=8, ipadx=12)
        self.lbl_file = ttk.Label(parent, text="Current file: (none)")
        self.lbl_file.pack(pady=15)

    def _build_search_tab(self, parent):
        box = ttk.LabelFrame(parent, text=" Search by Account Number ", padding=10)
        box.pack(fill="x", pady=(5, 10))
        ttk.Label(box, text="Account Number:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.search_acc_entry = ttk.Entry(box, width=24)
        self.search_acc_entry.grid(row=0, column=1, padx=5, pady=5)
        self.search_acc_entry.bind("<Return>", lambda _e: self.find_client())
        ttk.Button(box, text="Find", command=self.find_client).grid(row=0, column=2, padx=5, pady=5)

        details = ttk.LabelFrame(parent, text=" Client Details ", padding=10)
        details.pack(fill="both", expand=True)
        self.lbl_name = ttk.Label(details, text="Name: ---")
        self.lbl_ssn = ttk.Label(details, text="SSN: ***-**-****")
        self.lbl_acc = ttk.Label(details, text="Account #: ---")
        self.lbl_balance = ttk.Label(details, text="Balance: ---")
        for lbl in (self.lbl_name, self.lbl_ssn, self.lbl_acc, self.lbl_balance):
            lbl.pack(anchor="w", padx=10, pady=6)

    def _build_transaction_tab(self, parent):
        box = ttk.LabelFrame(parent, text=" Process Transaction ", padding=10)
        box.pack(fill="x", pady=(5, 10))

        ttk.Label(box, text="Account Number:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.trans_acc_entry = ttk.Entry(box, width=24)
        self.trans_acc_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(box, text="Amount ($):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.trans_amt_entry = ttk.Entry(box, width=24)
        self.trans_amt_entry.grid(row=1, column=1, padx=5, pady=5)

        buttons = ttk.Frame(box)
        buttons.grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(buttons, text="Deposit", command=self.deposit).pack(side="left", padx=10)
        ttk.Button(buttons, text="Withdraw", command=self.withdraw).pack(side="left", padx=10)

        self.lbl_trans_result = ttk.Label(parent, text="", font=("Segoe UI", 11, "italic"))
        self.lbl_trans_result.pack(pady=10)

    def _build_add_client_tab(self, parent):
        box = ttk.LabelFrame(parent, text=" New Account Information ", padding=10)
        box.pack(fill="x", pady=(5, 10))

        fields = [
            ("Account Number:", "add_acc_entry"),
            ("Full Name:", "add_name_entry"),
            ("SSN:", "add_ssn_entry"),
            ("Initial Balance ($):", "add_bal_entry"),
        ]
        for row, (text, attr) in enumerate(fields):
            ttk.Label(box, text=text).grid(row=row, column=0, padx=5, pady=5, sticky="e")
            entry = ttk.Entry(box, width=28)
            entry.grid(row=row, column=1, padx=5, pady=5)
            setattr(self, attr, entry)

        ttk.Button(box, text="Add Client", command=self.add_client).grid(
            row=len(fields), column=0, columnspan=2, pady=12
        )

    def _build_help_chat_tab(self, parent):
        ttk.Label(parent, text="Banking Help Assistant", style="PageHeading.TLabel").pack(
            anchor="w", pady=(0, 8)
        )
        ttk.Label(
            parent,
            text="Ask how to use the app or type a task like 'find an account'.",
        ).pack(anchor="w", pady=(0, 8))

        chat_frame = ttk.Frame(parent)
        chat_frame.pack(fill="both", expand=True)
        self.chat_history = tk.Text(
            chat_frame,
            wrap="word",
            height=12,
            state="disabled",
            background="#FFFFFF",
            foreground="#20352D",
            insertbackground="#176B50",
            font=("Segoe UI", 10),
            padx=12,
            pady=10,
            relief="solid",
            borderwidth=1,
            highlightthickness=0,
        )
        scrollbar = ttk.Scrollbar(chat_frame, orient="vertical", command=self.chat_history.yview)
        self.chat_history.configure(yscrollcommand=scrollbar.set)
        self.chat_history.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self._append_chat_message(
            "Assistant",
            "Hi! I can guide you to the right screen and answer questions about loading "
            "files, finding accounts, transactions, and adding clients.",
        )

        compose = ttk.Frame(parent)
        compose.pack(fill="x", pady=(8, 0))
        self.chat_entry = ttk.Entry(compose)
        self.chat_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.chat_entry.bind("<Return>", self._send_chat_message)
        ttk.Button(compose, text="Send", command=self._send_chat_message).pack(side="right")

    def _append_chat_message(self, speaker, message):
        self.chat_history.configure(state="normal")
        self.chat_history.insert(tk.END, f"{speaker}: {message}\n\n")
        self.chat_history.configure(state="disabled")
        self.chat_history.see(tk.END)

    def _send_chat_message(self, _event=None):
        message = self.chat_entry.get().strip()
        if not message:
            return "break"

        self.chat_entry.delete(0, tk.END)
        self._append_chat_message("You", message)
        answer, destination = self._assistant_response(message)
        self._append_chat_message("Assistant", answer)
        if destination:
            self.notebook.select(self.tab_frames[destination])
        return "break"

    @staticmethod
    def _assistant_response(message):
        """Answer app FAQs and direct common tasks to their notebook tabs."""
        text = " ".join(message.lower().replace("/", " ").split())
        has_phrase = lambda *phrases: any(
            re.search(rf"\b{re.escape(phrase)}\b", text) for phrase in phrases
        )

        if has_phrase("withdraw", "withdrawal"):
            return (
                "Enter the account number and a positive amount on the Deposit / Withdraw tab, "
                "then choose Withdraw.",
                "Deposit / Withdraw",
            )
        if has_phrase("deposit"):
            return (
                "Enter the account number and a positive amount on the Deposit / Withdraw tab, "
                "then choose Deposit.",
                "Deposit / Withdraw",
            )
        if has_phrase("add client", "new client", "new account", "open account"):
            return (
                "Use the Add Client tab to enter an account number, full name, SSN, and initial balance.",
                "Add Client",
            )
        if has_phrase("amount", "zero", "negative", "validation"):
            return (
                "Deposits and withdrawals require an amount greater than zero. A new client's "
                "initial balance may be zero, but not negative.",
                None,
            )
        if has_phrase("find", "search", "look up", "lookup", "balance"):
            return (
                "Open Find Client, enter the account number, and select Find. The displayed SSN is masked.",
                "Find Client",
            )
        if has_phrase("load", "open file", "import"):
            return (
                "Use the File tab and select Load Client File. The app accepts CSV or text files.",
                "File",
            )
        if has_phrase("save", "export"):
            return (
                "Use the File tab and select Save Data To File to choose where to save the client data.",
                "File",
            )
        if has_phrase("help", "what can you do", "faq", "questions"):
            return (
                "I can help with loading or saving a client file, finding an account, deposits, "
                "withdrawals, and adding a client. Ask me about one of those tasks.",
                None,
            )
        return (
            "I can help with files, finding accounts, deposits, withdrawals, or adding clients. "
            "What would you like to do?",
            None,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def mask_ssn(ssn):
        digits = ssn.replace("-", "").strip()
        return f"***-**-{digits[-4:]}" if len(digits) >= 4 else "***-**-****"

    @staticmethod
    def parse_amount(raw, allow_zero=False):
        """Return a float, or None if non-numeric / out of range."""
        try:
            value = float(raw)
        except ValueError:
            return None
        if value != value or value in (float("inf"), float("-inf")):
            return None
        if value < 0 or (value == 0 and not allow_zero):
            return None
        return value

    def set_status(self, message):
        self.status_var.set(message)

    def show_error(self, message):
        self.set_status(message)
        messagebox.showerror("Error", message)

    def show_info(self, message):
        self.set_status(message)
        messagebox.showinfo("Success", message)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def load_file(self):
        path = filedialog.askopenfilename(
            title="Select client file",
            filetypes=[("CSV or text files", "*.csv *.txt"), ("All files", "*.*")],
        )
        if not path:
            return

        # Build a fresh Bank from the file; only swap it in if loading worked.
        err = create_string_buffer(ERR_SIZE)
        new_ptr = self.lib.bank_create(path.encode("utf-8"), err, ERR_SIZE)
        if not new_ptr:
            self.show_error(f"Could not load file: {decode(err)}")
            return

        if self.bank_ptr:
            self.lib.bank_destroy(self.bank_ptr)  # old object destroyed exactly once
        self.bank_ptr = new_ptr
        self.lbl_file.config(text=f"Current file: {os.path.basename(path)}")
        self.show_info(f"Loaded client file: {os.path.basename(path)}")

    def save_file(self):
        path = filedialog.asksaveasfilename(
            title="Save client data",
            defaultextension=".csv",
            filetypes=[("CSV or text files", "*.csv *.txt"), ("All files", "*.*")],
        )
        if not path:
            return

        err = create_string_buffer(ERR_SIZE)
        ok = self.lib.bank_save_file(self.bank_ptr, path.encode("utf-8"), err, ERR_SIZE)
        if ok == 1:
            self.show_info(f"Saved data to: {os.path.basename(path)}")
        else:
            self.show_error(f"Save failed: {decode(err)}")

    def find_client(self):
        acc = self.search_acc_entry.get().strip()
        if not acc:
            self.show_error("Account number is required.")
            return

        name_buf = create_string_buffer(NAME_SIZE)
        ssn_buf = create_string_buffer(SSN_SIZE)
        balance = c_double(0.0)
        err = create_string_buffer(ERR_SIZE)

        ok = self.lib.bank_find_client(
            self.bank_ptr, acc.encode("utf-8"),
            name_buf, NAME_SIZE, ssn_buf, SSN_SIZE,
            ctypes.byref(balance), err, ERR_SIZE,
        )
        if ok == 1:
            self.lbl_name.config(text=f"Name: {decode(name_buf)}")
            self.lbl_ssn.config(text=f"SSN: {self.mask_ssn(decode(ssn_buf))}")
            self.lbl_acc.config(text=f"Account #: {acc}")
            self.lbl_balance.config(text=f"Balance: ${balance.value:,.2f}")
            self.set_status(f"Client {acc} found.")
        else:
            self._clear_details()
            self.show_error(f"Client not found: {decode(err)}")

    def _clear_details(self):
        self.lbl_name.config(text="Name: ---")
        self.lbl_ssn.config(text="SSN: ***-**-****")
        self.lbl_acc.config(text="Account #: ---")
        self.lbl_balance.config(text="Balance: ---")

    def deposit(self):
        self._transaction("Deposit", self.lib.bank_deposit)

    def withdraw(self):
        self._transaction("Withdrawal", self.lib.bank_withdraw)

    def _transaction(self, label, backend_fn):
        acc = self.trans_acc_entry.get().strip()
        if not acc:
            self.show_error("Account number is required.")
            return
        amount = self.parse_amount(self.trans_amt_entry.get().strip())
        if amount is None:
            self.show_error("Amount must be a number greater than 0.")
            return

        new_balance = c_double(0.0)
        err = create_string_buffer(ERR_SIZE)
        ok = backend_fn(
            self.bank_ptr, acc.encode("utf-8"), amount,
            ctypes.byref(new_balance), err, ERR_SIZE,
        )
        if ok == 1:
            msg = f"{label} successful. New balance: ${new_balance.value:,.2f}"
            self.lbl_trans_result.config(text=msg, foreground="green")
            self.set_status(msg)
        else:
            self.lbl_trans_result.config(text="", foreground="")
            self.show_error(f"{label} failed: {decode(err)}")

    def add_client(self):
        acc = self.add_acc_entry.get().strip()
        name = self.add_name_entry.get().strip()
        ssn = self.add_ssn_entry.get().strip()
        raw_bal = self.add_bal_entry.get().strip()

        if not (acc and name and ssn and raw_bal):
            self.show_error("All fields are required.")
            return
        balance = self.parse_amount(raw_bal, allow_zero=True)
        if balance is None:
            self.show_error("Initial balance must be a number that is 0 or greater.")
            return

        err = create_string_buffer(ERR_SIZE)
        ok = self.lib.bank_add_client(
            self.bank_ptr, acc.encode("utf-8"), name.encode("utf-8"),
            ssn.encode("utf-8"), balance, err, ERR_SIZE,
        )
        if ok == 1:
            for entry in (self.add_acc_entry, self.add_name_entry,
                          self.add_ssn_entry, self.add_bal_entry):
                entry.delete(0, tk.END)
            self.show_info(f"Client '{name}' added with account {acc}.")
        else:
            self.show_error(f"Could not add client: {decode(err)}")

    def on_close(self):
        if self.bank_ptr:
            self.lib.bank_destroy(self.bank_ptr)
            self.bank_ptr = None
        self.root.destroy()


def main():
    root = tk.Tk()
    try:
        BankApp(root)
    except Exception as exc:  # show startup problems instead of a blank window
        messagebox.showerror("Startup Error", str(exc))
        root.destroy()
        raise SystemExit(1)
    root.mainloop()


if __name__ == "__main__":
    main()
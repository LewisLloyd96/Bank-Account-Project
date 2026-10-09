
import tkinter as tk
from tkinter import filedialog, messagebox
import os


class BankApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Banking Application")
        self.root.geometry("500x300")
        self.root.resizable(False, False)

        # Store the selected file path.
        self.client_file = None

        # Application heading.
        heading = tk.Label(
            root,
            text="Banking Application",
            font=("Arial", 18, "bold")
        )
        heading.pack(pady=(25, 10))

        # Load Client File button.
        self.load_button = tk.Button(
            root,
            text="Load Client File",
            command=self.load_client_file,
            width=20
        )
        self.load_button.pack(pady=15)

        # Display the selected filename.
        self.file_label = tk.Label(
            root,
            text="No client file selected",
            wraplength=420
        )
        self.file_label.pack(pady=10)

        # Display application status.
        self.status_label = tk.Label(
            root,
            text="Please select a client data file.",
            fg="blue",
            wraplength=420
        )
        self.status_label.pack(pady=10)

    def load_client_file(self):
        # Open the file selection dialog.
        file_path = filedialog.askopenfilename(
            title="Select Client Data File",
            filetypes=[
                ("Client Data Files", "*.txt *.csv *.dat"),
                ("All Files", "*.*")
            ]
        )

        # Do nothing if the user cancels.
        if not file_path:
            return

        # Check that the selected path points to a file.
        if not os.path.isfile(file_path):
            messagebox.showerror(
                "File Error",
                "The selected file could not be found."
            )
            return

        # Save the selected path for later backend integration.
        
        self.client_file = file_path

        try:
            # Read the selected text file.
            with open(file_path, "r", encoding="utf-8-sig") as file:
                lines = file.readlines()

            # Count non-empty lines.
            record_count = sum(1 for line in lines if line.strip())

            filename = os.path.basename(file_path)

            self.file_label.config(
                text=f"Selected file: {filename}"
            )

            self.status_label.config(
                text=f"File read successfully. "
                     f"{record_count} non-empty lines found.",
                fg="green"
            )

            messagebox.showinfo(
                "File Read Successfully",
                f"File: {filename}\n"
                f"Non-empty lines: {record_count}\n\n"
                "The C++ backend is not connected yet."
            )

        except (OSError, UnicodeError) as error:
            self.status_label.config(
                text="Could not read the selected file.",
                fg="red"
            )

            messagebox.showerror(
                "File Error",
                f"Unable to read the selected file.\n\n{error}"
            )

        # Update the interface.
        filename = os.path.basename(file_path)
        self.file_label.config(
            text=f"Selected file: {filename}"
        )

        self.status_label.config(
            text="File selected. Backend loading is not connected yet.",
            fg="darkorange"
        )

        messagebox.showinfo(
            "File Selected",
            f"You selected:\n{filename}\n\n"
            "The C++ backend will be connected later."
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = BankApp(root)
    root.mainloop()

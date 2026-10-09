
import tkinter as tk

root = tk.Tk()
root.title("Tkinter Display Test")
root.geometry("500x400")
root.configure(bg="yellow")

frame = tk.Frame(root, bg="lightblue", width=450, height=300)
frame.pack(padx=20, pady=20, fill="both", expand=True)
frame.pack_propagate(False)

heading = tk.Label(
    frame,
    text="BANKING APPLICATION",
    font=("Arial", 18, "bold"),
    bg="lightblue",
    fg="black"
)
heading.pack(pady=20)

label = tk.Label(
    frame,
    text="Enter Account Number:",
    font=("Arial", 14),
    bg="lightblue",
    fg="black"
)
label.pack(pady=10)

entry = tk.Entry(frame, font=("Arial", 16))
entry.pack(pady=10)

button = tk.Button(frame, text="TEST BUTTON")
button.pack(pady=10)

root.mainloop()
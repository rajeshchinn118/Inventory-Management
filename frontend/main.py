import tkinter as tk
from gui import AppGUI

if __name__ == "__main__":
    root = tk.Tk()
    app = AppGUI(root)
    app.setup()
    root.mainloop()

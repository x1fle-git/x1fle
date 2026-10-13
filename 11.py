import tkinter as tk

clicks = 0

def count():
    global clicks
    clicks += 1
    label.config(text=clicks)

def reset():
    global clicks
    clicks = 0
    label.config(text=clicks)

window = tk.Tk()
window.title("Счетчик кликов")
window.geometry("300x250")

label = tk.Label(window, text="0", font=("Arial", 40))
label.pack(pady=50)

tk.Button(window, text="Клик", command=count).pack(pady=10)
tk.Button(window, text="Сброс", command=reset).pack(pady=10)

window.mainloop()

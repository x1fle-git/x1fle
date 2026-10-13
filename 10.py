import tkinter as tk

def on_click():
    name = entry.get()
    if name:
        label.config(text=f"Привет, {name}!")
    else:
        label.config(text="Вы ничего не ввели!")

window = tk.Tk()  
window.title("Приветствие")  
window.geometry("350x200")  

entry = tk.Entry(window, font=('Arial', 14))  
entry.pack(pady=20)

button = tk.Button(window, text="Поздороваться", command=on_click, font=("Arial", 12))
button.pack()

label = tk.Label(window, text='Введите ваше имя', font=("Arial", 14))
label.pack(pady=20)

window.mainloop()

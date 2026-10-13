import tkinter as tk

window = tk.Tk()
window.title("Моя визитка")
window.geometry("350x250")  

label = tk.Label(window, text="Антоний", font=("Arial", 20))  
label.pack(pady=20)
label = tk.Label(window, text="Студент", font=("Arial", 30))  
label.pack(pady=30)
label = tk.Label(window, text="Москва", font=("Arial", 10))  
label.pack(pady=40) 

def on_click():
    label.config(text="Вы нажали на кнопку! ") 

button = tk.Button(window, text="Нажми меня", command=on_click)  
button.pack(pady=10)  

window.mainloop()

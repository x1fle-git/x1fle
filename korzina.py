import tkinter as tk


root = tk.Tk()
root.title("Приложение")
root.geometry("400x500")

users = []
cart = []

products = [
    ("Яблоко", "50 руб"),
    ("Банан", "30 руб"),

]


def clear_window():
    for widget in root.winfo_children():
        widget.destroy()


def top_bar():
    bar = tk.Frame(root)
    bar.pack(fill="x", side="top")

    tk.Button(bar, text="Админ панель", command=show_admin).pack(side="right", padx=5, pady=5)


def show_register():
    clear_window()
    root.title("Регистрация")

    tk.Label(root, text="РЕГИСТРАЦИЯ", font=("Arial", 16, "bold")).pack(pady=20)

    tk.Label(root, text="Имя:").pack()
    name_entry = tk.Entry(root, width=30)
    name_entry.pack(pady=5)

    def register():      
        name = name_entry.get()
        users.append({"name": name})
        show_catalog()

    tk.Button(root, text="Зарегистрироваться", command=register, width=20).pack(pady=15)


def show_catalog():
    clear_window()
    root.title("Каталог")
    root.geometry("400x600")

    top_bar()

    tk.Label(root, text="КАТАЛОГ ПРОДУКТОВ", font=("Arial", 16, "bold")).pack(pady=15)

    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True, padx=10)

    for name, price in products:
        row = tk.Frame(frame, borderwidth=1, relief="solid")
        row.pack(fill="x", pady=3)

        tk.Label(row, text=name, font=("Arial", 13), anchor="w").pack(side="left", padx=10, pady=8)
        tk.Label(row, text=price, font=("Arial", 11), anchor="e").pack(side="right", padx=10)

    def go_back():
        show_register()

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Назад", command=go_back, width=12).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Корзина", command=show_cart, width=12).pack(side="left", padx=5)


def show_cart():
    clear_window()
    root.title("Корзина")
    root.geometry("400x500")

    top_bar()

    tk.Label(root, text="КОРЗИНА", font=("Arial", 16, "bold")).pack(pady=15)

    if len(cart) == 0:
        tk.Label(root, text="Корзина пуста", font=("Arial", 12)).pack(pady=20)
    else:
        for item in cart:
            tk.Label(root, text=item, font=("Arial", 12)).pack(pady=2)

    def go_back():
        show_catalog()

    tk.Button(root, text="Назад в каталог", command=go_back, width=20).pack(pady=20)


def show_admin():
    clear_window()
    root.title("Админ панель")
    root.geometry("400x500")

    top_bar()

    tk.Label(root, text="АДМИН ПАНЕЛЬ", font=("Arial", 16, "bold")).pack(pady=15)

    tk.Label(root, text=f"Пользователей: {len(users)}").pack(pady=5)
    tk.Label(root, text=f"Товаров: {len(products)}").pack(pady=5)

    def go_back():
        show_catalog()

    tk.Button(root, text="Назад в каталог", command=go_back, width=20).pack(pady=20)

show_register()
root.mainloop()
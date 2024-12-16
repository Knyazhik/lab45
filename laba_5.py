import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3


class Tariff:
    def __init__(self, name, price):
        self.name = name
        self.price = price


class Client:
    def __init__(self, name, tariff, weight):
        self.name = name
        self.tariff = tariff
        self.weight = weight


    def calculate_revenue(self):
        return self.tariff.price * self.weight


class DataBaseForm:
    def __init__(self, parent, clients, tariffs, company):
        self.top = tk.Toplevel(parent)
        self.top.title("Работа с базой данных")
        self.top.geometry("400x300")
        self.clients = clients
        self.tariffs = tariffs
        self.company = company

        tk.Button(self.top, text="Подсчитать общую выручку", command=self.count_revenue).pack(pady=10)

        self.revenue_label = tk.Label(self.top, text="Общая выручка: 0 руб.")
        self.revenue_label.pack(pady=10)

        tk.Button(self.top, text="Сохранить в БД", command=self.save_to_database).pack(pady=10)
        tk.Button(self.top, text="Загрузить из БД", command=self.load_from_database).pack(pady=10)


    def count_revenue(self):
        total_revenue = sum(client.calculate_revenue() for client in self.clients)
        self.revenue_label.config(text=f"Общая выручка: {total_revenue:.2f} руб.")


    def init_database(self):
        self.conn = sqlite3.connect('DataBaseForLab.db')
        self.cursor = self.conn.cursor()

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tariffs
            (name TEXT PRIMARY KEY, price REAL)
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients
            (name TEXT PRIMARY KEY, tariff_name TEXT, weight REAL,
            FOREIGN KEY(tariff_name) REFERENCES tariffs(name))
        ''')

        self.conn.commit()


    def save_to_database(self):
        try:
            self.init_database()
            self.cursor.execute("DELETE FROM clients")
            self.cursor.execute("DELETE FROM tariffs")

            for tariff in self.tariffs:
                self.cursor.execute("INSERT INTO tariffs (name, price) VALUES (?, ?)",
                                    (tariff.name, tariff.price))

            for client in self.clients:
                self.cursor.execute("""
                    INSERT INTO clients (name, tariff_name, weight)
                    VALUES (?, ?, ?)""",
                                    (client.name, client.tariff.name, client.weight))

            self.conn.commit()
            self.conn.close()
            messagebox.showinfo("Успех", "Данные успешно сохранены в базу данных")
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении в БД: {str(e)}")


    def load_from_database(self):
        try:
            self.init_database()
            #self.tariffs.clear()
            #self.clients.clear()
            #self.company.tariff_listbox.delete(0, tk.END)
            #self.company.client_listbox.delete(0, tk.END)

            self.cursor.execute("SELECT * FROM tariffs")
            for row in self.cursor.fetchall():
                tariff = Tariff(row[0], row[1])
                self.tariffs.append(tariff)
                self.company.tariff_listbox.insert(tk.END,
                                               f"Тариф: {tariff.name} - {tariff.price} руб.")

            self.cursor.execute("SELECT * FROM clients")
            for row in self.cursor.fetchall():
                tariff = next((t for t in self.tariffs if t.name == row[1]), None)
                if tariff:
                    client = Client(row[0], tariff, row[2])
                    self.clients.append(client)

            self.company.update_tariff_dropdown()

            for client in self.clients:
                self.company.client_listbox.insert(
                    tk.END,
                    f"Клиент: {client.name} - Объем перевозок: {client.weight}кг - Тариф: {client.tariff.name}"
                )

            self.conn.close()
            messagebox.showinfo("Успех", "Данные успешно загружены из базы данных")
            self.top.destroy()
            
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке из БД: {str(e)}")


class Company:
    def __init__(self, rootbeer):
        self.client_listbox = None
        self.tariff_dropdown = None
        self.tariff_var = None
        self.weight = None
        self.client_name = None
        self.tariff_listbox = None
        self.tariff_price = None
        self.tariff_name = None
        self.root = rootbeer
        self.root.title("NikitkaExpress")
        self.tariffs = []
        self.clients = []

        self.tab_control = ttk.Notebook(rootbeer)

        self.tariff_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tariff_tab, text='Тарифы')

        self.client_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.client_tab, text='Клиенты')

        self.tab_control.pack(expand=1, fill='both')

        self.setup_tariff_tab()
        self.setup_client_tab()

        tk.Button(rootbeer, text="Открыть статистику по грузоперевозкам", command=self.open_data_base).pack(pady=10)


    def open_data_base(self):
        DataBaseForm(self.root, self.clients, self.tariffs, self)


    def setup_tariff_tab(self):
        tk.Label(self.tariff_tab, text="Название тарифа:").grid(row=0, column=0, padx=5, pady=5)
        self.tariff_name = tk.Entry(self.tariff_tab)
        self.tariff_name.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.tariff_tab, text="Цена:").grid(row=1, column=0, padx=5, pady=5)
        self.tariff_price = tk.Entry(self.tariff_tab)
        self.tariff_price.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(self.tariff_tab, text="Создать тариф", command=self.create_tariff).grid(row=2, column=0, columnspan=2, pady=10)

        sort_frame = tk.Frame(self.tariff_tab)
        sort_frame.grid(row=3, column=0, columnspan=2, pady=5)
        tk.Button(sort_frame, text="Сортировать по имени", command=self.sort_tariffs_by_name).pack(side=tk.LEFT, padx=5)
        tk.Button(sort_frame, text="Сортировать по цене", command=self.sort_tariffs_by_price).pack(side=tk.LEFT, padx=5)

        self.tariff_listbox = tk.Listbox(self.tariff_tab, width=40, height=10)
        self.tariff_listbox.grid(row=4, column=0, columnspan=2, padx=5, pady=5)


    def setup_client_tab(self):
        tk.Label(self.client_tab, text="Имя клиента:").grid(row=0, column=0, padx=5, pady=5)
        self.client_name = tk.Entry(self.client_tab)
        self.client_name.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.client_tab, text="Объем перевозок (кг):").grid(row=1, column=0, padx=5, pady=5)
        self.weight = tk.Entry(self.client_tab)
        self.weight.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.client_tab, text="Выберите тариф:").grid(row=2, column=0, padx=5, pady=5)
        self.tariff_var = tk.StringVar()
        self.tariff_dropdown = ttk.Combobox(self.client_tab, textvariable=self.tariff_var)
        self.tariff_dropdown.grid(row=2, column=1, padx=5, pady=5)

        tk.Button(self.client_tab, text="Создать клиента", command=self.create_client).grid(row=3, column=0, columnspan=2, pady=10)

        sort_frame = tk.Frame(self.client_tab)
        sort_frame.grid(row=4, column=0, columnspan=2, pady=5)
        tk.Button(sort_frame, text="Сортировать по имени", command=self.sort_clients_by_name).pack(side=tk.LEFT, padx=5)
        tk.Button(sort_frame, text="Сортировать по весу", command=self.sort_clients_by_weight).pack(side=tk.LEFT, padx=5)

        self.client_listbox = tk.Listbox(self.client_tab, width=40, height=10)
        self.client_listbox.grid(row=5, column=0, columnspan=2, padx=5, pady=5)


    def sort_tariffs_by_name(self):
        self.tariffs.sort(key=lambda x: x.name)
        self.update_tariff_listbox()


    def sort_tariffs_by_price(self):
        self.tariffs.sort(key=lambda x: x.price, reverse=True)
        self.update_tariff_listbox()


    def sort_clients_by_name(self):
        self.clients.sort(key=lambda x: x.name)
        self.update_client_listbox()


    def sort_clients_by_weight(self):
        self.clients.sort(key=lambda x: x.weight, reverse=True)
        self.update_client_listbox()


    def update_tariff_listbox(self):
        self.tariff_listbox.delete(0, tk.END)
        for tariff in self.tariffs:
            self.tariff_listbox.insert(tk.END, f"Тариф: {tariff.name} - {tariff.price} руб.")


    def update_client_listbox(self):
        self.client_listbox.delete(0, tk.END)
        for client in self.clients:
            self.client_listbox.insert(tk.END,
                f"Клиент: {client.name} - Объем перевозок: {client.weight}кг - Тариф: {client.tariff.name}")


    def create_tariff(self):
        try:
            name = self.tariff_name.get()
            price = float(self.tariff_price.get())

            if name and (0 < price < 10000):
                tariff = Tariff(name, price)
                self.tariffs.append(tariff)
                self.tariff_listbox.insert(tk.END, f"Тариф: {name} - {price} руб.")
                self.update_tariff_dropdown()
                self.tariff_name.delete(0, tk.END)
                self.tariff_price.delete(0, tk.END)
            else:
                messagebox.showerror("Ошибка", "Заполните все поля корректно (больше 0, меньше 10000, не словами!")
        except ValueError:
            messagebox.showerror("Ошибка", "Цена должна быть числом")


    def create_client(self):
        try:
            name = self.client_name.get()
            mass = float(self.weight.get())
            selected_tariff = self.tariff_var.get()

            if name and (0 < mass < 10000) and selected_tariff:
                tariff = next((t for t in self.tariffs if t.name == selected_tariff), None)
                if tariff:
                    client = Client(name, tariff, mass)
                    self.clients.append(client)
                    self.client_listbox.insert(tk.END,
                                               f"Клиент: {name} - Объем перевозок: {mass}кг - Тариф: {tariff.name}")
                    self.client_name.delete(0, tk.END)
                    self.weight.delete(0, tk.END)
                else:
                    messagebox.showerror("Ошибка", "В��берите тариф")
            else:
                messagebox.showerror("Ошибка", "Заполните все поля корректно (больше 0, меньше 10000, не словами!")
        except ValueError:
            messagebox.showerror("Ошибка", "Масса багажа должна быть числом")


    def update_tariff_dropdown(self):
        tariff_names = [tariff.name for tariff in self.tariffs]
        self.tariff_dropdown['values'] = tariff_names


if __name__ == "__main__":
    root = tk.Tk()
    app = Company(root)
    root.mainloop()
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import json
import os
import shutil


#Класс базы данных
class Database:
    def __init__(self, filename="database.json"):
        self.filename = filename
        self.fields = ["ID", "Name", "Value", "Category"]
        self.key_field = "ID"  #Ключевое поле
        self.index = {}  #Индекс для быстрого поиска
        if not os.path.exists(self.filename):
            self._initialize_db()
        self._rebuild_index()

#Инициализация файла базы данных
    def _initialize_db(self):
        data = {"fields": self.fields, "records": []}
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

#Перестраивает индекс для быстрого поиска
    def _rebuild_index(self):
        self.index = {}
        data = self.read_db()
        for i, record in enumerate(data["records"]):
            self.index[record[self.key_field]] = i

#Чтение базы данных
    def read_db(self):
        with open(self.filename, "r", encoding="utf-8") as f:
            return json.load(f)

#Запись данных в базу
    def write_db(self, data):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)


# Добавление записи с проверкой уникальности
    def add_record(self, record):
        if record[self.key_field] in self.index:
            raise ValueError("Record with the same key already exists.")
        data = self.read_db()
        data["records"].append(record)
        self.write_db(data)
        self._rebuild_index()


#Удаление записей по полю
    def delete_record(self, field, value):
        data = self.read_db()
        records_to_keep = []
        for record in data["records"]:
            if record[field] != value:
                records_to_keep.append(record)
            elif field == self.key_field:
                # Удаляем запись из индекса
                self.index.pop(record[field], None)
        data["records"] = records_to_keep
        self.write_db(data)
        self._rebuild_index()

#Поиск записей по полю
    def search_records(self, field, value):
        data = self.read_db()
        if field == self.key_field and value in self.index:
            # Если поле ключевое, возвращаем сразу по индексу
            return [data["records"][self.index[value]]]
        return [r for r in data["records"] if r[field] == value]

    # Редактирование записи
    def edit_record(self, key_value, updated_record):
        data = self.read_db()
        if key_value not in self.index:
            raise ValueError("Record not found.")
        index = self.index[key_value]
        data["records"][index] = updated_record
        self.write_db(data)
        self._rebuild_index()

    #Очистка базы данных
    def clear_db(self):
        self.write_db({"fields": self.fields, "records": []})
        self._rebuild_index()

    #Создание резервной копии
    def backup_db(self, backup_filename):
        shutil.copy(self.filename, backup_filename)

    #Восстановление из резервной копии
    def restore_db(self, backup_filename):
        shutil.copy(backup_filename, self.filename)
        self._rebuild_index()



# Класс GUI
class DatabaseApp:
    def __init__(self, root):
        self.db = Database()
        self.root = root
        self.root.title("Database Manager")
        self.create_widgets()

    #Создание элементов интерфейса
    def create_widgets(self):
        #Таблица
        self.table = ttk.Treeview(self.root, columns=self.db.fields, show="headings")
        for field in self.db.fields:
            self.table.heading(field, text=field)
            self.table.column(field, width=100)
        self.table.pack(fill=tk.BOTH, expand=True)

        #Кнопки
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Add Record", command=self.add_record).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Delete Record", command=self.delete_record).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Search", command=self.search_record).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Edit Record", command=self.edit_record).grid(row=0, column=3, padx=5)
        tk.Button(btn_frame, text="Clear Database", command=self.clear_database).grid(row=0, column=4, padx=5)
        tk.Button(btn_frame, text="Backup", command=self.backup_database).grid(row=0, column=5, padx=5)
        tk.Button(btn_frame, text="Restore", command=self.restore_database).grid(row=0, column=6, padx=5)

        self.load_data()

    #Загрузка данных в таблицу
    def load_data(self):
        self.table.delete(*self.table.get_children())
        data = self.db.read_db()
        for record in data["records"]:
            self.table.insert("", tk.END, values=[record[field] for field in self.db.fields])

    #Добавление записи
    def add_record(self):
        record = {}
        for field in self.db.fields:
            value = simpledialog.askstring("Input", f"Enter {field}:")
            record[field] = value
        try:
            self.db.add_record(record)
            self.load_data()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    #Удаление записи
    def delete_record(self):
        field = simpledialog.askstring("Input", "Enter field to delete by:")
        value = simpledialog.askstring("Input", "Enter value to delete:")
        self.db.delete_record(field, value)
        self.load_data()

    #Поиск записей
    def search_record(self):
        field = simpledialog.askstring("Input", "Enter field to search by:")
        value = simpledialog.askstring("Input", "Enter value to search:")
        results = self.db.search_records(field, value)
        messagebox.showinfo("Search Results", f"Found {len(results)} record(s):\n{results}")

    #Редактирование записи
    def edit_record(self):
        key_value = simpledialog.askstring("Input", f"Enter {self.db.key_field} to edit:")
        updated_record = {}
        for field in self.db.fields:
            value = simpledialog.askstring("Input", f"Enter new {field}:")
            updated_record[field] = value
        try:
            self.db.edit_record(key_value, updated_record)
            self.load_data()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    #Очистка базы данных
    def clear_database(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to clear the database?"):
            self.db.clear_db()
            self.load_data()

    #Создание резервной копии
    def backup_database(self):
        backup_filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if backup_filename:
            self.db.backup_db(backup_filename)
            messagebox.showinfo("Success", "Backup created successfully.")

    #Восстановление из резервной копии
    def restore_database(self):
        backup_filename = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if backup_filename:
            self.db.restore_db(backup_filename)
            self.load_data()
            messagebox.showinfo("Success", "Database restored successfully.")


# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = DatabaseApp(root)
    root.mainloop()


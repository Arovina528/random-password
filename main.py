import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
import os
from datetime import datetime

class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Password Generator")
        self.root.geometry("650x550")
        self.root.resizable(False, False)

        # Хранение истории
        self.history_file = "history.json"
        self.history = self.load_history()

        # Переменные
        self.password_length = tk.IntVar(value=12)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_letters = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=True)

        # Интерфейс
        self.create_widgets()
        self.update_history_table()

    def create_widgets(self):
        # Рамка настроек
        settings_frame = tk.LabelFrame(self.root, text="Настройки пароля", padx=10, pady=10)
        settings_frame.pack(fill="x", padx=10, pady=10)

        # Ползунок длины пароля
        tk.Label(settings_frame, text="Длина пароля:").grid(row=0, column=0, sticky="w")
        self.length_scale = tk.Scale(settings_frame, from_=4, to=50, orient="horizontal",
                                     variable=self.password_length, length=300)
        self.length_scale.grid(row=0, column=1, padx=10)
        self.length_label = tk.Label(settings_frame, text="12")
        self.length_label.grid(row=0, column=2)
        self.length_scale.configure(command=lambda x: self.length_label.config(text=str(int(float(x)))))

        # Чекбоксы
        tk.Checkbutton(settings_frame, text="Цифры (0-9)", variable=self.use_digits).grid(row=1, column=0, sticky="w")
        tk.Checkbutton(settings_frame, text="Буквы (A-Z, a-z)", variable=self.use_letters).grid(row=2, column=0, sticky="w")
        tk.Checkbutton(settings_frame, text="Спецсимволы (!@#$%^&*)", variable=self.use_symbols).grid(row=3, column=0, sticky="w")

        # Кнопка генерации
        self.generate_btn = tk.Button(settings_frame, text="Сгенерировать пароль", command=self.generate_password,
                                      bg="lightblue", font=("Arial", 10, "bold"))
        self.generate_btn.grid(row=4, column=0, columnspan=3, pady=10)

        # Поле для отображения пароля
        self.password_var = tk.StringVar()
        password_entry = tk.Entry(self.root, textvariable=self.password_var, font=("Courier", 14), state="readonly",
                                  justify="center")
        password_entry.pack(fill="x", padx=10, pady=5)

        # Кнопка копирования
        self.copy_btn = tk.Button(self.root, text="📋 Копировать в буфер", command=self.copy_to_clipboard)
        self.copy_btn.pack(pady=5)

        # Таблица истории
        history_frame = tk.LabelFrame(self.root, text="История паролей", padx=10, pady=10)
        history_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("timestamp", "length", "password")
        self.tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=10)
        self.tree.heading("timestamp", text="Дата и время")
        self.tree.heading("length", text="Длина")
        self.tree.heading("password", text="Пароль")

        self.tree.column("timestamp", width=150)
        self.tree.column("length", width=50)
        self.tree.column("password", width=300)

        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопки управления историей
        btn_frame = tk.Frame(history_frame)
        btn_frame.pack(fill="x", pady=5)
        tk.Button(btn_frame, text="Очистить историю", command=self.clear_history).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Сохранить историю", command=self.save_history_to_file).pack(side="left", padx=5)

    def generate_password(self):
        # Проверка: выбран хотя бы один тип символов
        if not (self.use_digits.get() or self.use_letters.get() or self.use_symbols.get()):
            messagebox.showerror("Ошибка", "Выберите хотя бы один тип символов!")
            return

        length = self.password_length.get()
        if length < 4:
            messagebox.showerror("Ошибка", "Минимальная длина пароля — 4 символа!")
            return
        if length > 50:
            messagebox.showerror("Ошибка", "Максимальная длина пароля — 50 символов!")
            return

        # Формируем пул символов
        char_pool = ""
        if self.use_digits.get():
            char_pool += string.digits
        if self.use_letters.get():
            char_pool += string.ascii_letters
        if self.use_symbols.get():
            char_pool += "!@#$%^&*()_+-=[]{}|;:,.<>?"

        # Генерация пароля
        password = ''.join(random.choice(char_pool) for _ in range(length))

        # Отображаем пароль
        self.password_var.set(password)

        # Сохраняем в историю
        self.save_to_history(password, length)

    def save_to_history(self, password, length):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history.append({
            "timestamp": timestamp,
            "length": length,
            "password": password
        })
        # Ограничим историю 50 записями
        if len(self.history) > 50:
            self.history = self.history[-50:]
        self.save_history_to_file()
        self.update_history_table()

    def update_history_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for entry in reversed(self.history):
            self.tree.insert("", "end", values=(entry["timestamp"], entry["length"], entry["password"]))

    def clear_history(self):
        if messagebox.askyesno("Подтверждение", "Очистить всю историю?"):
            self.history = []
            self.save_history_to_file()
            self.update_history_table()

    def save_history_to_file(self):
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=4, ensure_ascii=False)

    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []

    def copy_to_clipboard(self):
        password = self.password_var.get()
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена!")
        else:
            messagebox.showwarning("Предупреждение", "Нет пароля для копирования!")

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGenerator(root)
    root.mainloop()
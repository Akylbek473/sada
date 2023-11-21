import tkinter as tk
import tkinter.messagebox as messagebox
import logging
import json
import re
import os
from pathlib import Path
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"C:\Users\HP\PycharmProjects\pythonProject9")



class BankSystem:
    def __init__(self):
        self.clients_file = "clients.json"
        self.bank_data = {'users': [], 'current_user': None}
        self.load_clients_from_file()
        logging.basicConfig(filename='errors.log', level=logging.ERROR)
        self.current_user = None 

    def save_clients_to_file(self):
        with open(self.clients_file, 'w') as file:
            json.dump(self.bank_data['users'], file, indent=2)

    def load_clients_from_file(self):
        if os.path.exists(self.clients_file):
            with open(self.clients_file, 'r') as file:
                self.bank_data['users'] = json.load(file)

# Регистр
    def register(self):
        username = entry_username.get()
        password = entry_password.get()
        try:
            if not re.match(r'^[^\s]{4,}$', username):
                raise ValueError("Неправильный формат логина")
            if not re.match(r'^[a-zA-Z0-9_-]{4,}$', password):
                raise ValueError("Неправильный формат пароля")
            user_exists = any(user['username'] == username for user in self.bank_data['users'])
            if not user_exists:
                new_user = {
                    'username': username,
                    'password': password,
                    'deposit': 0
                }
                self.bank_data['users'].append(new_user)
                self.bank_data['current_user'] = username
                self.save_clients_to_file()
                messagebox.showinfo("Регистрация", "Регистрация прошла успешно!")
                entry_username.delete(0, 'end')
                entry_password.delete(0, 'end')
            else:
                raise ValueError("Пользователь уже существует")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
            logging.error(str(e))

# Логин     
    def login(self):
        username = entry_username.get()
        password = entry_password.get()
        user = next((user for user in self.bank_data['users'] if user['username'] == username), None)
        if user and user['password'] == password:
            self.bank_data['current_user'] = username
            open_main_window(username)
        else:
            messagebox.showerror("Ошибка входа", "Неправильный логин или пароль")

# Пополнение        
    def deposit_input(self, amount_entry, error_label):
        try:
            amount = amount_entry.get()
            if float(amount) <= 0:
                raise ValueError("Сумма должна быть положительной \n и больше нуля.")
            float_amount = float(amount)
            for user in self.bank_data['users']:
                if user['username'] == self.bank_data['current_user']:
                    if 'deposit' in user:
                        user['deposit'] = float(user['deposit']) + float_amount
                    else:
                        user['deposit'] = float_amount
                    self.save_clients_to_file()
                    messagebox.showinfo("Внесение", f"На счет внесено {amount} $.")
        except ValueError as e:
            logging.error(f"Ошибка ввода: {e}")
            messagebox.showerror("Ошибка", str(e))
            raise ValueError("Пожалуйста, введите корректное \n числовое значение для суммы.")
        
# Снятие
    def withdraw_input(self, amount_entry, error_label):
        amount = amount_entry.get()
        try:
            float_amount = float(amount)
            if float(amount) <= 0:
                raise ValueError("Сумма должна быть \n положительной и больше нуля.")
            for user in self.bank_data['users']:
                if user['username'] == self.bank_data['current_user']:
                    if 'deposit' in user:
                        user['deposit'] = float(user['deposit']) - float_amount
                        self.save_clients_to_file()
                        messagebox.showinfo("Снятие", f'Со счета снято {amount} $.')
                    else:
                        print('Недостаточно средств на счете.')
                        raise ValueError("Недостаточно средств на счете.")
                    print('Ошибка при снятии со счета.')
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
            error_label.config(text=str(e))
            
# Проверка баланса
    def check_balance_input(self):
        user_found = False
        for user in self.bank_data['users']:
            if user['username'] == self.bank_data['current_user']:
                user_found = True
                deposit = user.get('deposit', 0)  
                messagebox.showinfo("Баланс", f'Баланс счета пользователя {user["username"]}: {deposit} $.')
                break
        if not user_found:
            messagebox.showerror('Ошибка при проверке баланса!\n Пожалуйста, повторите еще раз.')
            return

# кредит
    def apply_credit_input(self, amount_entry, error_label, loan_term):
        amount = amount_entry.get()
        try:
            amount = float(amount)
            if amount > 0:
                for user in self.bank_data['users']:
                    if user['username'] == self.bank_data['current_user']:
                        user['deposit'] += amount
                        annual_interest_rate = 0.06
                        monthly_interest_rate = annual_interest_rate / 12
                        monthly_payment = amount * (monthly_interest_rate * (1 + monthly_interest_rate) ** loan_term) / (
                                    (1 + monthly_interest_rate) ** loan_term - 1)
                        user['credit'] += monthly_payment
                        self.save_clients_to_file()
                        messagebox.showinfo("Регистрация", f'{amount} $ добавлен в карту.\n Ежемесячный платеж по кредиту ({loan_term} месяцев): {monthly_payment:.2f} $')
                        self.calculate_monthly_payment_input(monthly_payment, loan_term)
                        return True
            else:
                raise ValueError("Неверная сумма кредита. \n Укажите положительную сумму.")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
            logging.error(str(e))

# ежемесечный платеж                 
    def calculate_monthly_payment_input(self):
        user_found = False
        for user in self.bank_data['users']:
            if user['username'] == self.bank_data['current_user']:
                user_found = True
                credit = user.get('credit', 0)  
                messagebox.showinfo("Ежемесячный платеж", f'Ежемесячный платеж: {credit} $.')
                return
        if not user_found:
            messagebox.showerror('Ошибка при проверке баланса!\n Пожалуйста, повторите еще раз.')
            return
        
# информация о user-е  
    def check_info_user(self):
        user_found = False
        for user in self.bank_data['users']:
            if user['username'] == self.bank_data['current_user']:
                user_found = True
                username = user.get('username')  
                password = user.get('password')
                deposit = user.get('deposit', 0)  
                credit = user.get('credit', 0)  
                messagebox.showinfo("Info about me", f' Логин: {username} \n Пароль: {password} \n Баланс на счете: {deposit} $\n Ежемесячный платеж: {credit} $.')
                break
        if not user_found:
            messagebox.showerror('Ошибка при проверке!\n Пожалуйста, повторите еще раз.')
            return

# Перевести деньги между пользователями
    def transfer_to_user_input(self, target_username, amount):
        try:
            amount = float(amount)
            if amount < 0:
                raise ValueError("Сумма должна быть\n положительной и больше нуля.")
            source_user = next((user for user in self.bank_data['users'] if user['username'] == self.bank_data['current_user']), None)
            if source_user:
                target_user = next((user for user in self.bank_data['users'] if user['username'] == target_username), None)
                if target_user:
                    if source_user['deposit'] >= amount:
                        source_user['deposit'] -= amount
                        target_user['deposit'] += amount
                        self.save_clients_to_file()
                        messagebox.showinfo("Успех", f"Переведено {amount} $ от пользователя {self.bank_data['current_user']} пользователю {target_username}.")
                    else:
                        raise ValueError(f"Недостаточно средств на счете\n пользователя {self.bank_data['current_user']}.")
                else:
                    raise ValueError(f"Пользователь {target_username} не \n найден в базе данных.")
            else:
                raise ValueError("Пользователь не найден в базе данных.")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

# Выход
    def logout(self):
        self.current_user = None

bank_system = BankSystem()
def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

# главный страница
def open_main_window(username):
    global win
    win = tk.Tk()
    win.title(f"Добро пожаловать, {username}!")
    win.geometry("500x738")
    win.configure(bg = "#004D00")
    win.resizable(False, False)
    canvas = Canvas(win,bg = "#004D00",height = 738,width = 500,bd = 0,highlightthickness = 0,relief = "ridge")
    button_image_1 = PhotoImage(file=relative_to_assets("frame0/button_1.png"))
    button_1 = tk.Button(win,image=button_image_1,borderwidth=0,highlightthickness=0,command=lambda:deposit_in ,relief="flat")
    button_image_2 = PhotoImage(file=relative_to_assets("frame0/button_2.png"))
    button_2 = tk.Button(win,image=button_image_2,borderwidth=0,highlightthickness=0,command=lambda:withdraw ,relief="flat")
    button_image_3 = PhotoImage(file=relative_to_assets("frame0/button_3.png"))
    button_3 = tk.Button(win,image=button_image_3,borderwidth=0,highlightthickness=0,command=lambda:bank_system.check_balance_input,relief="flat")
    button_image_4 = PhotoImage(file=relative_to_assets("frame0/button_4.png"))
    button_4 = tk.Button(win,image=button_image_4,borderwidth=0,highlightthickness=0,command=lambda:apply_credit,relief="flat")
    button_image_5 = PhotoImage(file=relative_to_assets("frame0/button_5.png"))
    button_5 = tk.Button(win,image=button_image_5,borderwidth=0,highlightthickness=0,command=lambda:bank_system.calculate_monthly_payment_input,relief="flat")
    button_image_6 = PhotoImage(file=relative_to_assets("frame0/button_6.png"))
    button_6 = tk.Button(win,image=button_image_6,borderwidth=0,highlightthickness=0,command=lambda:transfer_to_user,relief="flat")
    button_image_7 = PhotoImage(file=relative_to_assets("frame0/button_7.png"))
    button_7 = tk.Button(win,image=button_image_7,borderwidth=0,highlightthickness=0,command=lambda:bank_system.check_info_user,relief="flat")
    button_image_8 = PhotoImage(file=relative_to_assets("frame0/button_8.png"))
    button_8 = tk.Button(win,image=button_image_8,borderwidth=0,highlightthickness=0,command=lambda:bank_system.logout,relief="flat")
    canvas.place(x = 0, y = 0)
    button_1.place(x=54.0,y=55.0,width=164.0,height=152.0)
    button_2.place(x=257.0,y=42.0,width=176.0,height=170.0) 
    button_3.place(x=47.0,y=213.0,width=165.0,height=157.0)
    button_4.place(x=250.0,y=203.0,width=189.0,height=185.0)
    button_5.place(x=34.0,y=369.0,width=184.0,height=181.0)
    button_6.place(x=250.0,y=379.0,width=183.0,height=171.0)
    button_7.place(x=27.0,y=532.0,width=201.0,height=187.0)
    button_8.place(x=250.0,y=533.0,width=189.0,height=186.0)
    win.mainloop()
   
# Депозит 2 код
def deposit_in():
        wint = tk.Tk()
        wint.title("Bank System")
        wint.geometry("320x200")
        wint['bg'] = '#fff'
        wint.resizable(False, False)
        amoun = tk.Label(wint, text="Введите сумму для пополнения:", font=("Arial", 13))
        ikon = tk.Label(wint, text="$", font=("Arial", 13))
        amount_entry = tk.Entry(wint, width=15, font=("Arial", 13))
        error_label = tk.Label(wint, text="", font=("Arial", 11), fg="red")
        button_1 = tk.Button(wint, text="Пополнить", font=("Arial", 13),command=lambda: bank_system.deposit_input(amount_entry, error_label))
        amoun.place(x=40, y=55)
        amount_entry.place(x=75, y=90)
        ikon.place(x=230, y=90)
        error_label.place(x=40, y=150)
        button_1.place(x=110, y=120)
        wint.mainloop()

# Снятие денег со счета 2 код
def withdraw():
    global wint1
    wint1=tk.Tk()
    wint1.title("Bank System")
    wint1.geometry("300x200")
    wint1.resizable(False, False)
    amoun=tk.Label(wint1, text="Введите сумму для снятие:", font=("Arial", 13))
    ikon = tk.Label(wint1, text="$", font=("Arial", 13))
    error_label = tk.Label(wint1, text="", font=("Arial", 11), fg="red")
    b1 = tk.Button(wint1, text="Снять", font=("Arial", 13),command=lambda: bank_system.withdraw_input(amount_entry, error_label))
    amount_entry = tk.Entry(wint1, width=15, font=("Arial", 13))
    amoun.place(x=50, y=60)
    amount_entry.place(x=80, y=85)
    error_label.place(x=40, y=150)
    ikon.place(x=230, y=85)
    b1.place(x=110, y=110)
    wint1.mainloop()

# Взять кредит 2 код
def apply_credit():
    global wint3
    wint3 = tk.Tk()
    wint3.title("Bank System")
    wint3.geometry("400x350")
    wint3.resizable(False, False)
    a1 = tk.Label(wint3, text=("Напишите сумму:"), font=("Arial", 13))
    ikon = tk.Label(wint3, text="$", font=("Arial", 13))
    amount_entry = tk.Entry(wint3, width=12, font=("Arial", 13))
    error_label = tk.Label(wint3, text="", font=("Arial", 11), fg="red")
    a2 = tk.Label(wint3, text=("Выберите срок кредита:"), font=("Arial", 13))
    y1 = tk.Button(wint3, text=("3 месяца"), font=("Arial", 13), command=lambda: bank_system.apply_credit_input(amount_entry,error_label,3))
    y2 = tk.Button(wint3, text=("6 месяцев"), font=("Arial", 13), command=lambda: bank_system.apply_credit_input(amount_entry,error_label,6))
    y3 = tk.Button(wint3, text=("12 месяцев"), font=("Arial", 13), command=lambda: bank_system.apply_credit_input(amount_entry,error_label,12))
    y4 = tk.Button(wint3, text=("24 месяца"), font=("Arial", 13), command=lambda: bank_system.apply_credit_input(amount_entry,error_label,24))
    y5 = tk.Button(wint3, text=("36 месяцев"), font=("Arial", 13), command=lambda: bank_system.apply_credit_input(amount_entry,error_label,36))
    a1.place(x=110, y=30)
    amount_entry.place(x=120, y=55)
    ikon.place(x=230, y=55)
    a2.place(x=110, y=80)
    y1.place(x=125, y=105)
    y2.place(x=125, y=145)
    y3.place(x=125, y=185)
    y4.place(x=125, y=225)
    y5.place(x=125, y=265)
    error_label.place(x=60, y=300)
    wint3.mainloop()

# Перевести деньги между пользователями 2 код
def transfer_to_user():
    global wint5
    wint5 = tk.Tk()
    wint5.geometry("350x200")
    wint5.title("Bank System")
    wint5.resizable(False, False)
    def transfer_funds():
        target_username = recipient_entry.get()
        amount = amount_entry.get()
        bank_system.transfer_to_user_input(target_username, amount)
    recipient_label = tk.Label(wint5, text="Имя получателя:", font=("Arial", 13))
    recipient_label.place(x=100,y=20)
    recipient_entry = tk.Entry(wint5, font=("Arial", 13))
    recipient_entry.place(x=75,y=50)
    amount_label = tk.Label(wint5, text="Сумма для перевода:", font=("Arial", 13))
    amount_label.place(x=85,y=80)
    amount_entry = tk.Entry(wint5, font=("Arial", 13))
    amount_entry.place(x=75,y=110)
    transfer_button = tk.Button(wint5, text="Перевести", command=transfer_funds, font=("Arial", 13))
    transfer_button.place(x=115,y=140)
    window.mainloop()

# вход
window = Tk()
window.geometry("360x500")
window.title("Bank System")
window.configure(bg="#000000")
canvas = Canvas(window,bg="#000000",height=500,width=360,bd=0,highlightthickness=0,relief="ridge")
canvas.place(x=0, y=0)
entry_image_1 = PhotoImage(file=relative_to_assets("frame0/entry_1.png"))
entry_bg_1 = canvas.create_image(180.0, 206.0, image=entry_image_1)
entry_username = tk.Entry(bd=0, bg="#A8A9B2", fg="#000716", highlightthickness=0)
entry_username.place(x=125.0, y=191.0, width=150.0, height=28.0)

entry_image_2 = PhotoImage(file=relative_to_assets("frame0/entry_2.png"))
entry_bg_2 = canvas.create_image(180.0, 266.0, image=entry_image_2)
entry_password = tk.Entry(bd=0, bg="#A8A9B2", fg="#000716", highlightthickness=0)
entry_password.place(x=125.0, y=251.0, width=150.0, height=28.0)

canvas.create_text(145.0, 165.0, anchor="nw", text="Логин", fill="#FFFFFF", font=("Inter", 12 * -1))
canvas.create_text(145.0, 229.0, anchor="nw", text="Пароль", fill="#FFFFFF", font=("Inter", 12 * -1))

canvas.create_rectangle(135.0, 17.0, 225.0, 144.0, fill="#000000", outline="")
image_image_1 = PhotoImage(file=relative_to_assets("frame0/image_1.png"))
image_1 = canvas.create_image(180.0, 78.0, image=image_image_1)

button_image_1 = PhotoImage(file=relative_to_assets("frame0/reg.png"))
button_1 = tk.Button(image=button_image_1,borderwidth=0,highlightthickness=0,command=lambda: (bank_system.register()),relief="flat")
button_1.place(x=116.0, y=335.0, width=158.0, height=61.0)

button_image_2 = PhotoImage(file=relative_to_assets("frame0/go.png"))
button_2 = tk.Button(image=button_image_2,borderwidth=0,highlightthickness=0,command=lambda: (bank_system.login()),relief="flat")
button_2.place(x=116.0, y=294.0, width=158.0, height=58.0)
error_label = tk.Label(text="", fg="red")
window.resizable(False, False)
window.mainloop()


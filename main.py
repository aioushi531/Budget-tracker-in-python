import os
import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

class BudgetTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Budget Tracker")
        self.root.geometry("600x600")
        self.root.minsize(600, 400)
        self.categories = []
        self.create_tabs()
        self.create_accounts_tab()
        self.edit_mode = False
        self.delete_button = None
        self.create_categories_tab()
        self.create_transactions_tab()
        self.transactions = []
        self.modal = None
        self.overlay = None
        self.account_type = None

        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 10, "bold"))
        self.accounts_tree.insert("", tk.END, values=("Regular", "Cash", "₱ 165.69"))

    def open_centered_window(self, window, width, height):
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()

        x_position = root_x + (root_width // 2) - (width // 2)
        y_position = root_y + (root_height // 2) - (height // 2)

        window.geometry(f"{width}x{height}+{x_position}+{y_position}")

    def create_tabs(self):
        notebook = ttk.Notebook(self.root)
        self.accounts_tab = ttk.Frame(notebook)
        self.categories_tab = ttk.Frame(notebook)
        self.transactions_tab = ttk.Frame(notebook)

        notebook.add(self.accounts_tab, text="Accounts")
        notebook.add(self.categories_tab, text="Categories")
        notebook.add(self.transactions_tab, text="Transactions")

        notebook.pack(expand=True, fill="both")

    """ACCOUNTS"""

    def create_accounts_tab(self):
        self.deletion_mode = False

        frame = ttk.Frame(self.accounts_tab)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        columns = ("Account Type", "Account Name", "Balance", "Delete")
        self.accounts_tree = ttk.Treeview(frame, columns=columns, show="headings")

        self.accounts_tree.heading("Account Type", text="   Account Type", anchor="w")
        self.accounts_tree.heading("Account Name", text="   Account Name", anchor="w")
        self.accounts_tree.heading("Balance", text="Balance   ", anchor="e")
        self.accounts_tree.heading("Delete", text="Delete", anchor="center")

        self.accounts_tree.column("Account Type", width=75, anchor="w")
        self.accounts_tree.column("Account Name", anchor="w")
        self.accounts_tree.column("Balance", width=75, anchor="e")
        self.accounts_tree.column("Delete", width=-1, anchor="center")

        self.accounts_tree["displaycolumns"] = ("Account Type", "Account Name", "Balance")

        self.accounts_tree.pack(fill="both", expand=True)
        self.accounts_tree.bind("<ButtonRelease-1>", self.on_treeview_click)

        add_accounts_button = ttk.Button(
            self.accounts_tab,
            text="Add accounts +",
            command=self.show_account_type_modal,
            padding=(10, 5)
        )
        add_accounts_button.place(relx=0.88, rely=0.94, anchor="center")

        delete_accounts_button = ttk.Button(
            self.accounts_tab,
            text="Delete accounts",
            command=self.toggle_deletion_mode,
            padding=(10, 5)
        )
        delete_accounts_button.place(relx=0.68, rely=0.94, anchor="center")

    def toggle_deletion_mode(self):
        self.deletion_mode = not self.deletion_mode
        if self.deletion_mode:
            self.accounts_tree["displaycolumns"] = ("Account Type", "Account Name", "Balance", "Delete")
            self.accounts_tree.column("Delete", width=75, minwidth=75, anchor="center")
            for item in self.accounts_tree.get_children():
                values = list(self.accounts_tree.item(item, "values"))
                if len(values) < 4:
                    values.append("Delete")
                else:
                    values[3] = "Delete"
                self.accounts_tree.item(item, values=tuple(values))
        else:
            self.accounts_tree["displaycolumns"] = ("Account Type", "Account Name", "Balance")
            self.accounts_tree.column("Delete", width=0, minwidth=0, anchor="center")

    def on_treeview_click(self, event):
        if not self.deletion_mode:
            return

        region = self.accounts_tree.identify("region", event.x, event.y)
        if region == "cell":
            col = self.accounts_tree.identify_column(event.x)
            if col == "#4":
                item = self.accounts_tree.identify_row(event.y)
                if item:
                    confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this account?")
                    if confirm:
                        self.accounts_tree.delete(item)

    def show_add_account_modal(self):
        if self.modal is not None:
            return

        self.overlay = tk.Frame(self.root, bg="gray75")
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.overlay.bind("<Button-1>", lambda event: self.close_modal())

        self.modal = ttk.Frame(self.root, relief="raised", borderwidth=2)
        self.modal.place(relx=0.5, rely=0.5, anchor="center", width=300, height=225)

        ttk.Label(self.modal, text=f"Account Type: {self.account_type}").pack(side="top", anchor="w", padx=10,
                                                                              pady=(10, 5))
        ttk.Label(self.modal, text="Account Name:").pack(pady=5)
        account_entry = ttk.Entry(self.modal)
        account_entry.pack(pady=5, fill='x', padx=10)

        ttk.Label(self.modal, text="Balance:").pack(pady=5)
        balance_entry = ttk.Entry(self.modal)
        balance_entry.pack(pady=5, fill='x', padx=10)

        def add_account():
            account_name = account_entry.get().strip()
            balance = balance_entry.get().strip()
            if not account_name or not balance:
                messagebox.showerror("Invalid Input", "All fields must be filled.")
                return
            try:
                balance = float(balance)
                formatted_balance = f"₱ {balance:,.2f}"
                item = self.accounts_tree.insert("", tk.END,
                                                 values=(self.account_type, account_name, formatted_balance, "Delete"))
                self.accounts_tree.item(item, tags=("account_name", "account_type", "balance"))
                self.accounts_tree.tag_configure("account_name", font=("Arial", 10, "bold"), foreground="black")
                self.accounts_tree.tag_configure("account_type", font=("Arial", 10), foreground="gray")
                self.accounts_tree.tag_configure("balance", font=("Arial", 10, "bold"), foreground="black")
                self.close_modal()
            except ValueError:
                messagebox.showerror("Invalid Input", "Balance must be a valid number.")

        button_frame = ttk.Frame(self.modal)
        button_frame.pack(fill='x', padx=10, pady=20)

        add_button = ttk.Button(button_frame, text="Add", command=add_account)
        add_button.pack(side="right", padx=5)

        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.close_modal)
        cancel_button.pack(side="right", padx=5)

    def subtract_from_account(self, account_name, amount):
        try:
            amount = float(amount)
            for item in self.accounts_tree.get_children():
                values = self.accounts_tree.item(item, "values")
                if values[1] == account_name:
                    current_balance = float(values[2].replace("₱", "").replace(",", "").strip())
                    new_balance = current_balance - amount
                    formatted_balance = f"₱ {new_balance:,.2f}"
                    self.accounts_tree.item(item, values=(values[0], values[1], formatted_balance))
                    return
            messagebox.showerror("Error", "Account not found.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Amount must be a valid number.")

    def show_account_type_modal(self):
        if self.modal is not None:
            return

        self.overlay = tk.Frame(self.root, bg="gray75")
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.overlay.bind("<Button-1>", lambda event: self.close_modal())

        self.modal = ttk.Frame(self.root, relief="raised", borderwidth=2)
        self.modal.place(relx=0.5, rely=0.5, anchor="center", width=300, height=200)

        style = ttk.Style()
        style.configure("LeftAligned.TButton", anchor="w", padding=(10, 5, 5, 5))

        content_frame = ttk.Frame(self.modal)
        content_frame.pack(expand=True, fill="both", pady=10)

        self.wallet_icon = Image.open("icons/wallet.png").resize((20, 20), Image.LANCZOS)
        self.wallet_photo = ImageTk.PhotoImage(self.wallet_icon)

        self.debt_icon = Image.open("icons/salary.png").resize((20, 20), Image.LANCZOS)
        self.debt_photo = ImageTk.PhotoImage(self.debt_icon)

        self.savings_icon = Image.open("icons/money.png").resize((20, 20), Image.LANCZOS)
        self.savings_photo = ImageTk.PhotoImage(self.savings_icon)

        ttk.Button(
            content_frame,
            text="Regular\nCash, Car...",
            image=self.wallet_photo,
            compound="left",
            style="LeftAligned.TButton",
            command=lambda: self.select_account_type("Regular")
        ).pack(fill="x", pady=5, padx=10)

        ttk.Button(
            content_frame,
            text="Debt\nCredit, Mortgage...",
            image=self.debt_photo,
            compound="left",
            style="LeftAligned.TButton",
            command=lambda: self.select_account_type("Debt")
        ).pack(fill="x", pady=5, padx=10)

        ttk.Button(
            content_frame,
            text="Savings\nSavings, Goal...",
            image=self.savings_photo,
            compound="left",
            style="LeftAligned.TButton",
            command=lambda: self.select_account_type("Savings")
        ).pack(fill="x", pady=5, padx=10)

    def select_account_type(self, account_type):
        self.account_type = account_type
        self.close_modal()
        self.show_add_account_modal()

    """CATEGORIES"""

    def create_categories_tab(self):
        if not hasattr(self, "categories") or not self.categories:
            self.categories = {
                "expenses": [
                    {"icon": "category icons/food.png", "name": "Food"},
                    {"icon": "category icons/transport.png", "name": "Transport"},
                    {"icon": "category icons/shopping.png", "name": "Shopping"},
                    {"icon": "category icons/entertainment.png", "name": "Entertainment"},
                    {"icon": "category icons/health.png", "name": "Health"},
                    {"icon": "category icons/education.png", "name": "Education"},
                    {"icon": "category icons/bills.png", "name": "Bills"},
                    {"icon": "category icons/savings.png", "name": "Savings"},
                ],
                "income": [
                    {"icon": "icons/salary.png", "name": "Salary"},
                    {"icon": "category icons/allowance.png", "name": "Allowance"}
                ]
            }

        for widget in self.categories_tab.winfo_children():
            widget.destroy()

        self.update_categories_display()

    def update_categories_display(self):
        for widget in self.categories_tab.winfo_children():
            widget.destroy()

        frame = ttk.Frame(self.categories_tab)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        for col in range(6):
            frame.grid_columnconfigure(col, weight=1)

        self.category_images = []

        if self.edit_mode:
            self.category_check_vars = {"expenses": {}, "income": {}}

        expenses_label = ttk.Label(frame, text="Expenses", font=("Arial", 12, "bold"))
        expenses_label.pack(fill="x", pady=(0, 5))

        expenses_frame = ttk.Frame(frame)
        expenses_frame.pack(expand=True, fill="both", pady=(0, 10))
        for col in range(6):
            expenses_frame.grid_columnconfigure(col, weight=1)

        for i, category in enumerate(self.categories.get("expenses", [])):
            try:
                img = Image.open(category["icon"]).resize((70, 70), Image.LANCZOS)
            except Exception:
                img = Image.open("icons/placeholder.png").resize((70, 70), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.category_images.append(photo)
            row, col = divmod(i, 5)
            category_frame = ttk.Frame(expenses_frame, borderwidth=2, relief="flat")
            category_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            label = ttk.Label(category_frame, image=photo, text=category["name"],
                              compound="top", padding=5)
            label.pack()

            if not self.edit_mode:
                label.bind("<Enter>", lambda event, f=category_frame: f.config(relief="solid"))
                label.bind("<Leave>", lambda event, f=category_frame: f.config(relief="flat"))
                label.bind("<Button-1>", lambda event, c=category: self.show_add_transaction(c))
            else:
                var = tk.BooleanVar()
                self.category_check_vars["expenses"][i] = var
                cb = ttk.Checkbutton(category_frame, variable=var,
                                     command=self.update_delete_button_visibility)
                cb.pack(anchor="center", pady=2)

        if self.edit_mode:
            try:
                plus_img = Image.open("icons/add.png").resize((70, 70), Image.LANCZOS)
            except Exception:
                plus_img = Image.open("icons/placeholder.png").resize((70, 70), Image.LANCZOS)
            plus_photo = ImageTk.PhotoImage(plus_img)
            self.category_images.append(plus_photo)
            plus_frame = ttk.Frame(expenses_frame, borderwidth=2, relief="flat")
            row, col = divmod(len(self.categories.get("expenses", [])), 5)
            plus_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            plus_button = ttk.Button(plus_frame, image=plus_photo, command=self.show_add_category_modal)
            plus_button.pack()
            caption = ttk.Label(plus_frame, text="add category", font=("Arial", 10))
            caption.pack()

        income_label = ttk.Label(frame, text="Income", font=("Arial", 12, "bold"))
        income_label.pack(fill="x", pady=(10, 5))

        income_frame = ttk.Frame(frame)
        income_frame.pack(expand=True, fill="both")
        for col in range(6):
            income_frame.grid_columnconfigure(col, weight=1)

        for i, category in enumerate(self.categories.get("income", [])):
            try:
                img = Image.open(category["icon"]).resize((70, 70), Image.LANCZOS)
            except Exception:
                img = Image.open("icons/placeholder.png").resize((70, 70), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.category_images.append(photo)
            row, col = divmod(i, 5)
            category_frame = ttk.Frame(income_frame, borderwidth=2, relief="flat")
            category_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            label = ttk.Label(category_frame, image=photo, text=category["name"],
                              compound="top", padding=5)
            label.pack()

            if not self.edit_mode:
                label.bind("<Enter>", lambda event, f=category_frame: f.config(relief="solid"))
                label.bind("<Leave>", lambda event, f=category_frame: f.config(relief="flat"))
                label.bind("<Button-1>", lambda event, c=category: self.show_add_transaction(c))
            else:
                var = tk.BooleanVar()
                self.category_check_vars["income"][i] = var
                cb = ttk.Checkbutton(category_frame, variable=var,
                                     command=self.update_delete_button_visibility)
                cb.pack(anchor="center", pady=2)

        if self.edit_mode:
            try:
                plus_img = Image.open("icons/add.png").resize((70, 70), Image.LANCZOS)
            except Exception:
                plus_img = Image.open("icons/placeholder.png").resize((70, 70), Image.LANCZOS)
            plus_photo = ImageTk.PhotoImage(plus_img)
            self.category_images.append(plus_photo)
            plus_frame = ttk.Frame(income_frame, relief="flat")
            row, col = divmod(len(self.categories.get("income", [])), 5)
            plus_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            plus_button = ttk.Button(plus_frame, image=plus_photo, command=self.show_add_category_modal)
            plus_button.pack()
            caption = ttk.Label(plus_frame, text="add category", font=("Arial", 10))
            caption.pack()

        edit_button = ttk.Button(
            self.categories_tab,
            text="Cancel Edit" if self.edit_mode else "Edit Categories",
            command=self.toggle_edit_mode,
            padding=(10, 5)
        )
        edit_button.place(relx=0.88, rely=0.9, anchor="center")

        if not self.edit_mode and hasattr(self, "delete_button") and self.delete_button is not None:
            self.delete_button.destroy()
            self.delete_button = None

    def toggle_edit_mode(self):
        self.edit_mode = not self.edit_mode
        self.update_categories_display()

    def update_delete_button_visibility(self):
        if not self.edit_mode:
            if hasattr(self, "delete_button") and self.delete_button is not None:
                self.delete_button.destroy()
                self.delete_button = None
            return

        selected = any(var.get() for cat in self.category_check_vars.values() for var in cat.values())
        if selected:
            if not hasattr(self, "delete_button") or self.delete_button is None:
                self.delete_button = ttk.Button(
                    self.categories_tab, text="Delete Selected", command=self.delete_selected_categories, padding=(10, 5)
                )
                self.delete_button.place(relx=0.7, rely=0.9, anchor="center")
        else:
            if hasattr(self, "delete_button") and self.delete_button is not None:
                self.delete_button.destroy()
                self.delete_button = None

    def delete_selected_categories(self):
        new_expenses = []
        for i, cat in enumerate(self.categories.get("expenses", [])):
            if i in self.category_check_vars["expenses"] and self.category_check_vars["expenses"][i].get():
                continue
            new_expenses.append(cat)
        new_income = []
        for i, cat in enumerate(self.categories.get("income", [])):
            if i in self.category_check_vars["income"] and self.category_check_vars["income"][i].get():
                continue
            new_income.append(cat)
        self.categories["expenses"] = new_expenses
        self.categories["income"] = new_income
        self.update_categories_display()

    def show_add_category_modal(self):
        if self.modal is not None:
            return

        self.overlay = tk.Frame(self.root, bg="gray75")
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.overlay.bind("<Button-1>", lambda event: self.close_modal())

        self.modal = ttk.Frame(self.root, relief="raised", borderwidth=2)
        self.modal.place(relx=0.5, rely=0.5, anchor="center", width=300, height=250)

        ttk.Label(self.modal, text="Choose an icon:").pack(pady=5)

        self.selected_icon = "icons/placeholder.png"
        self.icon_img = Image.open(self.selected_icon).resize((50, 50), Image.LANCZOS)
        self.icon_photo = ImageTk.PhotoImage(self.icon_img)

        self.icon_label = ttk.Label(self.modal, image=self.icon_photo)
        self.icon_label.pack(pady=5)

        self.choose_icon_button = ttk.Button(
            self.modal, text="Choose Icon", command=self.show_icon_selection_modal
        )
        self.choose_icon_button.pack(pady=5)

        ttk.Label(self.modal, text="Category Name:").pack(pady=5)
        self.category_entry = ttk.Entry(self.modal)
        self.category_entry.pack(pady=5, fill='x', padx=10)

        button_frame = ttk.Frame(self.modal)
        button_frame.pack(fill='x', padx=10, pady=10)

        add_button = ttk.Button(button_frame, text="Add", command=self.add_category)
        add_button.pack(side="right", padx=5)

        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.close_modal)
        cancel_button.pack(side="right", padx=5)

    def show_icon_selection_modal(self):
        icon_window = tk.Toplevel(self.root)
        icon_window.title("Choose an Icon")
        icon_window.geometry("400x300")
        self.open_centered_window(icon_window, 400, 400)  # Example size

        frame = ttk.Frame(icon_window)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        self.icon_images = []
        self.icon_buttons = []

        icon_folder = "icons/category icons"
        icon_files = [f for f in os.listdir(icon_folder) if f.endswith(".png")]

        for i, icon_file in enumerate(icon_files[:20]):
            img = Image.open(os.path.join(icon_folder, icon_file)).resize((50, 50), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.icon_images.append(photo)

            button = ttk.Button(frame, image=photo, command=lambda i=i: self.select_icon(i, icon_window))
            button.grid(row=i//5, column=i%5, padx=5, pady=5)
            self.icon_buttons.append(button)

    def select_icon(self, index, window):
        self.selected_icon = f"icons/category icons/{os.listdir('icons/category icons')[index]}"

        self.icon_img = Image.open(self.selected_icon).resize((50, 50), Image.LANCZOS)
        self.icon_photo = ImageTk.PhotoImage(self.icon_img)
        self.icon_label.config(image=self.icon_photo)
        self.icon_label.image = self.icon_photo

        self.choose_icon_button.config(text="Change Icon")

        window.destroy()

    def add_category(self):
        category_name = self.category_entry.get().strip()
        if not category_name:
            messagebox.showerror("Invalid Input", "Category name must be filled.")
            return

        self.categories["expenses"].append({"icon": self.selected_icon, "name": category_name})
        self.update_categories_display()
        self.close_modal()

    def add_to_account(self, account_name, amount):
        try:
            amount = float(amount)
            for item in self.accounts_tree.get_children():
                values = self.accounts_tree.item(item, "values")
                if values[1] == account_name:
                    current_balance = float(values[2].replace("₱", "").replace(",", "").strip())
                    new_balance = current_balance + amount
                    formatted_balance = f"₱ {new_balance:,.2f}"
                    self.accounts_tree.item(item, values=(values[0], values[1], formatted_balance))
                    return
            messagebox.showerror("Error", "Account not found.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Amount must be a valid number.")

    def show_add_transaction(self, category):
        if self.modal is not None:
            return

        is_income = False
        if "income" in self.categories:
            income_names = [cat["name"] for cat in self.categories["income"]]
            if category["name"] in income_names:
                is_income = True

        self.overlay = tk.Frame(self.root, bg="gray75")
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.modal = ttk.Frame(self.overlay, relief="raised", borderwidth=2)
        self.modal.place(relx=0.5, rely=0.5, anchor="center", width=300, height=420)

        top_frame = ttk.Frame(self.modal)
        top_frame.pack(fill="x", padx=10, pady=10)

        if is_income:
            left_frame = ttk.Frame(top_frame)
            left_frame.pack(side="left", expand=True, fill="both", padx=5)
            ttk.Label(left_frame, text="From Category", font=("Arial", 8)).pack()
            ttk.Label(left_frame, text=category["name"], font=("Arial", 12, "bold")).pack()

            right_frame = ttk.Frame(top_frame)
            right_frame.pack(side="left", expand=True, fill="both", padx=5)
            ttk.Label(right_frame, text="To Account", font=("Arial", 8)).pack()
            self.to_account_label = ttk.Label(right_frame, text="Cash", font=("Arial", 12, "bold"))
            self.to_account_label.pack()
            right_frame.bind("<Button-1>", lambda event: self.show_select_account_modal(self.to_account_label))
            for widget in right_frame.winfo_children():
                widget.bind("<Button-1>", lambda event: self.show_select_account_modal(self.to_account_label))
        else:
            left_frame = ttk.Frame(top_frame)
            left_frame.pack(side="left", expand=True, fill="both", padx=5)
            ttk.Label(left_frame, text="From Account", font=("Arial", 8)).pack()
            self.from_account_label = ttk.Label(left_frame, text="Cash", font=("Arial", 12, "bold"))
            self.from_account_label.pack()
            left_frame.bind("<Button-1>", lambda event: self.show_select_account_modal(self.from_account_label))
            for widget in left_frame.winfo_children():
                widget.bind("<Button-1>", lambda event: self.show_select_account_modal(self.from_account_label))

            right_frame = ttk.Frame(top_frame)
            right_frame.pack(side="left", expand=True, fill="both", padx=5)
            ttk.Label(right_frame, text="To Category", font=("Arial", 8)).pack()
            ttk.Label(right_frame, text=category["name"], font=("Arial", 12, "bold")).pack()

        input_var = tk.StringVar(value="₱")
        input_entry = tk.Entry(self.modal, textvariable=input_var, font=("Arial", 18), bd=0, justify="center")

        def validate_input(P):
            if P == "₱":
                return False
            elif P.startswith("₱") and all(char.isdigit() or char in ".+-*/x" for char in P[1:]):
                return True
            return False

        def on_key_press(event):
            allowed_chars = "0123456789.+-*/x"
            if event.keysym in ["Return", "KP_Enter"]:
                on_button_click("✔")
                return "break"
            elif event.keysym == "BackSpace":
                on_button_click("C")
                return "break"
            elif event.char not in allowed_chars:
                return "break"

        input_entry.config(validate="key", validatecommand=(self.root.register(validate_input), "%P"))
        input_entry.bind("<KeyPress>", on_key_press)
        input_entry.pack(fill="x", padx=10, pady=5, ipady=10)
        input_entry.focus_set()
        input_entry.icursor(tk.END)

        def on_focus_in(event):
            if notes_entry.get() == "Notes...":
                notes_entry.delete(0, tk.END)
                notes_entry.config(fg="black")

        def on_focus_out(event):
            if not notes_entry.get():
                notes_entry.insert(0, "Notes...")
                notes_entry.config(fg="gray")

        notes_entry = tk.Entry(self.modal, font=("Arial", 10), fg="gray")
        notes_entry.insert(0, "Notes...")
        notes_entry.bind("<FocusIn>", on_focus_in)
        notes_entry.bind("<FocusOut>", on_focus_out)
        notes_entry.pack(fill="x", padx=10, pady=5)

        calc_frame = ttk.Frame(self.modal)
        calc_frame.pack(pady=10, fill="both", expand=True)

        def on_button_click(value):
            current_text = input_var.get()
            if value in ["C", "CA"]:
                if len(current_text) > 1:
                    input_var.set(current_text[:-1])
                else:
                    input_var.set("₱")
            elif value == "✔":
                try:
                    expression = current_text[1:].replace("x", "*").strip()
                    if expression:
                        result = eval(expression)
                        input_var.set(f"₱{round(result, 2)}")
                except ZeroDivisionError:
                    input_var.set("₱0")
                except Exception:
                    input_var.set("₱0")
            else:
                if current_text == "₱0":
                    input_var.set(f"₱{value}")
                else:
                    input_var.set(current_text + value)

        buttons = [
            ["/", "7", "8", "9", "C"],
            ["*", "4", "5", "6", "CA"],
            ["-", "1", "2", "3", "✔"],
            ["+", "₱", "0", ".", ""]
        ]
        for r, row in enumerate(buttons):
            for c, char in enumerate(row):
                if char:
                    btn = ttk.Button(calc_frame, text=char, command=lambda v=char: on_button_click(v))
                    if char == "✔":
                        btn.grid(row=r, column=c, rowspan=2, sticky="nsew", padx=5, pady=5)
                    else:
                        btn.grid(row=r, column=c, sticky="nsew", padx=5, pady=5)
                calc_frame.grid_columnconfigure(c, weight=1)
        for r in range(4):
            calc_frame.grid_rowconfigure(r, weight=1, minsize=45)
        for c in range(5):
            calc_frame.grid_columnconfigure(c, weight=1, minsize=45)

        button_frame = ttk.Frame(self.modal)
        button_frame.pack(fill='x', padx=10, pady=10)

        def save_transaction():
            if is_income:
                account_used = self.to_account_label.cget("text")
            else:
                account_used = self.from_account_label.cget("text")
            amount_spent = input_var.get()
            transaction_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            notes = notes_entry.get() if notes_entry.get() != "Notes..." else ""
            category_spent = category["name"]

            amount_numeric = amount_spent.replace("₱", "").strip()
            try:
                amount_value = float(amount_numeric)
            except:
                amount_value = 0

            if is_income:
                display_amount = f"+ ₱{amount_value:,.2f}"
            else:
                display_amount = f"- ₱{amount_value:,.2f}"

            transaction = {
                "account": account_used,
                "amount": display_amount,
                "datetime": transaction_time,
                "notes": notes,
                "category": category_spent
            }
            print("DEBUG: Storing transaction:", transaction)
            self.transactions.append(transaction)
            if is_income:
                self.add_to_account(account_used, amount_numeric)
            else:
                self.subtract_from_account(account_used, amount_numeric)
            self.create_transactions_tab()
            self.close_modal()

        add_button = ttk.Button(button_frame, text="Add", command=save_transaction)
        add_button.pack(side="right", padx=5)
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.close_modal)
        cancel_button.pack(side="right", padx=5)

    def show_select_account_modal(self, target_label):
        self.account_selection_target = target_label

        self.account_modal = tk.Toplevel(self.root)
        self.account_modal.title("Select Account")
        self.account_modal.geometry("300x200")
        self.open_centered_window(self.account_modal, 200, 200)

        frame = ttk.Frame(self.account_modal)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        account_ids = self.accounts_tree.get_children()
        accounts = []
        for aid in account_ids:
            values = self.accounts_tree.item(aid, "values")
            if len(values) >= 2:
                accounts.append(values[1])

        if not accounts:
            accounts = ["Cash", "Savings", "Credit Card", "Investments"]

        for account in accounts:
            btn = ttk.Button(frame, text=account, command=lambda a=account: self.select_account(a))
            btn.pack(fill="x", padx=5, pady=5)

    def select_account(self, account):
        if hasattr(self, "account_selection_target"):
            self.account_selection_target.config(text=account)
        else:
            messagebox.showerror("Error", "No account selection target defined.")
        self.account_modal.destroy()

    """TRANSACTONS"""

    def create_transactions_tab(self):
        for widget in self.transactions_tab.winfo_children():
            widget.destroy()

        frame = ttk.Frame(self.transactions_tab)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        if not hasattr(self, "transactions") or not self.transactions:
            ttk.Label(frame, text="No transactions available", font=("Arial", 12)).pack(pady=20)
            return

        sorted_transactions = sorted(self.transactions, key=lambda t: t["datetime"], reverse=True)

        from collections import defaultdict
        transactions_by_date = defaultdict(list)
        for t in sorted_transactions:
            date_str = t["datetime"].split()[0]
            transactions_by_date[date_str].append(t)

        sorted_dates = sorted(transactions_by_date.keys(), reverse=True)

        for date_str in sorted_dates:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            day = dt.strftime("%d")
            weekday = dt.strftime("%A")
            month_year = dt.strftime("%B %Y")

            equation = ""
            for trans in transactions_by_date[date_str]:
                amt_str = trans["amount"].replace("₱", "").replace(",", "").strip()
                if not (amt_str.startswith('+') or amt_str.startswith('-')):
                    amt_str = "+" + amt_str
                equation += amt_str

            print("DEBUG: Equation for date", date_str, ":", equation)

            try:
                total_amount = eval(equation)
            except Exception as e:
                print("DEBUG: Error evaluating equation for date", date_str, ":", e)
                total_amount = 0.0

            if total_amount > 0:
                header_amount = f"+₱{total_amount:,.2f}"
            elif total_amount < 0:
                header_amount = f"-₱{abs(total_amount):,.2f}"
            else:
                header_amount = f"₱{total_amount:,.2f}"

            header_text = f"{day} | {weekday} {month_year} | {header_amount}"
            header_label = ttk.Label(frame, text=header_text, font=("Arial", 10, "bold"), anchor="center")
            header_label.pack(fill="x", pady=(10, 5))

            ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=5)

            for trans in transactions_by_date[date_str]:
                row_frame = ttk.Frame(frame)
                row_frame.pack(fill="x", pady=5)

                icon_path = "icons/placeholder.png"
                if hasattr(self, "categories"):
                    all_categories = []
                    for section in self.categories.values():
                        all_categories.extend(section)
                    for cat in all_categories:
                        if cat["name"] == trans["category"]:
                            icon_path = cat["icon"]
                            break

                try:
                    icon_img = Image.open(icon_path).resize((30, 30), Image.LANCZOS)
                    icon_photo = ImageTk.PhotoImage(icon_img)
                except Exception:
                    icon_photo = None

                if icon_photo:
                    icon_label = ttk.Label(row_frame, image=icon_photo)
                    icon_label.image = icon_photo  # keep a reference
                    icon_label.pack(side="left", padx=5)
                else:
                    ttk.Label(row_frame, text="[icon]").pack(side="left", padx=5)

                details = f"{trans['category']} \n{trans['account']}"
                if trans["notes"]:
                    details += f"\n{trans['notes']}"
                details_label = ttk.Label(row_frame, text=details, font=("Arial", 10))
                details_label.pack(side="left", padx=5, fill="x", expand=True)

                amount_label = ttk.Label(row_frame, text=trans["amount"], font=("Arial", 10, "bold"))
                amount_label.pack(side="right", padx=5)

                ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=5)

    def close_modal(self):
        if self.modal is not None:
            self.modal.destroy()
            self.modal = None
        if self.overlay is not None:
            self.overlay.destroy()
            self.overlay = None


root = tk.Tk()
app = BudgetTracker(root)
root.mainloop()


"""
TO DO:
Edit account data modal when click column
change add account, add category buttons to edit (hamburger menu) 
implement delete category and delete account
add transaction history and stuff




"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import traceback

file_paths = []

# -------------------------------
# 🧵 Thread Runner (SAFE)
# -------------------------------
def run_in_thread(task):
    def wrapper():
        try:
            update_status("Processing... Please wait ⏳")
            result = task()

            if result:
                root.after(0, result)

            update_status("Done ✅")

        except Exception:
            err = traceback.format_exc()
            root.after(0, lambda: messagebox.showerror("Error", err))
            update_status("Error ❌")

    threading.Thread(target=wrapper).start()

# -------------------------------
# 📂 Select Files
# -------------------------------
def select_files():
    global file_paths
    file_paths = filedialog.askopenfilenames(filetypes=[("CSV files", "*.csv")])

    if file_paths:
        update_status(f"{len(file_paths)} files selected ✅")

# -------------------------------
# 📊 Funnel Analysis
# -------------------------------
def funnel_analysis():
    if not file_paths:
        messagebox.showerror("Error", "Select files first!")
        return

    def task():
        total = {'view': 0, 'cart': 0, 'purchase': 0}

        for file in file_paths:
            for chunk in pd.read_csv(file, chunksize=50000, usecols=['event_type']):
                counts = chunk['event_type'].value_counts()
                for k in total:
                    total[k] += counts.get(k, 0)

        def show():
            plt.figure()
            sns.barplot(x=list(total.keys()), y=list(total.values()))
            plt.title("Funnel Analysis")
            plt.show()

        return show

    run_in_thread(task)

# -------------------------------
# 📈 Conversion Rate
# -------------------------------
def conversion_rate():
    if not file_paths:
        messagebox.showerror("Error", "Select files first!")
        return

    def task():
        views, purchases = 0, 0

        for file in file_paths:
            for chunk in pd.read_csv(file, chunksize=50000, usecols=['event_type']):
                counts = chunk['event_type'].value_counts()
                views += counts.get('view', 0)
                purchases += counts.get('purchase', 0)

        rate = (purchases / views) * 100 if views else 0

        return lambda: messagebox.showinfo("Conversion Rate", f"{rate:.2f}%")

    run_in_thread(task)

# -------------------------------
# 💰 Revenue
# -------------------------------
def revenue_analysis():
    if not file_paths:
        messagebox.showerror("Error", "Select files first!")
        return

    def task():
        revenue = 0

        for file in file_paths:
            for chunk in pd.read_csv(file, chunksize=50000, usecols=['event_type', 'price']):
                purchases = chunk[chunk['event_type'] == 'purchase']
                revenue += purchases['price'].sum()

        return lambda: messagebox.showinfo("Revenue", f"{revenue:.2f}")

    run_in_thread(task)

# -------------------------------
# 🏆 Top Brands
# -------------------------------
def top_brands():
    if not file_paths:
        messagebox.showerror("Error", "Select files first!")
        return

    def task():
        brand_total = {}

        for file in file_paths:
            for chunk in pd.read_csv(file, chunksize=50000, usecols=['event_type', 'price', 'brand']):
                purchases = chunk[chunk['event_type'] == 'purchase']
                grouped = purchases.groupby('brand')['price'].sum()

                for b, val in grouped.items():
                    brand_total[b] = brand_total.get(b, 0) + val

        top = sorted(brand_total.items(), key=lambda x: x[1], reverse=True)[:10]

        brands = [x[0] for x in top]
        values = [x[1] for x in top]

        def show():
            plt.figure()
            sns.barplot(x=brands, y=values)
            plt.xticks(rotation=45)
            plt.title("Top Brands")
            plt.show()

        return show

    run_in_thread(task)

# -------------------------------
# 🔄 Status Label
# -------------------------------
def update_status(text):
    status_label.config(text=text)

# -------------------------------
# 🖥️ GUI
# -------------------------------
root = tk.Tk()
root.title("Big Data E-Commerce Project")
root.geometry("420x450")

tk.Button(root, text="Select CSV Files", command=select_files).pack(pady=10)
tk.Button(root, text="Funnel Analysis", command=funnel_analysis).pack(pady=10)
tk.Button(root, text="Conversion Rate", command=conversion_rate).pack(pady=10)
tk.Button(root, text="Revenue", command=revenue_analysis).pack(pady=10)
tk.Button(root, text="Top Brands", command=top_brands).pack(pady=10)

status_label = tk.Label(root, text="Ready", fg="blue")
status_label.pack(pady=20)

root.mainloop()

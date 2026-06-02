import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import dataset

class ScatterPlotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Визуализация данных")
        self.root.geometry("900x700")
        
        if dataset.df is None:
            dataset.load_data()
        self.df = dataset.df
        
        if self.df is None:
            messagebox.showerror("Ошибка", "Нет данных")
            self.root.destroy()
            return
        
        self.num_cols = [c for c in self.df.select_dtypes(include=['number']).columns if c != 'Year']
        
        # мои параметры
        self.marker = {1:'.',2:'o',3:'v',4:'^',5:'s',6:'p',7:'*',8:'D',9:'x'}.get(5, 'o')
        
        self.setup_ui()
        self.update_plot()
    
    def setup_ui(self):
        frame = ttk.Frame(self.root)
        frame.pack(pady=10)
        
        ttk.Label(frame, text="X:").grid(row=0, column=0, padx=5)
        self.x_var = tk.StringVar(value=self.num_cols[0])
        self.x_cb = ttk.Combobox(frame, textvariable=self.x_var, values=self.num_cols, state="readonly", width=25)
        self.x_cb.grid(row=0, column=1, padx=5)
        self.x_cb.bind('<<ComboboxSelected>>', lambda e: self.update_plot())
        
        ttk.Label(frame, text="Y:").grid(row=0, column=2, padx=5)
        self.y_var = tk.StringVar(value=self.num_cols[1] if len(self.num_cols) > 1 else self.num_cols[0])
        self.y_cb = ttk.Combobox(frame, textvariable=self.y_var, values=self.num_cols, state="readonly", width=25)
        self.y_cb.grid(row=0, column=3, padx=5)
        self.y_cb.bind('<<ComboboxSelected>>', lambda e: self.update_plot())
        
        ttk.Button(frame, text="Сохранить", command=self.save_plot).grid(row=0, column=4, padx=20)
        
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=5)
        ttk.Label(btn_frame, text="Колонки:").pack(side=tk.LEFT, padx=5)
        
        for col in self.num_cols:
            ttk.Button(btn_frame, text=col, width=12, command=lambda c=col: self.set_col(c)).pack(side=tk.LEFT, padx=2)
        
        self.fig = plt.Figure(figsize=(10, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, self.root)
        self.canvas.get_tk_widget().pack(pady=10, fill=tk.BOTH, expand=True)
        
        self.status = ttk.Label(self.root, text="Готов", relief=tk.SUNKEN)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)
    
    def set_col(self, col):
        if self.x_var.get() == col:
            self.y_var.set(col)
        else:
            self.x_var.set(col)
        self.update_plot()
    
    def update_plot(self):
        x, y = self.x_var.get(), self.y_var.get()
        if not x or not y:
            return
        
        self.ax.clear()
        self.ax.scatter(self.df[x], self.df[y], alpha=0.6, marker=self.marker, s=30)
        self.ax.set_xlabel(x)
        self.ax.set_ylabel(y)
        self.ax.set_title(f'{x} vs {y}')
        self.ax.grid(True, alpha=0.3)
        self.canvas.draw()
        
        self.status.config(text=f"{x} vs {y}")
    
    def save_plot(self):
        filename = f"graph_{datetime.now().strftime('%H%M%S')}.png"
        self.fig.savefig(filename, dpi=150, bbox_inches='tight')
        self.status.config(text=f"Сохранено: {filename}")
        messagebox.showinfo("Сохранено", filename)

if __name__ == "__main__":
    root = tk.Tk()
    app = ScatterPlotApp(root)
    root.mainloop()
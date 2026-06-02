import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import dataset
import numpy as np

class VisualPlotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система улучшенной визуализации - Задание 3")
        self.root.geometry("1000x750")
        
        if dataset.df is None:
            dataset.load_data()
        self.df = dataset.df
        
        if self.df is None:
            messagebox.showerror("Ошибка", "Не удалось загрузить данные!")
            self.root.destroy()
            return
        
        self.numeric_cols = []
        self.categorical_cols = []
        
        for col in self.df.columns:
            if col == 'Year':
                self.categorical_cols.append(col)
                self.df[col] = self.df[col].astype(str)
            elif pd.api.types.is_numeric_dtype(self.df[col]):
                self.numeric_cols.append(col)
            else:
                self.categorical_cols.append(col)
        
        self.all_cols = self.numeric_cols + self.categorical_cols
        
        # мои параметры
        self.default_cmap = 'plasma'
        self.available_cmaps = [
            'viridis', 'plasma', 'inferno', 'magma', 'cividis', 'Greys', 'Purples', 'Blues',
            'Greens', 'Oranges', 'Reds', 'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
            'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn', 'binary', 'gist_yarg',
            'spring', 'summer', 'autumn', 'winter'
        ]
        
        print(f"Цветовая схема по умолчанию: {self.default_cmap}")
        
        self.setup_ui()
        self.update_plot()
    
    def setup_ui(self):
        control_panel = ttk.LabelFrame(self.root, text="Управление графиком", padding=10)
        control_panel.pack(pady=10, padx=10, fill=tk.X)
        
        ttk.Label(control_panel, text="Ось X:").grid(row=0, column=0, padx=5, pady=5)
        self.x_var = tk.StringVar(value=self.all_cols[0])
        self.x_combo = ttk.Combobox(control_panel, textvariable=self.x_var,
                                     values=self.all_cols, state="readonly", width=25)
        self.x_combo.grid(row=0, column=1, padx=5, pady=5)
        self.x_combo.bind('<<ComboboxSelected>>', lambda e: self.update_plot())
        
        ttk.Label(control_panel, text="Ось Y:").grid(row=0, column=2, padx=5, pady=5)
        self.y_var = tk.StringVar(value=self.all_cols[1] if len(self.all_cols) > 1 else self.all_cols[0])
        self.y_combo = ttk.Combobox(control_panel, textvariable=self.y_var,
                                     values=self.all_cols, state="readonly", width=25)
        self.y_combo.grid(row=0, column=3, padx=5, pady=5)
        self.y_combo.bind('<<ComboboxSelected>>', lambda e: self.update_plot())
        
        ttk.Label(control_panel, text="Цветовая схема:").grid(row=1, column=0, padx=5, pady=5)
        self.cmap_var = tk.StringVar(value=self.default_cmap)
        self.cmap_combo = ttk.Combobox(control_panel, textvariable=self.cmap_var,
                                        values=self.available_cmaps, state="readonly", width=25)
        self.cmap_combo.grid(row=1, column=1, padx=5, pady=5)
        self.cmap_combo.bind('<<ComboboxSelected>>', lambda e: self.update_plot())
        
        self.save_btn = ttk.Button(control_panel, text="Сохранить график", command=self.save_plot)
        self.save_btn.grid(row=1, column=2, padx=20, pady=5)
        
        self.info_label = ttk.Label(control_panel, text="", foreground="blue")
        self.info_label.grid(row=1, column=3, padx=5, pady=5)
        
        left_buttons_frame = ttk.LabelFrame(self.root, text="Быстрый выбор (X)", padding=5)
        left_buttons_frame.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.Y)
        
        for col in self.all_cols:
            btn = ttk.Button(left_buttons_frame, text=col, width=20,
                           command=lambda c=col: self.set_x_column(c))
            btn.pack(pady=2)
        
        bottom_buttons_frame = ttk.LabelFrame(self.root, text="Быстрый выбор (Y)", padding=5)
        bottom_buttons_frame.pack(side=tk.BOTTOM, padx=10, pady=5, fill=tk.X)
        
        for i in range(0, len(self.all_cols), 5):
            row_frame = ttk.Frame(bottom_buttons_frame)
            row_frame.pack()
            for col in self.all_cols[i:i+5]:
                btn = ttk.Button(row_frame, text=col, width=18,
                               command=lambda c=col: self.set_y_column(c))
                btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.figure = plt.Figure(figsize=(9, 6), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self.root)
        self.canvas.get_tk_widget().pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        self.status_bar = ttk.Label(self.root, text="Готов", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def set_x_column(self, col):
        self.x_var.set(col)
        self.update_plot()
    
    def set_y_column(self, col):
        self.y_var.set(col)
        self.update_plot()
    
    def determine_plot_type(self, x_col, y_col):
        x_is_num = x_col in self.numeric_cols
        y_is_num = y_col in self.numeric_cols
        
        if x_col == y_col:
            if x_is_num:
                return 'histogram'
            else:
                return 'pie'
        elif not x_is_num and y_is_num:
            return 'bar'
        elif x_is_num and not y_is_num:
            return 'boxplot'
        else:
            return 'scatter'
    
    def update_plot(self):
        x_col = self.x_var.get()
        y_col = self.y_var.get()
        cmap = self.cmap_var.get()
        
        if not x_col or not y_col:
            return
        
        plot_type = self.determine_plot_type(x_col, y_col)
        
        self.ax.clear()
        
        cmap_obj = plt.cm.get_cmap(cmap)
        
        plot_titles = {
            'scatter': 'Точечная диаграмма',
            'histogram': 'Гистограмма',
            'pie': 'Круговая диаграмма',
            'bar': 'Столбчатая диаграмма',
            'boxplot': 'Ящик с усами (Boxplot)'
        }
        
        self.info_label.config(text=f"Тип графика: {plot_titles.get(plot_type, plot_type)}")
        
        try:
            if plot_type == 'scatter':
                colors = self.df[y_col] if y_col in self.numeric_cols else None
                if colors is not None and colors.dtype in ['float64', 'int64']:
                    sc = self.ax.scatter(self.df[x_col], self.df[y_col], 
                                        c=colors, cmap=cmap_obj, alpha=0.6)
                    plt.colorbar(sc, ax=self.ax, label=y_col)
                else:
                    self.ax.scatter(self.df[x_col], self.df[y_col], alpha=0.6)
                self.ax.set_xlabel(x_col)
                self.ax.set_ylabel(y_col)
                
            elif plot_type == 'histogram':
                data = self.df[x_col].dropna()
                self.ax.hist(data, bins=10, color=cmap_obj(0.6), edgecolor='black', alpha=0.7)
                self.ax.set_xlabel(x_col)
                self.ax.set_ylabel('Частота')
                
            elif plot_type == 'pie':
                counts = self.df[x_col].value_counts()
                colors = [cmap_obj(i/len(counts)) for i in range(len(counts))]
                self.ax.pie(counts, labels=counts.index, autopct='%1.1f%%', colors=colors)
                self.ax.set_title(f'Распределение {x_col}')
                
            elif plot_type == 'bar':
                counts = self.df[x_col].value_counts()
                colors = [cmap_obj(i/len(counts)) for i in range(len(counts))]
                bars = self.ax.bar(range(len(counts)), counts.values, color=colors)
                self.ax.set_xticks(range(len(counts)))
                self.ax.set_xticklabels(counts.index, rotation=45, ha='right')
                self.ax.set_xlabel(x_col)
                self.ax.set_ylabel('Количество записей')
                
            elif plot_type == 'boxplot':
                categories = self.df[y_col].unique()
                data_to_plot = []
                labels = []
                for cat in categories:
                    cat_data = self.df[self.df[y_col] == cat][x_col].dropna()
                    if len(cat_data) > 0:
                        data_to_plot.append(cat_data)
                        labels.append(str(cat))
                
                bp = self.ax.boxplot(data_to_plot, labels=labels, patch_artist=True)
                for box, i in zip(bp['boxes'], range(len(data_to_plot))):
                    box.set_facecolor(cmap_obj(i/len(data_to_plot)))
                self.ax.set_xlabel(y_col)
                self.ax.set_ylabel(x_col)
                plt.setp(self.ax.get_xticklabels(), rotation=45, ha='right')
            
            self.ax.set_title(f'{plot_titles.get(plot_type, plot_type)}: {x_col} vs {y_col}', fontsize=12)
            self.ax.grid(True, alpha=0.3)
            self.figure.tight_layout()
            self.canvas.draw()
            
            self.status_bar.config(text=f"Отображен график типа: {plot_titles.get(plot_type, plot_type)}")
            
        except Exception as e:
            self.status_bar.config(text=f"Ошибка: {str(e)}")
            print(f"Ошибка при построении графика: {e}")
    
    def save_plot(self):
        now = datetime.now()
        filename = f"graph{now.strftime('%H_%M_%S')}.png"
        self.figure.savefig(filename, dpi=150, bbox_inches='tight')
        self.status_bar.config(text=f"График сохранен как {filename}")
        messagebox.showinfo("Сохранение", f"График сохранен в файл:\n{filename}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VisualPlotApp(root)
    root.mainloop()
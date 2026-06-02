import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import dataset
import numpy as np

class DrawPlotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система модификации визуализаций - Задание 4")
        self.root.geometry("1000x800")
        
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
        
        #мои параметры
        self.default_line_width = 7
        self.default_brush_color = '#18055f'
        self.default_cmap = 'plasma'
        
        self.available_cmaps = [
            'viridis', 'plasma', 'inferno', 'magma', 'cividis', 'Greys', 'Purples', 'Blues',
            'Greens', 'Oranges', 'Reds', 'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
            'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn', 'binary', 'gist_yarg',
            'spring', 'summer', 'autumn', 'winter'
        ]
        
        self.drawing_mode = False
        self.lines = []  
        self.current_line = None
        self.temp_line = None
        self.setup_ui()
        self.update_plot()
    
    def setup_ui(self):
        control_panel = ttk.LabelFrame(self.root, text="Управление", padding=10)
        control_panel.pack(pady=10, padx=10, fill=tk.X)
        
        ttk.Label(control_panel, text="Ось X:").grid(row=0, column=0, padx=5, pady=5)
        self.x_var = tk.StringVar(value=self.all_cols[0])
        self.x_combo = ttk.Combobox(control_panel, textvariable=self.x_var,
                                     values=self.all_cols, state="readonly", width=20)
        self.x_combo.grid(row=0, column=1, padx=5, pady=5)
        self.x_combo.bind('<<ComboboxSelected>>', lambda e: self.on_selection_change())
        
        ttk.Label(control_panel, text="Ось Y:").grid(row=0, column=2, padx=5, pady=5)
        self.y_var = tk.StringVar(value=self.all_cols[1] if len(self.all_cols) > 1 else self.all_cols[0])
        self.y_combo = ttk.Combobox(control_panel, textvariable=self.y_var,
                                     values=self.all_cols, state="readonly", width=20)
        self.y_combo.grid(row=0, column=3, padx=5, pady=5)
        self.y_combo.bind('<<ComboboxSelected>>', lambda e: self.on_selection_change())
        
        ttk.Label(control_panel, text="Цветовая схема:").grid(row=0, column=4, padx=5, pady=5)
        self.cmap_var = tk.StringVar(value=self.default_cmap)
        self.cmap_combo = ttk.Combobox(control_panel, textvariable=self.cmap_var,
                                        values=self.available_cmaps, state="readonly", width=12)
        self.cmap_combo.grid(row=0, column=5, padx=5, pady=5)
        self.cmap_combo.bind('<<ComboboxSelected>>', lambda e: self.on_selection_change())
        
        self.draw_btn = tk.Button(control_panel, text="🎨 Рисование", 
                                   command=self.toggle_drawing_mode,
                                   relief=tk.RAISED, bg='lightgray', width=12)
        self.draw_btn.grid(row=1, column=0, padx=5, pady=5)
        
        self.color_btn = tk.Button(control_panel, text="", 
                                    command=self.choose_color,
                                    width=4, height=1,
                                    bg=self.default_brush_color)
        self.color_btn.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(control_panel, text="Цвет").grid(row=1, column=2)
        
        self.line_width_var = tk.IntVar(value=self.default_line_width)
        self.width_scale = ttk.Scale(control_panel, from_=1, to=20, 
                                      variable=self.line_width_var,
                                      orient=tk.HORIZONTAL, length=100)
        self.width_scale.grid(row=1, column=3, padx=5, pady=5)
        self.width_label = ttk.Label(control_panel, text=f"Толщ: {self.default_line_width}")
        self.width_label.grid(row=1, column=4, padx=5)
        self.width_scale.configure(command=self.update_width_label)
        
        self.save_btn = ttk.Button(control_panel, text="💾 Сохранить", command=self.save_plot)
        self.save_btn.grid(row=1, column=5, padx=20, pady=5)
        
        self.undo_btn = ttk.Button(control_panel, text="↩ Отменить (Ctrl+Z)", command=self.undo_last_line)
        self.undo_btn.grid(row=1, column=6, padx=5, pady=5)
        
        self.clear_btn = ttk.Button(control_panel, text="🗑 Очистить всё", command=self.clear_all_lines)
        self.clear_btn.grid(row=1, column=7, padx=5, pady=5)
        
        self.root.bind('<Control-z>', lambda e: self.undo_last_line())
        self.root.bind('<Control-Z>', lambda e: self.undo_last_line())
        
        self.figure = plt.Figure(figsize=(10, 7), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self.root)
        self.canvas.get_tk_widget().pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        self.cid_press = self.canvas.mpl_connect('button_press_event', self.on_mouse_press)
        self.cid_release = self.canvas.mpl_connect('button_release_event', self.on_mouse_release)
        self.cid_motion = self.canvas.mpl_connect('motion_notify_event', self.on_mouse_motion)
        
        self.status_bar = ttk.Label(self.root, text="Готов. Нажмите 'Рисование' для активации", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def update_width_label(self, val):
        self.width_label.config(text=f"Толщ: {int(float(val))}")
    
    def choose_color(self):
        color = colorchooser.askcolor(title="Выберите цвет кисти", 
                                       color=self.color_btn.cget('bg'))
        if color[0] is not None:
            self.color_btn.config(bg=color[1])
    
    def toggle_drawing_mode(self):
        self.drawing_mode = not self.drawing_mode
        if self.drawing_mode:
            self.draw_btn.config(relief=tk.SUNKEN, bg='lightgreen', text="✏️ Рисование (Вкл)")
            self.status_bar.config(text="Режим рисования ВКЛЮЧЕН. Нажмите правую кнопку мыши для выключения")
            self.canvas.get_tk_widget().config(cursor="pencil")
        else:
            self.draw_btn.config(relief=tk.RAISED, bg='lightgray', text="🎨 Рисование")
            self.status_bar.config(text="Режим рисования ВЫКЛЮЧЕН")
            self.canvas.get_tk_widget().config(cursor="")
            if self.temp_line:
                self.temp_line.remove()
                self.temp_line = None
                self.canvas.draw()
    
    def on_selection_change(self):
        if self.drawing_mode:
            self.toggle_drawing_mode()
        self.lines = []
        if self.temp_line:
            self.temp_line = None
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
                
            elif plot_type == 'bar':
                counts = self.df[x_col].value_counts()
                colors = [cmap_obj(i/len(counts)) for i in range(len(counts))]
                self.ax.bar(range(len(counts)), counts.values, color=colors)
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
            
            self.ax.set_title(f'График: {x_col} vs {y_col}', fontsize=12)
            self.ax.grid(True, alpha=0.3)
            
            for line in self.lines:
                line[0].set_visible(True)
                if line[0] not in self.ax.lines:
                    self.ax.add_line(line[0])
            
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            self.status_bar.config(text=f"Ошибка: {str(e)}")
    
    def on_mouse_press(self, event):
        if not self.drawing_mode:
            return
        
        if event.inaxes != self.ax:
            return
        
        if event.button == 1:
            if self.temp_line:
                self.temp_line.remove()
                self.temp_line = None
            
            color = self.color_btn.cget('bg')
            width = self.line_width_var.get()
            self.current_line, = self.ax.plot([event.xdata, event.xdata], 
                                              [event.ydata, event.ydata],
                                              color=color, linewidth=width)
            self.canvas.draw()
            self.status_bar.config(text="Рисование линии...")
            
        elif event.button == 3:  # Правая кнопка
            if self.drawing_mode:
                self.toggle_drawing_mode()
    
    def on_mouse_motion(self, event):
        if not self.drawing_mode:
            return
        
        if self.current_line is None:
            return
        
        if event.inaxes != self.ax:
            return
        
        if event.xdata is not None and event.ydata is not None:
            x_data = self.current_line.get_xdata()
            y_data = self.current_line.get_ydata()
            
            self.current_line.set_xdata([x_data[0], event.xdata])
            self.current_line.set_ydata([y_data[0], event.ydata])
            
            self.canvas.draw_idle()
    
    def on_mouse_release(self, event):
        """Обработка отпускания кнопки"""
        if not self.drawing_mode:
            return
        
        if self.current_line is None:
            return
        
        if event.inaxes != self.ax or event.xdata is None or event.ydata is None:
            if self.current_line:
                self.current_line.remove()
                self.current_line = None
                self.canvas.draw()
            return
        
        if event.button == 1:
            self.lines.append((self.current_line, 
                               self.current_line.get_color(), 
                               self.current_line.get_linewidth()))
            self.current_line = None
            self.status_bar.config(text="Линия добавлена. Нажмите Ctrl+Z для отмены")
    
    def undo_last_line(self):
        if self.lines:
            last_line = self.lines.pop()
            last_line[0].remove()
            self.canvas.draw()
            self.status_bar.config(text="Последняя линия удалена")
        else:
            self.status_bar.config(text="Нет линий для отмены")
    
    def clear_all_lines(self):
        if self.lines:
            for line in self.lines:
                line[0].remove()
            self.lines = []
            self.canvas.draw()
            self.status_bar.config(text="Все линии очищены")
        else:
            self.status_bar.config(text="Нет линий для очистки")
    
    def save_plot(self):
        now = datetime.now()
        filename = f"graph{now.strftime('%H_%M_%S')}.png"
        self.figure.savefig(filename, dpi=150, bbox_inches='tight')
        self.status_bar.config(text=f"График сохранен как {filename}")
        messagebox.showinfo("Сохранение", f"График с рисунками сохранен в файл:\n{filename}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DrawPlotApp(root)
    root.mainloop()
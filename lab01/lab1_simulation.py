import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import math
from dataclasses import dataclass
from typing import List, Tuple
import matplotlib

matplotlib.use('TkAgg')


@dataclass
class SimulationResult:
    #класс хранения результатов моделирования
    dt: float
    trajectory: List[Tuple[float, float]]
    f_range: float
    max_height: float
    final_speed: float

class BallisticApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Моделирование полёта тела в атмосфере")
        self.root.geometry("1400x800")

        #нач параметры
        self.g = 9.81
        self.m = 1.0
        self.rho = 1.29
        self.C = 0.15
        self.S = 0.01  
        self.v0 = 100.0
        self.angle = 45.0
        
        self.results: List[SimulationResult] = [] #список для хранения результатов

        #цвета для разных траекторий
        self.colors = ['blue', 'red', 'green', 'brown', 'purple']
        self.setup_ui()

    def setup_ui(self):
        #создание интерфейса
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.grid(row=0, column=0, sticky="nw")

        plot_frame = ttk.Frame(self.root, padding="10")
        plot_frame.grid(row=0, column=1, sticky="nsew")

        table_frame = ttk.Frame(self.root, padding="10")
        table_frame.grid(row=1, column=0, columnspan=2, sticky="ew")

        #конфигурация сетки для растягивания графика
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        #панель управления
        ttk.Label(control_frame, text="Параметры запуска: ", font=('Arial', 12, 'bold')).grid(row=0, column=0,
                                                                                            columnspan=2, pady=10)
        #поля ввода параметров
        params = [
            ("Начальная скорость (м/с):", self.v0),
            ("Угол запуска (градусы):", self.angle),
            ("Масса тела (кг):", self.m),
            ("Плотность воздуха (кг/м^3):", self.rho),
            ("Коэффициент сопротивления:", self.C),
            ("Площадь сечения (м^2):", self.S),
        ]

        self.entries = {} #словарь для хранения полей ввода
        for i, (label, default) in enumerate(params, 1):
            ttk.Label(control_frame, text=label).grid(row=i, column=0, sticky="w", pady=5)
            entry = ttk.Entry(control_frame, width=15)
            entry.insert(0, str(default))
            entry.grid(row=i, column=1, pady=5)
            self.entries[label.split(":")[0]] = entry

        #поле для ввода шага моделирования
        ttk.Label(control_frame, text="Шаг моделирования (с):", font=('Arial', 10, 'bold')).grid(row=7, column=0,
                                                                                                sticky="w", pady=(20, 5))
        self.dt_entry = ttk.Entry(control_frame, width=15)
        self.dt_entry.insert(0, "0.01")
        self.dt_entry.grid(row=7, column=1, pady=(20, 5))

        #кнопки
        buttons_frame = ttk.Frame(control_frame)
        buttons_frame.grid(row=8, column=0, columnspan=2, pady=20)

        ttk.Button(buttons_frame, text="Запустить моделирование",
                   command=self.run_simulation).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Очистить результаты",
                   command=self.clear_results).pack(side=tk.LEFT, padx=5)

        #область для графика
        self.figure = Figure(figsize=(10, 6), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel('Дальность, м')
        self.ax.set_ylabel('Высота, м')
        self.ax.set_title('Траектории полета тела при разных шагах моделирования')
        self.ax.grid(True, alpha=0.3)

        self.canvas = FigureCanvasTkAgg(self.figure, plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        #таблица результатов
        ttk.Label(table_frame, text="Результаты моделирования",
                  font=('Arial', 12, 'bold')).pack()

        #создание колонок
        columns = ("Шаг (с)", "Дальность (м)", "Макс. высота (м)",
                   "Скорость в конеч. точке (м/с)", "Время полета (с)")

        self.tree = ttk.Treeview(table_frame, columns=columns,
                                 show="headings", height=8)

        #заголовки и ширина колонок
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor=tk.CENTER)

        #размещене таблицы
        self.tree.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def get_parameters(self):
        #получение параметров из полей ввода
        try:
            params = {
                'v0': float(self.entries['Начальная скорость (м/с)'].get()),
                'angle': float(self.entries['Угол запуска (градусы)'].get()),
                'm': float(self.entries['Масса тела (кг)'].get()),
                'rho': float(self.entries['Плотность воздуха (кг/м^3)'].get()),
                'C': float(self.entries['Коэффициент сопротивления'].get()),
                'S': float(self.entries['Площадь сечения (м^2)'].get()),
                'dt': float(self.dt_entry.get())
            }

            if params['dt'] <= 0:
                raise ValueError("Шаг моделирования должен быть положительным")
            if params['v0'] <= 0:
                raise ValueError("Начальная скорость должна быть положительной")
            if params['angle'] <= 0 or params['angle'] >= 90:
                raise ValueError("Угол должен быть в пределах 0-90 градусов")

            return params
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", f"Некорректные данные: {str(e)}")
            return None

    def calculate_drag_force(self, v, params):
        #расчет силы сопротивления воздуха
        return 0.5 * params['rho'] * params['C'] * params['S'] * v ** 2

    def run_simulation(self):
        #запуск моделирования полета
        params = self.get_parameters()
        if params is None:
            return

        dt = params['dt']

        #проверка на дублирование шага
        for result in self.results:
            if abs(result.dt - dt) < 1e-10:
                if not messagebox.askyesno("Подтверждение",
                                           f"Моделирование с шагом {dt} с уже выполнено. Повторить?"):
                    return

        #начальные условия
        angle_rad = math.radians(params['angle']) #преобразование в радианы
        x, y = 0.0, 0.0
        vx = params['v0'] * math.cos(angle_rad)
        vy = params['v0'] * math.sin(angle_rad)
        trajectory = [(x, y)]  #список для хранения траектории
        times = [0.0]
        t = 0.0
        max_height = 0.0

        #моделирование полета (метод Эйлера)
        while y >= 0:
            v = math.sqrt(vx ** 2 + vy ** 2) #расчет скорости

            #расчет сил
            drag_force = self.calculate_drag_force(v, params)

            #ускорения с учетом сопротивления воздуха
            ax = -drag_force * vx / (params['m'] * v) if v > 0 else 0
            ay = -self.g - drag_force * vy / (params['m'] * v) if v > 0 else -self.g

            #интегрирование методом Эйлера
            vx += ax * dt
            vy += ay * dt
            x += vx * dt
            y += vy * dt
            t += dt

            #сохранение траектории
            trajectory.append((x, y))
            times.append(t)

            #обновление максимальной высоты
            if y > max_height:
                max_height = y

        #расчет результатов
        range_distance = x 
        final_speed = math.sqrt(vx ** 2 + vy ** 2) if y <= 0 else 0
        flight_time = t

        #сохранение результатов
        result = SimulationResult(
            dt=dt,
            trajectory=trajectory,
            f_range=range_distance,
            max_height=max_height,
            final_speed=final_speed
        )

        #добавление в список результатов
        self.results.append(result)

        #обновление интерфейса
        self.update_plot()
        self.update_table()

    def update_plot(self):
        #обновление графика траекторий
        self.ax.clear()

        #отрисовка всех траекторий
        for i, result in enumerate(self.results):
            color = self.colors[i % len(self.colors)]
            x_vals = [p[0] for p in result.trajectory]
            y_vals = [p[1] for p in result.trajectory]

            self.ax.plot(x_vals, y_vals,
                         label=f'Δt = {result.dt:.4f} с',
                         color=color, linewidth=2)

            #отметка конечной точки
            self.ax.plot(x_vals[-1], y_vals[-1], 'o',
                         color=color, markersize=8)

        self.ax.set_xlabel('Дальность, м')
        self.ax.set_ylabel('Высота, м')
        self.ax.set_title('Траектории полета тела при разных шагах моделирования')
        self.ax.grid(True, alpha=0.3)
        self.ax.legend(loc='upper right')
        self.ax.set_xlim(left=0)
        self.ax.set_ylim(bottom=0)

        self.canvas.draw()

    def update_table(self):
        #обновление таблицы результатов
        for item in self.tree.get_children():
            self.tree.delete(item) #очистка таблицы

        #заполнение новыми данными
        for result in self.results:
            #расчет времени полета
            flight_time = len(result.trajectory) * result.dt

            self.tree.insert("", tk.END, values=(
                f"{result.dt:.6f}",
                f"{result.f_range:.2f}",
                f"{result.max_height:.2f}",
                f"{result.final_speed:.2f}",
                f"{flight_time:.2f}"
            ))

    def clear_results(self):
        #очистка всех результатов
        if messagebox.askyesno("Подтверждение",
                               "Очистить все результаты моделирования?"):
            self.results.clear()
            self.update_plot()
            self.update_table()

if __name__ == "__main__":
    root = tk.Tk()
    app = BallisticApp(root)

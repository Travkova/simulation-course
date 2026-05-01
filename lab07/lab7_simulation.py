import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class WeatherSimGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Моделирование погоды")
        self.root.geometry("1000x600")

        # Параметры модели
        self.Q = np.array([[-0.4,  0.3,  0.1],
                           [ 0.4, -0.8,  0.4],
                           [ 0.1,  0.4, -0.5]])
        self.rates = -np.diag(self.Q)
        self.P = np.zeros((3, 3))
        for i in range(3):
            for j in range(3):
                if i != j:
                    self.P[i, j] = self.Q[i, j] / self.rates[i]
        
        self.states_names = {1: "Ясно", 2: "Облачно", 3: "Пасмурно"}
        
        # Расчет теоретического распределения заранее
        A = self.Q.T.copy()
        A[-1] = 1.0
        b = np.array([0, 0, 1.0])
        self.theoretical_pi = np.linalg.solve(A, b)

        self.setup_ui()
        self.setup_plot()

    def setup_ui(self):
        # Верхняя панель управления
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(top_frame, text="Дней:", font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        self.days_entry = ttk.Entry(top_frame, width=10, font=('Arial', 10))
        self.days_entry.insert(0, "100")
        self.days_entry.pack(side=tk.LEFT, padx=5)

        self.btn_start = ttk.Button(top_frame, text="Прогнозирование", command=self.run_simulation)
        self.btn_start.pack(side=tk.LEFT, padx=20)

        ttk.Button(top_frame, text="Закрыть", command=self.root.quit).pack(side=tk.RIGHT, padx=5)

        # Основная область (Слева статистика, Справа график)
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ЛЕВАЯ ПАНЕЛЬ (Статистика)
        left_frame = tk.Frame(main_frame, bg="white", width=300, relief=tk.GROOVE, bd=2)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        left_frame.pack_propagate(False)

        ttk.Label(left_frame, text="Сравнение вероятностей", font=('Arial', 10, 'bold'), background='white').pack(anchor=tk.W, padx=10, pady=5)
        
        self.stats_frame = tk.Frame(left_frame, bg="white")
        self.stats_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        self.labels = {}
        self.create_stat_label("Ясно:", "em1", "th1", "er1")
        self.create_stat_label("Облачно:", "em2", "th2", "er2")
        self.create_stat_label("Пасмурно:", "em3", "th3", "er3")

        self.label_transitions = ttk.Label(self.stats_frame, text="Количество переходов: 0", font=('Arial', 9), background='white')
        self.label_transitions.pack(anchor=tk.W, pady=(10, 5))

        self.label_file = ttk.Label(self.stats_frame, text="", font=('Arial', 9), background='white', wraplength=250)
        self.label_file.pack(anchor=tk.W, pady=5)

        # ПРАВАЯ ПАНЕЛЬ (График)
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.fig, self.ax = plt.subplots(figsize=(7, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_stat_label(self, title, key_em, key_th, key_er):
        frame = tk.Frame(self.stats_frame, bg="white")
        frame.pack(fill=tk.X, pady=5)
        
        tk.Label(frame, text=title, font=('Arial', 9, 'bold'), bg='white').pack(anchor=tk.W)
        
        self.labels[key_em] = tk.Label(frame, text="Эмпирическая: -", font=('Arial', 9), bg='white')
        self.labels[key_em].pack(anchor=tk.W, padx=10)
        
        self.labels[key_th] = tk.Label(frame, text="Теоретическая: -", font=('Arial', 9), bg='white')
        self.labels[key_th].pack(anchor=tk.W, padx=10)
        
        self.labels[key_er] = tk.Label(frame, text="Ошибка: -", font=('Arial', 9), bg='white')
        self.labels[key_er].pack(anchor=tk.W, padx=10)

    def setup_plot(self):
        self.ax.set_title("")
        self.ax.set_xlabel("Время (дни)")
        self.ax.set_ylabel("Состояние погоды")
        self.ax.set_yticks([1, 2, 3])
        self.ax.set_yticklabels(['Ясно', 'Облачно', 'Пасмурно'])
        self.ax.set_ylim(0.5, 3.5)
        self.ax.grid(True)
        
        self.line, = self.ax.step([], [], where='post', color='navy', linewidth=2)
        self.fig.tight_layout()

    def run_simulation(self):
        try:
            T = float(self.days_entry.get())
            if T <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное количество дней.")
            return

        # Симуляция
        times = [0.0]
        states = [1]
        state = 1
        durations = np.zeros(3)
        current_t = 0.0

        while current_t < T:
            tau = np.random.exponential(1.0 / self.rates[state-1])
            new_t = current_t + tau
            
            if new_t >= T:
                durations[state-1] += (T - current_t)
                times.append(T)
                states.append(state)
                break
            
            durations[state-1] += tau
            times.append(new_t)
            states.append(state)
            
            next_state_idx = np.random.choice([0, 1, 2], p=self.P[state-1])
            state = next_state_idx + 1
            current_t = new_t

        # Обновление графика
        self.line.set_data(times, states)
        self.ax.set_xlim(0, T)
        self.canvas.draw()

        # Расчет статистики
        total_time = T
        emp_pi = durations / total_time
        
        # Обновление текста в левой панели
        for i in range(1, 4):
            idx = i - 1
            em_val = emp_pi[idx]
            th_val = self.theoretical_pi[idx]
            err_val = abs(em_val - th_val)
            
            self.labels[f"em{i}"].config(text=f"Эмпирическая: {em_val:.6f}")
            self.labels[f"th{i}"].config(text=f"Теоретическая: {th_val:.6f}")
            self.labels[f"er{i}"].config(text=f"Ошибка: {err_val:.6f}")

        transitions = len(states) - 1
        self.label_transitions.config(text=f"Количество переходов: {transitions}")
        
        # Подсчет матрицы переходов
        transition_counts = np.zeros((3, 3), dtype=int)
        for k in range(len(states) - 1):
            from_state = states[k] - 1
            to_state = states[k + 1] - 1
            transition_counts[from_state, to_state] += 1

        # Сохранение в CSV
        filename = f'weather_statistics.csv'
        
        with open(filename, 'w', encoding='utf-8-sig') as f:
            # Заголовок основной таблицы
            f.write("Состояние;Время (дни);Эмпирическая вероятность;Теоретическая вероятность;Абсолютная ошибка\n")
            
            # Данные по состояниям
            state_names = ['Ясно', 'Облачно', 'Пасмурно']
            for i in range(3):
                f.write(f"{state_names[i]};{durations[i]:.4f};{emp_pi[i]:.6f};{self.theoretical_pi[i]:.6f};{abs(emp_pi[i] - self.theoretical_pi[i]):.6f}\n")
            
            # Матрица переходов
            f.write("Переходы (из -> в):\n")
            f.write("Из\\В;Ясно;Облачно;Пасмурно\n")
            
            for i in range(3):
                row = f'{state_names[i]};'
                for j in range(3):
                    row += f'{transition_counts[i, j]};'
                f.write(row + '\n')
            
            f.write(f'Количество переходов: {transitions}\n')

        self.label_file.config(text=f"Статистика сохранена в файл: {filename}")
        messagebox.showinfo("Успех", f"Моделирование завершено!\n\nФайл сохранен:\n{filename}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherSimGUI(root)
    root.mainloop()

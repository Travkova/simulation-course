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
        self.root.geometry("1050x650")

        # Параметры модели: значения по умолчанию для предзаполнения полей
        self.Q_default = np.array([[-0.4,  0.3,  0.1],
                                   [ 0.4, -0.8,  0.4],
                                   [ 0.1,  0.4, -0.5]])
        self.Q = self.Q_default.copy()
        
        self.states_names = {1: "Ясно", 2: "Облачно", 3: "Пасмурно"}
        self.q_entries = []

        self.update_internal_matrices()
        self.setup_ui()
        self.setup_plot()

    def update_internal_matrices(self):
        """Пересчёт производных матриц и теоретического распределения"""
        self.rates = -np.diag(self.Q) #интенсивности выхода из состояний
        self.P = np.zeros((3, 3))  #м-ца переходов для вложенной ЦМДВ
        for i in range(3):
            for j in range(3):
                if i != j:
                    self.P[i, j] = self.Q[i, j] / self.rates[i] #вер-ть перехода из i в j
        
        # Теоретическое стационарное распределение π·Q = 0, Σπ = 1
        A = self.Q.T.copy()
        A[-1] = 1.0
        b = np.array([0, 0, 1.0])
        try:
            self.theoretical_pi = np.linalg.solve(A, b) #СЛУ для поиска стационар распределения pi
        except np.linalg.LinAlgError:
            self.theoretical_pi = np.zeros(3)

    def setup_ui(self):
        # Блок ввода матрицы Q
        q_frame = ttk.Frame(self.root, padding="5 5 5 10")
        q_frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(q_frame, text="Матрица интенсивностей Q:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, padx=5)

        state_labels = ['Ясно', 'Облачно', 'Пасмурно']
        for i in range(3):
            row_frame = ttk.Frame(q_frame)
            row_frame.pack(fill=tk.X, pady=2)
            ttk.Label(row_frame, text=f"Из {state_labels[i]}:", width=10, anchor=tk.W).pack(side=tk.LEFT, padx=5)
            row_entries = []
            for j in range(3):
                entry = ttk.Entry(row_frame, width=8, justify='center')
                entry.insert(0, str(self.Q_default[i, j]).replace('.', ','))
                entry.pack(side=tk.LEFT, padx=2)
                row_entries.append(entry)
            self.q_entries.append(row_entries)

        # Верхняя панель управления
        top_frame = ttk.Frame(self.root, padding="5")
        top_frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(top_frame, text="Дней:", font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        self.days_entry = ttk.Entry(top_frame, width=10, font=('Arial', 10))
        self.days_entry.insert(0, "100")
        self.days_entry.pack(side=tk.LEFT, padx=5)

        self.btn_start = ttk.Button(top_frame, text="Прогнозирование", command=self.run_simulation)
        self.btn_start.pack(side=tk.LEFT, padx=20)

        ttk.Button(top_frame, text="Закрыть", command=self.root.quit).pack(side=tk.RIGHT, padx=5)

        # Основная область: слева статистика, справа график
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Левая панель со статистикой
        left_frame = tk.Frame(main_frame, bg="white", width=320, relief=tk.GROOVE, bd=2)
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

        self.label_file = ttk.Label(self.stats_frame, text="", font=('Arial', 9), background='white', wraplength=280)
        self.label_file.pack(anchor=tk.W, pady=5)

        # Правая панель для графика
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

    def parse_matrix(self):
        """Считывание и валидация матрицы Q из интерфейса"""
        Q = np.zeros((3, 3))
        for i in range(3):
            for j in range(3):
                raw = self.q_entries[i][j].get().strip().replace(',', '.')
                if not raw:
                    raise ValueError(f"Поле [{i+1},{j+1}] пустое.")
                Q[i, j] = float(raw)

        # Валидация структуры инфинитезимальной матрицы
        for i in range(3):
            row_sum = 0.0
            for j in range(3):
                if i == j:
                    if Q[i, j] > 1e-9:
                        raise ValueError(f"q[{i+1},{j+1}] (диагональ) должна быть ≤ 0.")
                else:
                    if Q[i, j] < -1e-9:
                        raise ValueError(f"q[{i+1},{j+1}] (вне диагонали) должна быть ≥ 0.")
                row_sum += Q[i, j]
            
            if abs(row_sum) > 1e-4:
                raise ValueError(f"Сумма строки {i+1} должна быть 0 (сейчас {row_sum:.4f}).\nПроверьте диагональный элемент.")

        if np.any(-np.diag(Q) < 1e-9):
            raise ValueError("Интенсивность выхода из состояния не может быть 0 или отрицательной.")

        return Q

    def run_simulation(self):
        """ Ф-ция моделирования """
        try:
            # обновляем матрицу Q из интерфейса
            self.Q = self.parse_matrix()
            self.update_internal_matrices()

            # считываем длительность
            T = float(self.days_entry.get().replace(',', '.'))
            if T <= 0: raise ValueError("Время моделирования должно быть > 0.")
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e))
            return

        # симуляция цепи Маркова
        times = [0.0] #моменты времени переходов
        states = [1] #состояния в эти моменты
        state = 1    #нач состояние системы в момент времени t = 0
        durations = np.zeros(3) #общее время в каждом состоянии
        current_t = 0.0
        transition_counts = np.zeros((3, 3), dtype=int) #м-ца фактических переходов

        while current_t < T:
            tau = np.random.exponential(1.0 / self.rates[state-1]) #время до след перехода
            new_t = current_t + tau
            
            if new_t >= T:
                #если след переход выходит за пределы T - останавливаемся и добавляем остаток времени
                durations[state-1] += (T - current_t)
                times.append(T)
                states.append(state)
                break
            
            durations[state-1] += tau
            times.append(new_t)
            states.append(state)
            
            #выбираем след состояние по вероятностям из м-цы Р
            next_state_idx = np.random.choice([0, 1, 2], p=self.P[state-1]) #случ выбор след состояния системы
            next_state = next_state_idx + 1
            transition_counts[state-1, next_state_idx] += 1
            state = next_state
            current_t = new_t

        # Обновление графика
        self.line.set_data(times, states)
        self.ax.set_xlim(0, T)
        self.canvas.draw()

        # Расчет статистики
        emp_pi = durations / T #доля времени в каждом состоянии
        
        for i in range(1, 4):
            idx = i - 1
            em_val = emp_pi[idx] #эмп вер-ть
            th_val = self.theoretical_pi[idx] #теор вер-ть
            err_val = abs(em_val - th_val) #абсолютная ошибка
            
            self.labels[f"em{i}"].config(text=f"Эмпирическая: {em_val:.6f}")
            self.labels[f"th{i}"].config(text=f"Теоретическая: {th_val:.6f}")
            self.labels[f"er{i}"].config(text=f"Ошибка: {err_val:.6f}")

        transitions = int(np.sum(transition_counts)) #общее кол-во зафиксированных переходов
        self.label_transitions.config(text=f"Количество переходов: {transitions}")

        # Сохранение в CSV
        filename = 'weather_statistics.csv'
        with open(filename, 'w', encoding='utf-8-sig') as f:
            f.write("Состояние;Время (дни);Эмпирическая вероятность;Теоретическая вероятность;Абсолютная ошибка\n")
            state_names = ['Ясно', 'Облачно', 'Пасмурно']
            for i in range(3):
                f.write(f"{state_names[i]};{durations[i]:.4f};{emp_pi[i]:.6f};{self.theoretical_pi[i]:.6f};{abs(emp_pi[i] - self.theoretical_pi[i]):.6f}\n")
            
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

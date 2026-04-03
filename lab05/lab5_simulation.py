import tkinter as tk
from tkinter import ttk, messagebox
import time

class BaseGenerator:
    def __init__(self, b, m, seed):
        self.b = b
        self.m = m
        self.x = seed

    def rand(self):
        self.x = (self.b * self.x) % self.m
        return self.x / self.m

class YesNoApp:
    def __init__(self, parent, generator):
        self.parent = parent
        self.generator = generator
        self.frame = ttk.LabelFrame(parent, text="Скажи «да» или «нет»", padding=10)
        self.frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.create_widgets()
    
    def create_widgets(self):
        # Вопрос
        tk.Label(self.frame, text="Твой вопрос:", font=("Arial", 11)).pack(pady=5)
        self.question_entry = tk.Entry(self.frame, width=50, font=("Arial", 10))
        self.question_entry.pack(pady=5)
        
        # Вероятность
        prob_frame = tk.Frame(self.frame)
        prob_frame.pack(pady=10)
        tk.Label(prob_frame, text="Вероятность, что будет ДА (p):", font=("Arial", 11)).pack(side=tk.LEFT)
        self.prob_entry = tk.Entry(prob_frame, width=10, font=("Arial", 10))
        self.prob_entry.insert(0, "0.5")
        self.prob_entry.pack(side=tk.LEFT, padx=5)
        
        # Кнопка
        self.answer_button = tk.Button(
            self.frame,
            text="ПОЛУЧИТЬ ОТВЕТ",
            command=self.generate_answer,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10
        )
        self.answer_button.pack(pady=15)
        
        # Результат
        self.result_label = tk.Label(
            self.frame,
            text="",
            font=("Arial", 28, "bold"),
            pady=20
        )
        self.result_label.pack()
        
        # Статистика
        stats_frame = ttk.LabelFrame(self.frame, text="Статистика", padding=5)
        stats_frame.pack(fill="x", pady=10)
        
        self.stats_label = tk.Label(stats_frame, text="ДА: 0 | НЕТ: 0 | Всего: 0", font=("Arial", 10))
        self.stats_label.pack()
        
        # Счётчики
        self.da_count = 0
        self.net_count = 0
    
    def generate_answer(self):
        question = self.question_entry.get().strip()
        if not question:
            messagebox.showerror("Ошибка", "Напишите вопрос!")
            return
        
        try:
            prob = float(self.prob_entry.get())
            if prob < 0 or prob > 1:
                messagebox.showerror("Ошибка", "Вероятность должна быть от 0 до 1")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное число!")
            return
        
        # Генерация случайного числа и проверка
        alpha = self.generator.rand()
        
        if alpha < prob:
            result = "ДА!"
            color = "#4CAF50"
            self.da_count += 1
        else:
            result = "НЕТ!"
            color = "#f44336"
            self.net_count += 1
        
        self.result_label.config(text=result, fg=color)
        
        # Обновление статистики
        total = self.da_count + self.net_count
        if total > 0:
            da_freq = self.da_count / total
            net_freq = self.net_count / total
            self.stats_label.config(
                text=f"ДА: {self.da_count} (ṗ = {da_freq:.3f}) | "
                     f"НЕТ: {self.net_count} (ṗ = {net_freq:.3f}) | "
                     f"Всего: {total}"
            )
        
        # Очистка поля вопроса
        self.question_entry.delete(0, tk.END)
    
    def reset_stats(self):
        self.da_count = 0
        self.net_count = 0
        self.stats_label.config(text="ДА: 0 | НЕТ: 0 | Всего: 0")
        self.result_label.config(text="")

class Magic8BallApp:
    def __init__(self, parent, generator):
        self.parent = parent
        self.generator = generator
        self.frame = ttk.LabelFrame(parent, text="Шар предсказаний (Magic 8-Ball)", padding=10)
        self.frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Ответы (полная группа несовместных событий)
        self.answers = [
            "Бесспорно",
            "Предрешено",
            "Определённо ДА",
            "Никаких сомнений",
            "Можешь быть уверен в этом",
            "Мне кажется - ДА",
            "Вероятнее всего",
            "Хорошие перспективы",
            "Знаки говорят - ДА",
            "ДА",
            "Спроси позже",
            "Пока не ясно, попробуй снова",
            "Лучше не рассказывать",
            "Сейчас нельзя предсказать",
            "Сконцентрируйся и спроси опять",
            "Даже не думай",
            "Мой ответ — НЕТ",
            "Весьма сомнительно",
            "Перспективы не очень хорошие",
            "По моим данным — НЕТ"
        ]
        
        self.prob_entries = []
        self.create_widgets()
    
    def create_widgets(self):
        # Заголовок
        title_label = tk.Label(
            self.frame,
            text="ШАР ПРЕДСКАЗАНИЙ",
            font=("Arial", 18, "bold"),
            fg="#9370DB"
        )
        title_label.pack(pady=10)
        
        # Вопрос
        tk.Label(self.frame, text="Задай свой вопрос:", font=("Arial", 12)).pack(pady=5)
        self.question_entry = tk.Entry(self.frame, width=60, font=("Arial", 10))
        self.question_entry.pack(pady=5)
        
        # Рамка для вероятностей
        prob_main_frame = ttk.LabelFrame(self.frame, text="Настройка вероятностей ответов", padding=5)
        prob_main_frame.pack(fill="both", expand=True, pady=10)
        
        # Создаём canvas с прокруткой для вероятностей
        canvas = tk.Canvas(prob_main_frame, height=200)
        scrollbar = ttk.Scrollbar(prob_main_frame, orient="vertical", command=canvas.yview)
        self.prob_frame = tk.Frame(canvas)
        
        self.prob_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.prob_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Поля ввода вероятностей для всех ответов, кроме последнего
        for i in range(len(self.answers) - 1):
            frame = tk.Frame(self.prob_frame)
            frame.pack(pady=3, fill="x")
            
            tk.Label(frame, text=f"P({self.answers[i][:20]}):", width=25, anchor='w').pack(side=tk.LEFT, padx=5)
            entry = tk.Entry(frame, width=10)
            entry.insert(0, f"{1.0/len(self.answers):.3f}")
            entry.pack(side=tk.LEFT, padx=5)
            self.prob_entries.append(entry)
        
        # Последний ответ (автоматически вычисляется)
        last_frame = tk.Frame(self.prob_frame)
        last_frame.pack(pady=3, fill="x")
        self.last_prob_label = tk.Label(last_frame, text=f"P({self.answers[-1][:20]}):", width=25, anchor='w')
        self.last_prob_label.pack(side=tk.LEFT, padx=5)
        self.last_prob_value = tk.Label(last_frame, text="", fg="blue", font=("Arial", 10, "bold"))
        self.last_prob_value.pack(side=tk.LEFT, padx=5)
        
        # Кнопка
        self.ask_button = tk.Button(
            self.frame,
            text="СПРОСИТЬ ШАР",
            command=self.get_answer,
            bg="#9370DB",
            fg="white",
            font=("Arial", 14, "bold"),
            padx=20,
            pady=10
        )
        self.ask_button.pack(pady=15)
        
        # Результат
        self.result_label = tk.Label(
            self.frame,
            text="",
            font=("Arial", 20, "bold"),
            fg="#FF1493",
            pady=20,
            wraplength=600
        )
        self.result_label.pack()
        
        # Статистика
        stats_frame = ttk.LabelFrame(self.frame, text="Статистика ответов (эмпирические вероятности)", padding=5)
        stats_frame.pack(fill="both", expand=True, pady=10)
        
        # Таблица для статистики
        tree_frame = tk.Frame(stats_frame)
        tree_frame.pack(fill="both", expand=True)
        
        self.stats_tree = ttk.Treeview(tree_frame, columns=("answer", "count", "freq"), 
                                        show="headings", height=6)
        self.stats_tree.heading("answer", text="Ответ")
        self.stats_tree.heading("count", text="Частота (n_k)")
        self.stats_tree.heading("freq", text="Относительная частота (ṗ_k)")
        
        self.stats_tree.column("answer", width=200)
        self.stats_tree.column("count", width=100)
        self.stats_tree.column("freq", width=150)
        
        scroll_tree = ttk.Scrollbar(tree_frame, orient="vertical", command=self.stats_tree.yview)
        self.stats_tree.configure(yscrollcommand=scroll_tree.set)
        
        self.stats_tree.pack(side="left", fill="both", expand=True)
        scroll_tree.pack(side="right", fill="y")
        
        # Счётчики
        self.response_counts = [0] * len(self.answers)
        self.total_attempts = 0
        
        # Кнопка сброса
        tk.Button(self.frame, text="Сбросить статистику", command=self.reset_stats,
                 bg="#ff9800", fg="white", font=("Arial", 10)).pack(pady=5)
    
    def get_answer(self):
        question = self.question_entry.get().strip()
        if not question:
            messagebox.showerror("Ошибка", "Задайте вопрос!")
            return
        
        try:
            probs = [] #вероятности от пользователя
            for entry in self.prob_entries:
                p = float(entry.get())
                if p < 0 or p > 1:
                    messagebox.showerror("Ошибка", "Вероятность должна быть от 0 до 1")
                    return
                probs.append(p)
            
            sum_probs = sum(probs)
            if sum_probs >= 1:
                messagebox.showerror("Ошибка", f"Сумма вероятностей не может быть ≥ 1 (сейчас {sum_probs:.3f})")
                return
            
            last_prob = 1.0 - sum_probs #последняя вероятность
            probs.append(last_prob)
            
            self.last_prob_value.config(text=f"{last_prob:.4f}")
            
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числа!")
            return
        
        # Алгоритм генерации события из группы событий
        alpha = self.generator.rand() 
        cumulative = 0.0 #накапливаем сумму вероятностей
        chosen_index = 0 #индекс выбранного события
        
        for i, p in enumerate(probs):
            cumulative += p
            if alpha < cumulative:  #попала ли альфа в интервал
                chosen_index = i  #запоминаем индекс
                break
        
        # Сохраняем результат
        answer = self.answers[chosen_index]
        self.response_counts[chosen_index] += 1
        self.total_attempts += 1
        
        # Отображаем результат
        self.result_label.config(text=f" {answer} ")
        
        # Обновляем статистику
        self.update_statistics()
        
        # Очищаем поле вопроса
        self.question_entry.delete(0, tk.END)
    
    def update_statistics(self):
        # Очищаем таблицу
        for row in self.stats_tree.get_children():
            self.stats_tree.delete(row)
        
        # Заполняем таблицу
        for i, answer in enumerate(self.answers):
            count = self.response_counts[i]
            freq = count / self.total_attempts if self.total_attempts > 0 else 0.0
            self.stats_tree.insert("", tk.END, values=(answer, count, f"{freq:.4f}"))
    
    def reset_stats(self):
        self.response_counts = [0] * len(self.answers)
        self.total_attempts = 0
        self.update_statistics()
        self.result_label.config(text="")
        messagebox.showinfo("Статистика", "Статистика сброшена!")

class CombinedApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Моделирование случайных событий")
        self.root.geometry("750x800")
        
        # Инициализация генератора случайных чисел
        b = 2**32 + 3
        m = 2**63
        seed = int(time.time() * 1000) % m
        self.generator = BaseGenerator(b, m, seed)
        
        # Прогрев генератора
        for _ in range(100):
            self.generator.rand()
        
        # Создание вкладок
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Вкладка 1: ДА/НЕТ
        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text="Скажи «да» или «нет»")
        self.yes_no_app = YesNoApp(self.tab1, self.generator)
        
        # Вкладка 2: Шар предсказаний
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text="Шар предсказаний")
        self.magic_app = Magic8BallApp(self.tab2, self.generator)

def main():
    root = tk.Tk()
    app = CombinedApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

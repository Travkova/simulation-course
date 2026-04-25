import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy import stats

class StatisticalModelingApp:
    def __init__(self, main_window):
        """Конструктор класса. Инициализация элементов GUI """
        self.main_window = main_window
        self.main_window.title("ЛР№6: Моделирование СВ")
        self.main_window.geometry("1300x1050")

        self.style = ttk.Style()
        self.style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))

        self.tab_control = ttk.Notebook(main_window)
        self.tab_control.pack(expand=True, fill='both', padx=5, pady=5)

        self.discrete_tab = ttk.Frame(self.tab_control)
        self.normal_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.discrete_tab, text="lab06-1: ДСВ")
        self.tab_control.add(self.normal_tab, text="lab06-2: НормСВ")

        self._initialize_discrete_interface()
        self._initialize_normal_interface()

    # Часть 1: дискретная СВ
    def _initialize_discrete_interface(self):
        """GUI для ДСВ: поля ввода, таблица рез-тов, обл-ть для графика и вывода"""
        param_container = ttk.LabelFrame(self.discrete_tab, text=" Параметры распределения (X и P) ", padding=10)
        param_container.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self.value_fields, self.prob_fields = [], []
        ttk.Label(param_container, text="№", font='bold').grid(row=0, column=0, padx=5)
        ttk.Label(param_container, text="Значение X", font='bold').grid(row=0, column=1, padx=5)
        ttk.Label(param_container, text="Вероятность P", font='bold').grid(row=0, column=2, padx=5)

        default_values, default_probs = [1, 2, 3, 4, 5], [0.1, 0.2, 0.4, 0.2, 0.1]
        for idx in range(5):
            ttk.Label(param_container, text=f"{idx+1}").grid(row=idx+1, column=0)
            val_entry = ttk.Entry(param_container, width=15)
            val_entry.insert(0, str(default_values[idx]))
            val_entry.grid(row=idx+1, column=1, padx=5, pady=2)
            self.value_fields.append(val_entry)

            prob_entry = ttk.Entry(param_container, width=15)
            prob_entry.insert(0, str(default_probs[idx]))
            prob_entry.grid(row=idx+1, column=2, padx=5, pady=2)
            self.prob_fields.append(prob_entry)

        run_button = ttk.Button(param_container, text="ВЫЧИСЛИТЬ", command=self._execute_discrete_analysis)
        run_button.grid(row=1, column=3, rowspan=5, padx=20, sticky="nsew")

        ttk.Label(param_container, text="График для N:").grid(row=1, column=4, sticky=tk.S)
        self.sample_size_selector1 = ttk.Combobox(param_container, values=["10", "100", "1000", "10000"], width=8, state="readonly")
        self.sample_size_selector1.current(3)
        self.sample_size_selector1.grid(row=2, column=4, sticky=tk.N)

        result_columns = ("N", "E эмп.", "Погр-ть Е", "D эмп.", "Погр-ть D", "χ²", "χ² крит.", "Результат")
        self.results_table1 = ttk.Treeview(self.discrete_tab, columns=result_columns, show='headings', height=5)
        for col in result_columns:
            self.results_table1.heading(col, text=col.replace("_", " "))
            self.results_table1.column(col, width=110, anchor=tk.CENTER)
        self.results_table1.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        self.figure1, self.axes1 = plt.subplots(figsize=(5, 3))
        self.plot_canvas1 = FigureCanvasTkAgg(self.figure1, master=self.discrete_tab)
        self.plot_canvas1.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.conclusion_text1 = scrolledtext.ScrolledText(self.discrete_tab, height=4, font=('Consolas', 9))
        self.conclusion_text1.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        self.conclusion_text1.insert(tk.END, "Нажмите 'ВЫЧИСЛИТЬ' для генерации вывода.")
        self.conclusion_text1.config(state=tk.DISABLED)

    def _execute_discrete_analysis(self):
        """Вычисление серии экспериментов для ДСВ """
        try:
            values_array, probs_array = [], []
            for idx in range(len(self.value_fields)):
                raw_val, raw_prob = self.value_fields[idx].get().strip(), self.prob_fields[idx].get().strip()
                if raw_val and raw_prob:
                    values_array.append(float(raw_val))
                    probs_array.append(float(raw_prob))
            values_array, probs_array = np.array(values_array), np.array(probs_array)
            if not np.isclose(np.sum(probs_array), 1.0): #усл нормировки
                raise ValueError(f"Сумма вероятностей {np.sum(probs_array):.3f} != 1.0")
        except ValueError as err:
            messagebox.showerror("Ошибка ввода", str(err))
            return

        for row in self.results_table1.get_children(): 
            self.results_table1.delete(row)

        sample_sizes = [10, 100, 1000, 10000] #теор параметры
        theoretical_mean = np.sum(values_array * probs_array)
        theoretical_variance = np.sum(values_array**2 * probs_array) - theoretical_mean**2
        analysis_log = [] #для хранения рез-тов вывода

        for current_n in sample_sizes:
            #генерация выборки методом обратной ф-ции распр-ния
            cumulative_probs = np.cumsum(probs_array)
            generated_samples = values_array[np.searchsorted(cumulative_probs, np.random.rand(current_n))]

            #эмпирич характеристики
            empirical_mean = np.mean(generated_samples)
            empirical_variance = np.var(generated_samples)

            #относит погрешности
            mean_error = self._compute_relative_error(empirical_mean, theoretical_mean)
            var_error = self._compute_relative_error(empirical_variance, theoretical_variance)

            #критерий хи-квадрат
            observed_freq = np.array([np.sum(generated_samples == val) for val in values_array])
            expected_freq = probs_array * current_n
            expected_freq = expected_freq / np.sum(expected_freq) * np.sum(observed_freq)
            
            chi_square_stat, _ = stats.chisquare(observed_freq, f_exp=expected_freq)
            chi_square_crit = stats.chi2.ppf(0.95, df=len(values_array)-1)
            hypothesis_status = "H0 принята (α=0.05)" if chi_square_stat < chi_square_crit else "H0 отклонена"

            #добавление строки в таблицу
            self.results_table1.insert("", tk.END, values=(
                current_n, f"{empirical_mean:.3f}", f"{mean_error:.1f}%", 
                f"{empirical_variance:.3f}", f"{var_error:.1f}%", 
                f"{chi_square_stat:.2f}", f"{chi_square_crit:.2f}", hypothesis_status
            ))
            analysis_log.append((mean_error, var_error, hypothesis_status))
            
            #построение графика
            if current_n == int(self.sample_size_selector1.get()):
                self.axes1.clear()
                x_positions = np.arange(len(values_array))
                self.axes1.bar(x_positions - 0.2, probs_array, 0.4, label='Теория', alpha=0.6, color='blue')
                self.axes1.bar(x_positions + 0.2, observed_freq/current_n, 0.4, label=f'Эмпирика (N={current_n})', alpha=0.6, color='purple')
                self.axes1.set_xticks(x_positions)
                self.axes1.set_xticklabels([str(val) for val in values_array])
                self.axes1.set_ylabel("Вероятность")
                self.axes1.set_title(f"Сравнение распределений (N={current_n})")
                self.axes1.legend()
                self.axes1.grid(axis='y', linestyle='--', alpha=0.5, color='gray')
                self.axes1.set_axisbelow(True)
                self.plot_canvas1.draw()

        self._display_conclusion(self.conclusion_text1, "Дискретная СВ", analysis_log, theoretical_mean, theoretical_variance)

    # Часть 2: нормальная СВ
    def _initialize_normal_interface(self):
        param_container = ttk.LabelFrame(self.normal_tab, text=" Параметры нормального распределения ", padding=10)
        param_container.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        ttk.Label(param_container, text="M (μ):").grid(row=0, column=0)
        self.mean_input = ttk.Entry(param_container, width=10)
        self.mean_input.insert(0, "0")
        self.mean_input.grid(row=0, column=1, padx=5)

        ttk.Label(param_container, text="Sigma (σ):").grid(row=0, column=2)
        self.std_input = ttk.Entry(param_container, width=10)
        self.std_input.insert(0, "1")
        self.std_input.grid(row=0, column=3, padx=5)

        run_button = ttk.Button(param_container, text="МОДЕЛИРОВАТЬ", command=self._execute_normal_analysis)
        run_button.grid(row=0, column=4, padx=20)

        ttk.Label(param_container, text="График для N:").grid(row=0, column=5, padx=5)
        self.sample_size_selector2 = ttk.Combobox(param_container, values=["10", "100", "1000", "10000"], width=8, state="readonly")
        self.sample_size_selector2.current(3)
        self.sample_size_selector2.grid(row=0, column=6, padx=5)

        result_columns = ("N", "Е эмп.", "Погр-ть Е", "D эмп.", "Погр-ть D", "χ²", "χ² крит.", "Результат")
        self.results_table2 = ttk.Treeview(self.normal_tab, columns=result_columns, show='headings', height=5)
        for col in result_columns:
            self.results_table2.heading(col, text=col.replace("_", " "))
            self.results_table2.column(col, width=110, anchor=tk.CENTER)
        self.results_table2.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        self.figure2, self.axes2 = plt.subplots(figsize=(5, 3))
        self.plot_canvas2 = FigureCanvasTkAgg(self.figure2, master=self.normal_tab)
        self.plot_canvas2.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.conclusion_text2 = scrolledtext.ScrolledText(self.normal_tab, height=4, font=('Consolas', 9))
        self.conclusion_text2.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        self.conclusion_text2.insert(tk.END, "Нажмите 'МОДЕЛИРОВАТЬ' для генерации вывода.")
        self.conclusion_text2.config(state=tk.DISABLED)

    def _execute_normal_analysis(self):
        """Моделирование нормальной СВ методом Бокса-Мюллера """
        try:
            mu = float(self.mean_input.get())
            sigma = float(self.std_input.get())
            if sigma <= 0: 
                raise ValueError("σ должно быть > 0")
        except ValueError as err:
            messagebox.showerror("Ошибка ввода", str(err))
            return

        for row in self.results_table2.get_children(): 
            self.results_table2.delete(row)
        analysis_log = []

        for current_n in [10, 100, 1000, 10000]:
            uniform1 = np.random.rand(current_n) #метод Бокса-Мюллера для генерации норм величин
            uniform2 = np.random.rand(current_n)
            
            #защита от логарифма нуля (clip добавляет небольшое смещение)
            normal_samples = np.sqrt(-2 * np.log(np.clip(uniform1, 1e-10, 1.0))) * np.cos(2 * np.pi * uniform2) * sigma + mu

            empirical_mean, empirical_var = np.mean(normal_samples), np.var(normal_samples)
            mean_error = self._compute_relative_error(empirical_mean, mu)
            var_error = self._compute_relative_error(empirical_var, sigma**2)

            #критерий хи-квадрат (группировка в 10 интервалов)
            hist_counts, bin_edges = np.histogram(normal_samples, bins=10)
            cdf_values = stats.norm.cdf(bin_edges, mu, sigma)
            expected_counts = np.diff(cdf_values) * current_n
            
            #нормировка ожидаемых частот под сумму наблюдаемых
            expected_counts = expected_counts / np.sum(expected_counts) * np.sum(hist_counts)
            expected_counts = np.maximum(expected_counts, 1e-12)
            expected_counts = expected_counts / np.sum(expected_counts) * np.sum(hist_counts)

            chi_square_stat, _ = stats.chisquare(hist_counts, f_exp=expected_counts)
            chi_square_crit = stats.chi2.ppf(0.95, df=9)
            hypothesis_status = "H0 принята(α=0.05)" if chi_square_stat < chi_square_crit else "H0 отклонена"

            self.results_table2.insert("", tk.END, values=(
                current_n, f"{empirical_mean:.3f}", f"{mean_error:.1f}%", 
                f"{empirical_var:.3f}", f"{var_error:.1f}%", 
                f"{chi_square_stat:.2f}", f"{chi_square_crit:.2f}", hypothesis_status
            ))
            analysis_log.append((mean_error, var_error, hypothesis_status))

            if current_n == int(self.sample_size_selector2.get()):
                self.axes2.clear()
                self.axes2.hist(normal_samples, bins=30, density=True, alpha=0.5, color='olive', edgecolor='green', label='Эмпирика')
                x_domain = np.linspace(mu-4*sigma, mu+4*sigma, 100)
                self.axes2.plot(x_domain, stats.norm.pdf(x_domain, mu, sigma), 'g-', lw=2, label='Теория')
                self.axes2.set_title(f"Гистограмма и плотность (N={current_n})")
                self.axes2.legend()
                self.axes2.grid(True, linestyle=':', alpha=0.6, color='gray')
                self.axes2.set_axisbelow(True)
                self.plot_canvas2.draw()

        self._display_conclusion(self.conclusion_text2, "Нормальная СВ (Бокс-Мюллер)", analysis_log, mu, sigma**2)

    # Вспомогательные методы
    @staticmethod
    def _compute_relative_error(empirical_value, theoretical_value):
        """Возвращает относительную погрешность в процентах"""
        if abs(theoretical_value) < 1e-10:
            return abs(empirical_value)
        return abs(empirical_value - theoretical_value) / abs(theoretical_value) * 100

    def _display_conclusion(self, text_widget, distribution_name, log_entries, theoretical_mean, theoretical_variance):
        """Формирование и отображение вывода"""
        text_widget.config(state=tk.NORMAL)
        text_widget.delete(1.0, tk.END)
        
        mean_errors = [entry[0] for entry in log_entries]
        var_errors = [entry[1] for entry in log_entries]
        chi_results = [entry[2] for entry in log_entries]

        trend_description = "монотонно уменьшается" if mean_errors[0] > mean_errors[-1] else "имеет колебательный характер"
        hypothesis_passed = chi_results[-1].startswith("H0 принята")
        
        conclusion_text = (
            f"Вывод по {distribution_name}:\n"
            f"1. При росте N от 10 до 10 000 эмпирические M и D сходятся к теоретическим значениям "
            f"(M_теор={theoretical_mean:.3f}, D_теор={theoretical_variance:.3f}).\n"
            f"2. Относительная погрешность среднего: {mean_errors[0]:.1f}% → {mean_errors[-1]:.1f}% ({trend_description}).\n"
            f"3. Критерий χ² при N=10000: {chi_results[-1]}. Гипотеза о соответствии распределению {'подтверждена' if hypothesis_passed else 'отклонена'}."
        )
        text_widget.insert(tk.END, conclusion_text)
        text_widget.config(state=tk.DISABLED)


if __name__ == "__main__":
    root_window = tk.Tk()
    statistical_app = StatisticalModelingApp(root_window)
    root_window.mainloop()

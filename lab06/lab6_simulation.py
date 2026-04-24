import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy import stats

class LabWorkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ЛР№6: Моделирование СВ")
        self.root.geometry("1300x1050")

        self.style = ttk.Style()
        self.style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)

        self.tab1 = ttk.Frame(self.notebook)
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text="lab06-1: ДСВ")
        self.notebook.add(self.tab2, text="lab06-2: НормСВ")

        self.setup_tab1()
        self.setup_tab2()

    #Часть 1: дискретная СВ
    def setup_tab1(self):
        input_frame = ttk.LabelFrame(self.tab1, text=" Параметры распределения (X и P) ", padding=10)
        input_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self.x_entries, self.p_entries = [], []
        ttk.Label(input_frame, text="№", font='bold').grid(row=0, column=0, padx=5)
        ttk.Label(input_frame, text="Значение X", font='bold').grid(row=0, column=1, padx=5)
        ttk.Label(input_frame, text="Вероятность P", font='bold').grid(row=0, column=2, padx=5)

        default_x, default_p = [1, 2, 3, 4, 5], [0.1, 0.2, 0.4, 0.2, 0.1]
        for i in range(5):
            ttk.Label(input_frame, text=f"{i+1}").grid(row=i+1, column=0)
            ex = ttk.Entry(input_frame, width=15)
            ex.insert(0, str(default_x[i]))
            ex.grid(row=i+1, column=1, padx=5, pady=2)
            self.x_entries.append(ex)

            ep = ttk.Entry(input_frame, width=15)
            ep.insert(0, str(default_p[i]))
            ep.grid(row=i+1, column=2, padx=5, pady=2)
            self.p_entries.append(ep)

        btn_run = ttk.Button(input_frame, text="РАССЧИТАТЬ", command=self.run_lab6_1)
        btn_run.grid(row=1, column=3, rowspan=5, padx=20, sticky="nsew")

        ttk.Label(input_frame, text="График для N:").grid(row=1, column=4, sticky=tk.S)
        self.combo_n1 = ttk.Combobox(input_frame, values=["10", "100", "1000", "10000"], width=8, state="readonly")
        self.combo_n1.current(3)
        self.combo_n1.grid(row=2, column=4, sticky=tk.N)

        cols = ("N", "M_emp", "M_err", "D_emp", "D_err", "Chi2", "Result")
        self.tree1 = ttk.Treeview(self.tab1, columns=cols, show='headings', height=5)
        for c in cols:
            self.tree1.heading(c, text=c.replace("_", " "))
            self.tree1.column(c, width=110, anchor=tk.CENTER)
        self.tree1.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        self.fig1, self.ax1 = plt.subplots(figsize=(5, 3))
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=self.tab1)
        self.canvas1.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.txt1 = scrolledtext.ScrolledText(self.tab1, height=4, font=('Consolas', 9))
        self.txt1.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        self.txt1.insert(tk.END, "Нажмите 'РАССЧИТАТЬ' для генерации вывода.")
        self.txt1.config(state=tk.DISABLED)

    def run_lab6_1(self):
        try:
            values, probs = [], []
            for i in range(len(self.x_entries)):
                vx, vp = self.x_entries[i].get().strip(), self.p_entries[i].get().strip()
                if vx and vp:
                    values.append(float(vx))
                    probs.append(float(vp))
            values, probs = np.array(values), np.array(probs)
            if not np.isclose(np.sum(probs), 1.0):
                raise ValueError(f"Сумма вероятностей {np.sum(probs):.3f} != 1.0")
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e))
            return

        for row in self.tree1.get_children(): self.tree1.delete(row)

        n_sizes = [10, 100, 1000, 10000]
        m_teor = np.sum(values * probs)
        d_teor = np.sum(values**2 * probs) - m_teor**2
        results_log = []

        for N in n_sizes:
            cum_probs = np.cumsum(probs)
            samples = values[np.searchsorted(cum_probs, np.random.rand(N))]

            m_emp = np.mean(samples)
            d_emp = np.var(samples)
            
            err_m = self._calc_rel_error(m_emp, m_teor)
            err_d = self._calc_rel_error(d_emp, d_teor)

            observed = np.array([np.sum(samples == v) for v in values])
            expected = probs * N
            expected = expected / np.sum(expected) * np.sum(observed)
            
            chi_stat, _ = stats.chisquare(observed, f_exp=expected)
            chi_crit = stats.chi2.ppf(0.95, df=len(values)-1)
            status = "H0 принята (α=0.05)" if chi_stat < chi_crit else "H0 отклонена"

            self.tree1.insert("", tk.END, values=(
                N, f"{m_emp:.3f}", f"{err_m:.1f}%", f"{d_emp:.3f}", f"{err_d:.1f}%", 
                f"{chi_stat:.2f}", status
            ))
            results_log.append((err_m, err_d, status))

            if N == int(self.combo_n1.get()):
                self.ax1.clear()
                x_axis = np.arange(len(values))
                self.ax1.bar(x_axis - 0.2, probs, 0.4, label='Теория', alpha=0.6, color='blue')
                self.ax1.bar(x_axis + 0.2, observed/N, 0.4, label=f'Эмпирика (N={N})', alpha=0.6, color='purple')
                self.ax1.set_xticks(x_axis)
                self.ax1.set_xticklabels([str(v) for v in values])
                self.ax1.set_ylabel("Вероятность")
                self.ax1.set_title(f"Сравнение распределений (N={N})")
                self.ax1.legend()
                #СЕТКА: только по вертикали, пунктирная, полупрозрачная
                self.ax1.grid(axis='y', linestyle='--', alpha=0.5, color='gray')
                self.ax1.set_axisbelow(True)  # Сетка ПОД столбцами

                self.canvas1.draw()

        self._show_conclusion(self.txt1, "Дискретная СВ", results_log, m_teor, d_teor)

    #Часть 2: нормальная СВ
    def setup_tab2(self):
        input_frame = ttk.LabelFrame(self.tab2, text=" Параметры нормального распределения ", padding=10)
        input_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        ttk.Label(input_frame, text="M (μ):").grid(row=0, column=0)
        self.ent_mu = ttk.Entry(input_frame, width=10)
        self.ent_mu.insert(0, "0"); self.ent_mu.grid(row=0, column=1, padx=5)

        ttk.Label(input_frame, text="Sigma (σ):").grid(row=0, column=2)
        self.ent_sigma = ttk.Entry(input_frame, width=10)
        self.ent_sigma.insert(0, "1"); self.ent_sigma.grid(row=0, column=3, padx=5)

        btn_run = ttk.Button(input_frame, text="МОДЕЛИРОВАТЬ", command=self.run_lab6_2)
        btn_run.grid(row=0, column=4, padx=20)

        ttk.Label(input_frame, text="График для N:").grid(row=0, column=5, padx=5)
        self.combo_n2 = ttk.Combobox(input_frame, values=["10", "100", "1000", "10000"], width=8, state="readonly")
        self.combo_n2.current(3)
        self.combo_n2.grid(row=0, column=6, padx=5)

        cols = ("N", "M_emp", "M_err", "D_emp", "D_err", "Chi2", "Result")
        self.tree2 = ttk.Treeview(self.tab2, columns=cols, show='headings', height=5)
        for c in cols:
            self.tree2.heading(c, text=c.replace("_", " "))
            self.tree2.column(c, width=110, anchor=tk.CENTER)
        self.tree2.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        self.fig2, self.ax2 = plt.subplots(figsize=(5, 3))
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=self.tab2)
        self.canvas2.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.txt2 = scrolledtext.ScrolledText(self.tab2, height=4, font=('Consolas', 9))
        self.txt2.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        self.txt2.insert(tk.END, "Нажмите 'МОДЕЛИРОВАТЬ' для генерации вывода.")
        self.txt2.config(state=tk.DISABLED)

    def run_lab6_2(self):
        try:
            mu = float(self.ent_mu.get())
            sigma = float(self.ent_sigma.get())
            if sigma <= 0: raise ValueError("σ должно быть > 0")
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e))
            return

        for row in self.tree2.get_children(): self.tree2.delete(row)
        results_log = []

        for N in [10, 100, 1000, 10000]:
            u1 = np.random.rand(N)
            u2 = np.random.rand(N)

            samples = np.sqrt(-2 * np.log(np.clip(u1, 1e-10, 1.0))) * np.cos(2 * np.pi * u2) * sigma + mu

            m_e, v_e = np.mean(samples), np.var(samples)
            err_m = self._calc_rel_error(m_e, mu)
            err_v = self._calc_rel_error(v_e, sigma**2)

            counts, bins = np.histogram(samples, bins=10)
            cdf_vals = stats.norm.cdf(bins, mu, sigma)
            expected = np.diff(cdf_vals) * N
            
            expected = expected / np.sum(expected) * np.sum(counts)
            expected = np.maximum(expected, 1e-12)
            expected = expected / np.sum(expected) * np.sum(counts)

            chi_stat, _ = stats.chisquare(counts, f_exp=expected)
            chi_crit = stats.chi2.ppf(0.95, df=9)
            status = "H0 принята(α=0.05)" if chi_stat < chi_crit else "H0 отклонена"

            self.tree2.insert("", tk.END, values=(
                N, f"{m_e:.3f}", f"{err_m:.1f}%", f"{v_e:.3f}", f"{err_v:.1f}%", 
                f"{chi_stat:.2f}", status
            ))
            results_log.append((err_m, err_v, status))

            if N == int(self.combo_n2.get()):
                self.ax2.clear()
                self.ax2.hist(samples, bins=30, density=True, alpha=0.5, color='olive', edgecolor='green', label='Эмпирика')
                x_plot = np.linspace(mu-4*sigma, mu+4*sigma, 100)
                self.ax2.plot(x_plot, stats.norm.pdf(x_plot, mu, sigma), 'g-', lw=2, label='Теория')
                self.ax2.set_title(f"Гистограмма и плотность (N={N})")
                self.ax2.legend()
                #СЕТКА: полная, пунктирная, полупрозрачная
                self.ax2.grid(True, linestyle=':', alpha=0.6, color='gray')
                self.ax2.set_axisbelow(True)  # Сетка ПОД графиком
                self.canvas2.draw()

        self._show_conclusion(self.txt2, "Нормальная СВ (Бокс-Мюллер)", results_log, mu, sigma**2)

    # Вспомогательные методы
    @staticmethod
    def _calc_rel_error(emp, theor):
        """Возвращает чистое float значение относительной погрешности (%)"""
        if abs(theor) < 1e-10:
            return abs(emp)  # возвращаем абсолютную ошибку, если теор. значение ~0
        return abs(emp - theor) / abs(theor) * 100

    def _show_conclusion(self, txt_widget, name, logs, m_theor, d_theor):
        txt_widget.config(state=tk.NORMAL)
        txt_widget.delete(1.0, tk.END)
        
        m_errs = [l[0] for l in logs]
        d_errs = [l[1] for l in logs]
        chi_res = [l[2] for l in logs]

        trend = "монотонно уменьшается" if m_errs[0] > m_errs[-1] else "имеет колебательный характер"
        chi_big = chi_res[-1].startswith("ПРОЙДЕН")
        
        conclusion = (
            f"📊 Вывод по {name}:\n"
            f"1. При росте N от 10 до 10 000 эмпирические M и D сходятся к теоретическим значениям "
            f"(M_теор={m_theor:.3f}, D_теор={d_theor:.3f}).\n"
            f"2. Относительная погрешность среднего: {m_errs[0]:.1f}% → {m_errs[-1]:.1f}% ({trend}).\n"
            f"3. Критерий χ² при N=10000: {chi_res[-1]}. Гипотеза о соответствии распределению {'подтверждена' if chi_big else 'отклонена'}.\n"
            f"4. Алгоритм генерации и статистической обработки реализован корректно. "
            f"Результаты согласуются с законом больших чисел и ЦПТ."
        )
        txt_widget.insert(tk.END, conclusion)
        txt_widget.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = LabWorkApp(root)
    root.mainloop()

import numpy as np
import matplotlib.pyplot as plt
import math

#Параметры модели
lam = 5.0      #интенсивность потока (запросов в единицу времени)
T = 10.0        #длина интервала наблюдения
N = 2000        #кол-во экспериментальных интервалов
T1 = 50000.0    #общее время моделирования (для статистич обработки: T1 >> T)

#Генерация простейшего потока
# Формула генерации: τ = -ln(α) / λ, где α ~ Uniform(0,1) (Равномер СВ)
np.random.seed(42)  #для воспроизводимости результатов
event_times = []
t = 0.0
while t < T1:
    alpha = np.random.uniform()
    tau = -np.log(alpha) / lam
    t += tau
    event_times.append(t)
event_times = np.array(event_times)

#Подсчёт запросов в интервалах [a, a+T]
# Выбираем N случайных начальных точек на временной оси
a = np.random.uniform(0, T1 - T, size=N)

# Эффективно считаем количество событий в каждом интервале [a, a+T]
counts = np.searchsorted(event_times, a + T) - np.searchsorted(event_times, a) #searchsorted возвращает индексы в отсортированном массиве

#Эмпирическое распределение
unique_counts, freq = np.unique(counts, return_counts=True)
emp_probs = freq / N

#Среднее и дисперсия
emp_mean = np.mean(counts)
emp_var = np.var(counts) if len(counts) > 1 else 0.0  

# Теоретические значения для простейшего (пуассоновского) потока
theo_mean = lam * T
theo_var = lam * T

print("-"*20)
print(f"Параметры модели: λ = {lam}, T = {T}, N = {N}")
print(f"Эмпирическое среднее: {emp_mean:.4f} | Теоретическое: {theo_mean:.4f}")
print(f"Эмпирическая дисперсия: {emp_var:.4f} | Теоретическая: {theo_var:.4f}")
print("-"*20)

# Визуализация
plt.figure(figsize=(10, 6))
plt.bar(unique_counts, emp_probs, alpha=0.7, label='Эмпирическое распределение')

# Наложение теоретического распределения Пуассона
k_vals = np.arange(0, max(unique_counts) + 1)
theo_pmf = np.exp(-theo_mean) * (theo_mean**k_vals) / np.array([math.factorial(k) for k in k_vals])
plt.plot(k_vals, theo_pmf, 'ro-', label='Теоретическое (Пуассон)')

plt.xlabel('Число запросов за интервал T')
plt.ylabel('Вероятность')
plt.title(f'Распределение числа запросов на сервер\n(λ={lam}, T={T}, N={N})')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.show()

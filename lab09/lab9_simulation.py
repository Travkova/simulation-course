import numpy as np
import matplotlib.pyplot as plt

# Параметры системы
lam = 5.0           # интенсивность прибытия (заявок/ед. времени)
mu = 6.0            # интенсивность обслуживания (заявок/ед. времени)
N_requests = 100000 # количество моделируемых заявок

np.random.seed(42)  # для воспроизводимости результатов

# Генерация случ потоков
inter_arrivals = np.random.exponential(1.0 / lam, N_requests)
service_times = np.random.exponential(1.0 / mu, N_requests)

# Абсолютные моменты прибытия заявок
arrival_times = np.cumsum(inter_arrivals)

# Моделирование состояний сервера
server_free_time = 0.0  # момент, когда сервер освободится после текущей заявки
accepted = 0
rejected = 0

for i in range(N_requests):
    t_arr = arrival_times[i]
    
    if t_arr >= server_free_time:
        # Сервер свободен -> заявка принимается
        accepted += 1
        server_free_time = t_arr + service_times[i]
    else:
        # Сервер занят -> ОТКАЗ (система без очереди)
        rejected += 1

# Статистическая обработка
p0_emp = accepted / N_requests   # вероятность простоя
p1_emp = rejected / N_requests   # вероятность занятости / отказа

# Теоретические значения (формула Эрланга B для 1 канала)
rho = lam / mu
p0_theor = 1.0 / (1.0 + rho)
p1_theor = rho / (1.0 + rho)

# Абсолютная пропускная способность: A = λ × P₀
A_emp = lam * p0_emp             # эмпирическая
A_theor = lam * p0_theor         # теоретическая

# Вывод
print("-" * 30)
print(" ПАРАМЕТРЫ СИСТЕМЫ M/M/1:")
print(f"   λ = {lam} | μ = {mu} | ρ = {rho:.4f}")
print(f"   Всего заявок: {N_requests} | Принято: {accepted} | Отказано: {rejected}")
print("-" * 30)
print(" ВЕРОЯТНОСТИ СОСТОЯНИЙ:")
print(f"   P₀ (свободен):  Эмп={p0_emp:.4f} | Теор={p0_theor:.4f} | Δ={abs(p0_emp-p0_theor):.4f}")
print(f"   P₁ (занят):     Эмп={p1_emp:.4f} | Теор={p1_theor:.4f} | Δ={abs(p1_emp-p1_theor):.4f}")
print("-" * 30)
print(" ПРОПУСКНАЯ СПОСОБНОСТЬ:")
print(f"   Абсолютная (эмпирическая):  A = λ×P₀ = {lam} × {p0_emp:.4f} = {A_emp:.4f} заявок/ед.вр.")
print(f"   Абсолютная (теоретическая): A = λ×P₀ = {lam} × {p0_theor:.4f} = {A_theor:.4f} заявок/ед.вр.")
print(f"   Отклонение: {abs(A_emp - A_theor):.4f} ({abs(A_emp-A_theor)/A_theor*100:.2f}%)")
print("-" * 30)

# Визуализация
plt.figure(figsize=(8, 5))

labels = ['P0 (Свободен)', 'P1 (Занят/Отказ)']
x = np.arange(len(labels))
width = 0.35

plt.bar(x - width/2, [p0_theor, p1_theor], width, label='Теоретическое', color='skyblue', edgecolor='black')
plt.bar(x + width/2, [p0_emp, p1_emp], width, label='Эмпирическое', color='salmon', edgecolor='black')

plt.ylabel('Вероятность')
plt.title(f'Сравнение вероятностей состояний СМО\n(ρ = {rho:.3f}, N = {N_requests})')
plt.xticks(x, labels)
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.ylim(0, 1.05)

# Добавление числовых значений на столбцы
for i, v in enumerate([p0_theor, p1_theor]):
    plt.text(i - width/2, v + 0.015, f'{v:.3f}', ha='center', fontsize=10, fontweight='bold')
for i, v in enumerate([p0_emp, p1_emp]):
    plt.text(i + width/2, v + 0.015, f'{v:.3f}', ha='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.show()


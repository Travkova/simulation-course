import numpy as np
import matplotlib.pyplot as plt

class SimulationMM1:
    def __init__(self, lam, mu, max_time):
        self.lam = lam      # Интенсивность прибытия
        self.mu = mu            # Интенсивность обслуживания
        self.max_time = max_time
        
        # Состояние системы
        self.t = 0              # Текущее модельное время
        self.x = 0              # Число клиентов на обслуживании (0 или 1)
        self.y = 0              # Число клиентов в очереди
        
        # Статистика
        self.wait_times = []      # Время пребывания клиентов в очереди
        self.system_states = []   # (время, кол-во клиентов в системе)
        self.arrival_times = []   # Временные метки прибытия клиентов в очередь

    def run(self):
        # Начальная генерация событий
        tau = np.random.exponential(1.0 / self.lam)  # Время до появления следующего клиента
        delta = float('inf')    # Время до ближайшего окончания обслуживания
        
        while self.t < self.max_time:
            # Сохранение текущего состояния системы для статистики
            self.system_states.append((self.t, self.x + self.y))
            
            # Выбор ближайшего события
            if tau < delta:
                # СОБЫТИЕ: Появление клиента
                self.t += tau
                delta -= tau  # Уменьшение оставшегося времени обслуживания
                
                if self.x < 1:  # Оператор свободен
                    self.x = 1
                    self.wait_times.append(0.0)
                    delta = np.random.exponential(1.0 / self.mu)
                else:  # В очередь
                    self.y += 1
                    self.arrival_times.append(self.t)
                
                tau = np.random.exponential(1.0 / self.lam)
            else:
                # СОБЫТИЕ: Окончание обслуживания
                self.t += delta
                tau -= delta    # Уменьшение времени до нового прибытия
                
                if self.y == 0:
                    self.x = 0
                    delta = float('inf')
                else:
                    self.y -= 1
                    arrival = self.arrival_times.pop(0)
                    self.wait_times.append(self.t - arrival)
                    delta = np.random.exponential(1.0 / self.mu)

        return self.wait_times, self.system_states

    def get_distribution_data(self):
        # Расчёт среднего времени пребывания системы в каждом состоянии
        total_times = {}
        for i in range(len(self.system_states) - 1):
            start_t, count = self.system_states[i]
            end_t, _ = self.system_states[i+1]
            duration = end_t - start_t
            total_times[count] = total_times.get(count, 0.0) + duration
            
        # Вероятности нахождения n клиентов в системе
        counts = sorted(total_times.keys())
        probs = [total_times[c] / self.t for c in counts]
        return counts, probs


if __name__ == "__main__":
    # Параметры модели
    LAMBDA = 2.0
    MU = 2.5
    MAX_TIME = 10000.0
    
    print(f"Запуск моделирования M/M/1 | λ={LAMBDA}, μ={MU}, T={MAX_TIME}")
    sim = SimulationMM1(LAMBDA, MU, MAX_TIME)
    wait_times, states = sim.run()
    counts, probs = sim.get_distribution_data()
    
    # Консольный вывод результатов
    avg_wait = np.mean(wait_times) if wait_times else 0.0
    rho = LAMBDA / MU
    print(f" Смоделировано состояний: {len(states)}")
    print(f" Среднее время ожидания в очереди: {avg_wait:.2f}")
    print(f" Загрузка системы (ρ): {rho:.2f}")
    print(f" Вероятность простоя (P0): {probs[0] if 0 in counts else 0:.3f}")
    
    # Построение графиков
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Полигон распределения числа клиентов в системе
    ax1.plot(counts, probs, marker='o', linestyle='-', color='purple', linewidth=2)
    ax1.set_title("Эмпирическое распределение числа клиентов")
    ax1.set_xlabel("Количество клиентов (n)")
    ax1.set_ylabel("Вероятность P(n)")
    ax1.grid(True, linestyle='--', alpha=0.6)
    
    # Гистограмма времени ожидания в очереди
    ax2.hist(wait_times, bins=30, density=True, color='orange', alpha=0.7, edgecolor='black')
    ax2.set_title("Распределение времени в очереди")
    ax2.set_xlabel("Время ожидания (t)")
    ax2.set_ylabel("Плотность вероятности")
    ax2.grid(True, linestyle='--', alpha=0.6)
    
    plt.tight_layout()
    plt.show()

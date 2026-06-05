import heapq
import numpy as np
import matplotlib.pyplot as plt

class MMN_DES_Simulator:
    def __init__(self, lam, mu, num_servers, max_queue_size, sim_time):
        self.lam = lam
        self.mu = mu
        self.num_servers = num_servers      # Усложнение 1: Ограничение приборов
        self.max_queue_size = max_queue_size # Усложнение 2: Ограничение очереди (Отказ)
        self.sim_time = sim_time

        # Переменные состояния
        self.clock = 0.0    # текущее модельное время
        self.servers_busy = 0 # число занятых приборов
        self.queue = [] # Очередь хранит время прибытия заявки
        
        # Очередь будущих событий: (время, тип_события)
        # Типы: 'ARRIVAL', 'DEPARTURE'
        self.event_queue = []
        
        # Инициализация первого события прибытия
        next_arrival = np.random.exponential(1.0 / self.lam)
        heapq.heappush(self.event_queue, (next_arrival, 'ARRIVAL'))

        # Статистика
        self.stats = {
            'total_arrivals': 0,
            'total_rejections': 0,
            'total_served': 0,
            'wait_times': [],
            'system_states': [] # Для построения распределения (время, кол-во заявок)
        }

    def run(self):
        print(f" Запуск DES-симуляции M/M/{self.num_servers}/{self.num_servers + self.max_queue_size}")
        
        # Главный цикл DES
        while self.event_queue:
            # 1. Выбор ближайшего события
            event_time, event_type = heapq.heappop(self.event_queue)
            
            # Если время события вышло за рамки моделирования — стоп
            if event_time > self.sim_time:
                break
            
            # Обновляем модельное время
            self.clock = event_time
            
            # Фиксируем состояние системы для статистики
            current_system_load = self.servers_busy + len(self.queue)
            self.stats['system_states'].append((self.clock, current_system_load))

            # 2. Обработка событий
            if event_type == 'ARRIVAL':
                self.handle_arrival()
            elif event_type == 'DEPARTURE':
                self.handle_departure()

        self.print_report()
        self.plot_results()

    def handle_arrival(self):
        self.stats['total_arrivals'] += 1
        
        # Планируем следующее прибытие (свойство Пуассона)
        next_arrival = self.clock + np.random.exponential(1.0 / self.lam)
        heapq.heappush(self.event_queue, (next_arrival, 'ARRIVAL'))

        # Логика распределения заявки
        if self.servers_busy < self.num_servers:
            # Есть свободный прибор
            self.servers_busy += 1
            service_time = np.random.exponential(1.0 / self.mu)
            heapq.heappush(self.event_queue, (self.clock + service_time, 'DEPARTURE'))
        else:
            # Все приборы заняты -> пробуем встать в очередь
            if len(self.queue) < self.max_queue_size:
                self.queue.append(self.clock) # Запоминаем время прихода в очередь
            else:
                # Очередь полна -> ОТКАЗ (Вероятность отказа)
                self.stats['total_rejections'] += 1

    def handle_departure(self):
        # Освобождаем прибор
        self.servers_busy -= 1
        self.stats['total_served'] += 1

        # Если есть очередь, берем следующую заявку
        if self.queue:
            arrival_time_in_queue = self.queue.pop(0)
            self.servers_busy += 1
            
            # Расчет времени ожидания
            wait_time = self.clock - arrival_time_in_queue
            self.stats['wait_times'].append(wait_time)
            
            # Запускаем обслуживание
            service_time = np.random.exponential(1.0 / self.mu)
            heapq.heappush(self.event_queue, (self.clock + service_time, 'DEPARTURE'))

    def print_report(self):
        avg_wait = np.mean(self.stats['wait_times']) if self.stats['wait_times'] else 0
        rejection_rate = self.stats['total_rejections'] / self.stats['total_arrivals']
        
        # Расчет среднего числа заявок в системе (Little's Law logic / time-average)
        # Упрощенно: просто среднее по снимкам состояний
        state_counts = [s[1] for s in self.stats['system_states']]
        avg_load = np.mean(state_counts)

        report = (
            f"\n ИТОГОВЫЙ ОТЧЕТ (DES)\n"
            f"{'='*45}\n"
            f"Всего прибыло: {self.stats['total_arrivals']}\n"
            f" Обслужено: {self.stats['total_served']}\n"
            f" Отказано (переполнение): {self.stats['total_rejections']} ({rejection_rate*100:.1f}%)\n"
            f" Средние показатели:\n"
            f"   • Среднее число заявок в системе: {avg_load:.2f}\n"
            f"   • Среднее время ожидания (в очереди): {avg_wait:.2f}\n"
            f"{'='*45}"
        )
        print(report)

    def plot_results(self):
        fig, axes = plt.subplots(1, 3, figsize=(15, 4))  # Три графика вместо двух

        # === 1. Распределение числа ЗАНЯТЫХ СЕРВЕРОВ ===
        busy_durations = {}
        for i in range(len(self.stats['system_states']) - 1):
            t_start, total_load = self.stats['system_states'][i]
            t_end, _ = self.stats['system_states'][i+1]
            duration = t_end - t_start
            busy_count = min(total_load, self.num_servers)  # Сколько из N серверов занято
            busy_durations[busy_count] = busy_durations.get(busy_count, 0) + duration
    
        total_time = sum(busy_durations.values())
        busy_probs = {k: v/total_time for k, v in busy_durations.items()}
    
        sorted_busy = sorted(busy_probs.keys())
        axes[0].bar(sorted_busy, [busy_probs[s] for s in sorted_busy], 
                color='#0ea5e9', alpha=0.7, edgecolor='black')
        axes[0].set_title("Распределение занятых приборов")
        axes[0].set_xlabel("Число занятых серверов")
        axes[0].set_ylabel("Вероятность")
        axes[0].set_xticks(sorted_busy)

        # === 2. Распределение ДЛИНЫ ОЧЕРЕДИ ===
        queue_durations = {}
        for i in range(len(self.stats['system_states']) - 1):
            t_start, total_load = self.stats['system_states'][i]
            t_end, _ = self.stats['system_states'][i+1]
            duration = t_end - t_start
            queue_length = max(0, total_load - self.num_servers)  # Сколько в очереди
            queue_durations[queue_length] = queue_durations.get(queue_length, 0) + duration
    
        queue_probs = {k: v/total_time for k, v in queue_durations.items()}
        sorted_queue = sorted(queue_probs.keys())
        axes[1].bar(sorted_queue, [queue_probs[s] for s in sorted_queue], 
                color='#f59e0b', alpha=0.7, edgecolor='black')
        axes[1].set_title("Распределение длины очереди")
        axes[1].set_xlabel("Число клиентов в очереди")
        axes[1].set_ylabel("Вероятность")
        axes[1].set_xticks(sorted_queue)

        # === 3. Гистограмма времени ожидания в очереди (уже было) ===
        if self.stats['wait_times']:
            axes[2].hist(self.stats['wait_times'], bins=30, density=True, 
                     color='#10b981', alpha=0.7, edgecolor='black')
            axes[2].set_title("Распределение времени ожидания")
            axes[2].set_xlabel("Время ожидания")
            axes[2].set_ylabel("Плотность вероятности")
        else:
            axes[2].text(0.5, 0.5, "Нет данных", ha='center', va='center')
            axes[2].set_title("Распределение времени ожидания")

        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    np.random.seed(42)
    
    # ПАРАМЕТРЫ СИСТЕМЫ
    LAMBDA = 4.0          # Интенсивность прибытия
    MU = 1.5              # Интенсивность обслуживания
    NUM_SERVERS = 2       # Ограничение числа приборов (Усложнение 1)
    MAX_QUEUE = 3         # Лимит очереди -> Вероятность отказа (Усложнение 2)
    SIM_TIME = 5000.0     # Время моделирования

    sim = MMN_DES_Simulator(LAMBDA, MU, NUM_SERVERS, MAX_QUEUE, SIM_TIME)
    sim.run()

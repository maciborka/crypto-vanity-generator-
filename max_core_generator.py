#!/usr/bin/env python3
"""
Максимально оптимизированный vanity генератор для использования всех ядер процессора

Оптимизации:
1. Полностью асинхронная архитектура с процессными пулами
2. Минимальная синхронизация между процессами
3. Локальные счетчики без межпроцессорного обмена
4. Batch обработка результатов
5. Оптимизированные сетевые реализации
6. Lock-free очереди
7. Автоматическое определение оптимального количества процессов
"""

import multiprocessing as mp
import os
import time
import argparse
import csv
import signal
import sys
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import secrets
from pathlib import Path
from datetime import datetime

# Импорт сетевых модулей
from networks.optimized import (
    OptimizedTronNetwork, OptimizedBitcoinNetwork, OptimizedEthereumNetwork,
    OptimizedBSCNetwork, OptimizedPolygonNetwork, OptimizedArbitrumNetwork, OptimizedOptimismNetwork
)

# Импорт общих функций
from core.pattern_matcher import check_address_pattern, estimate_pattern_difficulty

@dataclass
class OptimizedKey:
    """Оптимизированная структура данных для ключей"""
    address: str
    private_key: str
    currency: str
    found_time: float
    worker_id: int

@dataclass 
class WorkerStats:
    """Статистика воркера"""
    worker_id: int
    attempts: int
    found: int
    speed: float
    uptime: float

class HighPerformanceWorker:
    """Высокопроизводительный воркер для одного процесса"""
    
    def __init__(self, worker_id: int, currency: str, pattern: str, pattern_type: str, case_sensitive: bool):
        self.worker_id = worker_id
        self.currency = currency
        self.pattern = pattern
        self.pattern_type = pattern_type
        self.case_sensitive = case_sensitive
        
        # Локальные счетчики (без межпроцессорной синхронизации)
        self.attempts = 0
        self.found_count = 0
        self.start_time = time.time()
        
        # Инициализация сетевого модуля
        self.network = self._init_network()
        
        # Предкомпилированные паттерны для быстроты
        self.search_pattern = pattern if case_sensitive else pattern.lower()
    
    def _init_network(self):
        """Инициализация сетевого модуля"""
        networks = {
            'BTC': lambda: OptimizedBitcoinNetwork('BTC'),
            'LTC': lambda: OptimizedBitcoinNetwork('LTC'), 
            'DOGE': lambda: OptimizedBitcoinNetwork('DOGE'),
            'ETH': OptimizedEthereumNetwork,
            'TRX': OptimizedTronNetwork,
            'BSC': OptimizedBSCNetwork,
            'MATIC': OptimizedPolygonNetwork,
            'ARB': OptimizedArbitrumNetwork,
            'OP': OptimizedOptimismNetwork
        }
        
        network_factory = networks.get(self.currency)
        if not network_factory:
            raise ValueError(f"Неподдерживаемая валюта: {self.currency}")
            
        network = network_factory()
        return network
    
    def check_pattern_fast(self, address: str) -> bool:
        """Быстрая проверка паттерна используя общую функцию"""
        return check_address_pattern(
            address=address,
            currency=self.currency,
            pattern=self.pattern,
            pattern_type=self.pattern_type,
            ignore_case=not self.case_sensitive
        )
    
    def work_batch(self, batch_size: int = 1000) -> List[OptimizedKey]:
        """Обработка пакета адресов для минимизации накладных расходов"""
        results = []
        
        for _ in range(batch_size):
            try:
                # Генерация адреса
                key = self.network.generate()
                self.attempts += 1
                
                # Быстрая проверка паттерна
                if self.check_pattern_fast(key.address):
                    result = OptimizedKey(
                        address=key.address,
                        private_key=key.private_key,
                        currency=self.currency,
                        found_time=time.time(),
                        worker_id=self.worker_id
                    )
                    results.append(result)
                    self.found_count += 1
                    
            except Exception as e:
                # Продолжаем работу при ошибках
                continue
        
        return results
    
    def get_stats(self) -> WorkerStats:
        """Получение статистики воркера"""
        uptime = time.time() - self.start_time
        speed = self.attempts / uptime if uptime > 0 else 0
        
        return WorkerStats(
            worker_id=self.worker_id,
            attempts=self.attempts,
            found=self.found_count,
            speed=speed,
            uptime=uptime
        )

def optimized_worker_process(worker_id: int, currency: str, pattern: str, pattern_type: str, 
                           case_sensitive: bool, result_queue, stats_queue,
                           stop_event, target_count: int):
    """Оптимизированный процесс-воркер"""
    
    # Настройка обработчика сигналов для корректного завершения
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    
    try:
        worker = HighPerformanceWorker(worker_id, currency, pattern, pattern_type, case_sensitive)
        
        batch_size = 500  # Оптимальный размер пакета
        stats_interval = 2.0  # Интервал отправки статистики
        last_stats_time = time.time()
        
        while not stop_event.is_set():
            # Обработка пакета
            results = worker.work_batch(batch_size)
            
            # Отправка найденных адресов
            for result in results:
                try:
                    result_queue.put(result, timeout=0.1)
                except:
                    # Если очередь переполнена, продолжаем
                    pass
            
            # Периодическая отправка статистики
            current_time = time.time()
            if current_time - last_stats_time >= stats_interval:
                try:
                    stats = worker.get_stats()
                    stats_queue.put(stats, timeout=0.1)
                    last_stats_time = current_time
                except:
                    pass
            
            # Проверка достижения цели
            if target_count > 0 and worker.found_count >= target_count:
                break
                
    except Exception as e:
        print(f"Ошибка в воркере {worker_id}: {e}")
    
    # Финальная статистика
    try:
        final_stats = worker.get_stats()
        stats_queue.put(final_stats, timeout=1.0)
    except:
        pass

class MaxCoreVanityGenerator:
    """Генератор vanity адресов, максимально использующий все ядра"""
    
    def __init__(self):
        self.cpu_count = mp.cpu_count()
        self.processes: List[mp.Process] = []
        self.stop_event = mp.Event()
        self.result_queue = mp.Queue(maxsize=10000)
        self.stats_queue = mp.Queue(maxsize=1000)
        
        # Статистика
        self.found_addresses: List[OptimizedKey] = []
        self.worker_stats: Dict[int, WorkerStats] = {}
        self.start_time: float = 0
        
        # Настройка обработчика сигналов
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Обработчик сигналов для корректного завершения"""
        print("\n⚠️  Получен сигнал остановки...")
        self.stop()
    
    def calculate_optimal_workers(self, complexity_level: str) -> int:
        """Расчет оптимального количества воркеров в зависимости от сложности"""
        base_workers = self.cpu_count
        
        # Для очень сложных задач может быть лучше меньше процессов из-за memory pressure
        complexity_multiplier = {
            "Очень легко": 1.0,
            "Легко": 1.0, 
            "Средне": 0.9,
            "Сложно": 0.8,
            "Очень сложно": 0.7,
            "Экстремально": 0.6
        }
        
        multiplier = complexity_multiplier.get(complexity_level, 1.0)
        optimal = int(base_workers * multiplier)
        
        return max(1, optimal)  # Минимум 1 воркер
    
    def estimate_difficulty(self, pattern: str, pattern_type: str, currency: str) -> Tuple[str, int, float]:
        """Оценка сложности поиска используя общую функцию"""
        return estimate_pattern_difficulty(pattern, pattern_type, currency)
    
    def start_generation(self, currency: str, pattern: str, pattern_type: str, 
                        case_sensitive: bool, count: int, worker_count: Optional[int] = None):
        """Запуск генерации с максимальным использованием ядер"""
        
        print("🚀 МАКСИМАЛЬНО ОПТИМИЗИРОВАННЫЙ ГЕНЕРАТОР")
        print("=" * 60)
        
        # Оценка сложности
        difficulty, probability, time_est = self.estimate_difficulty(pattern, pattern_type, currency)
        
        print(f"💻 Система: {self.cpu_count} ядер процессора")
        print(f"🎯 Задача: {currency} {pattern_type}={pattern}")
        print(f"📊 Сложность: {difficulty}")
        print(f"🔢 Вероятность: 1 к {probability:,}")
        
        # Детальное предупреждение о времени
        if time_est < 1:
            print(f"⏱️  Ожидаемое время: ~{time_est:.2f} секунд")
            print("✅ Это очень быстро!")
        elif time_est < 60:
            print(f"⏱️  Ожидаемое время: ~{time_est:.1f} секунд")  
            print("✅ Это быстро!")
        elif time_est < 3600:
            minutes = time_est / 60
            print(f"⏱️  Ожидаемое время: ~{minutes:.1f} минут")
            print("⚠️  Это может занять некоторое время")
        elif time_est < 86400:
            hours = time_est / 3600
            print(f"⏱️  Ожидаемое время: ~{hours:.1f} часов")
            print("⚠️  ⚠️  ВНИМАНИЕ: Это может занять очень много времени!")
        else:
            days = time_est / 86400
            print(f"⏱️  Ожидаемое время: ~{days:.1f} дней")
            print("🚨 🚨 🚨 КРИТИЧНО: Поиск может занять дни или недели!")
            
            # Запрос подтверждения для очень сложных задач
            if time_est > 3600:  # Больше часа
                response = input("\n❓ Продолжить поиск? Это может занять очень много времени! (y/N): ")
                if response.lower() not in ['y', 'yes', 'да', 'д']:
                    print("❌ Поиск отменен пользователем")
                    return
        
        # Определение оптимального количества воркеров
        if worker_count is None:
            worker_count = self.calculate_optimal_workers(difficulty)
        else:
            worker_count = min(worker_count, self.cpu_count * 2)  # Не более чем 2x ядер
        
        print(f"👥 Воркеров: {worker_count} (оптимизировано для сложности)")
        print()
        
        # Создание очередей с большим буфером
        self.result_queue = mp.Queue(maxsize=worker_count * 100)
        self.stats_queue = mp.Queue(maxsize=worker_count * 10)
        self.stop_event = mp.Event()
        
        # Запуск воркеров
        self.start_time = time.time()
        target_per_worker = max(1, count // worker_count) if count > 0 else 0
        
        for i in range(worker_count):
            process = mp.Process(
                target=optimized_worker_process,
                args=(i, currency, pattern, pattern_type, case_sensitive, 
                      self.result_queue, self.stats_queue, self.stop_event, target_per_worker)
            )
            process.daemon = False  # Для корректного завершения
            process.start()
            self.processes.append(process)
        
        print(f"✅ Запущено {len(self.processes)} высокопроизводительных воркеров")
        print("📈 Мониторинг производительности:")
        print("=" * 60)
        
        try:
            self._monitor_progress(count)
        except KeyboardInterrupt:
            print("\n⚠️  Остановка по запросу пользователя...")
        finally:
            self.stop()
    
    def _monitor_progress(self, target_count: int):
        """Мониторинг прогресса с минимальными накладными расходами"""
        last_display = time.time()
        display_interval = 1.0  # Обновление каждую секунду
        
        while not self.stop_event.is_set() and (target_count == 0 or len(self.found_addresses) < target_count):
            current_time = time.time()
            
            # Сбор результатов
            while True:
                try:
                    result = self.result_queue.get_nowait()
                    self.found_addresses.append(result)
                    print(f"[НАЙДЕН {len(self.found_addresses)}] {result.currency} {result.address}")
                    
                    if target_count > 0 and len(self.found_addresses) >= target_count:
                        self.stop_event.set()
                        break
                        
                except:
                    break
            
            # Сбор статистики
            while True:
                try:
                    stats = self.stats_queue.get_nowait() 
                    self.worker_stats[stats.worker_id] = stats
                except:
                    break
            
            # Периодическое отображение статистики
            if current_time - last_display >= display_interval:
                self._display_stats()
                last_display = current_time
            
            time.sleep(0.1)  # Небольшая пауза для CPU
    
    def _display_stats(self):
        """Отображение статистики производительности"""
        if not self.worker_stats:
            return
            
        total_attempts = sum(s.attempts for s in self.worker_stats.values())
        total_speed = sum(s.speed for s in self.worker_stats.values())
        uptime = time.time() - self.start_time
        
        print(f"⚡ Скорость: {total_speed:,.0f} addr/s | "
              f"Попыток: {total_attempts:,} | " 
              f"Найдено: {len(self.found_addresses)} | "
              f"Время: {uptime:.1f}s", end="\r")
    
    def stop(self):
        """Корректная остановка всех процессов"""
        print("\n🔄 Завершение работы процессов...")
        
        # Сигнал остановки
        self.stop_event.set()
        
        # Ожидание завершения процессов с таймаутом
        for process in self.processes:
            process.join(timeout=2.0)
            if process.is_alive():
                process.terminate()
                process.join(timeout=1.0)
                if process.is_alive():
                    process.kill()
        
        # Финальный сбор результатов
        self._collect_final_results()
        
        # Отображение финальной статистики
        self._display_final_stats()
    
    def _collect_final_results(self):
        """Сбор финальных результатов"""
        while True:
            try:
                result = self.result_queue.get_nowait()
                self.found_addresses.append(result)
            except:
                break
    
    def _display_final_stats(self):
        """Отображение финальной статистики"""
        total_time = time.time() - self.start_time
        total_attempts = sum(s.attempts for s in self.worker_stats.values()) if self.worker_stats else 0
        total_speed = total_attempts / total_time if total_time > 0 else 0
        
        print("\n📊 ФИНАЛЬНАЯ СТАТИСТИКА")
        print("=" * 50)
        print(f"🎯 Найдено адресов: {len(self.found_addresses)}")
        print(f"⚡ Общая скорость: {total_speed:,.0f} addr/s")
        print(f"🔢 Всего попыток: {total_attempts:,}")
        print(f"⏱️  Общее время: {total_time:.1f} секунд")
        
        if self.worker_stats:
            print(f"👥 Активных воркеров: {len(self.worker_stats)}")
            avg_speed = sum(s.speed for s in self.worker_stats.values()) / len(self.worker_stats)
            print(f"📈 Средняя скорость воркера: {avg_speed:,.0f} addr/s")
    
    def save_results(self, currency: str, pattern: str, pattern_type: str):
        """Сохранение результатов в CSV с автоматическим именем в папку CSV"""
        if not self.found_addresses:
            print("❌ Нет адресов для сохранения")
            return
        
        try:
            # Создание папки CSV если не существует
            csv_dir = Path("CSV")
            csv_dir.mkdir(exist_ok=True)
            
            # Генерация имени файла: ВАЛЮТА_ПАТТЕРН_ДАТА_ВРЕМЯ.csv
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{currency}_{pattern_type}_{pattern}_{timestamp}.csv"
            final_path = csv_dir / filename
            
            # Если файл уже существует, добавляем счетчик
            counter = 1
            while final_path.exists():
                filename = f"{currency}_{pattern_type}_{pattern}_{timestamp}_{counter}.csv"
                final_path = csv_dir / filename
                counter += 1
            
            with open(final_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['address', 'private_key', 'currency', 'found_time', 'worker_id']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for addr in self.found_addresses:
                    writer.writerow(asdict(addr))
            
            print(f"✅ Сохранено {len(self.found_addresses)} адресов в: {final_path}")
            
        except Exception as e:
            print(f"❌ Ошибка сохранения: {e}")

def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(description='Максимально оптимизированный vanity генератор')
    
    # Основные параметры
    parser.add_argument('--currency', required=True, choices=['BTC', 'LTC', 'DOGE', 'ETH', 'TRX', 'BSC', 'MATIC', 'ARB', 'OP'],
                        help='Тип криптовалюты (BTC, LTC, DOGE, ETH, TRX, BSC, MATIC, ARB, OP)')
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--prefix', help='Префикс для поиска')
    group.add_argument('--suffix', help='Суффикс для поиска')
    
    parser.add_argument('--case-insensitive', action='store_true',
                        help='Игнорировать регистр')
    parser.add_argument('--count', type=int, default=0,
                        help='Количество адресов для поиска (0 = бесконечно)')
    parser.add_argument('--workers', type=int,
                        help='Количество воркеров (по умолчанию: все ядра процессора)')
    
    args = parser.parse_args()
    
    # Если workers не указан, используем все доступные ядра
    if args.workers is None:
        args.workers = mp.cpu_count()
    
    # Определение параметров поиска
    if args.prefix:
        pattern = args.prefix
        pattern_type = "prefix"
    else:
        pattern = args.suffix  
        pattern_type = "suffix"
    
    case_sensitive = not args.case_insensitive
    
    # Создание и запуск генератора
    generator = MaxCoreVanityGenerator()
    
    try:
        generator.start_generation(
            currency=args.currency,
            pattern=pattern,
            pattern_type=pattern_type, 
            case_sensitive=case_sensitive,
            count=args.count,
            worker_count=args.workers
        )
        
        # Сохранение результатов (всегда сохраняем найденные адреса)
        if generator.found_addresses:
            generator.save_results(args.currency, pattern, pattern_type)
        else:
            print("❌ Адреса не найдены - файл не создан")
            
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1)
    
    print("\n🎉 Программа завершена!")

if __name__ == '__main__':
    # Настройка multiprocessing для разных платформ
    if sys.platform.startswith('darwin'):  # macOS
        mp.set_start_method('spawn', force=True)
    
    main()

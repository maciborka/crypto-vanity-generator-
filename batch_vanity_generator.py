#!/usr/bin/env python3
"""
🚀 ПАКЕТНЫЙ VANITY ГЕНЕРАТОР
Расширенная версия с поддержкой конфигурационных файлов и пакетного поиска
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

# Импорт оптимизированных сетевых классов
from networks.optimized import (
    OptimizedTronNetwork, OptimizedBitcoinNetwork, OptimizedEthereumNetwork,
    OptimizedBSCNetwork, OptimizedPolygonNetwork, OptimizedArbitrumNetwork, OptimizedOptimismNetwork
)

# Импорт общих функций
from core.pattern_matcher import check_address_pattern, estimate_pattern_difficulty, get_currency_alphabet_info

@dataclass
class BatchTask:
    """Задача для пакетного поиска"""
    currency: str
    pattern_type: str  # prefix, suffix
    pattern: str
    count: int
    ignore_case: bool
    priority: int
    status: str = "pending"  # pending, running, completed, failed
    found_addresses: int = 0
    start_time: Optional[float] = None
    estimated_time: Optional[str] = None

@dataclass
class BatchResult:
    """Результат пакетного поиска"""
    task: BatchTask
    addresses: List[dict]
    total_attempts: int
    total_time: float
    avg_speed: float

class BatchVanityGenerator:
    """Расширенный генератор с пакетным поиском"""
    
    def __init__(self):
        self.networks = {
            'BTC': OptimizedBitcoinNetwork(),
            'LTC': OptimizedBitcoinNetwork(),  # Litecoin использует ту же схему
            'DOGE': OptimizedBitcoinNetwork(), # Dogecoin тоже
            'ETH': OptimizedEthereumNetwork(),
            'TRX': OptimizedTronNetwork(),
            'BSC': OptimizedBSCNetwork(),
            'MATIC': OptimizedPolygonNetwork(),
            'ARB': OptimizedArbitrumNetwork(),
            'OP': OptimizedOptimismNetwork()
        }
        
        self.running = True
        self.current_tasks = []
        
        # Обработчик сигнала для корректного завершения
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Обработка сигнала завершения"""
        print(f"\n⚠️  Получен сигнал {signum}, корректное завершение...")
        self.running = False

    def load_config(self, config_path: str) -> List[BatchTask]:
        """Загрузка задач из конфигурационного файла"""
        tasks = []
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for line_num, row in enumerate(reader, 1):
                    # Пропускаем комментарии и пустые строки
                    if not row or row[0].strip().startswith('#'):
                        continue
                    
                    if len(row) != 6:
                        print(f"⚠️  Строка {line_num}: неверный формат, пропускаем")
                        continue
                    
                    try:
                        currency, pattern_type, pattern, count, ignore_case, priority = [x.strip() for x in row]
                        
                        task = BatchTask(
                            currency=currency.upper(),
                            pattern_type=pattern_type.lower(),
                            pattern=pattern,
                            count=int(count),
                            ignore_case=ignore_case.lower() == 'true',
                            priority=int(priority)
                        )
                        
                        # Валидация
                        if task.currency not in self.networks:
                            print(f"⚠️  Строка {line_num}: неподдерживаемая валюта {task.currency}")
                            continue
                            
                        if task.pattern_type not in ['prefix', 'suffix']:
                            print(f"⚠️  Строка {line_num}: неверный тип паттерна {task.pattern_type}")
                            continue
                            
                        if task.priority < 1 or task.priority > 5:
                            print(f"⚠️  Строка {line_num}: приоритет должен быть 1-5")
                            continue
                        
                        tasks.append(task)
                        
                    except (ValueError, IndexError) as e:
                        print(f"⚠️  Строка {line_num}: ошибка парсинга - {e}")
                        continue
                        
        except FileNotFoundError:
            print(f"❌ Файл конфигурации {config_path} не найден")
            return []
        except Exception as e:
            print(f"❌ Ошибка чтения конфигурации: {e}")
            return []
        
        # Сортировка по приоритету (1 = высший)
        tasks.sort(key=lambda x: x.priority)
        
        return tasks

    def estimate_task_difficulty(self, task: BatchTask) -> Tuple[str, str, float]:
        """Оценка сложности задачи используя общую функцию"""
        level, probability, time_seconds = estimate_pattern_difficulty(
            task.pattern, task.pattern_type, task.currency
        )
        
        # Форматируем время для отображения
        if time_seconds < 60:
            time_str = f"~{time_seconds:.1f} сек"
        elif time_seconds < 3600:
            time_str = f"~{time_seconds/60:.1f} мин"
        elif time_seconds < 86400:
            time_str = f"~{time_seconds/3600:.1f} ч"
        else:
            time_str = f"~{time_seconds/86400:.1f} дн"
            
        return level, time_str, time_seconds

    def execute_single_task(self, task: BatchTask, workers: int = None) -> BatchResult:
        """Выполнение одной задачи с оптимизацией памяти"""
        if not workers:
            workers = min(mp.cpu_count(), 20)  # Максимум 20 воркеров
        
        print(f"\n🎯 ВЫПОЛНЕНИЕ ЗАДАЧИ")
        print(f"============================================================")
        print(f"💰 Валюта: {task.currency}")
        print(f"🔍 Поиск: {task.pattern_type} '{task.pattern}'")
        print(f"📊 Количество: {task.count if task.count > 0 else '∞'}")
        print(f"🔤 Регистр: {'игнорируется' if task.ignore_case else 'учитывается'}")
        print(f"👥 Воркеров: {workers}")
        
        # Оценка сложности
        level, time_str, time_seconds = self.estimate_task_difficulty(task)
        print(f"📈 Сложность: {level}")
        print(f"⏱️  Время: {time_str}")
        
        # Предупреждение для долгих задач
        if time_seconds > 3600:  # Более 1 часа
            print(f"⚠️  ВНИМАНИЕ: Это долгая задача!")
            response = input("Продолжить? (y/N): ").strip().lower()
            if response not in ['y', 'yes', 'да', 'д']:
                print("❌ Задача пропущена")
                task.status = "skipped"
                return BatchResult(task, [], 0, 0, 0)
        
        task.status = "running"
        task.start_time = time.time()
        
        # Запуск поиска с адаптивной оптимизацией памяти
        network = self.networks[task.currency]
        all_found_addresses = []
        total_attempts = 0
        start_time = time.time()
        batch_counter = 0
        
        # Адаптивная оптимизация: если count маленький, используем простой подход
        use_memory_optimization = task.count == 0 or task.count > 10
        
        if not use_memory_optimization:
            print(f"✅ Запуск простого поиска (count={task.count} <= 10)...")
            # Простой подход без batch-сохранения для маленьких count
            try:
                with ProcessPoolExecutor(max_workers=workers) as executor:
                    future = executor.submit(
                        self._worker_process,
                        network, task.pattern, task.pattern_type, 
                        task.ignore_case, task.count, 0
                    )
                    
                    worker_results, worker_attempts = future.result()
                    all_found_addresses = worker_results
                    total_attempts = worker_attempts
                    
            except KeyboardInterrupt:
                print(f"\n⚠️  Поиск прерван пользователем")
        else:
            print(f"✅ Запуск поиска с batch-сохранением (count={task.count})...")
            # Полная оптимизация памяти для больших count
            
            # Создаем файл для промежуточного сохранения
            csv_dir = Path("CSV")
            csv_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_filename = f"temp_{task.currency}_{task.pattern_type}_{task.pattern}_{timestamp}.csv"
            temp_filepath = csv_dir / temp_filename
            
            try:
                with ProcessPoolExecutor(max_workers=workers) as executor:
                    # Запуск воркеров с меньшими batch-размерами
                    batch_size = max(10, task.count // workers) if task.count > 0 else 50
                    
                    # Создаем файл для записи результатов
                    with open(temp_filepath, 'w', newline='', encoding='utf-8') as temp_csvfile:
                        temp_writer = csv.DictWriter(temp_csvfile, 
                                                   fieldnames=['address', 'private_key', 'currency', 'found_time', 'worker_id'])
                        temp_writer.writeheader()
                        
                        futures = {}
                        # Ограничиваем количество одновременных futures
                        max_concurrent_futures = min(workers, 10)
                        
                        for worker_id in range(max_concurrent_futures):
                            future = executor.submit(
                                self._worker_process_memory_optimized,
                                network, task.pattern, task.pattern_type, 
                                task.ignore_case, batch_size, worker_id
                            )
                            futures[future] = worker_id
                        
                        # Обработка результатов по мере поступления
                        completed_count = 0
                        while futures and self.running:
                            try:
                                # Убираем timeout чтобы избежать TimeoutError
                                completed_futures = []
                                for future in list(futures.keys()):
                                    if future.done():
                                        completed_futures.append(future)
                                
                                if not completed_futures:
                                    time.sleep(0.1)  # Небольшая пауза если нет готовых результатов
                                    continue
                                    
                                for future in completed_futures:
                                    if not self.running:
                                        break
                                        
                                    try:
                                        worker_results, worker_attempts = future.result()
                                        
                                        # Сохраняем результаты сразу в файл
                                        if worker_results:
                                            temp_writer.writerows(worker_results)
                                            temp_csvfile.flush()  # Принудительная запись на диск
                                            all_found_addresses.extend(worker_results)
                                            batch_counter += 1
                                            
                                            print(f"💾 Batch {batch_counter}: сохранено {len(worker_results)} адресов")
                                        
                                        total_attempts += worker_attempts
                                        completed_count += len(worker_results)
                                        
                                        # Удаляем завершенный future
                                        worker_id = futures[future]
                                        del futures[future]
                                        
                                        # Проверяем достигнута ли цель
                                        if task.count > 0 and completed_count >= task.count:
                                            print(f"🎯 Цель достигнута: {completed_count}/{task.count}")
                                            # Отменяем остальные задачи
                                            for remaining_future in list(futures.keys()):
                                                remaining_future.cancel()
                                            futures.clear()
                                            break
                                            
                                        # Запускаем новый воркер если нужно продолжать
                                        if (task.count == 0 or completed_count < task.count) and len(futures) < max_concurrent_futures:
                                            new_future = executor.submit(
                                                self._worker_process_memory_optimized,
                                                network, task.pattern, task.pattern_type, 
                                                task.ignore_case, batch_size, worker_id
                                            )
                                            futures[new_future] = worker_id
                                            
                                    except Exception as e:
                                        print(f"❌ Ошибка воркера {futures.get(future, 'unknown')}: {e}")
                                        if future in futures:
                                            del futures[future]
                                        continue
                            
                            except Exception as e:
                                print(f"❌ Общая ошибка обработки: {e}")
                                break
                            
                            # Проверка лимитов памяти
                            if len(all_found_addresses) > 1000:  # Лимит в памяти
                                print(f"🧠 Очистка памяти: {len(all_found_addresses)} адресов в буфере")
                                # Оставляем только последние результаты в памяти для статистики
                                all_found_addresses = all_found_addresses[-100:]
            
            except KeyboardInterrupt:
                print(f"\n⚠️  Поиск прерван пользователем")
        
        # Общий блок обработки завершения для всех подходов
            
        total_time = time.time() - start_time
        avg_speed = total_attempts / total_time if total_time > 0 else 0
        
        task.status = "completed" 
        completed_count = len(all_found_addresses)
        task.found_addresses = completed_count
        
        # Сохранение результатов в зависимости от подхода
        if not use_memory_optimization and all_found_addresses:
            # Обычное сохранение для небольших count
            csv_dir = Path("CSV") 
            csv_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            final_filename = f"{task.currency}_{task.pattern_type}_{task.pattern}_{timestamp}.csv"
            final_filepath = csv_dir / final_filename
            
            with open(final_filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Currency', 'Pattern_Type', 'Pattern', 'Address', 'Private_Key', 'Attempts', 'Time'])
                for addr in all_found_addresses:
                    # Обработка как dict (из _worker_process) или как OptimizedKey
                    if isinstance(addr, dict):
                        writer.writerow([
                            task.currency, task.pattern_type, task.pattern,
                            addr['address'], addr['private_key'], 
                            addr.get('attempts_when_found', 0),
                            f"{total_time:.2f}s"
                        ])
                    else:
                        writer.writerow([
                            task.currency, task.pattern_type, task.pattern,
                            addr.address, addr.private_key, 
                            addr.attempts_when_found,
                            f"{total_time:.2f}s"
                        ])
            
            print(f"💾 Результаты сохранены в: {final_filename}")
            
        elif use_memory_optimization:
            # Batch подход - переименовываем временный файл в финальный
            if 'temp_filepath' in locals() and temp_filepath.exists() and completed_count > 0:
                final_filename = f"{task.currency}_{task.pattern_type}_{task.pattern}_{timestamp}.csv"
                final_filepath = csv_dir / final_filename
                temp_filepath.rename(final_filepath)
                print(f"💾 Финальные результаты сохранены в: {final_filepath}")
            elif 'temp_filepath' in locals() and temp_filepath.exists():
                # Удаляем пустой временный файл
                temp_filepath.unlink()
        
        print(f"\n📊 РЕЗУЛЬТАТ ЗАДАЧИ")
        print(f"==================================================")
        print(f"🎯 Найдено: {completed_count}")
        print(f"⚡ Скорость: {avg_speed:,.0f} адр/с")
        print(f"🔢 Попыток: {total_attempts:,}")
        print(f"⏱️  Время: {total_time:.1f} с")
        memory_mode = "batch-сохранение" if use_memory_optimization else "обычный режим"
        print(f"🧠 Память: {memory_mode}")
        
        return BatchResult(task, all_found_addresses[-10:] if len(all_found_addresses) > 10 else all_found_addresses, total_attempts, total_time, avg_speed)

    def _worker_process_memory_optimized(self, network, pattern: str, pattern_type: str, 
                                        ignore_case: bool, batch_size: int, worker_id: int) -> Tuple[List[dict], int]:
        """Оптимизированный рабочий процесс с управлением памятью"""
        found = []
        attempts = 0
        
        # Локальный счетчик для batch обработки
        local_batch_count = 0
        max_batch_size = min(batch_size, 50)  # Уменьшаем размер batch для частого возврата
        
        while self.running and len(found) < max_batch_size:
            try:
                key = network.generate()
                attempts += 1
                local_batch_count += 1
                
                # Проверка паттерна используя общую функцию
                if check_address_pattern(
                    address=key.address,
                    currency=key.currency,
                    pattern=pattern,
                    pattern_type=pattern_type,
                    ignore_case=ignore_case
                ):
                    found.append({
                        'address': key.address,
                        'private_key': key.private_key,
                        'currency': key.currency,
                        'found_time': int(time.time()),
                        'worker_id': worker_id
                    })
                    
                    print(f"[НАЙДЕН] Worker {worker_id}: {key.address}")
                    
                # Периодический отчет (реже чтобы не засорять вывод)
                if local_batch_count % 10000 == 0:
                    print(f"Worker {worker_id}: {attempts:,} попыток, {len(found)} найдено")
                    
                # Более мягкое ограничение - возвращаемся с результатами чаще
                if attempts >= 50000:  # Уменьшили лимит для более частого возврата результатов
                    print(f"Worker {worker_id}: завершение batch после {attempts} попыток")
                    break
                    
            except Exception as e:
                print(f"❌ Ошибка в воркере {worker_id}: {e}")
                break
        
        return found, attempts

    def _worker_process(self, network, pattern: str, pattern_type: str, 
                       ignore_case: bool, target_count: int, worker_id: int) -> Tuple[List[dict], int]:
        """Рабочий процесс поиска (оригинальная версия для совместимости)"""
        found = []
        attempts = 0
        
        while self.running:
            try:
                key = network.generate()
                attempts += 1
                
                # Проверка паттерна используя общую функцию
                if check_address_pattern(
                    address=key.address,
                    currency=key.currency,
                    pattern=pattern,
                    pattern_type=pattern_type,
                    ignore_case=ignore_case
                ):
                    found.append({
                        'address': key.address,
                        'private_key': key.private_key,
                        'currency': key.currency,
                        'found_time': int(time.time()),
                        'worker_id': worker_id
                    })
                    
                    print(f"[НАЙДЕН {len(found)}] {key.address}")
                    
                    # Проверяем лимит
                    if target_count > 0 and len(found) >= target_count:
                        break
                        
                # Периодический отчет
                if attempts % 10000 == 0:
                    print(f"Воркер {worker_id}: {attempts:,} попыток")
                    
            except Exception as e:
                print(f"❌ Ошибка в воркере {worker_id}: {e}")
                break
        
        return found, attempts

    def _save_results(self, task: BatchTask, addresses: List[dict]):
        """Сохранение результатов задачи"""
        # Создание папки CSV
        csv_dir = Path("CSV")
        csv_dir.mkdir(exist_ok=True)
        
        # Формирование имени файла
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{task.currency}_{task.pattern_type}_{task.pattern}_{timestamp}.csv"
        filepath = csv_dir / filename
        
        # Сохранение в CSV
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['address', 'private_key', 'currency', 'found_time', 'worker_id'])
            writer.writeheader()
            writer.writerows(addresses)
        
        print(f"💾 Сохранено {len(addresses)} адресов в: {filepath}")

    def execute_batch(self, config_path: str, workers: int = None):
        """Выполнение пакетного поиска"""
        print(f"🚀 ПАКЕТНЫЙ VANITY ГЕНЕРАТОР")
        print(f"============================================================")
        
        # Загрузка задач
        tasks = self.load_config(config_path)
        if not tasks:
            print("❌ Нет задач для выполнения")
            return
        
        print(f"📋 Загружено задач: {len(tasks)}")
        print(f"💻 Воркеров: {workers or mp.cpu_count()}")
        
        # Показ плана выполнения
        print(f"\n📅 ПЛАН ВЫПОЛНЕНИЯ:")
        print(f"============================================================")
        for i, task in enumerate(tasks, 1):
            level, time_str, _ = self.estimate_task_difficulty(task)
            print(f"{i:2}. {task.currency} {task.pattern_type}='{task.pattern}' "
                  f"(приоритет={task.priority}, {level}, {time_str})")
        
        # Подтверждение запуска
        print(f"\n⚠️  Пакетное выполнение может занять много времени!")
        response = input("Начать выполнение? (Y/n): ").strip().lower()
        if response in ['n', 'no', 'нет', 'н']:
            print("❌ Выполнение отменено")
            return
        
        # Выполнение задач
        results = []
        total_start = time.time()
        
        for i, task in enumerate(tasks, 1):
            if not self.running:
                break
                
            print(f"\n{'='*60}")
            print(f"📋 ЗАДАЧА {i}/{len(tasks)}")
            print(f"{'='*60}")
            
            result = self.execute_single_task(task, workers)
            results.append(result)
            
            # Короткая пауза между задачами
            if self.running and i < len(tasks):
                time.sleep(2)
        
        # Итоговая статистика
        total_time = time.time() - total_start
        total_found = sum(len(r.addresses) for r in results)
        total_attempts = sum(r.total_attempts for r in results)
        
        print(f"\n🎉 ПАКЕТНОЕ ВЫПОЛНЕНИЕ ЗАВЕРШЕНО")
        print(f"============================================================")
        print(f"⏱️  Общее время: {total_time/60:.1f} мин")
        print(f"🎯 Всего найдено: {total_found}")
        print(f"🔢 Всего попыток: {total_attempts:,}")
        print(f"⚡ Средняя скорость: {total_attempts/total_time:,.0f} адр/с")
        
        print(f"\n📊 ДЕТАЛЬНАЯ СТАТИСТИКА:")
        print(f"============================================================")
        for i, result in enumerate(results, 1):
            status_icon = "✅" if result.task.status == "completed" else "⚠️"
            print(f"{status_icon} {i:2}. {result.task.currency} {result.task.pattern_type}='{result.task.pattern}': "
                  f"{len(result.addresses)} найдено за {result.total_time:.1f}с")

def main():
    parser = argparse.ArgumentParser(description='🚀 Пакетный Vanity Address Generator')
    parser.add_argument('--config', default='config.csv',
                      help='Путь к файлу конфигурации (по умолчанию: config.csv)')
    parser.add_argument('--workers', type=int,
                      help='Количество воркеров (по умолчанию: все ядра)')
    parser.add_argument('--single', action='store_true',
                      help='Выполнить одну задачу из конфига')
    
    # Параметры для одиночного поиска (совместимость)
    parser.add_argument('--currency', choices=['BTC', 'ETH', 'TRX', 'LTC', 'DOGE', 'BSC', 'MATIC', 'ARB', 'OP'],
                      help='Криптовалюта (BTC, ETH, TRX, LTC, DOGE, BSC, MATIC, ARB, OP)')
    parser.add_argument('--prefix', help='Префикс для поиска')
    parser.add_argument('--suffix', help='Суффикс для поиска')
    parser.add_argument('--count', type=int, default=0, help='Количество адресов')
    parser.add_argument('--ignore-case', action='store_true', help='Игнорировать регистр')
    
    args = parser.parse_args()
    
    generator = BatchVanityGenerator()
    
    # Режим одиночного поиска (совместимость с max_core_generator.py)
    if args.currency and (args.prefix or args.suffix):
        pattern = args.prefix or args.suffix
        pattern_type = 'prefix' if args.prefix else 'suffix'
        
        task = BatchTask(
            currency=args.currency,
            pattern_type=pattern_type,
            pattern=pattern,
            count=args.count,
            ignore_case=args.ignore_case,
            priority=1
        )
        
        generator.execute_single_task(task, args.workers)
    
    # Режим пакетного поиска
    else:
        generator.execute_batch(args.config, args.workers)

if __name__ == "__main__":
    main()

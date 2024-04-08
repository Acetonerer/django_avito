import multiprocessing

bind = '0.0.0.0:8000'  # Привязываем к 0.0.0.0:8000 для прослушивания всех интерфейсов
workers = multiprocessing.cpu_count() * 2 + 1

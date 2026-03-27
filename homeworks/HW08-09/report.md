# HW08-09 – PyTorch MLP: регуляризация и оптимизация обучения

## 1. Кратко: что сделано

- Выбран датасет **CIFAR10** (вариант C). KMNIST недоступен при загрузке, CIFAR10 скачивается с зеркал PyTorch.
- Часть A: сравнение E1 (base), E2 (Dropout), E3 (BatchNorm), E4 (лучший + EarlyStopping).
- Часть B: O1 (LR слишком большой), O2 (LR слишком маленький), O3 (SGD+momentum + weight decay).

## 2. Среда и воспроизводимость

- Python: 3.13.9
- torch / torchvision: 2.7.1+cu118 / 0.22.1+cu118
- Устройство (CPU/GPU): cuda
- Seed: 42
- Как запустить: открыть `HW08-09.ipynb` и выполнить Run All.

## 3. Данные

- Датасет: CIFAR10
- Разделение: train 80% / val 20% (от train split) + test из torchvision
- Трансформации: ToTensor
- Комментарий: 10 классов, 32×32×3 RGB, 50k train + 10k test. MLP работает хуже, чем на MNIST — это нормально.

## 4. Базовая модель и обучение

- Модель MLP: 2 скрытых слоя (256, 128), ReLU
- Loss: CrossEntropyLoss
- Базовый Optimizer: Adam (lr=1e-3)
- Batch size: 128
- Epochs (макс): 15
- EarlyStopping: patience=5, по val_accuracy

## 5. Часть A (S08): регуляризация (E1-E4)

- E1 (base): 2 скрытых слоя 256-128, без Dropout/BatchNorm
- E2 (Dropout): как E1 + Dropout(p=0.3)
- E3 (BatchNorm): как E1 + BatchNorm
- E4 (EarlyStopping): лучший из (E2/E3) по val_accuracy + EarlyStopping(5)

## 6. Часть B (S09): LR, оптимизаторы, weight decay (O1-O3)

- O1: Adam, lr=1e-1 (слишком большой)
- O2: Adam, lr=1e-5 (слишком маленький)
- O3: SGD, momentum=0.9, weight_decay=1e-4, lr=1e-2

## 7. Результаты

Ссылки на файлы в репозитории:

- Таблица результатов: [./artifacts/runs.csv](./artifacts/runs.csv)
- Лучшая модель: [./artifacts/best_model.pt](./artifacts/best_model.pt)
- Конфиг лучшей модели: [./artifacts/best_config.json](./artifacts/best_config.json)
- Кривые лучшего прогона: [./artifacts/figures/curves_best.png](./artifacts/figures/curves_best.png)
- Кривые "плохих LR": [./artifacts/figures/curves_lr_extremes.png](./artifacts/figures/curves_lr_extremes.png)

Короткая сводка:

- Лучший эксперимент части A: **E4** (E3+EarlyStop)
- Лучшая val_accuracy: 51.69%
- Итоговая test_accuracy (для лучшей модели): Final test accuracy (E4): 0.5114
- O1 (lr=1e-1): val_acc ~10%, val_loss ~2.3 — loss высокий, accuracy очень низкая
- O2 (lr=1e-5): val_acc ~33%, обучение почти не идёт, метрики почти не меняются
- O3 (SGD+momentum+wd): val_acc 45.93%, хуже Adam (E2/E4 ~46–52%)

## 8. Анализ

В части A лучший результат показал E4 (E3 + EarlyStopping): BatchNorm дал небольшое преимущество над base (E1) и Dropout (E2). E2 с Dropout(0.3) показал худший val_acc (45.12%) — возможно, 0.3 слишком велик для CIFAR10. Переобучение на E1/E3 видно по расхождению train и val loss: val loss выходит на плато, а train продолжает падать. BatchNorm немного стабилизировал обучение.

O1 (lr=1e-1): loss высокий (~2.3), val_acc ~10% — типичный признак слишком большого LR: оптимизатор «перепрыгивает» минимум, модель не сходится. 
O2 (lr=1e-5): val_acc ~33%, почти без улучшения за 6 эпох — LR слишком мал, обновления весов почти нулевые.
O3 (SGD+momentum+wd): val_acc 45.93%, ниже чем у Adam при тех же 12 эпохах. 
Weight decay добавляет L2-регуляризацию и может немного снижать переобучение, но здесь основное ограничение — архитектура MLP и размер датасета.

## 9. Итоговый вывод

Базовым конфигом разумно считать E4: BatchNorm + EarlyStopping, Adam lr=1e-3. Для CIFAR10 MLP без свёрток даёт val_acc ~52%, что соответствует ожиданиям. Дальше имеет смысл попробовать: нормализацию данных (Normalize по mean/std CIFAR10) и более глубокую сеть или свёрточные слои — MLP слабо использует пространственную структуру изображений.

## 10. Приложение (опционально)

Не выполнялось.

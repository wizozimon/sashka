# CS2 Market Watch

CLI-инструмент для личного списка предметов: получает сводную цену Steam Community Market, сохраняет наблюдения в SQLite и показывает изменение к предыдущему замеру. Можно использовать для оценки инвентаря и отслеживания цены; торговые операции не выполняет.

## Быстрый старт

```bash
pip install -r requirements.txt
python tracker.py add "AK-47 | Redline (Field-Tested)"
python tracker.py update
python tracker.py report
```

По умолчанию используется USD (Steam currency ID 1). Имя предмета должно точно совпадать с `market_hash_name`. Интервал между запросами 3 секунды. Для ежедневного обновления настройте cron/Task Scheduler командой `python tracker.py update`.

Источник: публичный, но неофициально документированный endpoint Steam Community Market `priceoverview`. Доступность, формат, локализация цены и ограничения запросов могут меняться; ошибки/429 нужно повторить позже. Цена Steam — ориентир, не гарантированная цена продажи и не оценка сторонних площадок. Учитывайте комиссию и правила Steam. Не добавляйте cookies или пароль аккаунта.

# Internship Radar (HH.ru)

Сохраняет свежие вакансии по заданному запросу из публичного API HeadHunter, выводит зарплаты там, где они указаны, и сохраняет снимок в CSV для сравнения спроса. Удобно для поиска стажировок и небольшого анализа требований рынка.

## Запуск

```bash
pip install -r requirements.txt
python radar.py --text "стажер аналитик" --area 1 --pages 2 --output vacancies.csv
```

`area=1` — Москва в каталоге HH. API требует описательный User-Agent; задайте `HH_USER_AGENT`, например `StudentRadar/1.0 contact@example.com`. Скрипт не подает отклики и не собирает персональные данные.

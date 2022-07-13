# Веб-сервер синтеза речи Silero
Офлайн сервер синтеза речи на нейронных сетях

> Спасибо команде Silero за [синтез](https://github.com/snakers4/silero-models)
> Спасибо Kamnev Sergey за основу [сервера] (https://github.com/kamnsv/offline-neural-tts)

## Зависимости

	* Версия python >= 3.7x (64-bit)
	* CPU с поддержкой инструкций AVX2

```
pip install -r requirements.txt 
```
	
## Запуск

```
python server.py [PORT] [HOST]
```
> по умолчанию PORT=80 HOST=localhost

## Обращение

### GET запрос синтеза

Запрос: `http://[HOST]:[PORT]/?speak=[TEXT]` или `http://[HOST]:[PORT]/[TEXT]`

> **Ответ:**  `header 'Content-type: audio/wav'`

### POST запрос синтеза

```
header 'Content-Type: application/json' 
'{
    "text": "Добрый день! Как ваши дел+а?",
    "speaker": "xenia",
    "sample_rate": "48000", 
    "accent": "on", 
    "yo": "off",
    "abr": "on", 
}'
```

> **Ответ:** `/Добрый день_ Как ваши дел+а_`

### Страница тестирования POST

Запрос: `http://[HOST]:[PORT]`

### Запрос списка голосов

Запрос: `http://[HOST]:[PORT]/?speakers`

> **Ответ:** `["aidar", "baya", "eugene", "kseniya", "random", "xenia"]`
# offline-neural-tts
Офлайн сервер синтеза речи на нейронных сетях

> Основа синтеза речи взята [здесь](https://github.com/snakers4/silero-models)

## Зависимости

	* Версия python >= 3.7x (64-bit)
	* CPU с поддержкой инструкций AVX2
	
```
pip install https://github.com/kamnsv/ru_number_to_text/archive/refs/heads/master.zip
pip install -r requirements.txt 
```

> Скачать в корень https://models.silero.ai/models/tts/ru/v3_1_ru.pt


## Запуск

```
python server.py [PORT] [HOST]
```
> по умолчанию PORT=80 HOST=localhost

## Обращение

### GET запросы

Запрос: `http://[HOST]:[PORT]/[TEXT]`

> **Ответ:**  `header 'Content-type: audio/wav'`

### POST запросы

```
header 'Content-Type: application/json' 
'{
    "text": "Добрый день! Как ваши дел+а?",
    "speaker": "xenia",
    "sample_rate": "48000", 
    "accent": "on", 
    "yo": "off",
    "digit": "on", 
    "abr": "on", 
    "trans": "on" 
}'
```

> **Ответ:** `/Добрый день_ Как ваши дел+а_`

# dnevnik-spb

Электронынй дневник Санкт-Петербурга, работающий прям в телеграм боте!

Теперь не нужно тратить много времени, заходя на неудобную вэб-версию сайта электронного дневника. Вместо этого можно просто отправить команду боту и узнать свои оценки.

## Screenshots
<p float="left">
  <img src="/one.PNG" width="200"/>
  <img src="/two.PNG" width="200"/>
  <img src="/three.PNG" width="200"/>
  <img src="/four.PNG" width="200"/>
</p>

## Как это работает?
Скрипт по получению данных с сайта https://dnevnik2.petersburgedu.ru/ я повзаимствовал у одного очень классного чела (https://github.com/newtover/dnevnik)
Огромная ему благодарность! ❤️

О работе подробной скрипта можете почитать в его репозитории. Но вкратце, скрипт использует ID ученика и тянет данные с сайта "Петербургское Образование" по этому ID.

Бот написан на Python 3. Использовалась библиотека Telebot.
Полный списко библиотек есть в файл requirements.txt

Бот работает на серваке Heroku.

## Видос

Если интресно посмотреть процесс создания бота, то вот видос:

[![link to youtube video](https://i.imgur.com/jWIHX6b.jpg)](https://www.youtube.com/watch?v=ancElXQgOzY&t=1s "ссылка на видео")

⬆️⬆️⬆️ Ссылка на видео ⬆️⬆️⬆️

## License
dnevnik-spb is available under the MIT license. See the LICENSE file for more info.

---
name: sbl-audio
description: Готовит текст субботнего урока для озвучки в ElevenLabs — разбивает урок на части (вступление и каждый вопрос отдельно), подставляет памятный стих, библейские тексты и цитаты Духа пророчества, и называет файлы так, как их ждёт плеер SBL. Использовать, когда просят подготовить/сгенерировать текст для аудио урока, озвучить урок, сделать блоки для ElevenLabs, или называют номер урока с языком (например «9 урок на немецком для озвучки»).
---

# Текст урока для озвучки

## Откуда брать урок

Квартал лежит целиком по адресу:

```
https://app.sdarm.org/sbl/data/{lang}/{lang}-{year}-{quarter}.json
```

Запрашивать с обычным User-Agent браузера — иначе сервер отвечает 406.

Внутри: `lessons[]`, у каждого урока `no`, `title`, `keyTextRef`, `keyText`,
`keyNote`, `dailyLessons[]`. У дня — `sectionTitle` и `subsections[]`, внутри
`q[]` парами: текст вопроса, затем ссылка на Писание (`sOsis`).

Сам библейский текст — в отдельном файле издания:

```
https://app.sdarm.org/bible/data/{de-lut|en-kjv|ru-rst}.json
```

## Как режется урок

Одна часть — один файл. Вступление, дальше каждый вопрос отдельно.

| Часть | Файл |
|---|---|
| вступление | `de-09-0.mp3` |
| воскресенье, вопрос a | `de-09-1a.mp3` |
| воскресенье, вопрос b | `de-09-1b.mp3` |
| понедельник, вопрос a | `de-09-2a.mp3` |
| суббота | `de-09-7a.mp3` |

Цифра — день (1 воскресенье … 7 суббота), буква — вопрос. Номер урока двумя
цифрами. Пропусков в буквах быть не должно: плеер перебирает их подряд и
останавливается на первой отсутствующей.

## Главное правило

**Текст урока не меняется.** Ни вопрос, ни библейский стих, ни цитата Духа
пророчества. Ничего не сокращать, не пересказывать, не поправлять — переносить
слово в слово, как стоит в уроке и в издании Библии.

Сочиняется ровно одна вещь: **строка, которой объявляется ссылка**. Её нужно
произнести, а не показать: как она напечатана в уроке — `2. Korinther 2, 14. 15;` —
голос прочесть не может. Строка собирается заново, по правилам ниже, и цифр в
ней не остаётся.

## Блок 1 — вступление

```
[calm] [Номер словом] Lektion. [Название темы урока].
<break time="1.0s"/>
Leittext aus [Книга, Kapitel …, Vers … — словами]:
<break time="0.5s"/>
„[Текст памятного стиха]“
<break time="1.0s"/>
Aus dem Buch „[Название книги]“, Seite [Страница]:
<break time="0.5s"/>
„[Текст цитаты]“
```

## Блок 2 — вопрос

Образец, по которому равняться:

```
[clear] Frage b: Was wird im Leben sichtbar, wenn die Liebe Christi im Herzen gepflegt wird?
<break time="0.5s"/>
Zweiter Korinther, Kapitel zwei, die Verse vierzehn und fünfzehn:
<break time="0.5s"/>
„Aber Gott sei gedankt, der uns allezeit Sieg gibt in Christo …“
<break time="1.0s"/>
Und Zweiter Korinther, Kapitel fünf, Vers vierzehn:
<break time="0.5s"/>
„Denn die Liebe Christi dringt in uns also …“
<break time="1.0s"/>
Aus dem Buch „Der Weg zu Christus“, Seite 56:
<break time="0.5s"/>
„Wenn die Liebe des Heilandes im Herzen bewahrt wird …“
<break time="1.0s"/>
Aus dem Buch „Das Leben Jesu“, Seite 138 und 139:
<break time="0.5s"/>
„Die Welt soll sehen, dass wir nicht selbstsüchtig …“
```

## Как это устроено

**Вопрос — отдельной строкой**, ссылка на Писание в неё не входит. В уроке они
стоят вместе; здесь ссылка отделяется и произносится следующей строкой.

**Ссылка проговаривается целиком** — книга, глава, стих, ничего не
подразумевается цифрой. Как именно — отдельным разделом ниже.

**Номер урока и раздела** — тоже слова: `Neunte Lektion`, не `9.`. У раздела
номер проще опустить и назвать одно название: `[clear] Das Leben und das Licht.`
Цифрой остаются только страницы цитат — `Seite 56` голос читает верно.

**Второй и следующий отрывки** вводятся словом `Und`, через `<break time="1.0s"/>`.

**Каждая цитата — своим блоком** `Aus dem Buch „…“, Seite …:`. Страницы здесь
цифрами, а `und` между двумя страницами словом: `Seite 138 und 139`.

**Паузы**: `0.5s` перед текстом, который сейчас прозвучит; `1.0s` между
смысловыми блоками.

**Метки** `[calm]`, `[clear]` и `<break>` оставлять как есть — это указания
голосу, не текст.

## Как называется место Писания

Книга, глава, стих — вслух и по порядку. Ни `Kapitel`, ни `Vers` не
подразумеваются номером: их слышно.

| В уроке | Как звучит |
|---|---|
| `Johannes 1, 4. 5.` | `Johannes, Kapitel eins, die Verse vier und fünf` |
| `2. Korinther 2, 14. 15;` | `Zweiter Korinther, Kapitel zwei, die Verse vierzehn und fünfzehn` |
| `2Cor.5.14` | `Zweiter Korinther, Kapitel fünf, Vers vierzehn` |
| `1. Johannes 4, 9-12.` | `Erster Johannes, Kapitel vier, die Verse neun bis zwölf` |
| `1. Mose 3, 1-7;` | `Erstes Buch Mose, Kapitel drei, die Verse eins bis sieben` |
| `1. Könige 18, 41-45.` | `Erstes Buch der Könige, Kapitel achtzehn, die Verse einundvierzig bis fünfundvierzig` |
| `Psalm 32, 1. 2.` | `Psalm zweiunddreißig, die Verse eins und zwei` |

**Стих.** Один — `Vers vierzehn`. Два и больше — множественное `die Verse`:
`die Verse vierzehn und fünfzehn`. Подряд — через `bis`: `die Verse neun bis
zwölf`. Вразбивку — запятой и `und`: `die Verse eins, drei und fünf`.
`die Vers` не бывает: с артиклем `die` стоит только `Verse`.

**Глава.** `Kapitel` не опускается никогда — кроме псалма: у псалма номер и
есть имя, `Psalm zweiunddreißig`, и `Kapitel` перед ним не говорят.

**Номер книги** — тоже слово, и согласуется с книгой. Послания мужского рода
(`der Brief`), книги среднего (`das Buch`):

| Послания | Книги |
|---|---|
| `Erster Korinther`, `Zweiter Korinther` | `Erstes Buch Mose`, `Zweites Buch Mose` |
| `Erster Johannes` | `Erstes Buch Samuel` |
| `Erster Petrus`, `Zweiter Petrus` | `Erstes Buch der Könige` |
| `Erster Thessalonicher` | `Zweites Buch der Chronik` |
| `Erster Timotheus`, `Zweiter Timotheus` | |

**Какое это место — говорит `sOsis`, а не печатная строка.** В уроке попадаются
опечатки: при `2 Korinther 2:5, 14.` стоит `sOsis: 2Cor.5.14` — значит пятая
глава, стих четырнадцатый, и называется она.

По-английски и по-русски порядок тот же, слова свои: `John, chapter one, verses
four and five`; `Иоанна, глава первая, стихи четвёртый и пятый`.

## Чего не делать

Не добавлять пояснений, переходов и связок от себя. Не менять пунктуацию
внутри цитат. Не сокращать длинные цитаты многоточием. Не переводить —
язык блока это язык урока.

Не оставлять в ссылке цифр и сокращений: ни `2.` перед книгой, ни `Kap.`,
ни `14. 15.` — всё это на слух не читается.

Если у вопроса нет цитаты — блок кончается после стиха. Если нет стиха —
после вопроса. Пустые места ничем не заполнять.

Название раздела произносится один раз, в первом вопросе дня; у следующих
вопросов того же дня его опускать.

## Что отдавать

Готовые блоки, каждый под своим именем файла, чтобы их можно было по очереди
вставить в ElevenLabs и сохранить сразу правильно названными.

Файлы кладутся в `audio/` — см. `audio/README.md`.

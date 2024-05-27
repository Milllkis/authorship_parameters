# Исследование статистики распределения параметров текста при определении авторства | Investigation of Distribution of Text Parameters in Authorship Detection

В современном мире актуальна проблема определения авторства текста. Под этим мы подразумеваем процесс извлечения и анализа индивидуальных стилистических и лингвистических особенностей автора на основе его работ. Однако, исследование авторства включает в себя не только исследование характерных черт. Важно обращать внимание на то, что автор может использовать различные подходы к написанию произведения в зависимости от времени, контекста, темы и цели.

**Целью** настоящей работы является выявление уникальных черт внутри работ одного автора, а также их анализ на основе выбранных нами параметров.

Достижение поставленной цели требует выполнения следующих **задач**:
1) Сбор данных с открытых ресурсов осуществляется с помощью двух краулеров. Ознакомится с кодом каждого можно по следующим ссылкам: [первый](https://github.com/Milllkis/authorship_parameters/blob/main/crawler_mn.py) и [второй](https://github.com/Milllkis/authorship_parameters/blob/main/crawler_mk.py)
2) Предобработка собранных данных. Ознакомится с кодом можно [здесь](https://github.com/Milllkis/authorship_parameters/blob/main/preprocessing.py). 
3) Проведение анализа полученных текстовых материалов одного автора с целью выявления уникальных черт. Ознакомиться с кодом выделения параметров можно по следующим ссылкам: [синтаксические параметры](https://github.com/Milllkis/authorship_parameters/blob/main/SyntacticComplexity.py), [лексические параметры](https://github.com/Milllkis/authorship_parameters/blob/main/LexicalComplexity.py) и [параметры, основанные на дереве зависимостей](https://github.com/Milllkis/authorship_parameters/blob/main/DependencyTreeComplexity.py). Дополнительно предлагаем ознакомится со [сравнением парсеров для русского языка](https://github.com/Milllkis/authorship_parameters/blob/main/compare_parsers.ipynb).
4) Сравнение различных работ автора с учетом выбранных параметров. Ознакомится с кодом статистического анализа можно [здесь](https://github.com/Milllkis/authorship_parameters/blob/main/statistics.ipynb).

Ознакомиться с посчитанными значениями параметров для каждого автора можно по следующим ссылкам: [Автор 1409](https://github.com/Milllkis/authorship_parameters/blob/main/processed_1409.csv), [Автор 1476](https://github.com/Milllkis/authorship_parameters/blob/main/processed_1476.csv), [Автор 2083](https://github.com/Milllkis/authorship_parameters/blob/main/processed_2083.csv), [Автор 3368](https://github.com/Milllkis/authorship_parameters/blob/main/processed_3368.csv), [Автор 4291](https://github.com/Milllkis/authorship_parameters/blob/main/processed_4291.csv) и [Автор 918](https://github.com/Milllkis/authorship_parameters/blob/main/processed_918.csv).

Работу выполнила: Камская Милена
Научный руководитель: Клышинский Эдуард Станиславович

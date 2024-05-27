import re
import string
import numpy as np
import random
import pymorphy3
import nltk
from nltk import FreqDist
from nltk.corpus import stopwords
nltk.download('stopwords')
import math



def preprocess(text) -> str:
    """Предобработка текста.
    
    Параметры:
    text (str): Входной текст для предобработки.
    
    Возвращает:
    str: Предобработанный текст. """
    # приводим к нижнему регистру и убираем числа и пробелы между ними, а также возможные оставшиеся коды html
    text = re.sub('(?<=\d)\s+(?=\d)', '', text.lower())
    text = re.sub(r"[0-9]+", "", text)
    text = re.sub('<.*?>', '', text)
    text = re.sub('&.*?;', '', text)

    # заменяем тире, дефис и убираем кавычки-елочки
    text = text.replace("–", "")
    text = text.replace("—", "")
    text = text.replace("-", "")
    text = text.replace("«", "")
    text = text.replace("»", "")

    return text

def tokenize(text) -> list:
    """Токенизация текста на русском языке с использованием TreebankWordTokenizer().
    
    Параметры:
    text (str): Входной текст для токенизации.
    
    Возвращает:
    list: Список токенов. """
    text = preprocess(text)

    for symbol in list(string.punctuation):
        text = text.replace(symbol, " ")

    tokenized = nltk.tokenize.TreebankWordTokenizer()
    words = tokenized.tokenize(text)

    return words

def tokenize_rs(text) -> list:
    """Токенизация текста на русском языке с использованием TreebankWordTokenizer() и удалением стоп-слов.
    
    Параметры:
    text (str): Входной текст для токенизации.
    
    Возвращает:
    list: Список токенов.  """
    text = preprocess(text)

    for symbol in list(string.punctuation):
        text = text.replace(symbol, " ")

    tokenized = nltk.tokenize.TreebankWordTokenizer()
    words = tokenized.tokenize(text)

    stop_words = set(stopwords.words('russian'))
    filtered_sentence = [w for w in words if not w.lower() in stop_words]

    return filtered_sentence


class LexicalComplexity():
    def __init__(self, text, preprocessor=preprocess, tokenizer=tokenize, tokenizer_rs=tokenize_rs):
        """
        Инициализирует объект класса LexicalComplexity, вычисляющий метрики лексического разнообразия, плотности и сложности текста.

        Параметры:
        text (str): Текст для анализа.
        preprocessor (function): Функция предварительной обработки текста.
        tokenizer (function): Функция токенизации текста.
        tokenizer_rs (function): Функция токенизации текста с удалением стоп-слов.
        """
        self.text = text

        self.preprocessor = preprocessor
        self.tokenizer = tokenizer
        self.tokenizer_remove_stopwords = tokenizer_rs
        self.morph = pymorphy3.MorphAnalyzer()

        text = self.preprocessor(text)
        self.list_of_words = self.tokenizer(text)
        self.clear_list_of_words = self.tokenizer_remove_stopwords(text)

        self.words = len(self.list_of_words)
        self.clear_words = len(self.clear_list_of_words)

    def lexical_items(self, remove_stop_words=False) -> list:
        """
        Возвращает список типов лексем на основе леммы.

        Аргументы:
        remove_stop_words (bool): Флаг для удаления стоп-слов.

        Возвращает:
        list: Список типов лексем.
        """
        lex_items = []
        key_tags = ['NOUN', 'ADJF', 'ADJS', 'VERB', 'INFN', 'ADVB']

        if remove_stop_words:
            tokens = self.tokenizer_remove_stopwords(self.text)
            tags = [self.morph.parse(token)[0].tag.POS for token in tokens]

            for i in range(len(tags)):
                if tags[i] in key_tags:
                    lexem = self.morph.parse(tokens[i])[0].normal_form
                    lex_items.append(lexem)
        else:
            tokens = self.tokenizer(self.text)
            tags = [self.morph.parse(token)[0].tag.POS for token in tokens]

            for i in range(len(tags)):
                if tags[i] in key_tags:
                    lexem = self.morph.parse(tokens[i])[0].normal_form
                    lex_items.append(lexem)

        return lex_items

    def lexical_items_wordform(self, remove_stop_words=False) -> list:
        """
        Возвращает список типов лексем на основе словоформы.

        Аргументы:
        remove_stop_words (bool): Флаг для удаления стоп-слов.

        Возвращает:
        list: Список типов лексем.
        """
        lex_items = []
        key_tags = ['NOUN', 'ADJF', 'ADJS', 'VERB', 'INFN', 'ADVB']

        if remove_stop_words:
            tokens = self.tokenizer_remove_stopwords(self.text)
            tags = [self.morph.parse(token)[0].tag.POS for token in tokens]

            for i in range(len(tags)):
                if tags[i] in key_tags:
                    lex_items.append(tokens[i])
        else:
            tokens = self.tokenizer(self.text)
            tags = [self.morph.parse(token)[0].tag.POS for token in tokens]

            for i in range(len(tags)):
                if tags[i] in key_tags:
                    lex_items.append(tokens[i])

        return lex_items

    def ttr(self, remove_stop_words=False) -> float:
        """
        Возвращает Type-Token Ratio текста.

        Аргументы:
        remove_stop_words (bool): Флаг для удаления стоп-слов.

        Возвращает:
        float: Type-Token Ratio текста.
        """
        if remove_stop_words:
            return len(set(self.lexical_items(remove_stop_words=True))) / self.clear_words
        else:
            return len(set(self.lexical_items())) / self.words

    def rttr(self, remove_stop_words=False) -> float:
        """
        Возвращает Root Type-Token Ratio текста.

        Аргументы:
        remove_stop_words (bool): Флаг для удаления стоп-слов.

        Возвращает:
        float: Root Type-Token Ratio текста.
        """
        if remove_stop_words:
            return len(set(self.lexical_items(remove_stop_words=True))) / np.sqrt(self.clear_words)
        else:
            return len(set(self.lexical_items())) / np.sqrt(self.words)

    def cttr(self, remove_stop_words=False) -> float:
        """
        Возвращает Corrected Type-Token Ratio текста.

        Аргументы:
        remove_stop_words (bool): Флаг для удаления стоп-слов.

        Возвращает:
        float: Corrected Type-Token Ratio текста.
        """
        if remove_stop_words:
            return len(set(self.lexical_items(remove_stop_words=True))) / np.sqrt(2 * self.clear_words)
        else:
            return len(set(self.lexical_items())) / np.sqrt(2 * self.words)

    def mttr(self, remove_stop_words=False) -> float:
        """
        Возвращает Mass Type-Token Ratio текста.

        Аргументы:
        remove_stop_words (bool): Флаг для удаления стоп-слов.

        Возвращает:
        float: Mass Type-Token Ratio текста.
        """
        if remove_stop_words:
            return math.log10(self.clear_words) - math.log10(len(self.lexical_items(remove_stop_words=True))) / np.sqrt(math.log10(self.clear_words))
        else:
            return math.log10(self.words) - math.log10(len(self.lexical_items())) / np.sqrt(math.log10(self.words))

    def mtld_lemma(self, remove_stop_words=False) -> float:
        """
        Возвращает MTLD (Measure of Textual Lexical Diversity) на основе лемм.

        Аргументы:
        remove_stop_words (bool): Флаг для удаления стоп-слов.

        Возвращает:
        float: MTLD на основе лемм.
        """
        if remove_stop_words:
            tokens = self.lexical_items(remove_stop_words=True)
        else:
            tokens = self.lexical_items()
        segments = 0
        forward = 0
        backward = 0

        for direction in ['forward', 'backward']:  # Проход по тексту в прямом и обратном порядке
            if direction == 'backward':
                tokens = list(reversed(tokens))
            segment_start = 0
            segment_length = 0
            segment_unique_words = set()
            for token in tokens:
                segment_length += 1
                segment_unique_words.add(token)
                ttr = len(segment_unique_words) / segment_length  # Вычисляем TTR для текущего сегмента
                if ttr >= 0.72:
                    segments += 1
                    segment_start += segment_length
                    segment_length = 0
            if direction == 'backward':
                backward = len(set(tokens)) / segments
            else:
                forward = len(set(tokens)) / segments

        return np.mean([forward, backward])

    def mtld_wordform(self, remove_stop_words=False) -> float:
        """
        Возвращает MTLD (Measure of Textual Lexical Diversity) на основе словоформ.

        Аргументы:
        remove_stop_words (bool): Флаг для удаления стоп-слов.

        Возвращает:
        float: MTLD на основе словоформ.
        """
        if remove_stop_words:
            tokens = self.lexical_items_wordform(remove_stop_words=True)
        else:
            tokens = self.lexical_items_wordform()
        segments = 0
        forward = 0
        backward = 0

        for direction in ['forward', 'backward']:  # Проход по тексту в прямом и обратном порядке
            if direction == 'backward':
                tokens = list(reversed(tokens))
            segment_start = 0
            segment_length = 0
            segment_unique_words = set()
            for token in tokens:
                segment_length += 1
                segment_unique_words.add(token)
                ttr = len(segment_unique_words) / segment_length  # Вычисляем TTR для текущего сегмента
                if ttr >= 0.72:
                    segments += 1
                    segment_start += segment_length
                    segment_length = 0
            if direction == 'backward':
                backward = len(set(tokens)) / segments
            else:
                forward = len(set(tokens)) / segments

        return np.mean([forward, backward])

    def hdd(self, remove_stop_words=False) -> float:
        """
        Вычисляет индекс лексического разнообразия текста с использованием метода HDD (Heap's Diversity D).

        Аргументы:
        remove_stop_words (bool): Флаг для удаления стоп-слов.

        Возвращает:
        float: Индекс лексического разнообразия текста с использованием метода HDD (Heap's Diversity D).
        """
        if remove_stop_words:
            tokens = self.lexical_items(remove_stop_words=True)
        else:
            tokens = self.lexical_items()
        ttr_values = []  # Список для хранения значений TTR

        while len(tokens) >= 50:
            segment_length = random.randint(32, 50)
            segment_words = tokens[:segment_length]
            unique_words = set(segment_words)
            ttr = len(unique_words) / segment_length  # Вычисляем TTR для текущего сегмента
            ttr_values.append(ttr)
            tokens = tokens[segment_length:]  # Обрезаем текст до следующего сегмента

        if tokens:  # Если остались слова после цикла
            unique_words = set(tokens)
            ttr = len(unique_words) / len(tokens)
            ttr_values.append(ttr)

        return np.mean(ttr_values)

    def density_func(self, remove_stop_words=False) -> float:
        """
        Вычисляет индекс лексической плотности, основанный на отношении лексических слов и служебных слов.

        Аргументы:
        remove_stop_words (bool): Флаг для удаления стоп-слов.

        Возвращает:
        float: Индекс лексической плотности.
        """
        lexical_words = []
        functional_words = []

        if remove_stop_words:
            tokens = self.lexical_items(remove_stop_words=True)
        else:
            tokens = self.lexical_items()

        for word in tokens:
            parsed_word = self.morph.parse(word)[0]

            if parsed_word.tag.POS in ['NOUN', 'ADJF', 'VERB', 'ADVB']:
                lexical_words.append(word)
            else:
                functional_words.append(word)

        if len(functional_words) == 0:
            return 0.0

        return len(lexical_words) / len(functional_words)

    def density_total(self, remove_stop_words=False) -> float:
        """
        Вычисляет индекс лексической плотности, основанный на отношении лексических слов и общего количества слов.

        Аргументы:
        remove_stop_words (bool): Флаг для удаления стоп-слов.

        Возвращает:
        float: Индекс лексической плотности.
        """
        lexical_words = []

        if remove_stop_words:
            tokens = self.lexical_items(remove_stop_words=True)
        else:
            tokens = self.lexical_items()

        for word in tokens:
            parsed_word = self.morph.parse(word)[0]

            if parsed_word.tag.POS in ['NOUN', 'ADJF', 'VERB', 'ADVB']:
                lexical_words.append(word)

        if len(tokens) == 0:
            return 0.0

        return len(lexical_words) / len(tokens)

    def sophistication_lemmas(self, remove_stop_words=False) -> float:
        """
        Вычисляет уровень сложности текста на основе лемм.

        Аргументы:
        remove_stop_words (bool): Флаг для удаления стоп-слов.

        Возвращает:
        float: Уровень сложности текста на основе лемм.
        """
        if remove_stop_words:
            tokens = self.lexical_items(remove_stop_words=True)
        else:
            tokens = self.lexical_items()
        freq_dist = FreqDist(tokens)

        total_words = len(tokens)
        rare_words = sum(1 for word in freq_dist if freq_dist[word] == 1)

        return rare_words / total_words

    def sophistication_wordform(self, remove_stop_words=False) -> float:
        """
        Вычисляет уровень сложности текста на основе словоформ.

        Аргументы:
        remove_stop_words (bool): Флаг для удаления стоп-слов.

        Возвращает:
        float: Уровень сложности текста на основе словоформ.
        """
        if remove_stop_words:
            tokens = self.lexical_items_wordform(remove_stop_words=True)
        else:
            tokens = self.lexical_items_wordform()
        freq_dist = FreqDist(tokens)

        total_words = len(tokens)
        rare_words = sum(1 for word in freq_dist if freq_dist[word] == 1)

        return rare_words / total_words

    def giraud_lemma(self, remove_stop_words=False) -> float:
        """
        Вычисляет индекс Гиро на основе лемм.

        Аргументы:
        remove_stop_words (bool): Флаг для удаления стоп-слов.

        Возвращает:
        float: Индекс Гиро на основе лемм.
        """
        if remove_stop_words:
            total_lexemes = len(self.lexical_items(remove_stop_words=True))
            vocabulary_size = len(set(self.clear_list_of_words))
        else:
            total_lexemes = len(self.lexical_items())
            vocabulary_size = len(set(self.list_of_words))

        return vocabulary_size / (total_lexemes ** 0.5)

    def giraud_wordform(self, remove_stop_words=False) -> float:
        """
        Вычисляет индекс Гиро на основе словоформ.

        Аргументы:
        remove_stop_words (bool): Флаг для удаления стоп-слов.

        Возвращает:
        float: Индекс Гиро на основе словоформ.
        """
        if remove_stop_words:
            total_lexemes = len(self.lexical_items_wordform(remove_stop_words=True))
            vocabulary_size = len(set(self.clear_list_of_words))
        else:
            total_lexemes = len(self.lexical_items_wordform())
            vocabulary_size = len(set(self.list_of_words))

        return vocabulary_size / (total_lexemes ** 0.5)

import numpy as np
from spacy_conll import init_parser
from collections import Counter


class DependencyTreeMetrics:
    def __init__(self, text):
        """
        Инициализирует объект DependencyTreeMetrics, вычисляющий метрики сложности текста, основанные на дереве зависимостей.

        Параметры:
        text (str): Текст для анализа зависимостей.
        """
        self.text = text

        nlp_stanza = init_parser("ru", "stanza", ext_names={"conll_str": "conll_str"})
        self.doc = nlp_stanza(self.text)

    def tree_depth(self) -> list:
        """
        Вычисляет глубину дерева зависимостей для каждого предложения в тексте.

        Возвращает:
        list: Список значений глубины дерева зависимостей для каждого предложения.
        """
        depths = []
        for doc in self.doc.sents:
            max_depth = 0
            for token in doc:
                depth = 0
                for ancestor in token.ancestors:
                    depth += 1
                if depth > max_depth:
                    max_depth = depth
            depths.append(max_depth)

        return depths

    def tree_width(self) -> list:
        """
        Вычисляет ширину дерева зависимостей для каждого предложения в тексте.

        Возвращает:
        list: Список значений ширины дерева зависимостей для каждого предложения.
        """
        widths = []
        for doc in self.doc.sents:
            max_width = 0
            for token in doc:
                width = 0
                for child in token.children:
                    width += 1
                if width > max_width:
                    max_width = width
            widths.append(max_width)

        return widths

    def isc(self) -> float:
        """
        Вычисляет индекс структурной сложности предложений на основе глубины и ширины деревьев зависимостей.

        Возвращает:
        float: Индекс структурной сложности предложений.
        """
        return np.mean(self.tree_depth()) * np.mean(self.tree_width())

    def dep_freq(self) -> dict:
        """
        Вычисляет частоту различных типов зависимостей в тексте.

        Возвращает:
        dict: Словарь с частотой различных типов зависимостей.
        """
        result = []
        for doc in self.doc.sents:
            for token in doc:
                result.append(token.dep_)

        return Counter(result)

    def triple_pattern(self) -> list:
        """
        Извлекает тройные паттерны зависимостей из текста, исключая корневые и пунктуационные зависимости.

        Возвращает:
        list: Список троек зависимостей в формате (головное слово, зависимое слово, тип зависимости).
        """
        result = []
        for doc in self.doc.sents:
            for token in doc:
                if token.dep_ != "ROOT":
                    head = token.head
                    if token.dep_ != 'punct':
                        triple_dependency = (head.text, token.text, token.dep_)
                        result.append(triple_dependency)

        return result
import re
import stanza


nlp = stanza.Pipeline(lang='ru', processors='tokenize,pos,lemma,depparse')

def stanza_process(text) -> list:
    """Обрабатывает входной текст с использованием Stanza NLP pipeline и извлекает информацию об каждом слове в тексте.
    
    Параметры:
    text (str): Входной текст для обработки.
    
    Возвращает:
    list: Список, содержащий информацию о каждом слове в тексте в формате:
          ['word_id word_text word_upos word_head word_head_text word_deprel', ...]"""
    doc = nlp(text)
    total = []
    for sent in doc.sentences:
        for word in sent.words:
            result = f'{word.id} {word.text} {word.upos} {word.head} {sent.words[word.head-1].text if word.head > 0 else "root"} {word.deprel}'
            total.append(result)
    return total


class SyntacticComplexity:
    def __init__(self, text, stanza_processor=stanza_process):
        """
        Инициализирует объект SyntacticComplexity, вычисляющий метрики синтаксической сложности текста.

        Параметры:
        text (str): Текст для анализа синтаксической сложности.
        stanza_processor (function): Функция обработки текста на уровне предложения.
        """
        text = re.sub('(?<=\d)\s+(?=\d)', '', text)
        self.text = text

        self.stanza_processor = stanza_process

        self.parsed = []
        for sentence in re.split(r'(.*?[.!?])', self.text):
            stanza_processed = self.stanza_processor(sentence)
            if stanza_processed:
                self.parsed.append(stanza_processed)

    def sentence_count(self) -> int:
        """
        Вычисляет количество предложений в тексте.

        Возвращает:
        int: Количество предложений в тексте.
        """
        sent_count = len([t for t in re.split(r'[.!?\.]+', self.text) if len(t) > 0 and t != ' '])
        return sent_count

    def sentence_len(self) -> list:
        """
        Вычисляет длину каждого предложения в словах.

        Возвращает:
        list: Список длин предложений в тексте.
        """
        s_lens = []
        sentences = [t for t in re.split(r'[.!?\.]+', self.text) if len(t) > 0 and t != ' ']
        for sent in sentences:
            s_lens.append(len(sent.split()))
        return s_lens

    def clause_count(self) -> list:
        """
        Вычисляет количество клауз в каждом предложении.

        Возвращает:
        list: Список, включающий количество клауз в каждом предложении.
        """
        clause_count = []
        for sentence in self.parsed:
            clauses = []
            totals_verbes_id = []
            root_verb = 0
            taken_id = []
            deps = []
            for row in sentence:
                row = row.split()
                deps.append(int(row[3]))
                if row[2] == 'VERB' or row[2] == 'AUX':
                    totals_verbes_id.append(int(row[0]))
                if row[5] == 'root':
                    root_verb = int(row[0])

            if deps.count(0) == 1:
                for verb_id in totals_verbes_id:
                    if verb_id not in taken_id:
                        taken_id.append(verb_id)
                        head_id = [verb_id]
                        clause_c = 1
                        while head_id and set(head_id).issubset(deps):
                            for head in head_id:
                                dep_indexes = [i for i, ltr in enumerate(deps) if ltr == head]
                                for i in dep_indexes:
                                    clause_c += 1
                                    if sentence[i].split()[2] == 'VERB' or sentence[i].split()[2] == 'AUX':
                                        taken_id.append(i+1)
                            head_id = [i+1 for i, ltr in enumerate(deps) if ltr in head_id]
                        clauses.append(clause_c)
            if clauses:
                clause_count.append(len(clauses))
            else:
                clause_count.append(1)
        return clause_count

    def clause_len(self) -> list:
        """
        Вычисляет длину каждой клаузы в предложении.

        Возвращает:
        list: Список длин клауз в тексте.
        """
        clause_len_count = []
        for sentence in self.parsed:
            totals_verbes_id = []
            root_verb = 0
            taken_id = []
            deps = []
            for row in sentence:
                row = row.split()
                deps.append(int(row[3]))
                if row[2] == 'VERB' or row[2] == 'AUX':
                    totals_verbes_id.append(int(row[0]))
                if row[5] == 'root':
                    root_verb = int(row[0])

            if deps.count(0) == 1:
                for verb_id in totals_verbes_id:
                    if verb_id not in taken_id:
                        taken_id.append(verb_id)
                        head_id = [verb_id]
                        clause_len = 1
                        while head_id and set(head_id).issubset(deps):
                            for head in head_id:
                                dep_indexes = [i for i, ltr in enumerate(deps) if ltr == head]
                                for i in dep_indexes:
                                    clause_len += 1
                                    if sentence[i].split()[2] == 'VERB' or sentence[i].split()[2] == 'AUX':
                                        taken_id.append(i+1)
                            head_id = [i+1 for i, ltr in enumerate(deps) if ltr in head_id]
                        clause_len_count.append(clause_len)
        return clause_len_count

    def np_len(self) -> list:
        """
        Вычисляет длину каждой именной группы в предложениях.

        Возвращает:
        list: Список длин именных групп в тексте.
        """
        #nmod, amod, acl, advmod
        np_len_count = []
        deprels = ['amod', 'nmod', 'nummod', 'nummod:gov', 'acl', 'acl:relcl', 'det', 'case', 'obl', 'advmod', 'conj', 'cc']
        for sentence in self.parsed:
            totals_id = []
            taken_id = []
            deps = []
            for row in sentence:
                row = row.split()
                deps.append(int(row[3]))
                if row[2] == 'NOUN' or row[2] == 'PROPN' or row[2] == 'NUM':
                    totals_id.append(int(row[0]))

            if deps.count(0) == 1:
                for i in totals_id:
                    if i not in taken_id:
                        taken_id.append(i)
                        head_id = [i]
                        np_len = 1
                        while head_id and set(head_id).issubset(deps):
                            for head in head_id:
                                dep_indexes = [i for i, ltr in enumerate(deps) if ltr == head]
                                for i in dep_indexes:
                                    if sentence[i].split()[5] in deprels:
                                        np_len += 1
                                    if sentence[i].split()[2] == 'NOUN' or sentence[i].split()[2] == 'PROPN' or sentence[i].split()[2] == 'NUM':
                                        taken_id.append(i+1)
                            head_id = [i+1 for i, ltr in enumerate(deps) if ltr in head_id]
                        np_len_count.append(np_len)

        return np_len_count

    def compound_sent_count(self) -> int:
        """
        Подсчитывает количество сложносочиненных предложений.

        Возвращает:
        int: Количество сложносочиненных предложений.
        """
        compound_total = 0
        for sentence in self.parsed:
            root_id = 0
            for row in sentence:
                row = row.split()
                if row[5] == 'root':
                    root_id = row[0]
            for row in sentence:
                row = row.split()
                if row[3] == root_id and row[5] == 'conj':
                    compound_total += 1

        return compound_total

    def complex_sent_count(self) -> int:
        """
        Подсчитывает количество сложноподчиненных предложений.

        Возвращает:
        int: Количество сложноподчиненных предложений.
        """
        complex_total = 0
        for sentence in self.parsed:
            root_id = 0
            subject_id = 0
            mod_id = 0
            punct_id = 0
            for row in sentence:
                row = row.split()
                if row[5] == 'root':
                    root_id = row[0]
                if row[1] == ',' and row[5] == 'punct':
                    punct_id = int(row[0])
            for row in sentence:
                row = row.split()
                if row[3] == root_id and (row[2] == 'NOUN' or row[2] == 'PROPR'):
                    subject_id = row[0]
                if row[3] == root_id and (row[2] == 'ADV'):
                    mod_id = row[0]
                if (row[3] == root_id or row[3] == mod_id) and (row[5] == 'ccomp' or row[5] == 'advcl' or row[5] == 'parataxis') and (int(row[0]) > punct_id):
                    complex_total += 1
                if row[3] == subject_id and ('acl' in row[5]) and (int(row[0]) > punct_id):
                    complex_total += 1

        return complex_total

    def mean_dependency_distance(self) -> list:
        """
        Вычисляет среднее зависимостное расстояние (MDD) между словами в каждом предложении.

        Метод проходит по всем предложениям в тексте и вычисляет среднюю разницу в позициях между зависимым и главным словами.

        Возвращает:
        list: Список средних расстояний зависимости для каждого предложения.
        """
        distances = []
        for sentence in self.parsed:
            dependencies = 0
            d_distances_sum = 0
            for row in sentence:
                row = row.split()
                if row[3] != '0':
                    dependencies += 1
                    d_distances_sum = abs(int(row[3]) - int(row[0]))
            if dependencies != 0:
                distances.append(d_distances_sum/dependencies)

        return distances

words = {
    '1': 'один',
    '2': 'два',
    '3': 'три',
    '4': 'четыре',
    '5': 'пять',
    '6': 'шесть',
    '7': 'семь',
    '8': 'восемь',
    '9': 'девять',
    '10': 'десять',
    '11': 'одиннадцать',
    '12': 'двенадцать',
    '13': 'тринадцать',
    '14': 'четырнадцать',
    '15': 'пятнадцать',
    '16': 'шестнадцать',
    '17': 'семнадцать',
    '18': 'восемнадцать',
    '19': 'девятнадцать',
    '20': 'двадцать',
}


def num_to_words(text):
    values = text.split()
    try:
        result = [value if not value.isdigit() else words[value] for value in values]
        return ' '.join(result)
    except Exception as e:
        print('not in dict')
        return text

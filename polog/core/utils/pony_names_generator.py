import random


def pony_names_generator(epoch=0):
    """
    Бесконечный рандомный генератор имен поней из My Little Pony.
    Имена образуются путем рекомбинации половинок оригинальных имен из сериала.

    Исчерпав все варианты, повторяет их заново (но в другом порядке), добавив постфикс с римской записью поколения. К примеру:
    Princess Skyre II
    Derpy Pie II
    Rari Dash II

    Генератор реализован через рекурсию, так что технически он не совсем бесконечный, но на несколько десятков тысяч вариантов точно можно расчитывать.
    """
    all_names = []
    def name_generator(first_halfs, second_halfs, prefix=''):
        """
        Берем два списка с половинками имен и кладем их декартово произведение в список all_names.
        При необходимости, добавляем префиксы.
        """
        for half in first_halfs:
            for half_2 in second_halfs:
                full_name = prefix + half + half_2
                all_names.append(full_name)
    def number_generator(number):
        """
        Генератор римских цифр, взят отсюда:
        https://py.checkio.org/mission/roman-numerals/publications/mdeakyne/python-3/first/share/53882d47af904f942fc8daf06c0ed270/
        """
        ones = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"]
        tens = ["", "X", "XX", "XXX", "XL", "L", "LX", "LXX", "LXXX", "XC"]
        hunds = ["", "C", "CC", "CCC", "CD", "D", "DC", "DCC", "DCCC", "CM"]
        thous = ["", "M", "MM", "MMM", "MMMM"]
        thous = thous[number // 1000]
        hunds = hunds[number // 100 % 10]
        tens = tens[number // 10 % 10]
        ones = ones[number % 10]
        return thous + hunds + tens + ones
    name_generator(
        first_halfs = [
            'Twilight',
            'Apple',
            'Flutter',
            'Rari',
            'Pinkie',
            'Rainbow',
            'Derpy',
        ],
        second_halfs = [
            ' Sparkle',
            'jack',
            'shy',
            'ty',
            ' Pie',
            ' Dash',
            ' Hooves',
        ],
    )
    name_generator(
        first_halfs = [
            'Cad',
            'Sky',
            'Amo',
            'Cele',
            'Lu',
        ],
        second_halfs = [
            'ance',
            'star',
            're',
            'stia',
            'na',
        ],
        prefix='Princess '
    )
    random.shuffle(all_names)
    for x in all_names:
        if epoch == 0:
            yield x
        else:
            yield f'{x} {number_generator(epoch + 1)}'
    epoch += 1
    yield from pony_names_generator(epoch=epoch)

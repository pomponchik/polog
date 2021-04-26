import random


class PonyNamesGenerator:
    def get_next_pony(self, epoch=0):
        """
        "Бесконечный" рандомный генератор имен поней из My Little Pony.
        Имена образуются путем рекомбинации половинок оригинальных имен из сериала.

        Исчерпав все варианты, повторяет их заново (но в другом порядке), добавив постфикс с римской записью поколения. К примеру:
        Princess Skyre II
        Derpy Pie II
        Rari Dash II

        Генератор реализован через рекурсию, так что технически он не совсем бесконечный, но на несколько десятков тысяч вариантов точно можно расчитывать (при проверке на MacBook 70 000 комбинаций создавались, а 80 000 уже нет).
        """
        names = self.new_names_portion()
        random.shuffle(names)
        for name in names:
            if epoch == 0:
                yield name
            else:
                yield f'{name} {self.roman_numerals(epoch + 1)}'
        epoch += 1
        yield from self.get_next_pony(epoch=epoch)

    @classmethod
    def new_names_portion(cls):
        """
        Данный метод возвращает список имен, причем всегда одинаковый и в одинаковом порядке.
        """
        container = []
        cls.halfs_combinations(
            container,
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
        cls.halfs_combinations(
            container,
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
        return container

    @staticmethod
    def halfs_combinations(container, first_halfs, second_halfs, prefix=''):
        """
        Берем два списка с половинками имен и кладем их декартово произведение в список container.
        При необходимости, добавляем префиксы.
        """
        for half in first_halfs:
            for half_2 in second_halfs:
                new_name = f'{prefix}{half}{half_2}'
                container.append(new_name)

    @staticmethod
    def roman_numerals(number):
        """
        Генератор римских цифр, взят отсюда:
        https://py.checkio.org/mission/roman-numerals/publications/mdeakyne/python-3/first/share/53882d47af904f942fc8daf06c0ed270/
        """
        if number > 0:
            ones = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"]
            tens = ["", "X", "XX", "XXX", "XL", "L", "LX", "LXX", "LXXX", "XC"]
            hunds = ["", "C", "CC", "CCC", "CD", "D", "DC", "DCC", "DCCC", "CM"]
            thous = ["", "M", "MM", "MMM", "MMMM"]
            thous = thous[number // 1000]
            hunds = hunds[number // 100 % 10]
            tens = tens[number // 10 % 10]
            ones = ones[number % 10]
            return thous + hunds + tens + ones

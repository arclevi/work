class Record:
    def __init__(self, lines):
        try:
            with open(lines, encoding='gb2312') as f:
                lines = f.readlines()
        except Exception:
            pass
        lines = list(lines)
        self.title = lines[0].strip()
        assert self._title['test'] in self.title, self._title['error']
        self.serial_no = lines[1].split(':')[1].strip()
        self.temperature = lines[2].split(':')[1].strip()[:-1]
        self.date = lines[3].split(':')[1].strip()

    def insert2db(self):
        pass

    def __repr__(self):
        return f"<{str(self.__class__)[16:-2]} {self.title!r} {self.date!r} >"


class BiaoDuYinShu(Record):
    def __init__(self, lines, _title={'test': '因数', 'error': "非标度因数测试记录"}):
        self._title = _title
        super().__init__(lines)
        lines = [line.split() for line in lines if line.strip()]
        assert '因数' in lines[-3][0], "测试记录格式错误"
        self.bdys = float(lines[-3][1][:-8])
        self.xxd1 = float(lines[-2][1][:-1])
        self.xxd2 = float(lines[-1][1][:-1])
        lines = lines[5:-3]
        assert len(lines) == 81, "速率点共选择81个"
        self.lines = self.clean(lines)

    def clean(self, lines):
        def _clean(line):
            if len(line) == 2:
                return line[0][2:-3], line[1][2:-2]
            elif len(line) == 3:
                return line[1][:-3], line[2][2:-2]
            else:
                raise Exception('Error when cleaning')

        return [_clean(line) for line in lines]


class LingPian(Record):
    def __init__(self, lines, _title={'test': '零偏', 'error': "非零偏测试记录"}):
        self._title = _title
        super().__init__(lines)
        lines = [line.split() for line in lines if line.strip()]
        assert '零偏' in lines[-2][0], "测试记录格式错误"
        self.lp = float(lines[-2][1])
        self.lpwdx = float(lines[-1][1])
        lines = lines[5:-2]
        assert len(lines) == int(lines[-1][0]), "测试记录格式错误"
        self.lines = [line[1] for line in lines]
        self.mean10 = [line[2] for line in lines if len(line) == 3]

    @property
    def s10(self):
        if not hasattr(self, '_s10'):

            def _list_split(_list, n):
                return [
                    _list[i * n:(i + 1) * n] for i in range(len(_list) // n)
                ]

            def _mean(args):
                return '%.6f' % (sum(float(a) for a in args) / len(args))

            self._s10 = [_mean(n) for n in _list_split(self.lines, 10)]

        return self._s10


class YuZhiFenBianLv(Record):
    def __init__(self, lines, _title={'test': '阈值', 'error': "非阈值分辨率测试记录"}):
        self._title = _title
        super().__init__(lines)
        lines = [line.split() for line in lines if line.strip()]
        assert '分辨率' in lines[-1][0], "测试记录格式错误"
        self.yz = float(lines[-2][1][:-2])
        self.fbl = float(lines[-1][1][:-2])
        lines = lines[5:-2]
        assert len(lines) == 13, "速率点共选择13个"
        self.lines = self.clean(lines)

    def clean(self, lines):
        def _clean(line):
            if len(line) == 2:
                return line[0][2:-3], line[1][2:-2]
            elif len(line) == 3:
                return line[1][:-3], line[2][2:-2]
            else:
                raise Exception('Error when cleaning')

        return [_clean(line) for line in lines]


if __name__ == '__main__':

    def _process(path):

        try:
            with path.open(encoding='gb2312') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            with path.open(encoding='utf-8') as f:
                lines = f.readlines()
        lines = list(lines)
        if '因数' in lines[0]:
            return BiaoDuYinShu(lines)
        elif '零偏' in lines[0]:
            return LingPian(lines)
        elif '阈值' in lines[0]:
            return YuZhiFenBianLv(lines)
        else:
            raise Exception('error with open file')

    import pathlib
    libs = [_process(path) for path in pathlib.Path('10FA').glob('*.txt')]

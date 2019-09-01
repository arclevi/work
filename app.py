import click
from flask import Flask, render_template, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import DevConfig

app = Flask(__name__)
app.config.from_object(DevConfig)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class TestRecord(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String())
    serial_no = db.Column(db.String())
    temperature = db.Column(db.String())
    date = db.Column(db.String())
    bdys = db.relationship('BiaoDuYinShu', backref='tr', lazy='subquery')
    lp = db.relationship('LingPian', backref='tr', lazy='subquery')
    yzfbl = db.relationship('YuZhiFenBianLv', backref='tr', lazy='subquery')

    def __repr__(self):
        return "<TestRecord %r>" % self.title


class BiaoDuYinShu(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    bdys = db.Column(db.Float())
    xxd1 = db.Column(db.Float())
    xxd2 = db.Column(db.Float())
    data_json = db.Column(db.String())
    tr_id = db.Column(db.Integer(), db.ForeignKey('test_record.id'))

    def __repr__(self):
        return "<BiaoDuYinShu %r>" % self.tr


class LingPian(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    lp = db.Column(db.Float())
    lpwdx = db.Column(db.Float())
    data_json = db.Column(db.String())
    mean10_json = db.Column(db.String())
    tr_id = db.Column(db.Integer(), db.ForeignKey('test_record.id'))

    def __repr__(self):
        return "<BiaoDuYinShu %r>" % self.tr


class YuZhiFenBianLv(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    yz = db.Column(db.Float())
    fbl = db.Column(db.Float())
    data_json = db.Column(db.String())
    tr_id = db.Column(db.Integer(), db.ForeignKey('test_record.id'))

    def __repr__(self):
        return "<BiaoDuYinShu %r>" % self.tr


@app.shell_context_processor
def make_shell_context():
    return dict(db=db,
                TestRecord=TestRecord,
                BiaoDuYinShu=BiaoDuYinShu,
                LingPian=LingPian,
                YuZhiFenBianLv=YuZhiFenBianLv)


@app.route('/')
@app.route('/<int:page>')
def index(page=1):
    id = request.args.get('r', '1')
    test_record = TestRecord.query.get(id)
    test_records = TestRecord.query.paginate(page, 15)
    return render_template('index.html',
                           test_records=test_records,
                           test_record=test_record)


@app.cli.command()
@click.argument('_dir')
def initdb(_dir):
    import txt2sql
    import json

    def _process(path):
        try:
            with path.open(encoding='gb2312') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            with path.open(encoding='utf-8') as f:
                lines = f.readlines()
        lines = list(lines)
        if '因数' in lines[0]:
            return txt2sql.BiaoDuYinShu(lines)
        elif '零偏' in lines[0]:
            return txt2sql.LingPian(lines)
        elif '阈值' in lines[0]:
            return txt2sql.YuZhiFenBianLv(lines)
        else:
            raise Exception('error with open file')

    import pathlib
    libs = [_process(path) for path in pathlib.Path(_dir).glob('*.txt')]

    def obj2sql(obj):
        tr = TestRecord(title=obj.title,
                        serial_no=obj.serial_no,
                        temperature=obj.temperature,
                        date=obj.date)
        if 'LingPian' in str(obj.__class__):
            res = LingPian(lp=obj.lp,
                           lpwdx=obj.lpwdx,
                           data_json=json.dumps(obj.lines),
                           mean10_json=json.dumps(obj.mean10))
        elif 'BiaoDuYinShu' in str(obj.__class__):
            res = BiaoDuYinShu(
                bdys=obj.bdys,
                xxd1=obj.xxd1,
                xxd2=obj.xxd2,
                data_json=json.dumps(obj.lines),
            )
        elif 'YuZhiFenBianLv' in str(obj.__class__):
            res = YuZhiFenBianLv(
                yz=obj.yz,
                fbl=obj.fbl,
                data_json=json.dumps(obj.lines),
            )
        else:
            raise Exception('obj2sql error')
        res.tr = tr
        db.session.add(tr)
        db.session.add(res)
        db.session.commit()

    [obj2sql(lib) for lib in libs]
    click.echo('Initialized database.')

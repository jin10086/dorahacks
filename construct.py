#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gensim.models import word2vec
import jieba
import csv
import datetime
import pickle
import time
import re
import math
import random
from pyecharts import Scatter3D
from pyecharts.constants import DEFAULT_HOST
from pyecharts import Line
from pyecharts import Bar

STANDARD_CLASSES = ['购物', '数码', '服饰', '美容', '食品', '户外', '理财', '餐饮', '交通', '充值', '转账', '收款']


class RecordClassification(object):
    def __init__(self, model_filename):
        self.model = word2vec.Word2Vec.load(model_filename)
        self.standard_classes = STANDARD_CLASSES
        print('RecordClassification inited')

    def analyze_classes(self, _sentence):
        _sentence = _sentence.replace('）', '').replace('（', '').replace(' ', '')

        seg_seq = jieba.cut(_sentence, cut_all=False)
        seq_list = ' '.join(seg_seq).split(' ')

        start_score = 0.0
        class_specify = '购物'
        for sc in self.standard_classes:
            s = 0.0
            for k in seq_list:
                try:
                    s += self.model.wv.similarity(sc, k)
                except KeyError as ke:
                    pass
            if s > start_score:
                class_specify = sc
                start_score = s
        return class_specify


rc = RecordClassification('./word2vec_wx')


def get_between_days(end_date,begin_date):
    date_week_shift = dict()
    begin_date = datetime.datetime.strptime(begin_date, "%Y.%m.%d")
    end_date = datetime.datetime.strptime(end_date, "%Y.%m.%d")
    week_shift = begin_date.strftime("%Y.%m.%d")
    while begin_date <= end_date:
        date_str = begin_date.strftime("%Y.%m.%d")
        ts = time.strptime(date_str, "%Y.%m.%d")
        date_week_shift[date_str] = week_shift
        begin_date += datetime.timedelta(days=1)
        if ts.tm_wday == 6:
            week_shift = begin_date.strftime("%Y.%m.%d")
    return date_week_shift


def gen_construct(x):
    if len(x) != 0:
        for xi in x:
            xi['datetime'] = xi['datetime'].strftime('%Y.%m.%d%H')
        first_record_time = x[0]['datetime'][:10]
        last_record_time = x[-1]['datetime'][:10]
        date_week_shift = get_between_days(last_record_time, first_record_time)
        shift_data = list()
        for item in x:
            try:
                wk = date_week_shift[item['datetime'][:10]]
            except KeyError as ke:
                pass
            else:
                if item['name'] is not None:
                    class_name = rc.analyze_classes(item['name'])
                    raw = dict()
                    raw['wk'] = wk
                    raw['class_name'] = class_name
                    if isinstance( item['amount'],str):
                        raw['amount'] = float('%.2f' % float(re.search(r'\d+\.\d+', item['amount']).group()))
                    else:
                        raw['amount'] = 0.0

                    shift_data.append(raw)

        final_records = dict()
        weekday_values = list()
        for (k, v) in date_week_shift.items():
            if v not in weekday_values:
                weekday_values.append(v)
        for wv in weekday_values:
            consumption = dict()
            for sc in STANDARD_CLASSES:
                consumption[sc] = 0.0
            final_records[wv] = consumption

        for item in shift_data:
            final_records[item['wk']][item['class_name']] += item['amount']
            final_records[item['wk']][item['class_name']] = float(
                '%.2f' % math.log(final_records[item['wk']][item['class_name']] + 1))

        x_axis = weekday_values
        y_data = dict()
        for st in STANDARD_CLASSES:
            y_data[st] = list()
            for (k, v) in final_records.items():
                y_data[st].append(v[st])

        line_chart = Line("支付宝消费构成分析", width=1200,
                          height=600, )
        for (sc, index) in zip(STANDARD_CLASSES, range(0, len(STANDARD_CLASSES))):
            if index < len(STANDARD_CLASSES) - 1:
                line_chart.add(sc, x_axis, y_data[sc], is_stack=True,
                               is_fill=True, label_pos="outside", is_label_show=True)
            else:
                line_chart.add(sc, x_axis, y_data[sc], is_stack=True,
                               yaxis_name='log(e,amount)', yaxis_name_size=20,
                               yaxis_name_gap=30,
                               is_fill=True, label_pos="outside", is_label_show=True)
        line_chart.render(path=r'E:\dorahacks\templates\123.html')
        return True

if __name__ == '__main__':
    with open('data1.pickle', 'rb') as f:
        x = pickle.load(f)
    
    gen_construct(x[0])
    
    # '2017.09.1608:47'
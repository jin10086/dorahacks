import pickle
import pygal
from datetime import datetime, timedelta
from operator import itemgetter

def get_huabei():
    return 123123


def get_rank(p):
    for i in p:
        direction = i['amount'][0]
        if direction == '-':
            p[p.index(i)]['amount'] = float(i['amount'].replace('- ', ''))
        else:
            p[p.index(i)]['amount'] = 0
    rank = sorted(p, key=itemgetter('amount'), reverse=True)[:5]

    line_chart = pygal.HorizontalBar()
    line_chart.title = '消费排名'
    for i in rank:
        line_chart.add(i['name'], i['amount'])
    return line_chart


    

def get_chart(p):
    p = sorted(p, key=itemgetter('datetime'))
    date_start = p[0]['datetime']
    date_end = p[-1]['datetime']
    
    #generate a table with full dates
    table = {}
    for d in range((date_end - date_start).days + 1):
        table[date_start + timedelta(days=d)] = 0
    
    #fill in amount into the table
    for line in p:
        date = line['datetime']
        # date = datetime.strptime(line['datetime'][:10], '%Y.%m.%d')
        direction = line['amount'][0]
        if direction == '-':
            amount = float(line['amount'].replace('- ', ''))
        else: continue
        table[date] += amount
        
    series = []
    accu_amount = 0
    for date in sorted(table.keys()):
        amount = table[date]
        if date.weekday() == 0:
            accu_amount += amount
            series.append((date, accu_amount))
            accu_amount = 0
        else:
            accu_amount += amount


    datetimeline = pygal.DateTimeLine(
        x_label_rotation=45, truncate_label=-1,
        x_value_formatter=lambda dt: dt.strftime('%Y.%m.%d'))
    datetimeline.add("消费趋势", series)
    return datetimeline



def get_pie(p):

    pie = {}
    for line in p:
        direction = line['amount'][0]
        if direction == '-':
            amount = float(line['amount'].replace('- ', ''))
        else: continue
        if line['tradeType'] in pie.keys():
            pie[line['tradeType']] += amount
        else: pie[line['tradeType']] = amount
    pie_chart = pygal.Pie()
    pie_chart.title = '消费占比'
    for tradeType in pie.keys():
        pie_chart.add(tradeType, pie[tradeType])

    return pie_chart


#if '__name__' == '__main__':
#    get_chart()
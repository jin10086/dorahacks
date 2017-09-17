from flask import Flask, render_template
import charts
from cookie import pachong
from construct import gen_construct
from pyecharts.constants import DEFAULT_HOST
from construct import RecordClassification

rc = RecordClassification('./word2vec_wx')
app = Flask(__name__)


# TODO: 首页登录
@app.route('/')
def profile():
    return render_template('index.html')

@app.route('/construct')
def construct():
    return render_template('123.html')

# 展示用户画像
@app.route('/profile')
def home():
    (p, huabei) = pachong()
    chart = charts.get_chart(p).render_data_uri()
    pie = charts.get_pie(p).render_data_uri()
    rank = charts.get_rank(p).render_data_uri()
    # gen_construct(p, rc)
    return render_template('profile.html', chart=chart, pie=pie, rank=rank, huabei=huabei
                           )


if __name__ == '__main__':
    
    app.run(port=8000)

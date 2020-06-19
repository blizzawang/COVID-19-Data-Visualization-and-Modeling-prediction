"""
�༶��2019211120
ѧ�ţ�2019210628
������������
���ݣ��¹ڷ�����������ݿ��ӻ�
"""

# ʹ�õĿ�
import time
import json
import requests
from datetime import datetime
import numpy as np
import matplotlib
import matplotlib.figure
from matplotlib.font_manager import FontProperties
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

plt.rcParams['font.sans-serif'] = ['FangSong']  # ����Ĭ������
plt.rcParams['axes.unicode_minus'] = False  # �������ͼ��ʱ��������

def get_everyday_data(everyday_data_url):
    '''
    ��ȡÿ�������
    :param everyday_data_url: ���ÿ�����ݵ�·��
    :return: ����ÿ��������б���ȷ����ơ�����������
    '''
    data = json.loads(requests.get(url=everyday_data_url).json()['data'])  # ��ȡ����
    data.sort(key=lambda x: x['date'])  # �����ݰ���ʱ����������

    # ������������б������б�ȷ���б������б������б������б�
    date_list, confirm_list, suspect_list, dead_list, heal_list = list(), list(), list(), list(), list()

    # �������ݣ��õ���Ҫ������
    for item in data:
        month, day = item['date'].split('/')
        date_list.append(datetime.strptime('2020-%s-%s' % (month, day), '%Y-%m-%d'))  # ��ʽ������
        confirm_list.append(int(item['confirm']))
        suspect_list.append(int(item['suspect']))
        dead_list.append(int(item['dead']))
        heal_list.append(int(item['heal']))

    return date_list, confirm_list, suspect_list, dead_list, heal_list

def get_area_distribution_data(area_distribution_data_url):
    '''
    ��ȡ������ȷ��ֲ�����
    :param area_distribution_data_url: �������ֲ����ݵ�·��
    :return: ���ظ�����ȷ����ֵ�����
    '''
    result_data = {}  # �洢������ݵ��ֵ�
    data = json.loads(requests.get(url=area_distribution_data_url).json()['data'])['areaTree'][0]['children']  # ��ȡ����

    # �������ݣ���ȡ��Ҫ������
    for item in data:
        if item['name'] not in result_data:  # ��������������Ϊ�ֵ��key
            result_data.update({item['name']: 0})

        for city_data in item['children']:  # ��ȷ��������Ϊ�ֵ��value
            result_data[item['name']] += int(city_data['total']['confirm'])

    return result_data

def plot_curve_graph():
    '''
    ����ÿ����������ͼ
    :return:
    '''
    date_list, confirm_list, suspect_list, dead_list, heal_list = get_everyday_data(everyday_data_url)  # ��ȡÿ�������

    # ���ñ������ز���
    plt.figure('2019-nCoV����ͳ��ͼ��', facecolor='#f4f4f4', figsize=(10, 8))
    plt.title('2019-nCoV��������', fontsize=20)

    # ��ͼ
    plt.plot(date_list, confirm_list, label='ȷ��')
    plt.plot(date_list, suspect_list, label='����')
    plt.plot(date_list, heal_list, label='����')
    plt.plot(date_list, dead_list, label='����')

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))  # ��ʽ��ʱ��
    plt.gcf().autofmt_xdate()  # �Ż���ע������Զ���б����
    plt.grid(linestyle=':')  # ��ʾ����
    plt.legend()  # ��ʾͼ��
    plt.savefig('2019-nCoV��������.png')  # ����Ϊ�ļ�

def plot_distribution_graph(province_positions):
    '''
    ���Ƹ�����ȷ��ֲ�ͼ
    :param province_positions: ��ʡλ��
    :return:
    '''
    data = get_area_distribution_data(area_distribution_data_url)  # ��ȡ������ȷ��ֲ�����

    # ��ز�������
    width, height, rect, lat_min, lat_max, lon_min, lon_max = 1600, 800, [0.1, 0.12, 0.8, 0.8], 0, 60, 77, 140
    # ƥ��ͼ����ɫ
    handles = [
        matplotlib.patches.Patch(color='#ffaa85', alpha=1, linewidth=0),
        matplotlib.patches.Patch(color='#ff7b69', alpha=1, linewidth=0),
        matplotlib.patches.Patch(color='#bf2121', alpha=1, linewidth=0),
        matplotlib.patches.Patch(color='#7f1818', alpha=1, linewidth=0),
    ]
    # ����ͼ����ǩ
    labels = ['1-9��', '10-99��', '100-999��', '>1000��']

    fig = matplotlib.figure.Figure()
    # ���û�ͼ��ߴ�
    fig.set_size_inches(width / 100, height / 100)
    axes = fig.add_axes(rect)

    # �ֲ�������ͶӰ
    m = Basemap(projection='lcc', llcrnrlon=77, llcrnrlat=14, urcrnrlon=140, urcrnrlat=51, lat_1=33, lat_2=45,
                lon_0=100, ax=axes)

    # ��ȡshape�ļ���shape�ļ���Ҫ�������ǣ�����½�ֽ��ߡ������ߡ������ֽ��ߡ�
    m.readshapefile('files/shapefiles/china', 'province', drawbounds=True)
    m.readshapefile('files/shapefiles/china_nine_dotted_line', 'section', drawbounds=True)
    m.drawcoastlines(color='black')  # �޼���
    m.drawcountries(color='black')  # ������
    m.drawparallels(np.arange(lat_min, lat_max, 10), labels=[1, 0, 0, 0])  # ��������
    m.drawmeridians(np.arange(lon_min, lon_max, 10), labels=[0, 0, 0, 1])  # ��γ����

    for p_info, p_shape in zip(m.province_info, m.province):  # ����shape�ļ����õ����ʡ����
        p_name = p_info['OWNER'].strip('\x00')
        f_cname = p_info['FCNAME'].strip('\x00')
        if p_name != f_cname:  # �����ƺ���
            continue

        for key in data.keys():  # ���ò�ͬ���ݷ�Χ�������ɫ
            if key in p_name:
                if data[key] == 0:
                    color = '#f0f0f0'
                elif data[key] < 10:
                    color = '#ffaa85'
                elif data[key] < 100:
                    color = '#ff7b69'
                elif data[key] < 1000:
                    color = '#bf2121'
                else:
                    color = '#7f1818'
                break

        # ������õ���ɫ����ͼ��
        poly = Polygon(p_shape, facecolor=color, edgecolor=color)
        axes.add_patch(poly)

        pos = province_positions[p_name]
        text = p_name.replace("������", "").replace("�ر�������", "").replace("׳��", "").replace("ά���", "")\
            .replace("����", "").replace("ʡ", "").replace("��", "")  # �滻ʡ������

        # ָ���ֿⲢ���������С
        font15 = FontProperties(fname='files/fonts/simsun.ttf', size=15)
        font10 = FontProperties(fname='files/fonts/simsun.ttf', size=10)

        pset = set()
        if text not in pset:
            x, y = m(pos[0], pos[1])
            axes.text(x, y, text, fontproperties=font10, color='#00FFFF')
            pset.add(text)

    axes.legend(handles, labels, bbox_to_anchor=(0.5, -0.11), loc='lower center', ncol=4, prop=font15)
    axes.set_title("2019-nCoV�����ͼ", fontproperties=font15)
    FigureCanvasAgg(fig)
    fig.savefig('2019-nCoV�����ͼ.png')

if __name__ == '__main__':

    ts = int(time.time() * 1000)  # ʱ���
    # ���ÿ�����ݵ�·��
    everyday_data_url = 'https://view.inews.qq.com/g2/getOnsInfo?name=wuwei_ww_cn_day_counts&callback=&_=%d' % ts
    # �������ֲ����ݵ�·��
    area_distribution_data_url = 'https://view.inews.qq.com/g2/getOnsInfo?name=disease_h5&callback=&_=%d' % ts

    # ��ʡλ��
    province_positions = {
        "����ʡ": [121.7, 40.9],
        "����ʡ": [124.5, 43.5],
        "������ʡ": [125.6, 46.5],
        "������": [116.0, 39.9],
        "�����": [117.0, 38.7],
        "���ɹ�������": [110.0, 41.5],
        "���Ļ���������": [105.2, 37.0],
        "ɽ��ʡ": [111.0, 37.0],
        "�ӱ�ʡ": [114.0, 37.8],
        "ɽ��ʡ": [116.5, 36.0],
        "����ʡ": [111.8, 33.5],
        "����ʡ": [107.5, 33.5],
        "����ʡ": [111.0, 30.5],
        "����ʡ": [119.2, 32.5],
        "����ʡ": [115.5, 31.8],
        "�Ϻ���": [121.0, 31.0],
        "����ʡ": [110.3, 27.0],
        "����ʡ": [114.0, 27.0],
        "�㽭ʡ": [118.8, 28.5],
        "����ʡ": [116.2, 25.5],
        "�㶫ʡ": [113.2, 23.1],
        "̨��ʡ": [120.5, 23.5],
        "����ʡ": [108.0, 19.0],
        "����׳��������": [107.3, 23.0],
        "������": [106.5, 29.5],
        "����ʡ": [101.0, 24.0],
        "����ʡ": [106.0, 26.5],
        "�Ĵ�ʡ": [102.0, 30.5],
        "����ʡ": [103.0, 35.0],
        "�ຣʡ": [95.0, 35.0],
        "�½�ά���������": [85.5, 42.5],
        "����������": [85.0, 31.5],
        "����ر�������": [115.1, 21.2],
        "�����ر�������": [112.5, 21.2]
    }

    plot_curve_graph()  # ����ÿ����������ͼ
    plot_distribution_graph(province_positions)  # ���Ƹ�����ȷ��ֲ�����

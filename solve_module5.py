"""Ответы на 5.1–5.6 по реальным CSV из Приложения 4.

Запуск: python scripts/solve_module5.py /путь/к/Прил_4_...zip
Либо укажите каталог, содержащий четыре *_analytics.csv.
Без файлов реальные числовые ответы невозможно вычислить.
"""
import argparse
import io
import re
import sys
import zipfile
from pathlib import Path

import pandas as pd

START = pd.Timestamp('2026-01-01', tz='UTC')
END = pd.Timestamp('2026-04-01', tz='UTC')
FEB = pd.Timestamp('2026-02-01', tz='UTC')
MAR = pd.Timestamp('2026-03-01', tz='UTC')


def norm(s):
    return re.sub(r'[^a-z0-9а-яё]', '', str(s).lower())


def col(df, *names, required=True):
    cols = {norm(c): c for c in df.columns}
    for name in names:
        if norm(name) in cols:
            return cols[norm(name)]
    if required:
        raise ValueError(f"Нет одного из столбцов {names}; фактические: {list(df.columns)}")
    return None


def read_csv(source, filename):
    if source.is_dir():
        matches = list(source.glob(filename))
        if not matches:
            raise FileNotFoundError(filename)
        blob = matches[0].read_bytes()
    else:
        with zipfile.ZipFile(source) as z:
            matches = [n for n in z.namelist() if Path(n).name.lower() == filename.lower()]
            if not matches:
                raise FileNotFoundError(f'{filename} отсутствует в {source}')
            blob = z.read(matches[0])
    for encoding in ('utf-8-sig', 'utf-8', 'cp1251'):
        try:
            text = blob.decode(encoding)
            sample = text[:2000]
            sep = ';' if sample.count(';') > sample.count(',') else ','
            return pd.read_csv(io.StringIO(text), sep=sep)
        except UnicodeDecodeError:
            continue
    raise ValueError(f'Не удалось распознать кодировку {filename}')


def parse_time(series):
    return pd.to_datetime(series, errors='coerce', utc=True, dayfirst=False)


def prepare(source):
    s = read_csv(source, 'Sessions_analytics.csv')
    o = read_csv(source, 'Orders_analytics.csv')
    items = read_csv(source, 'Order_items_analytics.csv')
    products = read_csv(source, 'Shoe_models_analytics.csv')
    sessions = pd.DataFrame({
        'session_id': s[col(s,'session_id','sessionid','id')],
        'user_id': s[col(s,'user_id','userid','visitor_id','customer_id')],
        'start_time': parse_time(s[col(s,'session_start','started_at','start_time','session_start_time','session_datetime','created_at','start_datetime','session_date')]),
        'device_type': s[col(s,'device_type','device')].astype(str),
        'traffic_source': s[col(s,'traffic_source','source','channel')].astype(str),
    })
    orders = pd.DataFrame({
        'order_id': o[col(o,'order_id','orderid','id')],
        'session_id': o[col(o,'session_id','sessionid')],
        'ordered_at': parse_time(o[col(o,'order_date','order_datetime','created_at','ordered_at','order_time','date')]),
        'status': o[col(o,'status','order_status')].astype(str).str.strip().str.lower(),
    })
    user_col = col(o,'user_id','customer_id','userid',required=False)
    if user_col is not None:
        orders['user_id'] = o[user_col]
    else:
        orders = orders.merge(sessions[['session_id','user_id']].drop_duplicates('session_id'),on='session_id',how='left')
    order_items = pd.DataFrame({
        'order_id':items[col(items,'order_id','orderid')],
        'product_id':items[col(items,'shoe_model_id','model_id','product_id','shoe_id')],
        'quantity':pd.to_numeric(items[col(items,'quantity','qty','count')],errors='coerce'),
        'discount_percent':pd.to_numeric(items[col(items,'discount_percent','discount','discount_pct')],errors='coerce'),
    })
    line_total_col=col(items,'line_total','total_price','item_total','total_amount',required=False)
    unit_price_col=col(items,'unit_price','price','price_at_order','unit_price_before_discount',required=False)
    if line_total_col is not None:
        order_items['line_total'] = pd.to_numeric(items[line_total_col],errors='coerce')
    elif unit_price_col is not None:
        # В зависимости от семантики unit_price в исходном файле скидка
        # может уже быть учтена: при необходимости уточните формулу.
        order_items['line_total'] = pd.to_numeric(items[unit_price_col],errors='coerce')*order_items['quantity']*(1-order_items['discount_percent'].fillna(0)/100)
    else:
        raise ValueError('В Order_items_analytics.csv не обнаружена цена: unit_price или line_total')
    models = pd.DataFrame({
        'product_id':products[col(products,'shoe_model_id','model_id','product_id','shoe_id','id')],
        'category':products[col(products,'category')].astype(str),
    })
    # В модуле 5 учитываются заказы за январь-март, только completed.
    completed=orders[(orders.ordered_at>=START)&(orders.ordered_at<END)&(orders.status=='completed')].copy()
    scoped_sessions=sessions[(sessions.start_time>=START)&(sessions.start_time<END)].copy()
    completed_items=order_items.merge(completed[['order_id']].drop_duplicates(),on='order_id',how='inner')
    return scoped_sessions,completed,completed_items,models


def solve(source):
    sessions, orders, items, models=prepare(source)
    # 5.1 Конверсия = уникальные покупатели устройства / уникальные посетители устройства.
    visitors=sessions.groupby('device_type')['user_id'].nunique()
    purchased=orders.merge(sessions[['session_id','device_type']],on='session_id',how='inner')
    buyers=purchased.groupby('device_type')['user_id'].nunique()
    conversion=buyers.reindex(visitors.index,fill_value=0).div(visitors)
    answer1=conversion.idxmax() if not conversion.empty else 'нет данных'

    # 5.2 Первое посещение и первая завершённая покупка за <=7 суток.
    earliest_session=sessions.groupby('user_id')['start_time'].min()
    earliest_order=orders.groupby('user_id')['ordered_at'].min()
    times=pd.concat([earliest_session.rename('session'),earliest_order.rename('purchase')],axis=1).dropna()
    minutes=(times.purchase-times.session).dt.total_seconds()/60
    minutes=minutes[(minutes>=0)&(minutes<=7*24*60)]
    answer2=float(minutes.median()) if not minutes.empty else float('nan')

    # 5.3 Январская когорта: канал по первой сессии, возврат в феврале.
    first_session=sessions.sort_values(['start_time','session_id']).drop_duplicates('user_id')
    january=first_session[(first_session.start_time>=START)&(first_session.start_time<FEB)].copy()
    returned=set(sessions[(sessions.start_time>=FEB)&(sessions.start_time<MAR)]['user_id'])
    january['returned']=january.user_id.isin(returned)
    retention=january.groupby('traffic_source')['returned'].mean()
    answer3=retention.idxmax() if not retention.empty else 'нет данных'

    # 5.4 IQR = Q3-Q1, отсев значений за пределами [Q1-1.5IQR;Q3+1.5IQR].
    totals=items.groupby('order_id')['line_total'].sum()
    if totals.empty:
        answer4=0
        lower=upper=float('nan')
    else:
        q1,q3=totals.quantile([.25,.75]);iqr=q3-q1
        lower,upper=q1-1.5*iqr,q3+1.5*iqr
        answer4=int(totals.between(lower,upper,inclusive='both').sum())

    # 5.5 Корреляция Пирсона по парам (скидка, число пар) каждой позиции.
    answer5=items['discount_percent'].corr(items['quantity'])

    # 5.6 Сумма quantity по категориям товаров из завершённых заказов.
    sold=items.merge(models.drop_duplicates('product_id'),on='product_id',how='inner')
    category_quantities=sold.groupby('category')['quantity'].sum()
    answer6=category_quantities.idxmax() if not category_quantities.empty else 'нет данных'

    print('5.1:',answer1)
    print('5.2:',f'{answer2:g}' if pd.notna(answer2) else 'не определено')
    print('5.3:',answer3)
    print('5.4:',answer4)
    print('5.5:',f'{answer5:.3f}' if pd.notna(answer5) else 'не определено')
    print('5.6:',answer6)
    print('\nКонтрольные показатели для самостоятельной проверки:')
    print('Конверсии:\n',conversion.to_string())
    print('Удержание:\n',retention.to_string())
    print('Продажи по категориям:\n',category_quantities.to_string())
    print('Заказов с рассчитанной суммой:',len(totals),'нижняя/верхняя граница выбросов:',lower,upper)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path,help='ZIP-файл Приложения 4 или каталог CSV')
    args=parser.parse_args()
    if not args.source.exists():
        parser.error('Файл или каталог не найден: '+str(args.source))
    solve(args.source)

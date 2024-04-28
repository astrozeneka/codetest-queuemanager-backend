from datetime import time, datetime

from QueueDataManager import QueueDataManager
import pandas as pd
import matplotlib.pyplot as plt
queueDataManager = QueueDataManager(None)

def plotQueue():
    queueList = queueDataManager.getCollection()
    queueList = pd.DataFrame(queueList)
    queueList['create_date'] = pd.to_datetime(queueList['create_date'])
    col_list = queueList.columns.to_list()
    print()

    # Figure 1. Barchar, x is the day, y is the number of entity, categorized by "category"
    queueList['day'] = queueList['create_date'].dt.day
    queueList['day+month'] = queueList['create_date'].dt.strftime('%d-%m')
    print()
    fig, ax = plt.subplots()
    bar_data = queueList.groupby(['day+month', 'category']).size().unstack()
    bar_data.plot(kind='bar', stacked=True, ax=ax)
    plt.title('Number of queue by day and category')
    filename = 'export-' + str(datetime.now()) + '.pdf'
    plt.savefig(filename)
    return filename

if __name__ == '__main__':
    """queueList = queueDataManager.getCollection()
    queueList = pd.DataFrame(queueList)
    queueList['create_date'] = pd.to_datetime(queueList['create_date'])
    col_list = queueList.columns.to_list()
    print()

    # Figure 1. Barchar, x is the day, y is the number of entity, categorized by "category"
    queueList['day'] = queueList['create_date'].dt.day
    queueList['day+month'] = queueList['create_date'].dt.strftime('%d-%m')
    print()
    fig, ax = plt.subplots()
    bar_data = queueList.groupby(['day+month', 'category']).size().unstack()
    bar_data.plot(kind='bar', stacked=True, ax=ax)
    plt.title('Number of queue by day and category')
    plt.show()
    print()"""

from multiprocessing import Process
from roebots import csv


def sub_process(csv_path, value, n_cols, rows):
    writer = csv.MultiProcessCSVWriter(csv_path, [f'col_{x}' for x in range(n_cols)])
    for x in range(rows):
        writer.write([value] * n_cols)


if __name__ == '__main__':
    processes = [Process(target=sub_process, args=('test.csv', c, 8, 50)) for c in 'ABCDEFGHIJ']
    for p in processes:
        p.start()
    
    for p in processes:
        p.join()

    print('Done!')

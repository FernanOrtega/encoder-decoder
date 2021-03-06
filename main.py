import os
import sys
import time
from random import shuffle

import numpy as np
from sklearn.model_selection import KFold

from dataset_preprocessor import preprocess_dataset
from model_factory import fit_model, get_model
from validation import evaluate
from word_vectorizer import WordEmbeddings

np.random.seed(123)


def save_results(results, output_csv_path):
    import csv
    with open(output_csv_path, 'w') as outcsv:
        # configure writer to write standard csv file
        writer = csv.writer(outcsv, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL,
                            lineterminator='\n')
        writer.writerow(
            ['P_macro', 'R_macro', 'F1_macro', 'TNR_macro',
             'P_micro', 'R_micro', 'F1_micro', 'TNR_micro',
             'P_macro_t', 'R_macro_t', 'F1_macro_t', 'TNR_macro_t',
             'P_micro_t', 'R_micro_t', 'F1_micro_t', 'TNR_micro_t'])
        for item in results:
            writer.writerow(item)


def execute_experiments(dataset, w2v_model, n_splits, model_option, output_csv_path):
    results = []

    shuffle(dataset)
    folds = KFold(n_splits=n_splits, random_state=7, shuffle=False)
    splits = [(train_index, test_index) for train_index, test_index in folds.split(dataset)]

    x, y, label_encoder = preprocess_dataset(dataset, w2v_model)
    for train_index, test_index in splits:
        dataset_split = np.array(dataset)[test_index]
        x_train, x_test = x[train_index], x[test_index]
        y_train, y_test = y[train_index], [row[1] for row in dataset_split]
        l_sizes = [len(row[0]) for row in dataset_split]
        model = fit_model(model_option, x_train, y_train, w2v_model)
        results.append(evaluate(x_test, y_test, l_sizes, model, label_encoder))

    save_results(results, output_csv_path)


def main():
    args = sys.argv[1:]

    if len(args) != 6:
        print('Wrong number of arguments')
        print('Usage (relative paths!!): main.py <dataset path> <lang> <word2vec model path>'
              ' <# folds> <model option> <output csv path>')
        exit()

    # dir_path = os.path.dirname(os.path.realpath(__file__))
    # dataset_path = os.path.join(dir_path, args[0])
    dataset_path = args[0]
    data_set = [eval(file_line) for file_line in open(dataset_path, encoding='utf-8')]
    lang = args[1]
    start = time.time()
    # w2v_path = os.path.join(dir_path, args[2])
    w2v_path = args[2]
    w2v_model = WordEmbeddings(lang, w2v_path)
    end = time.time()
    print('WV loaded', (end - start))
    n_splits = int(args[3])
    model_option = get_model(args[4])
    # output_csv_path = os.path.join(dir_path, args[5])
    output_csv_path = args[5]

    execute_experiments(data_set, w2v_model, n_splits, model_option, output_csv_path)


if __name__ == '__main__':
    main()

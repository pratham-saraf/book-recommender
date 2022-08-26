import json
import random
import pickle
from scipy.sparse import load_npz
import csv
import time

def recommender(books):

    st = time.time()

    liked_books = books
    liked_books = list(map(str,liked_books))
    
    book_id = random.choice(liked_books)
    print(book_id)

    model = pickle.load(open("model/data/recommedation_model.sav", 'rb'))
    sparse_matrix = load_npz("model/data/sparse_matrix.npz")

    print("loaded model and sparse matrix")
    with open('model/data/book_id_map.csv', mode='r') as infile:
        reader = csv.reader(infile)
        next(reader)
        book_id_to_row = {}
        row_to_book_id = {}
        for row in reader:
            book_id_to_row[int(row[1])] = int(row[0])
            row_to_book_id[int(row[0])] = int(row[1])

    query_id = book_id_to_row[int(book_id)]
    query = sparse_matrix[query_id,:].toarray().reshape(1,-1)
    indices = model.kneighbors(query, n_neighbors=100, return_distance=False)
    indices = indices[0]
    results = []
    for i in indices:
        results.append({"book_id":f"{row_to_book_id[i]}"})
    results = json.dumps(results)
    print(time.time()-st)
    return results
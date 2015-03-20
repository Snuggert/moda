def mapper(k, v):
    return {'id2': k, 'data': str(v)}


def reducer(docs):
    return ',   '.join(map(str, [v for k, v in docs]))

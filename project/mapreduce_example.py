def mapper(docs):
    return [{'id2': k, 'data': str(v)} for k, v in docs]


def reducer(docs):
    return ',   '.join(map(str, docs))

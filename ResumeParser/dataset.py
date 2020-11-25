import utils

def read_data():
    train=utils.convert_json_to_spacy("D:\\ProjectProd\\Resume_Parser\\input\\train_1.json")

    test=utils.convert_json_to_spacy("D:\\ProjectProd\\Resume_Parser\\input\\test.json")

    return train,test
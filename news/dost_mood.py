# pipenv install dostoevsky
# INCOMPATIBLE WITH scikit-learn == 0.19.2 !!!!!!!!!!!!!!!!!!!
#
# from dostoevsky.tokenization import RegexTokenizer
# from dostoevsky.models import FastTextSocialNetworkModel
#
#
# class RuModel(FastTextSocialNetworkModel):
#     # Переопределяем метод __init__, чтобы работал путь к модельке
#     MODEL_PATH = 'news/models/fasttext-social-network-model.bin'
#     tokenizer = RegexTokenizer()
#
#     def __init__(self, lemmatize: bool = False):
#         super(FastTextSocialNetworkModel, self).__init__(
#             tokenizer=self.tokenizer,
#             lemmatize=lemmatize,
#             model_path=self.MODEL_PATH,
#             corpus=None
#         )

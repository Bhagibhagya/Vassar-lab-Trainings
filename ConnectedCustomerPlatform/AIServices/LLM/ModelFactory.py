from langchain_community.chat_models import *
from langchain_community.embeddings import *

LLM_MODEL_MAPPING = {
    "LlamaEdgeChatService": LlamaEdgeChatService,
    "ChatOpenAI": ChatOpenAI,
    "BedrockChat": BedrockChat,
    "AzureChatOpenAI": AzureChatOpenAI,
    "FakeListChatModel": FakeListChatModel,
    "PromptLayerChatOpenAI": PromptLayerChatOpenAI,
    "ChatDatabricks": ChatDatabricks,
    "ChatDeepInfra": ChatDeepInfra,
    "ChatEverlyAI": ChatEverlyAI,
    "ChatAnthropic": ChatAnthropic,
    "ChatCohere": ChatCohere,
    "ChatGooglePalm": ChatGooglePalm,
    "ChatMlflow": ChatMlflow,
    "ChatMLflowAIGateway": ChatMLflowAIGateway,
    "ChatOllama": ChatOllama,
    "ChatVertexAI": ChatVertexAI,
    "JinaChat": JinaChat,
    "ChatHuggingFace": ChatHuggingFace,
    "HumanInputChatModel": HumanInputChatModel,
    "MiniMaxChat": MiniMaxChat,
    "ChatAnyscale": ChatAnyscale,
    "ChatLiteLLM": ChatLiteLLM,
    "ChatLiteLLMRouter": ChatLiteLLMRouter,
    "ErnieBotChat": ErnieBotChat,
    "ChatJavelinAIGateway": ChatJavelinAIGateway,
    "ChatKonko": ChatKonko,
    "PaiEasChatEndpoint": PaiEasChatEndpoint,
    "QianfanChatEndpoint": QianfanChatEndpoint,
    "ChatTongyi": ChatTongyi,
    "ChatFireworks": ChatFireworks,
    "ChatYandexGPT": ChatYandexGPT,
    "ChatBaichuan": ChatBaichuan,
    "ChatHunyuan": ChatHunyuan,
    "GigaChat": GigaChat,
    "ChatSparkLLM": ChatSparkLLM,
    "VolcEngineMaasChat": VolcEngineMaasChat,
    "GPTRouter": GPTRouter,
    "ChatYuan2": ChatYuan2,
    "ChatZhipuAI": ChatZhipuAI,
}


EMBEDDING_MODEL_MAPPING = {
    "OpenAIEmbeddings": OpenAIEmbeddings,
    "AzureOpenAIEmbeddings": AzureOpenAIEmbeddings,
    "BaichuanTextEmbeddings": BaichuanTextEmbeddings,
    "ClarifaiEmbeddings": ClarifaiEmbeddings,
    "CohereEmbeddings": CohereEmbeddings,
    "DatabricksEmbeddings": DatabricksEmbeddings,
    "ElasticsearchEmbeddings": ElasticsearchEmbeddings,
    "FastEmbedEmbeddings": FastEmbedEmbeddings,
    "HuggingFaceEmbeddings": HuggingFaceEmbeddings,
    "HuggingFaceInferenceAPIEmbeddings": HuggingFaceInferenceAPIEmbeddings,
    "InfinityEmbeddings": InfinityEmbeddings,
    "GradientEmbeddings": GradientEmbeddings,
    "JinaEmbeddings": JinaEmbeddings,
    "LlamaCppEmbeddings": LlamaCppEmbeddings,
    "LLMRailsEmbeddings": LLMRailsEmbeddings,
    "HuggingFaceHubEmbeddings": HuggingFaceHubEmbeddings,
    "MlflowEmbeddings": MlflowEmbeddings,
    "MlflowCohereEmbeddings": MlflowCohereEmbeddings,
    "MlflowAIGatewayEmbeddings": MlflowAIGatewayEmbeddings,
    "ModelScopeEmbeddings": ModelScopeEmbeddings,
    "TensorflowHubEmbeddings": TensorflowHubEmbeddings,
    "SagemakerEndpointEmbeddings": SagemakerEndpointEmbeddings,
    "HuggingFaceInstructEmbeddings": HuggingFaceInstructEmbeddings,
    "MosaicMLInstructorEmbeddings": MosaicMLInstructorEmbeddings,
    "SelfHostedEmbeddings": SelfHostedEmbeddings,
    "SelfHostedHuggingFaceEmbeddings": SelfHostedHuggingFaceEmbeddings,
    "SelfHostedHuggingFaceInstructEmbeddings": SelfHostedHuggingFaceInstructEmbeddings,
    "FakeEmbeddings": FakeEmbeddings,
    "DeterministicFakeEmbedding": DeterministicFakeEmbedding,
    "AlephAlphaAsymmetricSemanticEmbedding": AlephAlphaAsymmetricSemanticEmbedding,
    "AlephAlphaSymmetricSemanticEmbedding": AlephAlphaSymmetricSemanticEmbedding,
    "SentenceTransformerEmbeddings": SentenceTransformerEmbeddings,
    "GooglePalmEmbeddings": GooglePalmEmbeddings,
    "MiniMaxEmbeddings": MiniMaxEmbeddings,
    "VertexAIEmbeddings": VertexAIEmbeddings,
    "BedrockEmbeddings": BedrockEmbeddings,
    "DeepInfraEmbeddings": DeepInfraEmbeddings,
    "EdenAiEmbeddings": EdenAiEmbeddings,
    "DashScopeEmbeddings": DashScopeEmbeddings,
    "EmbaasEmbeddings": EmbaasEmbeddings,
    "OctoAIEmbeddings": OctoAIEmbeddings,
    "SpacyEmbeddings": SpacyEmbeddings,
    "NLPCloudEmbeddings": NLPCloudEmbeddings,
    "GPT4AllEmbeddings": GPT4AllEmbeddings,
    "XinferenceEmbeddings": XinferenceEmbeddings,
    "LocalAIEmbeddings": LocalAIEmbeddings,
    "AwaEmbeddings": AwaEmbeddings,
    "HuggingFaceBgeEmbeddings": HuggingFaceBgeEmbeddings,
    "ErnieEmbeddings": ErnieEmbeddings,
    "JavelinAIGatewayEmbeddings": JavelinAIGatewayEmbeddings,
    "OllamaEmbeddings": OllamaEmbeddings,
    "QianfanEmbeddingsEndpoint": QianfanEmbeddingsEndpoint,
    "JohnSnowLabsEmbeddings": JohnSnowLabsEmbeddings,
    "VoyageEmbeddings": VoyageEmbeddings,
    "BookendEmbeddings": BookendEmbeddings,
    "VolcanoEmbeddings": VolcanoEmbeddings,
    "OCIGenAIEmbeddings": OCIGenAIEmbeddings,
}




class ModelFactory:
    
    model_mapping : dict = {}
    
    def __init__(self, model_mapping):
        self.model_mapping = model_mapping

    def create_model_instance(self, model_map_name, **kwargs):
        # print(self.model_mapping, model_map_name)
        model = self.model_mapping.get(model_map_name)
        if model:
            try:
                return model(**kwargs)
            except TypeError as e:
                raise TypeError(f"Error creating model instance for '{model_map_name}': {e}")
        else:
            raise ValueError(f"Model '{model_map_name}' not found in the model mapping.")
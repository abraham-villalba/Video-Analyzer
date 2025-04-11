from api.config import Config
from langchain_ollama.chat_models import ChatOllama
from langchain_openai.chat_models import ChatOpenAI
from api.utils.logger import logger
from api.utils.schemas import TopicResponse
from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

LANGUAGES = {
    'en': 'english',
    'es': 'spanish',
    'fr': 'french',
    'de': 'deutch',
    'infer': 'infer'
}

def extract_topics(transcript: str, language: str, keyframes_descriptions: list) -> list:
    """
    Extract topics from a transcript and keyframe descriptions using an LLM.

    :param transcript: The video transcript.
    :type transcript: str
    :param language: Language code or "infer".
    :type language: str
    :param keyframes_descriptions: Descriptions of keyframes.
    :type keyframes_descriptions: list
    :returns: A list of extracted topics.
    :rtype: list
    """
    # LLM Selection
    logger.info(f"Extracting topics from for transcript and {len(keyframes_descriptions)} keyframe descriptions in {language}. Using ({Config.LLM_MODEL},{Config.LLM_WRAPPER})")
    if Config.LLM_WRAPPER == 'openai':
        model = ChatOpenAI(
                    api_key=Config.OPENAI_API_KEY, 
                    model=Config.LLM_MODEL,
                    temperature=0.2,
                    max_tokens=300,
                    timeout=None,
                    max_retries=2
                )
    else:
        model = ChatOllama(model=Config.LLM_MODEL, temperature=0.2, max_tokens=300)
    
    language_instructions = "" if language == "infer" else f"The topics must be in {LANGUAGES.get(language, 'english')}"
    system_prompt = f"Extract the main topics from the video transcript and keyframe descriptions. {language_instructions} Provide 7 topics as maximum."
    
    desc = '\n'.join([f'Frame {i + 1}: {desc}' for i, desc in enumerate(keyframes_descriptions)])
    prompt = f"Transcript: {transcript}\nKeyframe descriptions: {desc}"
    
    try:
        structured_model = model.with_structured_output(TopicResponse)
        result = structured_model.invoke(
            [
                SystemMessage(
                    content=system_prompt
                ),
                HumanMessage(content=prompt)
            ]
        )
        topics = result.topics
    except Exception as e:
        logger.error(f"Error while extracting topics... {str(e)}")
        topics = []
    
    logger.debug(f"Topics extracted: {topics}")
    return topics

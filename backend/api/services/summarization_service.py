from api.config import Config
from langchain_ollama.chat_models import ChatOllama
from langchain_openai.chat_models import ChatOpenAI
from api.utils.logger import logger
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

# LLM Selection
if Config.LLM_WRAPPER == 'openai':
    logger.info(f"Using OpenAI models for summarization -> {Config.LLM_MODEL}")
    model = ChatOpenAI(
                api_key=Config.OPENAI_API_KEY, 
                model=Config.LLM_MODEL,
                temperature=0.2,
                max_tokens=300,
                timeout=None,
                max_retries=2
            )
else:
    logger.info(f"Using Ollama models for summarization -> {Config.LLM_MODEL}")
    model = ChatOllama(model=Config.LLM_MODEL, temperature=0.2, max_tokens=300)


def generate_transcript_summary(transcript: str, summary_type = 'concise', language="infer"):
    """
    Generate a summary based on a transcript using an LLM.

    :param transcript: The transcript to summarize
    :type transcript: str
    :param summary_type: Type of summary to generate, either concise or detailed.
    :type summary_type: str
    :param language: Language to generate the transcript summary
    :type language: str
    """
    logger.info(f"Generating summary for transcript in a {summary_type} way ({language}).")
    language_instructions = "" if language == "infer" else f"Your summary must be in {LANGUAGES.get(language, 'english')}"
    prompt = f"Summarize the following text in a {summary_type} way, use {'100' if summary_type == 'concise' else '200'} words. {language_instructions} Provide the result without introductions."
    try:
        result = model.invoke(
            [
                SystemMessage(
                    content=prompt
                ),
                HumanMessage(content=transcript)
            ]
        )
        summary = result.content
    except Exception as e:
        logger.error(f"Error while generating transcript summary... {e}")
        summary = ""
    
    logger.debug(f"Summary result: {summary}")
    return summary

def generate_holistic_summary(transcript: str, keyframes_descriptions: list, summary_type = "concise", language = "infer") -> str:
    """
    Generate a holistic summary based on a trascript and keyframe descriptions using an LLM.

    :param transcript: The transcript to summarize
    :type transcript: str
    :param keyframes_descriptions: The keyframe descriptions to use to generate summary.
    :type keyframes_descriptions: list
    :param language: Language to generate the holistic summary
    :type language: str
    :return: The generated holistic summary
    """
    logger.info(f"Generating holistic summary for transcript and {len(keyframes_descriptions)} keyframe descriptions in a {summary_type} way ({language}).")
    language_instructions = "" if language == "infer" else f"Your summary must be in {LANGUAGES.get(language, 'english')}"
    system_prompt = f"Summarize the following video using the following transcript and keyframe descriptions in a {summary_type} way, use {'100' if summary_type == 'concise' else '200'} words. {language_instructions} Provide the result without introductions."
    desc = '\n'.join([f'Frame {i + 1}: {desc}' for i, desc in enumerate(keyframes_descriptions)])
    prompt = f"Transcript: {transcript}\nKeyframe descriptions: {desc}"
    logger.debug(f"Prompt: {system_prompt}\n{prompt}")
    try:
        result = model.invoke(
            [
                SystemMessage(
                    content=system_prompt
                ),
                HumanMessage(content=prompt)
            ]
        )
        summary = result.content
    except Exception as e:
        logger.error(f"Error while generating transcript summary... {e}")
        summary = ""
    
    logger.debug(f"Summary result: {summary}")
    return summary
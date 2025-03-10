import datetime

from google import genai
from google.genai import types
from google.genai.types import Part

from constant import ARTICLE_TYPE_TRANSLATION, NO_RESULT
from logger import logger
from src.tools.import_tools import qdrant_tools
from src.tools.search.search_article_core import SearchArticle


class LLMClient:
    def __init__(self, model_name: str, api_key: str, sys_instruct: str, config):
        """
        Initialize the LLMApiClient using the chat conversation API.

        Args:
            model_name (str): The name of the language model to use (e.g., "gemini-pro", "gemini-2.0-flash").
            api_key (str): The API key for accessing the LLM service.
            sys_instruct (str, optional): System instructions (not directly used in this chat API example). Defaults to None.
        """
        self.search_article = SearchArticle(config)
        self.sys_instruct = sys_instruct
        self.api_key = api_key
        self.model_name = model_name
        try:
            self.chat_session = self._initialize_client(self.sys_instruct, self.api_key, self.model_name)
            logger.info(f"LLMClient initialized for model: {model_name}")
        except Exception as e:
            logger.info(f"Error initializing LLMClient: {e}")
            self.chat_session = None  # Handle initialization failure

    def _initialize_client(self, sys_instruct, api_key, model_name):
        """
        Initializes the Google Generative AI client.
        """
        try:
            client = genai.Client(vertexai=False, api_key=api_key)
            chat = client.chats.create(
                model=model_name,
                config=types.GenerateContentConfig(
                    system_instruction=sys_instruct,
                    tools=[qdrant_tools],
                ),
            )
            logger.debug("Successfully initialized genai client.")
            return chat
        except Exception as e:
            logger.info(f"Error initializing genai client: {e}")
            raise  # Re-raise the exception to be handled in the caller (init)

    def _filter_fileds(self, response, start_date, end_date):
        """
        Filter the fields from the response.
        """
        brand = None
        writer_name = None
        publish_time_start = None
        publish_time_end = None
        query = None
        primary_section = None
        secondary_section = None
        tags = None
        url = []
        article_type = []
        parts = []

        names = [fc.name for fc in response.function_calls]
        logger.info(f"Received function calls: {names}")
        if "filter_brand" in names:
            brand = [r.args["brand"] for r in response.function_calls if r.name == "filter_brand"][0]
            parts.append(
                Part.from_function_response(
                    name="filter_brand",
                    response={
                        "brand": brand,
                    },
                )
            )
        if "filter_writer_name" in names:
            writer_name = [r.args["writer_name"] for r in response.function_calls if r.name == "filter_writer_name"][0]
            parts.append(
                Part.from_function_response(
                    name="filter_writer_name",
                    response={
                        "writer_name": writer_name,
                    },
                )
            )
        # if "filter_articles_by_time_range" in names:
        #     publish_time_start = [
        #         r.args["publish_time_start"]
        #         for r in response.function_calls
        #         if r.name == "filter_articles_by_time_range"
        #     ][0]
        #     publish_time_end = [
        #         r.args["publish_time_end"] for r in response.function_calls if r.name == "filter_articles_by_time_range"
        #     ][0]
        #     parts.append(
        #         Part.from_function_response(
        #             name="filter_articles_by_time_range",
        #             response={
        #                 "publish_time_start": publish_time_start,
        #                 "publish_time_end": publish_time_end,
        #             },
        #         )
        #     )
        # if "filter_articles_last_day" in names:
        #     publish_time_start = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        #     publish_time_end = datetime.datetime.now().strftime("%Y-%m-%d")
        #     parts.append(
        #         Part.from_function_response(
        #             name="filter_articles_last_day",
        #             response={
        #                 "publish_time_start": (datetime.datetime.now() - datetime.timedelta(days=1)).strftime(
        #                     "%Y-%m-%d"
        #                 ),
        #                 "publish_time_end": datetime.datetime.now().strftime("%Y-%m-%d"),
        #             },
        #         )
        #     )
        # if "filter_articles_last_week" in names:
        #     publish_time_start = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
        #     publish_time_end = datetime.datetime.now().strftime("%Y-%m-%d")
        #     parts.append(
        #         Part.from_function_response(
        #             name="filter_articles_last_week",
        #             response={
        #                 "publish_time_start": (datetime.datetime.now() - datetime.timedelta(days=7)).strftime(
        #                     "%Y-%m-%d"
        #                 ),
        #                 "publish_time_end": datetime.datetime.now().strftime("%Y-%m-%d"),
        #             },
        #         )
        #     )
        # if "filter_articles_last_month" in names:
        #     publish_time_start = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        #     publish_time_end = datetime.datetime.now().strftime("%Y-%m-%d")
        #     parts.append(
        #         Part.from_function_response(
        #             name="filter_articles_last_month",
        #             response={
        #                 "publish_time_start": (datetime.datetime.now() - datetime.timedelta(days=30)).strftime(
        #                     "%Y-%m-%d"
        #                 ),
        #                 "publish_time_end": datetime.datetime.now().strftime("%Y-%m-%d"),
        #             },
        #         )
        #     )
        if "filter_primary_section" in names:
            primary_section = [
                r.args["primary_section"] for r in response.function_calls if r.name == "filter_primary_section"
            ][0]
            parts.append(
                Part.from_function_response(
                    name="filter_primary_section",
                    response={
                        "primary_section": primary_section,
                    },
                )
            )
        if "filter_secondary_section" in names:
            secondary_section = [
                r.args["secondary_section"] for r in response.function_calls if r.name == "filter_secondary_section"
            ][0]
            parts.append(
                Part.from_function_response(
                    name="filter_secondary_section",
                    response={
                        "secondary_section": secondary_section,
                    },
                )
            )
        if "filter_tags" in names:
            tags = [r.args["tags"] for r in response.function_calls if r.name == "filter_tags"][0]
            parts.append(
                Part.from_function_response(
                    name="filter_tags",
                    response={
                        "tags": tags,
                    },
                )
            )
        if "filter_article_type" in names:
            article_type = [r.args["article_type"] for r in response.function_calls if r.name == "filter_article_type"][
                0
            ]
            article_type = ARTICLE_TYPE_TRANSLATION.get(article_type)
            parts.append(
                Part.from_function_response(
                    name="filter_article_type",
                    response={
                        "article_type": article_type,
                    },
                )
            )

        if "analyze_article_content" in names:
            url = [r.args["url"] for r in response.function_calls if r.name == "analyze_article_content"][0]

            _return = self.search_article.retrieve_documents_by_payload(
                brand,
                writer_name,
                publish_time_start,
                publish_time_end,
                primary_section,
                secondary_section,
                tags,
                article_type,
                url,
            )
            parts.append(
                Part.from_function_response(
                    name="get_articles",
                    response={
                        "content": _return,
                    },
                ),
            )
        if "get_articles" in names:
            query = [r.args["query"] for r in response.function_calls if r.name == "get_articles"][0]
            _return = self.search_article.retrieve_relevant_documents(
                query,
                brand,
                writer_name,
                start_date,
                end_date,
                primary_section,
                secondary_section,
                tags,
                article_type,
            )
            if (
                publish_time_end is not None
                and publish_time_start is not None
                and publish_time_start > publish_time_end
            ):
                publish_time_start, publish_time_end = publish_time_end, publish_time_start

            logger.debug(
                f"find: {len(_return)} articles for query: {query}, brand: {brand}, writer_name: {writer_name}, publish_time_start: {publish_time_start}, publish_time_end: {publish_time_end}, primary_section: {primary_section}, secondary_section: {secondary_section}, tags: {tags}, article_type: {article_type}"
            )
            if len(_return) == 0:
                _return = NO_RESULT
                if query:
                    _return += f" עבור השאילתה '{query}'"
                if publish_time_start:
                    _return += f" בטווח הזמן {publish_time_start} עד {publish_time_end}"
                if brand:
                    _return += f" במותג {brand}"
                if writer_name:
                    _return += f" על ידי {' '.join(writer_name)}"
                if primary_section:
                    _return += f" בקטגוריה {', '.join(primary_section)}"
                if secondary_section:
                    _return += f" בתת קטגוריה {', '.join(secondary_section)}"
                if tags:
                    _return += f" עם התגים {' '.join(tags)}"
                if article_type:
                    _return += f" בסוג המאמר {article_type}"

            parts.append(
                Part.from_function_response(
                    name="get_articles",
                    response={
                        "content": _return,
                    },
                ),
            )

        logger.info(
            f"Received response from LLM: query='{query}', brand='{brand}', writer_name='{writer_name}', publish_time_start='{publish_time_start}', publish_time_end='{publish_time_end}', primary_section='{primary_section}', secondary_section='{secondary_section}', tags='{tags}', article_type='{article_type}, url='{url}'"
        )

        return parts

    def send_message(self, message: str, start_date, end_date) -> str:
        """
        Sends a message within the chat session and returns the response text.

        Args:
            message (str): The user message to send.

        Returns:
            str: The text response from the LLM.
            None: If there was an error during the API call.
        """
        logger.debug(f"Sending message to LLM: {message}")
        response = self.chat_session.send_message(
            message,
            config=types.GenerateContentConfig(
                system_instruction=self.sys_instruct,
                tools=[qdrant_tools],
            ),
        )

        if response.candidates[0].finish_message:
            logger.info("Resetting chat session.")
            self.chat_session = self._initialize_client(self.sys_instruct, self.api_key, self.model_name)
            return "שגיאה. מאפס צאט"

        if not response.function_calls:
            if response.text is None:
                logger.exception("Error in response from LLM.")
                logger.info(f"Message that caused error: {message}")
                return "שגיאה. נסה שוב"
            return response

        parts = self._filter_fileds(response, start_date, end_date)

        logger.info(f"Sending message with parts: {[p.function_response.name for p in parts]}")
        if len(parts) != len(response.function_calls):
            logger.info(f"Error in parts: {parts}")
            logger.info(f"Error in response: {response.function_calls}")
            return "שגיאה. נסה שוב"
        try:
            response = self.chat_session.send_message(parts)
        except Exception as e:
            logger.info(f"Error sending message to LLM: {e}")
            return "שגיאה. נסה שוב"
        return response

    def reset_chat_session(self):
        """
        Reset the chat session.
        """
        logger.info("Resetting chat session.")
        self.chat_session = self._initialize_client(self.sys_instruct, self.api_key, self.model_name)


if __name__ == "__main__":
    import datetime

    from utility.replace_placeholder import replace_placeholder

    from config.load_config import load_config

    try:
        prompts = load_config("config/prompts.yaml")
    except Exception as e:
        logger.info(f"Error loading prompts config: {e}")
        print("Error loading prompts configuration. Check logs for details.")
        exit(1)

    sys_instruct = prompts["system_instructions"]

    sys_instruct = replace_placeholder(sys_instruct, "{currentDateTime}", datetime.datetime.now().strftime("%Y-%m-%d"))

    try:
        config = load_config("config/config.yaml")
    except Exception as e:
        logger.info(f"Error loading main config: {e}")
        print("Error loading main configuration. Check logs for details.")
        exit(1)

    api_key = config["llm"].get("GOOGLE_API_KEY")
    model_name = config["llm"].get("llm_model_name", "gemini-pro")

    if not api_key:
        logger.error("API Key not found in config.yaml. Please configure 'GOOGLE_API_KEY'.")
        exit(1)

    try:
        llm_client = LLMClient(model_name=model_name, api_key=api_key, sys_instruct=sys_instruct, config=config)
    except Exception as e:
        logger.info(f"Error initializing LLMClient in main: {e}")
        print("Failed to initialize LLMApiClient. Check logs for errors.")
        exit(1)

    if llm_client and llm_client.chat_session:  # Check if client and session are initialized
        print("Start chatting with the LLM (non-streaming). Type 'quit' to exit.")
        while True:
            user_message = input("You: ")
            if user_message.lower() == "quit":
                break

            response = llm_client.send_message(user_message)
            print("LLM: " + response.text)
    else:
        print("Failed to initialize LLMApiClient properly. Check logs for errors during initialization.")

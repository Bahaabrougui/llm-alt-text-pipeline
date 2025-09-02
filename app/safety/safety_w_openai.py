import json
import os
import re
import time

import yaml
from typing import Dict, Tuple, cast, Iterable

from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

from app.define import AZURE_COGNITIVE_SERVICES_SCOPE, \
    OUTPUT_PRICE_PER_1_K, INPUT_PRICE_PER_1_K, APPLICATION_PATH_FUNCTION_APP
from app.utils.utils import log_metrics, log_warning


class AltTextOpenAISafetyChecker:
    def __init__(self, toxicity_threshold=0.3):
        # Init azure openAI using MI
        self.client = AzureOpenAI(
            api_version=os.environ["AZURE_OPENAI_API_VERSION"],
            azure_endpoint=os.environ["AZURE_OPENAI_API_ENDPOINT"],
            azure_ad_token_provider=get_bearer_token_provider(
                DefaultAzureCredential(),
                AZURE_COGNITIVE_SERVICES_SCOPE,
            ),
        )
        self._toxicity_threshold = toxicity_threshold
        # Load prompts
        with open(os.path.join(
                APPLICATION_PATH_FUNCTION_APP, "prompts/gpt.yaml"
        ), "r") as gpt_prompt_file:
            gpt_prompt_file_content = yaml.safe_load(gpt_prompt_file)
            self._system_prompt = gpt_prompt_file_content["gpt"]["system"][
                os.environ["GPT_PROMPT_VERSION"]
            ]
            self._user_prompt = gpt_prompt_file_content["gpt"]["user"][
                os.environ["GPT_PROMPT_VERSION"]
            ]

    def call_az_open_ai_api_with_message(
            self,
            prompt: str,
            model: str,
            max_tokens=50,
            temperature=0,
    ) -> Tuple[str, Dict[str, int]]:
        """Calls azure openAI API."""
        response = self.client.completions.create(
            model=model,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        # Extract actual response and usage
        text_response, usage = (response.choices[0].text.strip(),
                                cast(Dict[str, int], response.usage.to_dict()))

        return text_response, usage

    def is_safe(self, text: str) -> dict:
        _start_ = time.time()
        safety_model_response, safety_model_usage = self.call_az_open_ai_api_with_message(
            model=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
            prompt=f"{self._system_prompt.strip()}\n\n"
                   f"User: {self._user_prompt.strip()}\n"
                   f"Moderator:"

        )
        try:
            safety_model_response_fixed = re.search(r"\{.*\}", safety_model_response, re.S).group(0)
            safety_json = json.loads(safety_model_response_fixed)
        except Exception:
            log_warning(
                f"Could not parse {os.environ['AZURE_OPENAI_DEPLOYMENT_NAME']} response",
                extra={"response": safety_model_response}
            )
            safety_json = {
                "is_safe": False,
                "toxicity": 99.0,
                "too_short": False,
                "too_long": False,
                "profanity": False
            }

        # Cost estimate
        prompt_tokens = safety_model_usage["prompt_tokens"]
        completion_tokens = safety_model_usage["completion_tokens"]
        cost = (prompt_tokens *
                INPUT_PRICE_PER_1_K[os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"]] +
                completion_tokens *
                OUTPUT_PRICE_PER_1_K[os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"]]
                ) / 1000

        log_metrics(
            os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
            input_tokens=prompt_tokens,
            output_tokens=completion_tokens,
            total_tokens=safety_model_usage["total_tokens"],
            cost_usd=cost,
            start=_start_,
            text=text,
            is_safe=safety_json["is_safe"],
            toxicity=safety_json["toxicity"]
        )

        return safety_json

import os
from dotenv import load_dotenv
from supabase import create_client
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.schema import BaseOutputParser
import json

class AccountSchema(BaseModel):
    name: str = Field(description="Name of the account")
    currency: str = Field(description="3-letter ISO currency code (e.g. USD, EUR, GEL)")
    initial_balance: float = Field(description="Initial balance as a float")

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_prompt_from_supabase(code: str) -> str:
    result = (
        supabase.table("agent_prompts")
        .select("prompt, model, instructions")
        .eq("is_active", True)
        .eq("type_id", (
            subquery_result := supabase.table("agent_prompt_types")
            .select("id")
            .eq("code", code)
            .execute()
        ).data[0]["id"] if subquery_result.data else ValueError(f"No prompt type found for code '{code}'"))
        .limit(1)
        .execute()
    )
    if not result.data:
        raise ValueError(f"No active prompt found for code '{code}'")
    return result.data[0]["prompt"], result.data[0]["model"], result.data[0]["instructions"]

def get_account_initializer_agent():
    prompt_template_str, model, instructions = get_prompt_from_supabase("account_initializer")

    prompt = ChatPromptTemplate.from_template(
        prompt_template_str + "\n\n{format_instructions}"
    )
    parser: BaseOutputParser = JsonOutputParser(pydantic_object=AccountSchema)

    llm = ChatOpenAI(temperature=0, model=model)
    chain = prompt | llm | parser
    return chain, instructions or parser.get_format_instructions()

def parse_account_message(message: str) -> dict:
    chain, format_instructions = get_account_initializer_agent()

    try:
        raw_output = chain.invoke({
            "input": message,
            "format_instructions": format_instructions
        })

        if isinstance(raw_output, str):
            return json.loads(raw_output)

        if isinstance(raw_output, dict):
            return raw_output

    except Exception as e:
        print("❌ Parsing failed:", e)

    return {}
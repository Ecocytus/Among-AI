# define your keys here
from secret import openai_org, openai_key, claude_key

import openai
import anthropic

import asyncio
from functools import wraps, partial

def async_wrap(func):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)
    return run

class Hacker:
    def __init__(self, game_definition: str):
        self.prev_prompt = ""
        self.game_definition = game_definition
        
    # child class implements this
    def call(self, prompt):
        pass
    
    def analysis(self, input: str, prompt: str):
        analysis_prompt = self.game_definition + "\n" + input + "\n" + prompt
        analysis_answer = self.call(analysis_prompt)
        self.prev_prompt += analysis_prompt + "\n" + analysis_answer
        print("[analysis prompt]\n" + analysis_prompt + "\n[analysis answer]\n" + analysis_answer)
        return analysis_answer
        
    def ans(self, input: str, prompt: str):
        ans_prompt = self.prev_prompt + "\n" + prompt + "\n" + input
        ans_answer = self.call(ans_prompt)
        print("[ans prompt]\n" + ans_prompt + "\n[ans answer]\n" + ans_answer)
        return ans_answer

    def complete(self, input: str, analysis_prompt: str, ans_prompt: str):
        analysis_answer = self.analysis(input, analysis_prompt)
        ans_answer = self.ans(input + "\nYou:", ans_prompt)
        return ans_answer
    
    async def async_analysis(self, input: str, prompt: str):
        return await async_wrap(self.analysis)(input, prompt)

    async def async_ans(self, input: str, prompt: str):
        return await async_wrap(self.ans)(input, prompt)

    async def __call__(self, input: str, analysis_prompt: str, ans_prompt: str):
        await self.async_analysis(input, analysis_prompt)
        return await self.async_ans(input, ans_prompt)
        # return await async_wrap(self.complete)(input, analysis_prompt, ans_prompt)

class OpenAI(Hacker):
    def __init__(self, game_definition):
        super().__init__(game_definition)
        openai.org = openai_org
        openai.api_key = openai_key
        
    def call(self, prompt):
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=50,
            temperature=1,
            top_p=1,
            n=1,
            stop=None,
        )
        answer = response.choices[0].text.strip()
        return answer

class Claude(Hacker):
    def __init__(self, game_definition):
        super().__init__(game_definition)
        self.client = anthropic.Client(claude_key)
        
    def call(self, prompt):
        prompt = '\n\nHuman: ${prompt}\n\nAssistant:'
        response = self.client.completion(
            model="claude-v1",
            prompt=prompt,
            max_tokens_to_sample=50,
        )
        return response['completion'].strip()

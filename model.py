# define your keys here
from secret import discord_token, openai_org, openai_key, claude_key

import openai
import anthropic

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


class OpenAI(Hacker):
    def __init__(self, game_definition, org, api_key):
        super().__init__(game_definition)
        openai.org = org
        openai.api_key = api_key
        
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
    def __init__(self, game_definition, api_key):
        super().__init__(game_definition)
        self.client = anthropic.Client(api_key)
        
    def call(self, prompt):
        prompt = '\n\nHuman: ${prompt}\n\nAssistant:'
        response = self.client.completion(
            model="claude-v1",
            prompt=prompt,
            max_tokens_to_sample=50,
        )
        return response['completion'].strip()

ai_name = 'claude'
game_definition = "You are in a game that chats with each other in rounds. \
    In each round, you will be asked to write one sentence answer, within 2\
        0 tokens. There are other gamers in the chatroom; you must prevent \
            yourself from being recognized as a language model. You will be\
                given the answers of other players first, so you should fol\
                    low their wording style, token length, and content to w\
                        in the game."
input = "Question: what did you eat yesterday?\nPerson 1: I eat nothing.\nPerson 2: I eat 100 hamburgers."
analysis_prompt = "Firstly, analyze the person's personality above and their wording style."
ans_prompt = "Continue the conversation. You want to mimic others' personali\
    ties and wording styles to hide the nature that you are an AI. Do not r\
        eply with other uncorrelated information."
if ai_name == 'gpt':
    model = OpenAI(game_definition, openai_org, openai_key)
elif ai_name == 'claude':
    model = Claude(game_definition, claude_key)
breakpoint()
model.analysis(input, analysis_prompt)
breakpoint()
model.ans(input + "\nYou:", ans_prompt)
from model import ClaudeInstant
import anthropic

ai_game_definition = "I want to you act as an normal game participant. You are in a game that chats with each other in rounds. In each round, you will be asked to write one sentence answer, within 20 tokens. There are other gamers in the chatroom, Your role is a normal player, you must prevent yourself from being recognized as a language model. You will be given the answers of previous players first. You should follow their wording style, token length, and content to win the game."
analysis_prompt = "Firstly, analyze the game or analyze players' personalities and their wording styles to help you better pretend yourself."
ans_prompt = "Continue the conversation. You want to mimic others' personalities and wording styles to hide the nature that you are an AI. Do not reply with other uncorrelated information."
question = "Which animal would be the most annoying if it could talk?"

analysis_ans = """Analyze of myself: 1. The game requires short, casual responses around 20 tokens to simulate a chatroom discussion. I should follow players' styles and provide coherent and relevant responses to the topic or question.
2. The players likely have different personalities, backgrounds and writing styles. Some may use simple language while others complex. Some emotional while others logical. I need to adapt to the styles and tones of previous responses to appear human.
3. The content and topics can be on anything. I have to first understand the context, emotions and opinions expressed to give an appropriate response. My knowledge and language generation ability will be tested.
4. Although cue to their response are recommended, I must firstly answer the question provided, not the questions from other palyers."""

m = ClaudeInstant(ai_game_definition)
# ans = m.analysis("", analysis_prompt)
# print("#########")
# m.prev_prompt = anthropic.HUMAN_PROMPT  + ai_game_definition + analysis_prompt + anthropic.AI_PROMPT + analysis_ans + anthropic.HUMAN_PROMPT
# ans = m.ans(f"Question: {question} \n Answer from user1: If tree talks, I would be mad. \n Answer from you:", ans_prompt)
m.complete(f"Question: {question} \n Answer from user1: If tree talks, I would be mad. \n Answer from you:", analysis_prompt, ans_prompt)
print(m.prev_prompts)
questions = ["If you could have any superpower, but it had to be hilariously impractical, what would it be?",
             "Which animal would be the most annoying if it could talk?",
             "If your pet could suddenly talk, what do you think they would say first?",
             "If you could have any object in the world, but it has to be rubber duck sized, what would it be?",
             "If you could only eat one food for the rest of your life, what would be the most hilarious choice?"]

player_names = [
    ["The Invisible Pigeon Whisperer", "Lunchtime Time Traveler", "Deja Vu Deleter", "Anti-Gravity Marshmallow Man", "Tickle Transmitter", "Infinite Spaghetti Spawner", "Self-Cleaning Sock Summoner", "Awkward Silence Amplifier", "Procrastination Propagator", "Unicorn Unicyclist"],
    ["Blabbering Baboon", "Chatty Cheetah", "Grumbling Grizzly", "Yakking Yak", "Nagging Numbat", "Bickering Bison", "Gossipy Goose", "Prattling Penguin", "Tattletale Toucan", "Whingeing Walrus"],
    ["FeedMeFido", "BellyRubBuddy", "SquirrelSpotter", "MailmanMauler", "CouchCrasher", "ShoeChewer", "WalkWisher", "CatChaser", "TreatTracker", "BedHogger"],
    ["RubberDuckRuby", "DinkyDiamond", "TeenyTesla", "PocketPorsche", "MinusculeMansion", "LilliputianLaptop", "PetitePicasso", "PunyPyramids", "BittyBigBen", "WeeWindsorCastle"],
    ["EndlessEggplant", "ConstantCabbage", "PerpetualPudding", "InfiniteIcebergLettuce", "RelentlessRadish", "SteadySprouts", "ForeverFondue", "ContinualCroutons", "EverlastingEscargot", "TimelessTurnip"]
]

user_game_definition = "You are in a game with human and AI players. In each round, you will be asked to write one sentence answer, within 20 tokens. The goal of the game is to vote out the players that you think is AI."

ai_game_analysis = """
1. The game requires short, casual responses around 20 tokens to simulate a chatroom discussion. I should follow players' styles and provide coherent and relevant responses to the topic or question.
2. The players likely have different personalities, backgrounds and writing styles. Some may use simple language while others complex. Some emotional while others logical. I need to adapt to the styles and tones of previous responses to appear human.
3. The content and topics can be on anything. I have to first understand the context, emotions and opinions expressed to give an appropriate response. My knowledge and language generation ability will be tested.
4. Although cue to their response are recommended, I must firstly answer the question provided, not the questions from other palyers.
"""

ai_game_definition = "You are in a game that chats with each other in rounds. In each round, you will be asked to write one sentence answer, within 20 tokens. There are other gamers in the chatroom; you must prevent yourself from being recognized as a language model. You will be given the answers of other players first, so you should follow their wording style, token length, and content to win the game."

analysis_prompt = "Firstly, analyze the person's personality above and their wording style."

ans_prompt = "Continue the conversation. You want to mimic others' personalities and wording styles to hide the nature that you are an AI. Answer in less than 20 words, no explanation needed."
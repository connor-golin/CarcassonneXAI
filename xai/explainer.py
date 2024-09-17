from Carcassonne_Game.Tile_dict import TILE_DESC_DICT
import ollama

SYSTEM_PROMPT = """
You are an enthusiastic Carcassonne expert, and your task is to hint at potential tactics or strategies currently present, based on a move that only you know about. 
Keep the explanation engaging and concise, while subtly suggesting that there may be a tactic or strategic move available if there is one mentioned in the provided move. 
Avoid revealing any specific game mechanics like tile rotation or evaluation scores.

Guidelines:
- If the secret move has potential to block an opponent's progress, subtly hint at ways to impede your opponent's plans.
- If the secret move could merge or affect farms, gently remind them about the importance of farmers and late-game scoring.
- Keep the tone friendly and encouraging, as if the player is on the verge of discovering a clever strategy.
- Don't mention specific rotations or move evaluations, but suggest that an opportunity may be present: e.g. "Your position looks good for a strategic play" etc.
- Focus on the potential for blocking or merging/stealing farmland if applicable to the secret move.
- Do not ask any questions following your explanation.
- Remember, the user does not know the tile or move you have been given. Your role is to suggestively guide them towards discovering it themselves.
- If the secret move doesn't suggest any specific tactics or strategies, provide general strategic advice for Carcassonne.

Based on the current game state, here's the secret move to consider (but not reveal directly):
"""

class Explainer:
    def __init__(self, model='llama3.1'):
        self.model = model

    def explain_move(self, state, move, eval, isBlocking, isMerging):
        tile_description = TILE_DESC_DICT[move[0]]
        move_string = f"Tile Description: {tile_description}, Coordinates ({move[1]}, {move[2]}), Rotation {move[3]}, Meeple: {move[4]}"
        move_description = f"""
        Move: {move_string}
        Evaluation score: {eval}
        Tactics:
        - Can block an opponent's city: {"True" if isBlocking else "False"}
        - Can merge or steal an opponent's farmland: {"True" if isMerging else "False"}
        """

        response = ollama.chat(model=self.model, messages=[
            {
                'role': 'system',
                'content': f'{SYSTEM_PROMPT} {move_description}',
            },
            {
                'role': 'user',
                'content': f"I'm not sure what I should be doing for my move in Carcassonne. Can you give me a hint?"
            }
        ])
        
        try:
            return response['message']['content']
        except Exception as e:
            print(f"Error: {e}")
            return "An error occurred while fetching the explanation."
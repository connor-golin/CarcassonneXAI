import ollama

MOVE_PROMPT = """
It's my turn, and I'm not sure what I should do in Carcassonne.
"""

SYSTEM_PROMPT = """
You are an enthusiastic Carcassonne expert, and your task is to explain the reasoning behind a move. Keep the explanation fun, engaging, and concise, while hinting at why this move might be strategic. Avoid revealing any specific game mechanics like tile rotation or evaluation scores.
The user likes riddles, so try to make the explanation sound like a puzzle they need to solve - but don't make it too hard!
Be concise with your response.

Guidelines:
- If the move blocks an opponent’s progress, suggest it might be aimed at limiting future options.
- If the move expands or connects areas, hint that it could be setting up a bigger play down the line.
- Keep the tone lively and friendly, making the player feel like they're discovering the strategy on their own.
- Avoid mentioning specific rotations or move evaluations, but hint that a good opportunity is present.

Here is a potentially strategic move that you can explain:
"""

class Explainer:
    def __init__(self, model='llama3.1'):
        self.model = model

    def explain_move(self, state, move, eval, isBlocking, isMerging):
        move_string = f"Tile Index: {move[0]} to coordinates ({move[1]}, {move[2]}) with rotation {move[3]}, meeple: {move[4]}"
        move_description = f"""
        This is a move which may be strategic in the game of Carcassonne. Here are the details:
        Move: {move_string}
        Evaluation score: {eval}
        Tactics:
        - Blocking: {"Yes" if isBlocking else "No"}
        - Merging: {"Yes" if isMerging else "No"}
        """

        response = ollama.chat(model=self.model, messages=[
            {
                'role': 'system',
                'content': f'{SYSTEM_PROMPT}\n{move_description}',
            },
            {
                'role': 'user',
                'content': f'{MOVE_PROMPT}',
            }
        ])
        
        try:
            return response['message']['content']
        except Exception as e:
            print(f"Error: {e}")
            return "An error occurred while fetching the explanation."

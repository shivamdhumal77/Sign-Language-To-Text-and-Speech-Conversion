# Word and Sentence Recommendations Dictionary
WORD_DICT = [
    # Common Words
    "HELLO", "HELP", "YES", "NO", "PLEASE", "THANKYOU", "SORRY", "WELCOME",
    "GOOD", "BAD", "AMAZING", "NICE", "LOVE", "LIKE", "HATE",

    # Daily Life
    "WATER", "FOOD", "APPLE", "BREAD", "RICE", "MILK", "TEA", "COFFEE",
    "EAT", "DRINK", "SLEEP", "WAKE", "HOME", "OFFICE", "SCHOOL", "COLLEGE",

    # People
    "MOTHER", "FATHER", "BROTHER", "SISTER", "FRIEND", "TEACHER", "STUDENT",

    # Places
    "INDIA", "HOSPITAL", "MARKET", "PARK", "HOTEL", "ROOM",

    # Actions
    "GO", "COME", "STOP", "WAIT", "RUN", "WALK", "SIT", "STAND",

    # Emotions
    "HAPPY", "SAD", "ANGRY", "EXCITED", "TIRED", "SCARED",

    # Technology
    "PHONE", "LAPTOP", "INTERNET", "CAMERA", "MACHINE", "AI", "ROBOT",

    # Sentences
    "HELLO HOW ARE YOU",
    "I NEED HELP",
    "THANK YOU VERY MUCH",
    "PLEASE HELP ME",
    "I AM FINE",
    "GOOD MORNING",
    "GOOD NIGHT",
    "WHAT IS YOUR NAME",
    "MY NAME IS",
    "I AM LEARNING SIGN LANGUAGE",
    "THIS IS AMAZING",
    "I LOVE MACHINE LEARNING",
    "WELCOME TO INDIA",
    "HAVE A NICE DAY",
    "SEE YOU SOON",
    "TAKE CARE",
    "PLEASE WAIT",
    "STOP HERE",
    "GO HOME",
    "I AM HAPPY",
    "I AM SAD",
    "I NEED WATER",
    "I NEED FOOD",
    "CALL THE DOCTOR",
    "OPEN THE DOOR",
    "CLOSE THE DOOR",
    "TURN ON THE LIGHT",
    "TURN OFF THE LIGHT"
]

class WordRecommender:
    def __init__(self, word_dict=None, limit=5):
        """Initialize word recommender."""
        self.word_dict = word_dict or WORD_DICT
        self.limit = limit
    
    def get_recommendations(self, current_word: str) -> list:
        """Get word recommendations based on current input."""
        if not current_word:
            return []
        
        current_word = current_word.upper()
        matches = [
            word for word in self.word_dict 
            if word.startswith(current_word) and word != current_word
        ]
        
        return matches[:self.limit]

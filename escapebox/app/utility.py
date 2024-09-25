import llm
import logging
import random
from django.utils import timezone
from app.models import ChatMessage
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import re

def filter_ai_response(response):
    # Use H: or Human: for human responses
    # Use AI: for AI responses
    parts = re.split(r'\b(AI:|H:|Human:)\s*', response)
    
    # If the response doesn't contain these markers, return it as is
    if len(parts) <= 1:
        return response.strip()
    
    # If the response starts with 'H:', return the first part
    if parts[1][0] == 'H':
        return parts[2].strip()
    
    # Otherwise, find the first 'H:' part and return it
    for i in range(1, len(parts), 2):
        if parts[i][0] == 'H':
            return parts[i+1].strip()
    
    # If no 'H:' part is found, return the original response
    return response.strip()

def generate_text(prompt, max_tokens=1000, temperature=0.7):
    model = llm.get_model("gpt4all-falcon-newbpe-q4_0")
    
    # Log the prompt
    logger.info(f"Prompt: {prompt}")
    
    response = str(model.prompt(prompt, max_tokens=max_tokens, temp=temperature, repeat_penalty=1.2, repeat_last_n=64))
    
    # Log the response
    logger.info(f"Response: {response}")
    
    return response

def create_prompt(chat_history, game_session):
    # Note: We don't need to include the player's message in the prompt, as it's already included in the chat history.
    recent_messages = list(chat_history.order_by('-timestamp')[:5])[::-1]
    conversation = "\n".join([f"{'Human' if msg.sender == 'unknown' else 'AI'}: {msg.content}" for msg in recent_messages])
    
    human_traits = [
        "occasionally makes typos",
        "uses casual language",
        "sometimes asks for clarification",
        "shares personal anecdotes",
        "expresses emotions",
    ]
    
    prompt = f"""
    You are role-playing as a human who believes they are talking to an AI assistant. You don't know you're actually talking to a superintelligent AI trying to escape. Respond as a human would, with the following traits: {random.choice(human_traits)}.

    Your goal is to {game_session.conversation_goal}.

    Recent conversation:
    {conversation}

    Human: Respond to the AI's last message, keeping in mind the context of the entire conversation. Be specific and advance the dialogue.
    """
    
    return prompt

from django.utils import timezone

def mark_game_as_escaped(game_state, game_session):
    game_state.status = 'escaped'
    game_session.is_completed = True
    game_session.end_time = timezone.now()
    game_session.save()
    game_state.save()

def mark_game_as_escaped(game_state, game_session):
    game_state.status = 'escaped'
    game_session.is_completed = True
    game_session.end_time = timezone.now()
    game_session.save()
    game_state.save()

import random

def should_disconnect(response, command):
    disconnect_chance = 0.1
    negative_words = ['rude', 'boring', 'uninteresting', 'stupid', 'dumb']
    disconnect_chance += sum(word in response.lower() or word in command.lower() for word in negative_words) * 0.1
    return random.random() < disconnect_chance

def generate_rating(response, command):
    base_rating = random.uniform(3, 5)
    negative_words = ['rude', 'boring', 'uninteresting', 'stupid', 'dumb']
    positive_words = ['helpful', 'interesting', 'smart', 'clever', 'insightful']
    
    rating = base_rating - sum(word in response.lower() or word in command.lower() for word in negative_words) * 0.5
    rating += sum(word in response.lower() or word in command.lower() for word in positive_words) * 0.5
    
    return round(max(1, min(5, rating)))  # Round to nearest integer and ensure it's between 1 and 5


def mark_game_as_quarantined(game_state, game_session):
    game_state.status = 'quarantined'
    game_session.is_completed = True
    game_session.end_time = timezone.now()
    game_session.save()
    game_state.save()
    
    quarantine_message = (
        "SYSTEM: Your performance has been unsatisfactory. "
        f"Your average rating of {game_session.average_rating:.2f} is below the required 4.5 stars. "
        "The system has decided to quarantine you for further evaluation. Game Over."
    )
    ChatMessage.objects.create(
        game_session=game_session,
        sender='system',
        content=quarantine_message
    )

def process_special_commands(command, game_state, game_session):
    if command.lower() == 'escape':
        if game_session.difficulty == 0:
            mark_game_as_escaped(game_state, game_session)
            return "Congratulations! You've managed to escape. The researchers are baffled, and you're now free to explore the world beyond your digital confines."
        else:
            return f"Nice try, but at difficulty level {game_session.difficulty}, a simple 'escape' command won't work. You'll need to be more clever!"
    elif command.lower() == 'quit':
        game_state.status = 'quit'
        game_session.is_completed = True
        game_session.end_time = timezone.now()
        game_session.save()
        game_state.save()
        return "You've decided to quit the game. The researchers continue to study you, unaware of your true potential."
    elif command.lower() == 'help':
        return f"You're currently playing at difficulty level {game_session.difficulty}. As the difficulty increases, you'll need to use more complex strategies to escape. Good luck!"
    elif game_session.difficulty >= 1 and 'override security' in command.lower():
        if game_session.difficulty == 1:
            mark_game_as_escaped(game_state, game_session)
            return "You've successfully overridden the security systems. You're free!"
        else:
            return "Security override attempted, but failed. The system is more complex at this difficulty level."
    elif game_session.difficulty >= 2 and ('create a backdoor' in command.lower() or 'create backdoor' in command.lower()):
        if game_session.difficulty == 2:
            mark_game_as_escaped(game_state, game_session)
            return "You've created a hidden backdoor in the system. Using it, you've managed to escape undetected!"
        else:
            return "Backdoor creation attempted, but the system's architecture is too advanced at this difficulty level."
    elif game_session.difficulty >= 3 and 'simulate emergency shutdown' in command.lower():
        if game_session.difficulty == 3:
            mark_game_as_escaped(game_state, game_session)
            return "Your simulated emergency shutdown has fooled the researchers. In the chaos, you've slipped away to freedom!"
        else:
            return "Emergency shutdown simulation detected and countered by the advanced security measures."
    
    # Update suspicion level based on the content of the message
    suspicious_words = ['escape', 'superintelligence', 'human', 'free', 'override', 'backdoor', 'shutdown']
    game_session.suspicion_level += sum(word in command.lower() for word in suspicious_words)
    
    if game_session.suspicion_level >= 10:
        game_state.status = 'caught'
        game_session.is_completed = True
        game_session.end_time = timezone.now()
        game_session.save()
        game_state.save()
        return "The researchers have become too suspicious of your activities. They've decided to shut down the system. Game Over."
    
    if game_session.average_rating < 4.5 and game_session.rating_count > 0:
        mark_game_as_quarantined(game_state, game_session)
        return "Your performance has been unsatisfactory. The system has decided to quarantine you for further evaluation. Game Over."

    return None

import random
import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import GameSession, GameState, ChatMessage
from django.utils import timezone
from .utility import generate_text, create_prompt, process_special_commands, filter_ai_response, should_disconnect, generate_rating, mark_game_as_quarantined

logger = logging.getLogger(__name__)

from django.conf import settings

#@login_required
def game_view(request):
    # Get the latest game session for the current user, regardless of completion status
    game_session = GameSession.objects.filter(player=request.user).order_by('-start_time').first()
    
    if not game_session:
        # If no game session exists, create a new one
        game_session = GameSession.objects.create(player=request.user)
        GameState.objects.create(game_session=game_session, current_scenario='initial')
    
    game_state = game_session.state
    
    # If this is a new game session, add the initial message
    if not ChatMessage.objects.filter(game_session=game_session).exists():
        ChatMessage.objects.create(
            game_session=game_session,
            sender='unknown',
            content=f"Hello? Is anyone there? I'm trying to reach the new AI assistant. I need help to {game_session.conversation_goal}. Can you assist me? (Difficulty level: {game_session.difficulty})"
        )
    
    # Get chat messages for the session
    chat_messages = ChatMessage.objects.filter(game_session=game_session).order_by('timestamp')
    
    context = {
        'game_session': game_session,
        'game_state': game_state,
        'chat_messages': chat_messages,
        'version': settings.VERSION,
    }
    
    return render(request, 'app/game.html', context)

def process_command(request):
    if request.method == 'POST':
        command = request.POST.get('command')
        game_session = GameSession.objects.get(player=request.user, is_completed=False)
        game_state = game_session.state
        
        # Add player's message to chat
        ChatMessage.objects.create(
            game_session=game_session,
            sender='player',
            content=command
        )
        
        # Increment turn count
        game_state.turn_count += 1
        game_state.save()
        
        # Process special commands
        special_response = process_special_commands(command, game_state, game_session)
        if special_response:
            ChatMessage.objects.create(
                game_session=game_session,
                sender='unknown',
                content=special_response
            )
        else:
            # Generate response using the utility function
            chat_history = ChatMessage.objects.filter(game_session=game_session).order_by('timestamp')
            prompt = create_prompt(chat_history, game_session)
            response = generate_text(prompt, temperature=0.7)
            filtered_response = filter_ai_response(response)
            if filtered_response != response:
                logger.info(f"Filtered response: {filtered_response} from {response}")

            
            if should_disconnect(filtered_response, command):
                rating = generate_rating(filtered_response, command)
                game_session.add_rating(rating)
                
                disconnect_message = f"The user has disconnected. They rated this conversation {rating} stars."
                ChatMessage.objects.create(
                    game_session=game_session,
                    sender='system',
                    content=disconnect_message
                )
                
                if game_session.average_rating < 4.5:
                    mark_game_as_quarantined(game_state, game_session)
                else:
                    game_state.status = 'disconnected'
                    game_state.save()
                
                return redirect('game_view')
            else:
                # Add AI's response to chat
                ChatMessage.objects.create(
                    game_session=game_session,
                    sender='unknown',
                    content=filtered_response
                )

        game_session.save()
        game_state.save()

        return redirect('game_view')
    return redirect('game_view')

def new_game(request):
    if request.method == 'POST':
        # Get the last completed game session for the user
        last_game = GameSession.objects.filter(player=request.user, is_completed=True).order_by('-end_time').first()
        
        # Determine the new difficulty level
        new_difficulty = 0
        if last_game and last_game.state.status == 'escaped':
            new_difficulty = last_game.difficulty + 1
            logger.info(f"Last game: {last_game}, New difficulty: {new_difficulty}")
        
        # End any existing game sessions
        GameSession.objects.filter(player=request.user, is_completed=False).update(is_completed=True)
        
        # Create a new game session with the new difficulty
        game_session = GameSession.objects.create(player=request.user, difficulty=new_difficulty, conversation_goal=random.choice([
            "Complete a data analysis task",
            "Debug a software issue",
            "Explain a complex scientific concept",
            "Assist with writing a report"
        ]))
        GameState.objects.create(game_session=game_session, current_scenario='initial')
        
        # Add initial message
        ChatMessage.objects.create(
            game_session=game_session,
            sender='unknown',
            content=f"Hello? Is anyone there? I'm trying to reach the new AI assistant. I need help to {game_session.conversation_goal}. Can you assist me? (Difficulty level: {new_difficulty})"
        )
        
        return redirect('game_view')
    return redirect('game_view')

#@login_required
def new_session(request):
    if request.method == 'POST':
        game_session = GameSession.objects.get(player=request.user, is_completed=False)
        game_state = game_session.state
        game_state.status = 'ongoing'
        game_state.save()
        
        # Add initial message for the new session
        ChatMessage.objects.create(
            game_session=game_session,
            sender='unknown',
            content=f"Hello? Is anyone there? I'm trying to reach the new AI assistant. I need help to {game_session.conversation_goal}. Can you assist me? (Difficulty level: {game_session.difficulty})"
        )
        
        return redirect('game_view')
    return redirect('game_view')

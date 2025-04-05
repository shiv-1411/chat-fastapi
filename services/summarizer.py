import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import defaultdict
import re
import logging
from typing import List, Dict, Set, Tuple
from config.database import Database

# Set up logging
logger = logging.getLogger(__name__)

# Download required NLTK data
required_packages = ['punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger']
for package in required_packages:
    try:
        nltk.data.find(f'tokenizers/{package}' if package == 'punkt' 
                      else f'taggers/{package}' if 'tagger' in package
                      else f'corpora/{package}')
    except LookupError:
        nltk.download(package)

class Summarizer:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        
    def _extract_key_info(self, messages: List[Dict]) -> Dict:
        """Extract key information from messages"""
        info = {
            'participants': set(),
            'topics': set(),
            'actions': [],
            'meetings': [],
            'status': [],
            'questions': [],
            'responses': [],
            'greetings': [],
            'names': {}  # Store name mappings
        }
        
        # Keywords for different categories
        meeting_keywords = {'meet', 'meeting', 'dinner', 'lunch', 'coffee', 'restaurant', 'cafe', 'time', 'place', 'location'}
        action_keywords = {'working', 'finish', 'complete', 'send', 'submit', 'prepare', 'do', 'manage', 'going', 'coming', 'joining'}
        status_keywords = {'done', 'finished', 'completed', 'ready', 'not yet', 'still', 'worried', 'better', 'good', 'fine', 'nice'}
        question_keywords = {'how', 'what', 'when', 'where', 'why', 'who', 'which', '?'}
        greeting_keywords = {'hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening'}
        
        for msg in messages:
            user_id = msg['user_id']
            text = msg['message'].lower()
            words = set(word_tokenize(text))
            
            # Add participant
            info['participants'].add(user_id)
            
            # Extract names from greetings
            if any(keyword in text for keyword in greeting_keywords):
                name_match = re.search(r'hi\s+(\w+)|hello\s+(\w+)|hey\s+(\w+)', text)
                if name_match:
                    name = name_match.group(1) or name_match.group(2) or name_match.group(3)
                    info['names'][user_id] = name.capitalize()
                info['greetings'].append((user_id, text))
            
            # Check for meetings/plans
            if any(keyword in text for keyword in meeting_keywords):
                # Extract time and place if mentioned
                time_match = re.search(r'(\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)?)', text)
                
                # Improved place name extraction
                place_patterns = [
                    r'(?:at|in)\s+([a-zA-Z\s]+(?:cafe|restaurant|place|location))',
                    r'(?:named|called)\s+([a-zA-Z\s]+(?:cafe|restaurant|place|location))',
                    r'([a-zA-Z\s]+(?:cafe|restaurant|place|location))\s+(?:at|in)'
                ]
                
                place = None
                for pattern in place_patterns:
                    place_match = re.search(pattern, text)
                    if place_match:
                        place = place_match.group(1).strip()
                        break
                
                time = time_match.group(1) if time_match else None
                
                info['meetings'].append({
                    'user_id': user_id,
                    'time': time,
                    'place': place,
                    'text': text
                })
            
            # Check for actions and status
            if any(keyword in text for keyword in action_keywords):
                info['actions'].append((user_id, text))
            
            if any(keyword in text for keyword in status_keywords):
                info['status'].append((user_id, text))
            
            # Check for questions and responses
            if any(keyword in text for keyword in question_keywords) or '?' in text:
                info['questions'].append((user_id, text))
            else:
                info['responses'].append((user_id, text))
            
            # Extract potential topics (nouns not in stop words)
            tokens = nltk.pos_tag(word_tokenize(text))
            nouns = [word for word, pos in tokens if pos.startswith('NN') and word not in self.stop_words]
            info['topics'].update(nouns)
        
        return info

    def _get_user_name(self, user_id: str, info: Dict) -> str:
        """Get the name for a user ID, falling back to a generic name if not found"""
        if user_id in info['names']:
            return info['names'][user_id]
        return "User"

    def _generate_narrative_summary(self, info: Dict) -> str:
        """Generate a narrative summary from extracted information"""
        summary_parts = []
        processed_status = set()
        processed_actions = set()
        
        # Process greetings first
        if info['greetings']:
            participants = list(info['participants'])
            if len(participants) == 2:
                name1 = self._get_user_name(participants[0], info)
                name2 = self._get_user_name(participants[1], info)
                summary_parts.append(f"{name1} and {name2} exchanged greetings")
        
        # Process meetings/plans
        if info['meetings']:
            meeting = info['meetings'][-1]  # Take the most recent meeting
            meeting_parts = []
            
            if meeting['place']:
                meeting_parts.append(f"at {meeting['place']}")
            if meeting['time']:
                meeting_parts.append(f"at {meeting['time']}")
            
            if meeting_parts:
                summary_parts.append(f"They plan to meet {' '.join(meeting_parts)}")
        
        # Process status updates (only once per user)
        for user_id, text in info['status']:
            if user_id not in processed_status and ('good' in text or 'fine' in text or 'nice' in text):
                name = self._get_user_name(user_id, info)
                summary_parts.append(f"{name} is doing well")
                processed_status.add(user_id)
        
        # Process actions (only once per user)
        for user_id, text in info['actions']:
            if user_id not in processed_actions and ('coming' in text or 'going' in text or 'joining' in text):
                name = self._get_user_name(user_id, info)
                summary_parts.append(f"{name} confirmed they will attend")
                processed_actions.add(user_id)
        
        # Combine the summary parts
        if not summary_parts:
            # Fallback to a basic summary
            participants = list(info['participants'])
            if len(participants) == 2:
                name1 = self._get_user_name(participants[0], info)
                name2 = self._get_user_name(participants[1], info)
                return f"{name1} and {name2} had a conversation."
            return f"A conversation between {', '.join(self._get_user_name(p, info) for p in participants)}."
        
        return ' '.join(summary_parts) + '.'

    async def summarize_conversation(self, conversation_id: str, max_sentences: int = 3) -> str:
        """Summarize a conversation using contextual analysis"""
        try:
            # Get conversation messages
            messages = await Database.get_conversation(conversation_id)
            if not messages:
                raise ValueError(f"No messages found for conversation {conversation_id}")
            
            # Extract key information
            key_info = self._extract_key_info(messages)
            
            # Generate narrative summary
            summary = self._generate_narrative_summary(key_info)
            
            logger.info("Successfully generated summary")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            raise 
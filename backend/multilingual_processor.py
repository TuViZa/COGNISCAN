import whisper
import torch
import librosa
import numpy as np
from typing import Dict, List, Optional, Tuple
import json
import re
from datetime import datetime
import asyncio
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import langdetect

class MultilingualSpeechProcessor:
    """
    Multilingual Speech-to-Text and Semantic Analysis Processor
    Supports Hindi, Marathi, and English with regional language support
    """
    
    def __init__(self):
        # Initialize Whisper model for multilingual transcription
        self.whisper_model = whisper.load_model("base")
        
        # Initialize multilingual BERT models for semantic analysis
        self.semantic_models = {
            'en': pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest"),
            'hi': pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest"),  # Fallback
            'mr': pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")  # Fallback
        }
        
        # Language-specific coherence models
        self.coherence_models = self._initialize_coherence_models()
        
        # Supported languages
        self.supported_languages = {
            'en': 'English',
            'hi': 'Hindi',
            'mr': 'Marathi'
        }
        
        # Regional language patterns for coherence analysis
        self.language_patterns = {
            'hi': {
                'connectors': ['और', 'पर', 'क्योंकि', 'लेकिन', 'तो', 'जब', 'अगर', 'इसलिए'],
                'question_words': ['क्या', 'कैसे', 'क्यों', 'कब', 'कहां', 'कौन'],
                'tense_markers': ['था', 'थी', 'थे', 'है', 'हैं', 'होगा', 'होगी']
            },
            'mr': {
                'connectors': ['आणि', 'पर', 'कारण', 'पण', 'म्हणून', 'जेव्हा', 'जर', 'तर'],
                'question_words': ['काय', 'कसे', 'का', 'केव्हा', 'कुठे', 'कोण'],
                'tense_markers': ['होता', 'होती', 'होते', 'आहे', 'आहेत', 'असेल']
            },
            'en': {
                'connectors': ['and', 'but', 'because', 'so', 'when', 'if', 'however', 'therefore'],
                'question_words': ['what', 'how', 'why', 'when', 'where', 'who'],
                'tense_markers': ['was', 'were', 'is', 'are', 'will', 'would', 'has', 'have']
            }
        }
    
    def _initialize_coherence_models(self) -> Dict:
        """Initialize language-specific coherence analysis models"""
        # For demonstration, using rule-based coherence analysis
        # In production, these would be trained models for each language
        return {
            'en': self._english_coherence_analyzer,
            'hi': self._hindi_coherence_analyzer,
            'mr': self._marathi_coherence_analyzer
        }
    
    async def process_audio_file(self, audio_path: str, preferred_language: str = 'auto') -> Dict:
        """
        Process audio file for multilingual transcription and semantic analysis
        """
        try:
            # Step 1: Transcribe audio using Whisper
            transcription_result = await self._transcribe_audio(audio_path, preferred_language)
            
            if not transcription_result['success']:
                return transcription_result
            
            transcript = transcription_result['transcript']
            detected_language = transcription_result['language']
            
            # Step 2: Analyze semantic coherence
            coherence_analysis = await self._analyze_semantic_coherence(
                transcript, 
                detected_language
            )
            
            # Step 3: Extract linguistic features
            linguistic_features = await self._extract_linguistic_features(
                transcript, 
                detected_language
            )
            
            # Step 4: Sentiment and emotional analysis
            sentiment_analysis = await self._analyze_sentiment(
                transcript, 
                detected_language
            )
            
            return {
                'success': True,
                'transcript': transcript,
                'language': detected_language,
                'language_name': self.supported_languages.get(detected_language, 'Unknown'),
                'coherence_analysis': coherence_analysis,
                'linguistic_features': linguistic_features,
                'sentiment_analysis': sentiment_analysis,
                'processing_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _transcribe_audio(self, audio_path: str, preferred_language: str = 'auto') -> Dict:
        """Transcribe audio using Whisper with language detection"""
        try:
            # Load audio
            audio = whisper.load_audio(audio_path)
            
            # Transcribe with automatic language detection
            if preferred_language == 'auto':
                result = self.whisper_model.transcribe(
                    audio, 
                    language=None,  # Auto-detect
                    task="transcribe"
                )
            else:
                result = self.whisper_model.transcribe(
                    audio, 
                    language=preferred_language,
                    task="transcribe"
                )
            
            # Detect language if auto-detect was used
            detected_language = result.get('language', 'en')
            transcript = result['text'].strip()
            
            # Validate detected language
            if detected_language not in self.supported_languages:
                # Fallback to English if unsupported language detected
                detected_language = 'en'
            
            return {
                'success': True,
                'transcript': transcript,
                'language': detected_language,
                'confidence': result.get('avg_logprob', 0.0)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Transcription failed: {str(e)}"
            }
    
    async def _analyze_semantic_coherence(self, transcript: str, language: str) -> Dict:
        """Analyze semantic coherence of the transcript"""
        try:
            coherence_analyzer = self.coherence_models.get(language, self.coherence_models['en'])
            
            coherence_score = coherence_analyzer(transcript)
            
            # Additional coherence metrics
            sentences = self._split_sentences(transcript, language)
            
            # Logical flow analysis
            logical_flow_score = self._analyze_logical_flow(sentences, language)
            
            # Topic consistency
            topic_consistency = self._analyze_topic_consistency(transcript, language)
            
            # Narrative structure
            narrative_structure = self._analyze_narrative_structure(sentences, language)
            
            return {
                'overall_coherence': coherence_score,
                'logical_flow': logical_flow_score,
                'topic_consistency': topic_consistency,
                'narrative_structure': narrative_structure,
                'sentence_count': len(sentences),
                'detailed_metrics': {
                    'connective_usage': self._count_connectives(transcript, language),
                    'pronoun_references': self._analyze_pronoun_references(transcript, language),
                    'temporal_consistency': self._analyze_temporal_consistency(transcript, language)
                }
            }
            
        except Exception as e:
            return {
                'overall_coherence': 0.5,
                'error': str(e)
            }
    
    def _english_coherence_analyzer(self, transcript: str) -> float:
        """English-specific coherence analysis"""
        try:
            # Rule-based coherence scoring for English
            sentences = transcript.split('.')
            
            if len(sentences) < 2:
                return 0.5
            
            coherence_score = 0.5  # Base score
            
            # Check for logical connectors
            connectors = self.language_patterns['en']['connectors']
            connector_count = sum(1 for connector in connectors if connector.lower() in transcript.lower())
            coherence_score += min(connector_count * 0.1, 0.3)
            
            # Check sentence length variation (good for coherence)
            sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
            if sentence_lengths:
                length_variance = np.std(sentence_lengths) / np.mean(sentence_lengths)
                coherence_score += min(length_variance * 0.2, 0.2)
            
            return min(coherence_score, 1.0)
            
        except:
            return 0.5
    
    def _hindi_coherence_analyzer(self, transcript: str) -> float:
        """Hindi-specific coherence analysis"""
        try:
            # Hindi-specific coherence patterns
            coherence_score = 0.5
            
            # Check for Hindi connectors
            connectors = self.language_patterns['hi']['connectors']
            connector_count = sum(1 for connector in connectors if connector in transcript)
            coherence_score += min(connector_count * 0.15, 0.3)
            
            # Check for proper tense usage
            tense_markers = self.language_patterns['hi']['tense_markers']
            tense_count = sum(1 for marker in tense_markers if marker in transcript)
            coherence_score += min(tense_count * 0.1, 0.2)
            
            return min(coherence_score, 1.0)
            
        except:
            return 0.5
    
    def _marathi_coherence_analyzer(self, transcript: str) -> float:
        """Marathi-specific coherence analysis"""
        try:
            # Marathi-specific coherence patterns
            coherence_score = 0.5
            
            # Check for Marathi connectors
            connectors = self.language_patterns['mr']['connectors']
            connector_count = sum(1 for connector in connectors if connector in transcript)
            coherence_score += min(connector_count * 0.15, 0.3)
            
            # Check for proper tense usage
            tense_markers = self.language_patterns['mr']['tense_markers']
            tense_count = sum(1 for marker in tense_markers if marker in transcript)
            coherence_score += min(tense_count * 0.1, 0.2)
            
            return min(coherence_score, 1.0)
            
        except:
            return 0.5
    
    def _split_sentences(self, text: str, language: str) -> List[str]:
        """Split text into sentences based on language-specific patterns"""
        if language == 'en':
            # English sentence splitting
            sentences = re.split(r'[.!?]+', text)
        elif language == 'hi':
            # Hindi sentence splitting (Devanagari script)
            sentences = re.split(r'[।!?]+', text)
        elif language == 'mr':
            # Marathi sentence splitting (Devanagari script)
            sentences = re.split(r'[।!?]+', text)
        else:
            # Default splitting
            sentences = re.split(r'[.!?।]+', text)
        
        return [s.strip() for s in sentences if s.strip()]
    
    def _analyze_logical_flow(self, sentences: List[str], language: str) -> float:
        """Analyze logical flow between sentences"""
        try:
            if len(sentences) < 2:
                return 0.5
            
            flow_score = 0.5
            
            # Check for logical connectors between sentences
            connectors = self.language_patterns[language]['connectors']
            
            for i in range(1, len(sentences)):
                # Check if current sentence starts with a connector
                sentence_start = sentences[i][:20].lower()
                if any(connector in sentence_start for connector in connectors):
                    flow_score += 0.1
            
            return min(flow_score, 1.0)
            
        except:
            return 0.5
    
    def _analyze_topic_consistency(self, transcript: str, language: str) -> float:
        """Analyze topic consistency throughout the transcript"""
        try:
            # Simple topic consistency based on keyword repetition
            words = transcript.lower().split()
            
            if len(words) < 10:
                return 0.5
            
            # Count word frequencies
            word_freq = {}
            for word in words:
                if len(word) > 3:  # Ignore very short words
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Calculate consistency based on word distribution
            if word_freq:
                max_freq = max(word_freq.values())
                avg_freq = sum(word_freq.values()) / len(word_freq)
                consistency = min(max_freq / (avg_freq * 3), 1.0)
            else:
                consistency = 0.5
            
            return consistency
            
        except:
            return 0.5
    
    def _analyze_narrative_structure(self, sentences: List[str], language: str) -> float:
        """Analyze narrative structure (beginning, middle, end)"""
        try:
            if len(sentences) < 3:
                return 0.5
            
            structure_score = 0.5
            
            # Check for temporal markers
            if language == 'en':
                temporal_markers = ['once', 'then', 'after', 'finally', 'later']
            elif language == 'hi':
                temporal_markers = ['एक बार', 'फिर', 'बाद में', 'आखिरकार']
            elif language == 'mr':
                temporal_markers = ['एकदा', 'मग', 'नंतर', 'शेवटी']
            else:
                temporal_markers = []
            
            temporal_count = sum(1 for marker in temporal_markers if marker in ' '.join(sentences).lower())
            structure_score += min(temporal_count * 0.15, 0.3)
            
            return min(structure_score, 1.0)
            
        except:
            return 0.5
    
    def _count_connectives(self, transcript: str, language: str) -> int:
        """Count logical connectives in transcript"""
        connectors = self.language_patterns[language]['connectors']
        return sum(1 for connector in connectors if connector in transcript)
    
    def _analyze_pronoun_references(self, transcript: str, language: str) -> float:
        """Analyze pronoun reference consistency"""
        try:
            # Simplified pronoun analysis
            if language == 'en':
                pronouns = ['he', 'she', 'it', 'they', 'this', 'that']
            elif language == 'hi':
                pronouns = ['वह', 'वे', 'यह', 'वह', 'ये']
            elif language == 'mr':
                pronouns = ['तो', 'ती', 'ते', 'त्या', 'हे', 'ही']
            else:
                return 0.5
            
            pronoun_count = sum(1 for pronoun in pronouns if pronoun in transcript.lower())
            word_count = len(transcript.split())
            
            if word_count > 0:
                pronoun_ratio = pronoun_count / word_count
                return min(pronoun_ratio * 10, 1.0)  # Normalize to 0-1
            
            return 0.5
            
        except:
            return 0.5
    
    def _analyze_temporal_consistency(self, transcript: str, language: str) -> float:
        """Analyze temporal consistency in the narrative"""
        try:
            tense_markers = self.language_patterns[language]['tense_markers']
            tense_count = sum(1 for marker in tense_markers if marker in transcript)
            
            # More tense markers generally indicate better temporal awareness
            return min(tense_count * 0.2, 1.0)
            
        except:
            return 0.5
    
    async def _extract_linguistic_features(self, transcript: str, language: str) -> Dict:
        """Extract detailed linguistic features"""
        try:
            words = transcript.split()
            sentences = self._split_sentences(transcript, language)
            
            features = {
                'word_count': len(words),
                'sentence_count': len(sentences),
                'avg_sentence_length': len(words) / len(sentences) if sentences else 0,
                'unique_words': len(set(words)),
                'vocabulary_richness': len(set(words)) / len(words) if words else 0,
                'complexity_score': self._calculate_complexity(transcript, language),
                'language_specific_features': self._get_language_specific_features(transcript, language)
            }
            
            return features
            
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_complexity(self, transcript: str, language: str) -> float:
        """Calculate linguistic complexity score"""
        try:
            words = transcript.split()
            
            # Complex words (longer than 6 characters)
            complex_words = [w for w in words if len(w) > 6]
            complexity_ratio = len(complex_words) / len(words) if words else 0
            
            # Connectors indicate complex sentence structure
            connectors = self.language_patterns[language]['connectors']
            connector_count = sum(1 for connector in connectors if connector in transcript)
            connector_ratio = connector_count / len(words) if words else 0
            
            # Combined complexity score
            complexity_score = (complexity_ratio + connector_ratio) / 2
            return min(complexity_score * 2, 1.0)  # Normalize to 0-1
            
        except:
            return 0.5
    
    def _get_language_specific_features(self, transcript: str, language: str) -> Dict:
        """Get language-specific linguistic features"""
        features = {}
        
        if language == 'hi':
            # Hindi-specific features
            features.update({
                'devanagari_script_usage': self._check_devanagari_usage(transcript),
                'hindi_verb_forms': self._count_hindi_verbs(transcript),
                'honorifics_usage': self._count_hindi_honorifics(transcript)
            })
        elif language == 'mr':
            # Marathi-specific features
            features.update({
                'devanagari_script_usage': self._check_devanagari_usage(transcript),
                'marathi_verb_forms': self._count_marathi_verbs(transcript),
                'regional_markers': self._count_marathi_markers(transcript)
            })
        else:
            # English features
            features.update({
                'latin_script_usage': 1.0,
                'phrasal_verbs': self._count_phrasal_verbs(transcript),
                'idioms_usage': self._count_idioms(transcript)
            })
        
        return features
    
    def _check_devanagari_usage(self, transcript: str) -> float:
        """Check usage of Devanagari script"""
        devanagari_chars = len(re.findall(r'[\u0900-\u097F]', transcript))
        total_chars = len(transcript)
        return devanagari_chars / total_chars if total_chars > 0 else 0
    
    def _count_hindi_verbs(self, transcript: str) -> int:
        """Count Hindi verb forms"""
        hindi_verbs = ['है', 'हैं', 'था', 'थी', 'थे', 'होगा', 'होगी', 'करता', 'करती', 'करते']
        return sum(1 for verb in hindi_verbs if verb in transcript)
    
    def _count_hindi_honorifics(self, transcript: str) -> int:
        """Count Hindi honorifics"""
        honorifics = ['जी', 'साहब', 'श्रीमान', 'श्रीमती', 'बाबू']
        return sum(1 for honorific in honorifics if honorific in transcript)
    
    def _count_marathi_verbs(self, transcript: str) -> int:
        """Count Marathi verb forms"""
        marathi_verbs = ['आहे', 'आहेत', 'होता', 'होती', 'होते', 'असेल', 'असती', 'असते']
        return sum(1 for verb in marathi_verbs if verb in transcript)
    
    def _count_marathi_markers(self, transcript: str) -> int:
        """Count Marathi regional markers"""
        markers = ['ना', 'तर', 'म्हणजे', 'जेव्हा', 'कारण', 'पण']
        return sum(1 for marker in markers if marker in transcript)
    
    def _count_phrasal_verbs(self, transcript: str) -> int:
        """Count English phrasal verbs"""
        phrasal_verbs = ['get up', 'look for', 'turn on', 'turn off', 'give up', 'make up']
        return sum(1 for pv in phrasal_verbs if pv in transcript.lower())
    
    def _count_idioms(self, transcript: str) -> int:
        """Count English idioms"""
        idioms = ['break a leg', 'piece of cake', 'hit the nail on the head', 'let the cat out of the bag']
        return sum(1 for idiom in idioms if idiom in transcript.lower())
    
    async def _analyze_sentiment(self, transcript: str, language: str) -> Dict:
        """Analyze sentiment and emotional content"""
        try:
            # Use appropriate model or fallback
            model = self.semantic_models.get(language, self.semantic_models['en'])
            
            # For demonstration, using rule-based sentiment analysis
            # In production, this would use proper multilingual sentiment models
            
            sentiment_score = self._rule_based_sentiment(transcript, language)
            
            return {
                'sentiment_score': sentiment_score,
                'sentiment_label': self._get_sentiment_label(sentiment_score),
                'emotional_indicators': self._analyze_emotional_indicators(transcript, language),
                'confidence': 0.7  # Placeholder confidence
            }
            
        except Exception as e:
            return {
                'sentiment_score': 0.5,
                'sentiment_label': 'neutral',
                'error': str(e)
            }
    
    def _rule_based_sentiment(self, transcript: str, language: str) -> float:
        """Rule-based sentiment analysis"""
        try:
            positive_words = {
                'en': ['good', 'happy', 'love', 'excellent', 'wonderful', 'great', 'amazing'],
                'hi': ['अच्छा', 'खुश', 'प्यार', 'बेहतरीन', 'शानदार', 'महान'],
                'mr': ['चांगला', 'आनंदी', 'प्रेम', 'उत्कृष्ट', 'भव्य', 'ग्रेट']
            }
            
            negative_words = {
                'en': ['bad', 'sad', 'hate', 'terrible', 'awful', 'poor', 'difficult'],
                'hi': ['बुरा', 'दुखी', 'नफरत', 'भयानक', 'खराब', 'कठिन'],
                'mr': ['वाईट', 'दुःखी', 'द्वेष', 'भयंकर', 'खराब', 'कठीण']
            }
            
            pos_words = positive_words.get(language, positive_words['en'])
            neg_words = negative_words.get(language, negative_words['en'])
            
            pos_count = sum(1 for word in pos_words if word in transcript.lower())
            neg_count = sum(1 for word in neg_words if word in transcript.lower())
            
            total_sentiment_words = pos_count + neg_count
            if total_sentiment_words == 0:
                return 0.5  # Neutral
            
            sentiment_score = (pos_count - neg_count) / total_sentiment_words
            return (sentiment_score + 1) / 2  # Normalize to 0-1
            
        except:
            return 0.5
    
    def _get_sentiment_label(self, score: float) -> str:
        """Convert sentiment score to label"""
        if score > 0.6:
            return 'positive'
        elif score < 0.4:
            return 'negative'
        else:
            return 'neutral'
    
    def _analyze_emotional_indicators(self, transcript: str, language: str) -> Dict:
        """Analyze emotional indicators in speech"""
        try:
            indicators = {
                'enthusiasm': self._detect_enthusiasm(transcript, language),
                'anxiety': self._detect_anxiety(transcript, language),
                'confidence': self._detect_confidence(transcript, language),
                'confusion': self._detect_confusion(transcript, language)
            }
            
            return indicators
            
        except:
            return {'error': 'Failed to analyze emotional indicators'}
    
    def _detect_enthusiasm(self, transcript: str, language: str) -> float:
        """Detect enthusiasm in speech"""
        enthusiasm_words = {
            'en': ['excited', 'wonderful', 'amazing', 'fantastic', 'love'],
            'hi': ['उत्साहित', 'शानदार', 'अद्भुत', 'प्यार'],
            'mr': ['उत्साही', 'अद्भुत', 'फांटास्टिक', 'प्रेम']
        }
        
        words = enthusiasm_words.get(language, enthusiasm_words['en'])
        count = sum(1 for word in words if word in transcript.lower())
        return min(count * 0.2, 1.0)
    
    def _detect_anxiety(self, transcript: str, language: str) -> float:
        """Detect anxiety indicators"""
        anxiety_words = {
            'en': ['worried', 'anxious', 'nervous', 'scared', 'afraid'],
            'hi': ['चिंतित', 'चिंता', 'नर्वस', 'डर', 'भय'],
            'mr': ['चिंतित', 'चिंता', 'नर्वस', 'भीत', 'डर']
        }
        
        words = anxiety_words.get(language, anxiety_words['en'])
        count = sum(1 for word in words if word in transcript.lower())
        return min(count * 0.2, 1.0)
    
    def _detect_confidence(self, transcript: str, language: str) -> float:
        """Detect confidence indicators"""
        confidence_words = {
            'en': ['sure', 'confident', 'certain', 'definitely', 'absolutely'],
            'hi': ['निश्चित', 'विश्वास', 'जरूर', 'बिल्कुल'],
            'mr': ['निश्चित', 'विश्वास', 'नक्की', 'खात्री']
        }
        
        words = confidence_words.get(language, confidence_words['en'])
        count = sum(1 for word in words if word in transcript.lower())
        return min(count * 0.2, 1.0)
    
    def _detect_confusion(self, transcript: str, language: str) -> float:
        """Detect confusion indicators"""
        confusion_words = {
            'en': ['confused', 'unsure', 'uncertain', 'maybe', 'perhaps'],
            'hi': ['भ्रमित', 'अनिश्चित', 'शायद', 'हो सकता है'],
            'mr': ['गोंधळून', ['अनिश्चित', 'कदाचित', 'होऊ शकतो']
        }
        
        words = confusion_words.get(language, confusion_words['en'])
        count = sum(1 for word in words if word in transcript.lower())
        return min(count * 0.2, 1.0)

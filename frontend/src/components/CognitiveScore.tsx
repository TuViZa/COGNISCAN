'use client';

import React from 'react';
import { Brain, TrendingUp, AlertTriangle, CheckCircle } from 'lucide-react';

interface CognitiveScoreProps {
  score: number;
  analysis: {
    facial_analysis: {
      micro_expressions: string;
      eye_contact: string;
      facial_symmetry: string;
    };
    speech_analysis: {
      pitch_variance: string;
      speech_rate: string;
      pause_frequency: string;
    };
    language_analysis: {
      coherence: string;
      vocabulary_richness: string;
      sentence_complexity: string;
    };
  };
  timestamp: string;
}

export default function CognitiveScore({ score, analysis, timestamp }: CognitiveScoreProps) {
  const getScoreColor = (score: number) => {
    if (score >= 85) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreIcon = (score: number) => {
    if (score >= 85) return <CheckCircle className="w-6 h-6 text-green-600" />;
    if (score >= 70) return <TrendingUp className="w-6 h-6 text-yellow-600" />;
    return <AlertTriangle className="w-6 h-6 text-red-600" />;
  };

  const getScoreMessage = (score: number) => {
    if (score >= 85) return 'Excellent cognitive health indicators';
    if (score >= 70) return 'Normal cognitive functioning';
    return 'Requires further evaluation';
  };

  const formatDate = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 max-w-2xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Cognitive Assessment Results</h2>
        <span className="text-sm text-gray-500">{formatDate(timestamp)}</span>
      </div>

      {/* Overall Score */}
      <div className="text-center mb-8">
        <div className="flex justify-center mb-4">
          {getScoreIcon(score)}
        </div>
        <div className={`text-5xl font-bold mb-2 ${getScoreColor(score)}`}>
          {score.toFixed(1)}
        </div>
        <div className="text-gray-600 mb-2">Cognitive Score</div>
        <div className="text-sm text-gray-500">{getScoreMessage(score)}</div>
      </div>

      {/* Score Progress Bar */}
      <div className="mb-8">
        <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
          <div 
            className={`h-full transition-all duration-500 ${
              score >= 85 ? 'bg-green-500' : 
              score >= 70 ? 'bg-yellow-500' : 'bg-red-500'
            }`}
            style={{ width: `${score}%` }}
          />
        </div>
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>0</span>
          <span>50</span>
          <span>70</span>
          <span>85</span>
          <span>100</span>
        </div>
      </div>

      {/* Detailed Analysis */}
      <div className="space-y-6">
        {/* Facial Analysis */}
        <div className="border-l-4 border-blue-500 pl-4">
          <div className="flex items-center gap-2 mb-3">
            <Brain className="w-5 h-5 text-blue-600" />
            <h3 className="font-semibold text-gray-800">Facial Analysis</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="text-sm text-gray-600 mb-1">Micro-expressions</div>
              <div className="font-medium text-gray-800">{analysis.facial_analysis.micro_expressions}</div>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="text-sm text-gray-600 mb-1">Eye Contact</div>
              <div className="font-medium text-gray-800">{analysis.facial_analysis.eye_contact}</div>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="text-sm text-gray-600 mb-1">Facial Symmetry</div>
              <div className="font-medium text-gray-800">{analysis.facial_analysis.facial_symmetry}</div>
            </div>
          </div>
        </div>

        {/* Speech Analysis */}
        <div className="border-l-4 border-green-500 pl-4">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-5 h-5 bg-green-600 rounded-full flex items-center justify-center">
              <div className="w-2 h-2 bg-white rounded-full"></div>
            </div>
            <h3 className="font-semibold text-gray-800">Speech Analysis</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="text-sm text-gray-600 mb-1">Pitch Variance</div>
              <div className="font-medium text-gray-800">{analysis.speech_analysis.pitch_variance}</div>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="text-sm text-gray-600 mb-1">Speech Rate</div>
              <div className="font-medium text-gray-800">{analysis.speech_analysis.speech_rate}</div>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="text-sm text-gray-600 mb-1">Pause Frequency</div>
              <div className="font-medium text-gray-800">{analysis.speech_analysis.pause_frequency}</div>
            </div>
          </div>
        </div>

        {/* Language Analysis */}
        <div className="border-l-4 border-purple-500 pl-4">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-5 h-5 bg-purple-600 rounded flex items-center justify-center">
              <span className="text-white text-xs font-bold">L</span>
            </div>
            <h3 className="font-semibold text-gray-800">Language Analysis</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="text-sm text-gray-600 mb-1">Coherence</div>
              <div className="font-medium text-gray-800">{analysis.language_analysis.coherence}</div>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="text-sm text-gray-600 mb-1">Vocabulary Richness</div>
              <div className="font-medium text-gray-800">{analysis.language_analysis.vocabulary_richness}</div>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="text-sm text-gray-600 mb-1">Sentence Complexity</div>
              <div className="font-medium text-gray-800">{analysis.language_analysis.sentence_complexity}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Recommendations */}
      <div className="mt-8 p-4 bg-yellow-50 rounded-lg">
        <h3 className="font-semibold text-yellow-900 mb-2">Recommendations:</h3>
        <ul className="text-sm text-yellow-800 space-y-1">
          {score >= 85 && (
            <>
              <li>• Continue maintaining your current cognitive health routine</li>
              <li>• Regular mental stimulation and social activities</li>
            </>
          )}
          {score >= 70 && score < 85 && (
            <>
              <li>• Consider increasing cognitive exercises and puzzles</li>
              <li>• Maintain regular sleep schedule and physical activity</li>
            </>
          )}
          {score < 70 && (
            <>
              <li>• Schedule a follow-up assessment with a healthcare provider</li>
              <li>• Consider comprehensive neurological evaluation</li>
              <li>• Increase cognitive stimulation activities</li>
            </>
          )}
        </ul>
      </div>
    </div>
  );
}

'use client';

import React, { useState } from 'react';
import VideoRecorder from '@/components/VideoRecorder';
import AccessibilityEnhancedVideoRecorder from '@/components/AccessibilityEnhancedVideoRecorder';
import CognitiveScore from '@/components/CognitiveScore';
import CaregiverDashboard from '@/components/CaregiverDashboard';
import DoctorPortal from '@/components/DoctorPortal';
import { Brain, Users, BarChart3, Settings, Eye } from 'lucide-react';

interface AssessmentResult {
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

export default function Home() {
  const [currentView, setCurrentView] = useState<'patient' | 'caregiver' | 'doctor'>('patient');
  const [isProcessing, setIsProcessing] = useState(false);
  const [assessmentResult, setAssessmentResult] = useState<AssessmentResult | null>(null);
  const [accessibilityMode, setAccessibilityMode] = useState<'standard' | 'high-contrast' | 'large-text' | 'screen-reader'>('standard');
  const [showAccessibility, setShowAccessibility] = useState(false);

  const handleRecordingComplete = async (videoBlob: Blob) => {
    setIsProcessing(true);
    
    try {
      const formData = new FormData();
      formData.append('file', videoBlob, 'recording.webm');
      
      const response = await fetch('http://localhost:8000/api/upload-video', {
        method: 'POST',
        body: formData,
      });
      
      if (response.ok) {
        const result = await response.json();
        setAssessmentResult({
          score: result.cognitive_score,
          analysis: result.analysis,
          timestamp: result.timestamp
        });
      } else {
        throw new Error('Upload failed');
      }
    } catch (error) {
      console.error('Error uploading video:', error);
      alert('Failed to process video. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const getAccessibilityClass = () => {
    switch (accessibilityMode) {
      case 'high-contrast':
        return 'contrast-200';
      case 'large-text':
        return 'text-lg';
      case 'screen-reader':
        return 'sr-only-focusable';
      default:
        return '';
    }
  };

  return (
    <div className={`min-h-screen bg-gray-50 ${getAccessibilityClass()}`}>
      {/* Header */}
      <header className="nakshatra-gradient shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
                <Brain className="w-6 h-6 text-yellow-500" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">Cogniscan</h1>
                <p className="text-yellow-100 text-sm">AI-Based Early Cognitive Decline Detection</p>
              </div>
            </div>
            
            {/* Navigation */}
            <div className="flex gap-2">
              <button
                onClick={() => setCurrentView('patient')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  currentView === 'patient'
                    ? 'bg-white text-yellow-600'
                    : 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200'
                }`}
                aria-label="Patient portal"
                aria-current={currentView === 'patient' ? 'page' : undefined}
              >
                Patient Portal
              </button>
              <button
                onClick={() => setCurrentView('caregiver')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  currentView === 'caregiver'
                    ? 'bg-white text-yellow-600'
                    : 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200'
                }`}
                aria-label="Caregiver portal"
                aria-current={currentView === 'caregiver' ? 'page' : undefined}
              >
                Caregiver Portal
              </button>
              <button
                onClick={() => setCurrentView('doctor')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  currentView === 'doctor'
                    ? 'bg-white text-yellow-600'
                    : 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200'
                }`}
                aria-label="Doctor portal"
                aria-current={currentView === 'doctor' ? 'page' : undefined}
              >
                Doctor Portal
              </button>
            </div>

            {/* Accessibility Toggle */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowAccessibility(!showAccessibility)}
                className={`p-2 rounded-lg bg-yellow-100 text-yellow-800 hover:bg-yellow-200 transition-colors`}
                aria-label="Accessibility options"
                aria-expanded={showAccessibility}
                aria-controls="accessibility-panel"
              >
                <Settings className="w-5 h-5" />
              </button>
              <button
                className={`p-2 rounded-lg bg-yellow-100 text-yellow-800 hover:bg-yellow-200 transition-colors`}
                aria-label="Accessibility mode"
              >
                <Eye className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Accessibility Panel */}
      {showAccessibility && (
        <div id="accessibility-panel" className="bg-yellow-50 border-b-2 border-yellow-200 p-4">
          <div className="max-w-7xl mx-auto">
            <h3 className="font-bold text-yellow-900 mb-3">Accessibility Options:</h3>
            <div className="flex flex-wrap gap-3">
              {[
                { value: 'standard', label: 'Standard' },
                { value: 'high-contrast', label: 'High Contrast' },
                { value: 'large-text', label: 'Large Text' },
                { value: 'screen-reader', label: 'Screen Reader' }
              ].map((mode) => (
                <button
                  key={mode.value}
                  onClick={() => setAccessibilityMode(mode.value as any)}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    accessibilityMode === mode.value
                      ? 'bg-yellow-600 text-white'
                      : 'bg-white text-yellow-800 border border-yellow-300 hover:bg-yellow-100'
                  }`}
                  aria-pressed={accessibilityMode === mode.value}
                >
                  {mode.label}
                </button>
              ))}
            </div>
            <div className="mt-3 text-sm text-yellow-700">
              Current mode: <strong>{accessibilityMode.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}</strong>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentView === 'patient' ? (
          <div className="space-y-8">
            {/* Patient Welcome */}
            {!assessmentResult && (
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold text-gray-800 mb-4">Welcome to Your Daily Check-in</h2>
                <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                  Take 2 minutes to complete today's cognitive assessment. Our AI will analyze your speech patterns, 
                  facial expressions, and language to monitor your cognitive health.
                </p>
                {accessibilityMode !== 'standard' && (
                  <div className="mt-4 p-4 bg-blue-50 rounded-lg border-2 border-blue-200">
                    <p className="text-blue-800 font-medium">
                      Accessibility mode is active. Enhanced visual and navigation features are enabled.
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* Video Recorder - Choose based on accessibility mode */}
            {!assessmentResult && (
              accessibilityMode !== 'standard' ? (
                <AccessibilityEnhancedVideoRecorder 
                  onRecordingComplete={handleRecordingComplete}
                  isProcessing={isProcessing}
                  accessibilityMode={accessibilityMode}
                />
              ) : (
                <VideoRecorder 
                  onRecordingComplete={handleRecordingComplete}
                  isProcessing={isProcessing}
                />
              )
            )}

            {/* Assessment Results */}
            {assessmentResult && (
              <div className="space-y-6">
                <CognitiveScore 
                  score={assessmentResult.score}
                  analysis={assessmentResult.analysis}
                  timestamp={assessmentResult.timestamp}
                />
                
                <div className="text-center">
                  <button
                    onClick={() => setAssessmentResult(null)}
                    className="nakshatra-bg hover:opacity-90 text-white font-medium py-3 px-8 rounded-full transition-opacity"
                  >
                    Complete Another Assessment
                  </button>
                </div>
              </div>
            )}
          </div>
        ) : currentView === 'caregiver' ? (
          <CaregiverDashboard />
        ) : (
          <DoctorPortal />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-8 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <p className="text-gray-400">© 2024 Cogniscan - Nakshatra Health Technologies</p>
            <p className="text-gray-500 text-sm mt-2">Early detection for better cognitive health outcomes</p>
            <div className="mt-4 flex justify-center gap-4 text-sm text-gray-400">
              <span>Accessibility Compliant</span>
              <span>•</span>
              <span>Privacy First</span>
              <span>•</span>
              <span>AI-Powered</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

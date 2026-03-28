'use client';

import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Video, VideoOff, Mic, MicOff, Circle, Square, Upload, Volume2, Settings, Eye } from 'lucide-react';

interface AccessibilityEnhancedVideoRecorderProps {
  onRecordingComplete: (videoBlob: Blob) => void;
  isProcessing: boolean;
  accessibilityMode?: 'standard' | 'high-contrast' | 'large-text' | 'screen-reader';
}

export default function AccessibilityEnhancedVideoRecorder({ 
  onRecordingComplete, 
  isProcessing,
  accessibilityMode = 'standard'
}: AccessibilityEnhancedVideoRecorderProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [isVideoEnabled, setIsVideoEnabled] = useState(true);
  const [isAudioEnabled, setIsAudioEnabled] = useState(true);
  const [recordedBlob, setRecordedBlob] = useState<Blob | null>(null);
  const [recordingTime, setRecordingTime] = useState(0);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [volumeLevel, setVolumeLevel] = useState(0);
  const [showSettings, setShowSettings] = useState(false);
  const [announcements, setAnnouncements] = useState<string[]>([]);
  
  const videoRef = useRef<HTMLVideoElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const recordingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const volumeAnalyzerRef = useRef<ScriptProcessorNode | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);

  // Accessibility configurations
  const accessibilityConfig = {
    standard: {
      fontSize: 'text-base',
      buttonSize: 'p-3',
      contrast: 'contrast-100',
      focusRing: 'focus:ring-2 focus:ring-blue-500'
    },
    'high-contrast': {
      fontSize: 'text-lg',
      buttonSize: 'p-4',
      contrast: 'contrast-200',
      focusRing: 'focus:ring-4 focus:ring-yellow-400'
    },
    'large-text': {
      fontSize: 'text-xl',
      buttonSize: 'p-5',
      contrast: 'contrast-100',
      focusRing: 'focus:ring-3 focus:ring-blue-500'
    },
    'screen-reader': {
      fontSize: 'text-lg',
      buttonSize: 'p-4',
      contrast: 'contrast-150',
      focusRing: 'focus:ring-4 focus:ring-blue-600'
    }
  };

  const config = accessibilityConfig[accessibilityMode];

  // Screen reader announcements
  const announce = useCallback((message: string) => {
    setAnnouncements(prev => [...prev, message]);
    // Also use ARIA live region
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', 'polite');
    announcement.setAttribute('aria-atomic', 'true');
    announcement.className = 'sr-only';
    announcement.textContent = message;
    document.body.appendChild(announcement);
    setTimeout(() => document.body.removeChild(announcement), 1000);
  }, []);

  // Volume monitoring for accessibility
  const setupVolumeMonitoring = useCallback((mediaStream: MediaStream) => {
    try {
      audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
      const source = audioContextRef.current.createMediaStreamSource(mediaStream);
      const analyzer = audioContextRef.current.createAnalyser();
      
      analyzer.fftSize = 256;
      const bufferLength = analyzer.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);
      
      volumeAnalyzerRef.current = audioContextRef.current.createScriptProcessor(256, 1, 1);
      
      volumeAnalyzerRef.current.onaudioprocess = () => {
        analyzer.getByteFrequencyData(dataArray);
        const average = dataArray.reduce((a, b) => a + b) / bufferLength;
        setVolumeLevel(average / 128); // Normalize to 0-1
      };
      
      source.connect(analyzer);
      analyzer.connect(volumeAnalyzerRef.current);
      volumeAnalyzerRef.current.connect(audioContextRef.current.destination);
      
    } catch (error) {
      console.error('Error setting up volume monitoring:', error);
    }
  }, []);

  const startRecording = useCallback(async () => {
    try {
      announce('Starting video recording. Please allow camera and microphone access.');
      
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: isVideoEnabled,
        audio: isAudioEnabled
      });
      
      setStream(mediaStream);
      
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
      
      // Setup volume monitoring for accessibility
      if (isAudioEnabled) {
        setupVolumeMonitoring(mediaStream);
      }
      
      const mediaRecorder = new MediaRecorder(mediaStream, {
        mimeType: 'video/webm;codecs=vp8,opus'
      });
      
      chunksRef.current = [];
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };
      
      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'video/webm' });
        setRecordedBlob(blob);
        onRecordingComplete(blob);
        
        // Cleanup audio context
        if (audioContextRef.current) {
          audioContextRef.current.close();
          audioContextRef.current = null;
        }
        
        // Stop all tracks
        if (stream) {
          stream.getTracks().forEach(track => track.stop());
        }
        
        announce('Recording completed successfully.');
      };
      
      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);
      
      // Start timer with accessibility announcements
      recordingIntervalRef.current = setInterval(() => {
        setRecordingTime((prev) => {
          const newTime = prev + 1;
          
          // Announce at important intervals
          if (newTime === 60) {
            announce('1 minute completed. 1 minute remaining.');
          } else if (newTime === 90) {
            announce('30 seconds remaining.');
          } else if (newTime === 120) {
            announce('Time completed. Recording will stop automatically.');
            stopRecording();
            return prev;
          }
          
          return newTime;
        });
      }, 1000);
      
    } catch (error) {
      console.error('Error accessing media devices:', error);
      announce('Unable to access camera or microphone. Please check your device permissions.');
      alert('Unable to access camera/microphone. Please check permissions.');
    }
  }, [isVideoEnabled, isAudioEnabled, onRecordingComplete, stream, announce, setupVolumeMonitoring]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current);
      }
      
      announce('Recording stopped.');
    }
  }, [isRecording, announce]);

  const toggleVideo = useCallback(() => {
    if (stream) {
      const videoTracks = stream.getVideoTracks();
      videoTracks.forEach(track => {
        track.enabled = !isVideoEnabled;
      });
      setIsVideoEnabled(!isVideoEnabled);
      announce(`Camera ${!isVideoEnabled ? 'enabled' : 'disabled'}.`);
    }
  }, [stream, isVideoEnabled, announce]);

  const toggleAudio = useCallback(() => {
    if (stream) {
      const audioTracks = stream.getAudioTracks();
      audioTracks.forEach(track => {
        track.enabled = !isAudioEnabled;
      });
      setIsAudioEnabled(!isAudioEnabled);
      announce(`Microphone ${!isAudioEnabled ? 'enabled' : 'disabled'}.`);
    }
  }, [stream, isAudioEnabled, announce]);

  const handleFileUpload = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type.startsWith('video/')) {
      announce('Video file uploaded. Processing will begin shortly.');
      onRecordingComplete(file);
    } else {
      announce('Please select a valid video file.');
    }
  }, [onRecordingComplete, announce]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getVolumeColor = (level: number) => {
    if (level < 0.3) return 'bg-green-500';
    if (level < 0.7) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  // Keyboard navigation support
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === ' ' && !isRecording) {
        event.preventDefault();
        startRecording();
      } else if (event.key === 'Escape' && isRecording) {
        event.preventDefault();
        stopRecording();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isRecording, startRecording, stopRecording]);

  return (
    <div className={`bg-white rounded-2xl shadow-lg p-6 max-w-2xl mx-auto ${config.contrast}`}>
      {/* Screen reader announcements */}
      <div aria-live="polite" aria-atomic="true" className="sr-only">
        {announcements.map((announcement, index) => (
          <div key={index}>{announcement}</div>
        ))}
      </div>

      <div className="mb-6">
        <h2 className={`text-2xl font-bold text-gray-800 mb-2 ${config.fontSize}`}>
          Daily Cognitive Check-in
        </h2>
        <p className={`text-gray-600 ${config.fontSize === 'text-xl' ? 'text-lg' : ''}`}>
          Record a 2-minute video response. Press spacebar to start, Escape to stop.
        </p>
      </div>

      {/* Accessibility Settings */}
      <div className="mb-4 flex justify-end">
        <button
          onClick={() => setShowSettings(!showSettings)}
          className={`flex items-center gap-2 px-3 py-2 rounded-lg border border-gray-300 ${config.buttonSize} ${config.focusRing}`}
          aria-label="Accessibility settings"
          aria-expanded={showSettings}
        >
          <Settings className="w-5 h-5" />
          <span className={config.fontSize}>Accessibility</span>
        </button>
      </div>

      {/* Accessibility Options Panel */}
      {showSettings && (
        <div className="mb-6 p-4 border-2 border-blue-500 rounded-lg bg-blue-50">
          <h3 className="font-bold text-blue-800 mb-3">Accessibility Options:</h3>
          <div className="grid grid-cols-2 gap-3">
            {Object.keys(accessibilityConfig).map((mode) => (
              <button
                key={mode}
                onClick={() => announce(`Accessibility mode changed to ${mode}`)}
                className={`px-3 py-2 rounded ${accessibilityMode === mode ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 border border-gray-300'} ${config.focusRing}`}
                aria-pressed={accessibilityMode === mode}
              >
                {mode.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Video Preview with Enhanced Accessibility */}
      <div className="relative bg-gray-900 rounded-xl overflow-hidden mb-6 aspect-video">
        {!isRecording && !recordedBlob && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <Video className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-400 text-lg">Camera preview will appear here</p>
              <p className="text-gray-500 text-sm mt-2">Allow camera and microphone access to begin</p>
            </div>
          </div>
        )}
        
        <video
          ref={videoRef}
          autoPlay
          muted
          playsInline
          className="w-full h-full object-cover"
          style={{ display: isRecording ? 'block' : 'none' }}
          aria-label="Live camera feed"
        />
        
        {recordedBlob && !isRecording && (
          <video
            src={URL.createObjectURL(recordedBlob)}
            controls
            className="w-full h-full object-cover"
            aria-label="Recorded video playback"
          />
        )}
        
        {isRecording && (
          <div className="absolute top-4 right-4 bg-red-500 text-white px-4 py-2 rounded-full flex items-center gap-2">
            <Circle className="w-4 h-4 fill-current" />
            <span className={`font-medium ${config.fontSize}`}>REC {formatTime(recordingTime)}</span>
          </div>
        )}

        {/* Volume Indicator for Accessibility */}
        {isRecording && isAudioEnabled && (
          <div className="absolute bottom-4 left-4 flex items-center gap-2">
            <Volume2 className="w-5 h-5 text-white" />
            <div className="w-24 h-2 bg-gray-700 rounded-full overflow-hidden">
              <div 
                className={`h-full transition-all duration-100 ${getVolumeColor(volumeLevel)}`}
                style={{ width: `${volumeLevel * 100}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Enhanced Controls */}
      <div className="space-y-4">
        {/* Recording Controls */}
        <div className="flex justify-center gap-4">
          {!isRecording ? (
            <button
              onClick={startRecording}
              disabled={isProcessing}
              className={`nakshatra-bg hover:opacity-90 text-white font-medium py-4 px-8 rounded-full flex items-center gap-2 transition-opacity disabled:opacity-50 text-lg ${config.focusRing}`}
              aria-label="Start recording"
              aria-describedby="recording-help"
            >
              <Circle className="w-6 h-6 fill-current" />
              Start Recording
            </button>
          ) : (
            <button
              onClick={stopRecording}
              className="bg-red-500 hover:bg-red-600 text-white font-medium py-4 px-8 rounded-full flex items-center gap-2 transition-colors text-lg"
              aria-label="Stop recording"
            >
              <Square className="w-6 h-6" />
              Stop Recording
            </button>
          )}
        </div>

        <div id="recording-help" className="text-sm text-gray-600 text-center">
          Use spacebar to start/stop recording, or click the buttons
        </div>

        {/* Media Controls */}
        {stream && !recordedBlob && (
          <div className="flex justify-center gap-4">
            <button
              onClick={toggleVideo}
              className={`p-4 rounded-full transition-colors ${config.buttonSize} ${config.focusRing}`}
              aria-label={isVideoEnabled ? 'Disable camera' : 'Enable camera'}
              aria-pressed={!isVideoEnabled}
            >
              {isVideoEnabled ? 
                <Video className="w-6 h-6 text-white" /> : 
                <VideoOff className="w-6 h-6 text-gray-600" />
              }
            </button>
            
            <button
              onClick={toggleAudio}
              className={`p-4 rounded-full transition-colors ${config.buttonSize} ${config.focusRing}`}
              aria-label={isAudioEnabled ? 'Disable microphone' : 'Enable microphone'}
              aria-pressed={!isAudioEnabled}
            >
              {isAudioEnabled ? 
                <Mic className="w-6 h-6 text-white" /> : 
                <MicOff className="w-6 h-6 text-gray-600" />
              }
            </button>
          </div>
        )}

        {/* File Upload */}
        <div className="flex justify-center">
          <label className="cursor-pointer">
            <input
              type="file"
              accept="video/*"
              onChange={handleFileUpload}
              disabled={isProcessing}
              className="hidden"
              aria-label="Upload video file"
            />
            <div className={`flex items-center gap-2 text-gray-600 hover:text-gray-800 transition-colors ${config.fontSize}`}>
              <Upload className="w-5 h-5" />
              <span>Or upload a video file</span>
            </div>
          </label>
        </div>

        {/* Processing Status */}
        {isProcessing && (
          <div className="text-center py-4">
            <div className="inline-flex items-center gap-2 text-gray-600">
              <div className="w-6 h-6 border-4 border-gray-300 border-t-nakshatra-yellow rounded-full animate-spin"></div>
              <span className={config.fontSize}>Processing your video...</span>
            </div>
            <div className="text-sm text-gray-500 mt-2">
              This may take a few moments. Please wait.
            </div>
          </div>
        )}
      </div>

      {/* Instructions */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg border-2 border-blue-200">
        <h3 className="font-semibold text-blue-900 mb-2 text-lg">Today's Prompt:</h3>
        <p className="text-blue-800 text-lg leading-relaxed">
          "Describe your favorite childhood memory and how it makes you feel today. 
          Take your time and speak naturally for about 2 minutes."
        </p>
        <div className="mt-3 text-sm text-blue-700">
          <p>Tips for best results:</p>
          <ul className="list-disc list-inside mt-1 space-y-1">
            <li>Speak clearly and at a natural pace</li>
            <li>Ensure good lighting on your face</li>
            <li>Minimize background noise</li>
            <li>Look directly at the camera when possible</li>
          </ul>
        </div>
      </div>

      {/* Keyboard Shortcuts Help */}
      <div className="mt-4 p-3 bg-gray-100 rounded-lg">
        <h4 className="font-semibold text-gray-700 mb-2 flex items-center gap-2">
          <Eye className="w-4 h-4" />
          Keyboard Shortcuts:
        </h4>
        <div className="text-sm text-gray-600 grid grid-cols-2 gap-2">
          <div><kbd className="px-2 py-1 bg-white rounded">Spacebar</kbd> - Start/Stop recording</div>
          <div><kbd className="px-2 py-1 bg-white rounded">Escape</kbd> - Stop recording</div>
        </div>
      </div>
    </div>
  );
}

'use client';

import React, { useState, useRef, useCallback } from 'react';
import { Video, VideoOff, Mic, MicOff, Circle, Square, Upload } from 'lucide-react';

interface VideoRecorderProps {
  onRecordingComplete: (videoBlob: Blob) => void;
  isProcessing: boolean;
}

export default function VideoRecorder({ onRecordingComplete, isProcessing }: VideoRecorderProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [isVideoEnabled, setIsVideoEnabled] = useState(true);
  const [isAudioEnabled, setIsAudioEnabled] = useState(true);
  const [recordedBlob, setRecordedBlob] = useState<Blob | null>(null);
  const [recordingTime, setRecordingTime] = useState(0);
  const [stream, setStream] = useState<MediaStream | null>(null);
  
  const videoRef = useRef<HTMLVideoElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const recordingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const startRecording = useCallback(async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: isVideoEnabled,
        audio: isAudioEnabled
      });
      
      setStream(mediaStream);
      
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
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
        
        // Stop all tracks
        if (stream) {
          stream.getTracks().forEach(track => track.stop());
        }
      };
      
      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);
      
      // Start timer for 2-minute limit
      recordingIntervalRef.current = setInterval(() => {
        setRecordingTime((prev) => {
          if (prev >= 120) {
            stopRecording();
            return prev;
          }
          return prev + 1;
        });
      }, 1000);
      
    } catch (error) {
      console.error('Error accessing media devices:', error);
      alert('Unable to access camera/microphone. Please check permissions.');
    }
  }, [isVideoEnabled, isAudioEnabled, onRecordingComplete, stream]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current);
      }
    }
  }, [isRecording]);

  const toggleVideo = useCallback(() => {
    if (stream) {
      const videoTracks = stream.getVideoTracks();
      videoTracks.forEach(track => {
        track.enabled = !isVideoEnabled;
      });
      setIsVideoEnabled(!isVideoEnabled);
    }
  }, [stream, isVideoEnabled]);

  const toggleAudio = useCallback(() => {
    if (stream) {
      const audioTracks = stream.getAudioTracks();
      audioTracks.forEach(track => {
        track.enabled = !isAudioEnabled;
      });
      setIsAudioEnabled(!isAudioEnabled);
    }
  }, [stream, isAudioEnabled]);

  const handleFileUpload = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type.startsWith('video/')) {
      onRecordingComplete(file);
    }
  }, [onRecordingComplete]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 max-w-2xl mx-auto">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">Daily Check-in</h2>
        <p className="text-gray-600">
          Record a 2-minute response to today's prompt. The system will analyze your speech patterns, 
          facial expressions, and cognitive indicators.
        </p>
      </div>

      {/* Video Preview */}
      <div className="relative bg-gray-900 rounded-xl overflow-hidden mb-6 aspect-video">
        {!isRecording && !recordedBlob && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <Video className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-400">Camera preview will appear here</p>
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
        />
        
        {recordedBlob && !isRecording && (
          <video
            src={URL.createObjectURL(recordedBlob)}
            controls
            className="w-full h-full object-cover"
          />
        )}
        
        {isRecording && (
          <div className="absolute top-4 right-4 bg-red-500 text-white px-3 py-1 rounded-full flex items-center gap-2">
            <Circle className="w-3 h-3 fill-current" />
            <span className="text-sm font-medium">REC {formatTime(recordingTime)}</span>
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="space-y-4">
        {/* Recording Controls */}
        <div className="flex justify-center gap-4">
          {!isRecording ? (
            <button
              onClick={startRecording}
              disabled={isProcessing}
              className="nakshatra-bg hover:opacity-90 text-white font-medium py-3 px-8 rounded-full flex items-center gap-2 transition-opacity disabled:opacity-50"
            >
              <Circle className="w-5 h-5 fill-current" />
              Start Recording
            </button>
          ) : (
            <button
              onClick={stopRecording}
              className="bg-red-500 hover:bg-red-600 text-white font-medium py-3 px-8 rounded-full flex items-center gap-2 transition-colors"
            >
              <Square className="w-5 h-5" />
              Stop Recording
            </button>
          )}
        </div>

        {/* Media Controls */}
        {stream && !recordedBlob && (
          <div className="flex justify-center gap-4">
            <button
              onClick={toggleVideo}
              className={`p-3 rounded-full transition-colors ${
                isVideoEnabled 
                  ? 'nakshatra-bg text-white' 
                  : 'bg-gray-200 text-gray-600'
              }`}
            >
              {isVideoEnabled ? <Video className="w-5 h-5" /> : <VideoOff className="w-5 h-5" />}
            </button>
            
            <button
              onClick={toggleAudio}
              className={`p-3 rounded-full transition-colors ${
                isAudioEnabled 
                  ? 'nakshatra-bg text-white' 
                  : 'bg-gray-200 text-gray-600'
              }`}
            >
              {isAudioEnabled ? <Mic className="w-5 h-5" /> : <MicOff className="w-5 h-5" />}
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
            />
            <div className="flex items-center gap-2 text-gray-600 hover:text-gray-800 transition-colors">
              <Upload className="w-4 h-4" />
              <span className="text-sm">Or upload a video file</span>
            </div>
          </label>
        </div>

        {/* Processing Status */}
        {isProcessing && (
          <div className="text-center py-4">
            <div className="inline-flex items-center gap-2 text-gray-600">
              <div className="w-4 h-4 border-2 border-gray-300 border-t-nakshatra-yellow rounded-full animate-spin"></div>
              <span>Processing your video...</span>
            </div>
          </div>
        )}
      </div>

      {/* Instructions */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h3 className="font-semibold text-blue-900 mb-2">Today's Prompt:</h3>
        <p className="text-blue-800">
          "Describe your favorite childhood memory and how it makes you feel today. 
          Take your time and speak naturally for about 2 minutes."
        </p>
      </div>
    </div>
  );
}

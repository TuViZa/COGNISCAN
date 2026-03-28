'use client';

import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Users, AlertTriangle, TrendingUp, Calendar, Activity, Bell } from 'lucide-react';

interface Patient {
  id: string;
  name: string;
  lastScore: number;
  lastAssessment: string;
  riskLevel: 'low' | 'medium' | 'high';
}

interface Alert {
  id: string;
  patientName: string;
  message: string;
  severity: 'high' | 'medium' | 'low';
  timestamp: string;
}

interface HistoricalData {
  date: string;
  score: number;
}

export default function CaregiverDashboard() {
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [patientHistory, setPatientHistory] = useState<HistoricalData[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [showNotifications, setShowNotifications] = useState(false);

  // Mock data
  const patients: Patient[] = [
    { id: '1', name: 'John Smith', lastScore: 82, lastAssessment: '2024-03-28', riskLevel: 'low' },
    { id: '2', name: 'Mary Johnson', lastScore: 68, lastAssessment: '2024-03-28', riskLevel: 'high' },
    { id: '3', name: 'Robert Davis', lastScore: 75, lastAssessment: '2024-03-27', riskLevel: 'medium' },
    { id: '4', name: 'Linda Wilson', lastScore: 88, lastAssessment: '2024-03-28', riskLevel: 'low' },
  ];

  const mockAlerts: Alert[] = [
    {
      id: '1',
      patientName: 'Mary Johnson',
      message: 'Cognitive score dropped below threshold (68)',
      severity: 'high',
      timestamp: '2024-03-28T10:30:00Z'
    },
    {
      id: '2',
      patientName: 'Robert Davis',
      message: 'Missed daily assessment',
      severity: 'medium',
      timestamp: '2024-03-28T09:15:00Z'
    }
  ];

  const generateMockHistory = (patientId: string): HistoricalData[] => {
    const history: HistoricalData[] = [];
    const today = new Date();
    
    for (let i = 29; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      
      // Generate realistic score with some variation
      const baseScore = patientId === '2' ? 68 : patientId === '3' ? 75 : 82;
      const variation = Math.random() * 10 - 5;
      const score = Math.max(60, Math.min(95, baseScore + variation));
      
      history.push({
        date: date.toISOString().split('T')[0],
        score: Math.round(score)
      });
    }
    
    return history;
  };

  useEffect(() => {
    setAlerts(mockAlerts);
  }, []);

  useEffect(() => {
    if (selectedPatient) {
      setPatientHistory(generateMockHistory(selectedPatient.id));
    }
  }, [selectedPatient]);

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'high': return 'text-red-600 bg-red-50';
      case 'medium': return 'text-yellow-600 bg-yellow-50';
      case 'low': return 'text-green-600 bg-green-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'high': return <AlertTriangle className="w-4 h-4 text-red-600" />;
      case 'medium': return <AlertTriangle className="w-4 h-4 text-yellow-600" />;
      case 'low': return <Activity className="w-4 h-4 text-blue-600" />;
      default: return null;
    }
  };

  const formatDate = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const unreadAlertsCount = alerts.filter(alert => !alert.id.includes('read')).length;

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-800">Caregiver Dashboard</h1>
            <p className="text-gray-600 mt-1">Monitor patient cognitive health trends</p>
          </div>
          
          {/* Notifications */}
          <div className="relative">
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="relative p-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <Bell className="w-6 h-6 text-gray-600" />
              {unreadAlertsCount > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                  {unreadAlertsCount}
                </span>
              )}
            </button>
            
            {showNotifications && (
              <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
                <div className="p-4 border-b border-gray-200">
                  <h3 className="font-semibold text-gray-800">Recent Alerts</h3>
                </div>
                <div className="max-h-96 overflow-y-auto">
                  {alerts.map(alert => (
                    <div key={alert.id} className="p-4 border-b border-gray-100 hover:bg-gray-50">
                      <div className="flex items-start gap-3">
                        {getSeverityIcon(alert.severity)}
                        <div className="flex-1">
                          <p className="text-sm font-medium text-gray-800">{alert.patientName}</p>
                          <p className="text-sm text-gray-600 mt-1">{alert.message}</p>
                          <p className="text-xs text-gray-500 mt-2">{formatDate(alert.timestamp)}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Patients</p>
              <p className="text-2xl font-bold text-gray-800 mt-1">{patients.length}</p>
            </div>
            <Users className="w-8 h-8 text-blue-600" />
          </div>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">High Risk</p>
              <p className="text-2xl font-bold text-red-600 mt-1">
                {patients.filter(p => p.riskLevel === 'high').length}
              </p>
            </div>
            <AlertTriangle className="w-8 h-8 text-red-600" />
          </div>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Avg Score</p>
              <p className="text-2xl font-bold text-gray-800 mt-1">
                {Math.round(patients.reduce((acc, p) => acc + p.lastScore, 0) / patients.length)}
              </p>
            </div>
            <TrendingUp className="w-8 h-8 text-green-600" />
          </div>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Assessments Today</p>
              <p className="text-2xl font-bold text-gray-800 mt-1">
                {patients.filter(p => p.lastAssessment === '2024-03-28').length}
              </p>
            </div>
            <Calendar className="w-8 h-8 text-purple-600" />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Patients List */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-xl font-bold text-gray-800 mb-4">Patients</h2>
            <div className="space-y-3">
              {patients.map(patient => (
                <div
                  key={patient.id}
                  onClick={() => setSelectedPatient(patient)}
                  className={`p-4 rounded-lg border cursor-pointer transition-all ${
                    selectedPatient?.id === patient.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-semibold text-gray-800">{patient.name}</h3>
                      <p className="text-sm text-gray-600 mt-1">Score: {patient.lastScore}</p>
                      <p className="text-xs text-gray-500 mt-1">
                        Last: {new Date(patient.lastAssessment).toLocaleDateString()}
                      </p>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRiskColor(patient.riskLevel)}`}>
                      {patient.riskLevel}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Cognitive Trend Chart */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-xl font-bold text-gray-800 mb-4">
              {selectedPatient ? `${selectedPatient.name} - Cognitive Trend` : 'Cognitive Trend'}
            </h2>
            
            {selectedPatient ? (
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={patientHistory}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="date" 
                      tick={{ fontSize: 12 }}
                      tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                    />
                    <YAxis domain={[60, 100]} />
                    <Tooltip 
                      labelFormatter={(value) => new Date(value).toLocaleDateString()}
                      formatter={(value) => [`${value}`, 'Cognitive Score']}
                    />
                    <Legend />
                    <Line 
                      type="monotone" 
                      dataKey="score" 
                      stroke="#F4E04D" 
                      strokeWidth={2}
                      dot={{ fill: '#F4E04D', r: 4 }}
                      activeDot={{ r: 6 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-80 flex items-center justify-center">
                <div className="text-center">
                  <TrendingUp className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">Select a patient to view their cognitive trend</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

'use client';

import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import { Activity, Brain, Download, FileText, TrendingDown, AlertTriangle, Mic, Eye, Heart, Calendar, Filter, Search } from 'lucide-react';

interface Patient {
  id: string;
  name: string;
  age: number;
  gender: string;
  lastAssessment: string;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  baselineEstablished: boolean;
  cognitiveScore: number;
}

interface DigitalBiomarker {
  name: string;
  value: number;
  status: 'normal' | 'elevated' | 'reduced' | 'critical';
  trend: 'stable' | 'improving' | 'declining';
  description: string;
}

interface ClinicalAssessment {
  patientId: string;
  date: string;
  cognitiveScore: number;
  digitalBiomarkers: DigitalBiomarker[];
  anomalyDetection: {
    isAnomaly: boolean;
    anomalyScore: number;
    affectedMetrics: string[];
  };
  multilingualAnalysis?: {
    language: string;
    coherence: number;
    sentiment: string;
    emotionalIndicators: {
      enthusiasm: number;
      anxiety: number;
      confidence: number;
      confusion: number;
    };
  };
}

export default function DoctorPortal() {
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [clinicalData, setClinicalData] = useState<ClinicalAssessment[]>([]);
  const [digitalBiomarkers, setDigitalBiomarkers] = useState<DigitalBiomarker[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [riskFilter, setRiskFilter] = useState<string>('all');
  const [showDetailedView, setShowDetailedView] = useState(false);

  // Mock patient data
  const patients: Patient[] = [
    { id: '1', name: 'Rajesh Kumar', age: 68, gender: 'Male', lastAssessment: '2024-03-28', riskLevel: 'high', baselineEstablished: true, cognitiveScore: 65 },
    { id: '2', name: 'Meena Patel', age: 72, gender: 'Female', lastAssessment: '2024-03-28', riskLevel: 'medium', baselineEstablished: true, cognitiveScore: 75 },
    { id: '3', name: 'Amit Sharma', age: 65, gender: 'Male', lastAssessment: '2024-03-27', riskLevel: 'low', baselineEstablished: true, cognitiveScore: 88 },
    { id: '4', name: 'Sunita Rao', age: 70, gender: 'Female', lastAssessment: '2024-03-28', riskLevel: 'critical', baselineEstablished: false, cognitiveScore: 58 },
    { id: '5', name: 'Vikram Singh', age: 75, gender: 'Male', lastAssessment: '2024-03-26', riskLevel: 'medium', baselineEstablished: true, cognitiveScore: 72 },
  ];

  // Generate mock clinical data
  useEffect(() => {
    if (selectedPatient) {
      generateClinicalData(selectedPatient.id);
    }
  }, [selectedPatient]);

  const generateClinicalData = (patientId: string) => {
    const mockData: ClinicalAssessment[] = [];
    const today = new Date();
    
    for (let i = 29; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      
      const baseScore = patientId === '1' ? 65 : patientId === '4' ? 58 : patientId === '2' ? 75 : 82;
      const variation = Math.random() * 10 - 5;
      const score = Math.max(50, Math.min(95, baseScore + variation));
      
      const biomarkers: DigitalBiomarker[] = [
        {
          name: 'Vocal Tremor Frequency',
          value: 3.2 + Math.random() * 2,
          status: score < 70 ? 'elevated' : 'normal',
          trend: score < 70 ? 'declining' : 'stable',
          description: 'Frequency of vocal tremors indicating motor control'
        },
        {
          name: 'Emotional Blunting Index',
          value: score < 70 ? 0.7 : 0.3,
          status: score < 70 ? 'elevated' : 'normal',
          trend: score < 70 ? 'declining' : 'stable',
          description: 'Reduction in emotional expression and facial animation'
        },
        {
          name: 'Speech Pause Duration',
          value: score < 70 ? 2.8 : 1.2,
          status: score < 70 ? 'elevated' : 'normal',
          trend: score < 70 ? 'declining' : 'stable',
          description: 'Average duration of pauses during speech'
        },
        {
          name: 'Pitch Variance',
          value: score < 70 ? 0.8 : 1.5,
          status: score < 70 ? 'reduced' : 'normal',
          trend: score < 70 ? 'declining' : 'stable',
          description: 'Variation in pitch during normal speech'
        },
        {
          name: 'Facial Symmetry Score',
          value: score < 70 ? 0.6 : 0.9,
          status: score < 70 ? 'reduced' : 'normal',
          trend: score < 70 ? 'declining' : 'stable',
          description: 'Symmetry of facial expressions and movements'
        }
      ];

      const multilingualAnalysis = Math.random() > 0.5 ? {
        language: Math.random() > 0.5 ? 'Hindi' : 'Marathi',
        coherence: 0.6 + Math.random() * 0.3,
        sentiment: score < 70 ? 'negative' : 'positive',
        emotionalIndicators: {
          enthusiasm: score < 70 ? 0.3 : 0.7,
          anxiety: score < 70 ? 0.8 : 0.2,
          confidence: score < 70 ? 0.4 : 0.8,
          confusion: score < 70 ? 0.7 : 0.2
        }
      } : undefined;

      mockData.push({
        patientId,
        date: date.toISOString().split('T')[0],
        cognitiveScore: Math.round(score),
        digitalBiomarkers: biomarkers,
        anomalyDetection: {
          isAnomaly: score < 70 && Math.random() > 0.5,
          anomalyScore: score < 70 ? 2.3 + Math.random() : 0.5,
          affectedMetrics: score < 70 ? ['cognitive_score', 'vocal_tremors', 'emotional_blunting'] : []
        },
        multilingualAnalysis
      });
    }
    
    setClinicalData(mockData);
    setDigitalBiomarkers(mockData[mockData.length - 1]?.digitalBiomarkers || []);
  };

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'critical': return 'text-red-600 bg-red-50 border-red-200';
      case 'high': return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'low': return 'text-green-600 bg-green-50 border-green-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getBiomarkerStatusColor = (status: string) => {
    switch (status) {
      case 'critical': return 'text-red-600';
      case 'elevated': return 'text-orange-600';
      case 'reduced': return 'text-blue-600';
      case 'normal': return 'text-green-600';
      default: return 'text-gray-600';
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving': return <TrendingDown className="w-4 h-4 text-green-600" />;
      case 'declining': return <TrendingDown className="w-4 h-4 text-red-600 rotate-180" />;
      default: return <Activity className="w-4 h-4 text-gray-600" />;
    }
  };

  const filteredPatients = patients.filter(patient => {
    const matchesSearch = patient.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRisk = riskFilter === 'all' || patient.riskLevel === riskFilter;
    return matchesSearch && matchesRisk;
  });

  const generatePDFReport = () => {
    // In a real implementation, this would generate and download a PDF
    alert('PDF report generation would be implemented here using jspdf or similar library');
  };

  const radarData = digitalBiomarkers.map(biomarker => ({
    biomarker: biomarker.name.split(' ')[0],
    value: biomarker.value * 20, // Scale for radar chart
    fullMark: 100
  }));

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-800">Clinical Decision Support Portal</h1>
            <p className="text-gray-600 mt-1">Advanced Digital Biomarker Analysis & Patient Monitoring</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={generatePDFReport}
              disabled={!selectedPatient}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Download className="w-4 h-4" />
              Generate Report
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Patient List */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-gray-800">Patients</h2>
              <div className="flex gap-2">
                <div className="relative">
                  <Search className="w-4 h-4 absolute left-3 top-2.5 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-9 pr-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <select
                  value={riskFilter}
                  onChange={(e) => setRiskFilter(e.target.value)}
                  className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="all">All Risks</option>
                  <option value="critical">Critical</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
              </div>
            </div>
            
            <div className="space-y-3">
              {filteredPatients.map(patient => (
                <div
                  key={patient.id}
                  onClick={() => setSelectedPatient(patient)}
                  className={`p-4 rounded-lg border cursor-pointer transition-all ${
                    selectedPatient?.id === patient.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h3 className="font-semibold text-gray-800">{patient.name}</h3>
                      <p className="text-sm text-gray-600">{patient.age} years, {patient.gender}</p>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getRiskColor(patient.riskLevel)}`}>
                      {patient.riskLevel}
                    </span>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-600">Score: {patient.cognitiveScore}</span>
                    <span className="text-gray-500">
                      {patient.baselineEstablished ? 
                        <span className="text-green-600">✓ Baseline</span> : 
                        <span className="text-orange-600">No Baseline</span>
                      }
                    </span>
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    Last: {new Date(patient.lastAssessment).toLocaleDateString()}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Clinical Dashboard */}
        <div className="lg:col-span-2 space-y-6">
          {selectedPatient ? (
            <>
              {/* Patient Overview */}
              <div className="bg-white rounded-xl shadow-sm p-6">
                <div className="flex justify-between items-start mb-6">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-800">{selectedPatient.name}</h2>
                    <p className="text-gray-600">{selectedPatient.age} years, {selectedPatient.gender}</p>
                  </div>
                  <div className="text-right">
                    <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium border ${getRiskColor(selectedPatient.riskLevel)}`}>
                      <AlertTriangle className="w-4 h-4" />
                      {selectedPatient.riskLevel.toUpperCase()} RISK
                    </div>
                    <div className="text-sm text-gray-500 mt-1">
                      Latest Score: {selectedPatient.cognitiveScore}
                    </div>
                  </div>
                </div>

                {/* Digital Biomarkers */}
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                    <Brain className="w-5 h-5 text-blue-600" />
                    Digital Biomarkers
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {digitalBiomarkers.map((biomarker, index) => (
                      <div key={index} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <h4 className="font-medium text-gray-800">{biomarker.name}</h4>
                            <p className="text-xs text-gray-600 mt-1">{biomarker.description}</p>
                          </div>
                          <div className="flex items-center gap-2">
                            {getTrendIcon(biomarker.trend)}
                            <span className={`text-sm font-medium ${getBiomarkerStatusColor(biomarker.status)}`}>
                              {biomarker.value.toFixed(2)}
                            </span>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="flex-1 bg-gray-200 rounded-full h-2">
                            <div 
                              className={`h-2 rounded-full ${
                                biomarker.status === 'critical' ? 'bg-red-500' :
                                biomarker.status === 'elevated' ? 'bg-orange-500' :
                                biomarker.status === 'reduced' ? 'bg-blue-500' : 'bg-green-500'
                              }`}
                              style={{ width: `${Math.min(biomarker.value * 20, 100)}%` }}
                            />
                          </div>
                          <span className="text-xs text-gray-500 capitalize">{biomarker.status}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Biomarker Radar Chart */}
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">Biomarker Overview</h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <RadarChart data={radarData}>
                        <PolarGrid />
                        <PolarAngleAxis dataKey="biomarker" />
                        <PolarRadiusAxis angle={90} domain={[0, 100]} />
                        <Radar name="Current Values" dataKey="value" stroke="#F4E04D" fill="#F4E04D" fillOpacity={0.6} />
                      </RadarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Cognitive Trend */}
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">Cognitive Score Trend</h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={clinicalData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis 
                          dataKey="date" 
                          tick={{ fontSize: 12 }}
                          tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                        />
                        <YAxis domain={[50, 100]} />
                        <Tooltip 
                          labelFormatter={(value) => new Date(value).toLocaleDateString()}
                          formatter={(value) => [`${value}`, 'Cognitive Score']}
                        />
                        <Legend />
                        <Line 
                          type="monotone" 
                          dataKey="cognitiveScore" 
                          stroke="#F4E04D" 
                          strokeWidth={2}
                          dot={{ fill: '#F4E04D', r: 3 }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Anomaly Detection */}
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5 text-orange-600" />
                    Anomaly Detection
                  </h3>
                  {clinicalData.filter(d => d.anomalyDetection.isAnomaly).length > 0 ? (
                    <div className="space-y-3">
                      {clinicalData.filter(d => d.anomalyDetection.isAnomaly).slice(-3).map((assessment, index) => (
                        <div key={index} className="border border-orange-200 bg-orange-50 rounded-lg p-4">
                          <div className="flex justify-between items-start">
                            <div>
                              <p className="font-medium text-orange-800">Anomaly Detected</p>
                              <p className="text-sm text-orange-600 mt-1">
                                Date: {new Date(assessment.date).toLocaleDateString()}
                              </p>
                              <p className="text-sm text-orange-600">
                                Score: {assessment.cognitiveScore} (Anomaly Score: {assessment.anomalyDetection.anomalyScore.toFixed(2)})
                              </p>
                            </div>
                            <div className="text-right">
                              <p className="text-xs text-orange-600">Affected Metrics:</p>
                              <div className="flex flex-wrap gap-1 mt-1">
                                {assessment.anomalyDetection.affectedMetrics.map((metric, i) => (
                                  <span key={i} className="px-2 py-1 bg-orange-200 text-orange-800 rounded text-xs">
                                    {metric.replace('_', ' ')}
                                  </span>
                                ))}
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-4 text-gray-500">
                      <Activity className="w-8 h-8 mx-auto mb-2" />
                      <p>No anomalies detected in recent assessments</p>
                    </div>
                  )}
                </div>

                {/* Multilingual Analysis */}
                {clinicalData[clinicalData.length - 1]?.multilingualAnalysis && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                      <Mic className="w-5 h-5 text-purple-600" />
                      Multilingual Analysis
                    </h3>
                    <div className="border border-gray-200 rounded-lg p-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <p className="text-sm text-gray-600">Language</p>
                          <p className="font-medium text-gray-800">
                            {clinicalData[clinicalData.length - 1].multilingualAnalysis?.language}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Semantic Coherence</p>
                          <p className="font-medium text-gray-800">
                            {(clinicalData[clinicalData.length - 1].multilingualAnalysis?.coherence || 0).toFixed(2)}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Sentiment</p>
                          <p className="font-medium text-gray-800 capitalize">
                            {clinicalData[clinicalData.length - 1].multilingualAnalysis?.sentiment}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Emotional Indicators</p>
                          <div className="flex gap-2 mt-1">
                            <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded">
                              E: {(clinicalData[clinicalData.length - 1].multilingualAnalysis?.emotionalIndicators.enthusiasm || 0).toFixed(2)}
                            </span>
                            <span className="text-xs px-2 py-1 bg-red-100 text-red-800 rounded">
                              A: {(clinicalData[clinicalData.length - 1].multilingualAnalysis?.emotionalIndicators.anxiety || 0).toFixed(2)}
                            </span>
                            <span className="text-xs px-2 py-1 bg-green-100 text-green-800 rounded">
                              C: {(clinicalData[clinicalData.length - 1].multilingualAnalysis?.emotionalIndicators.confidence || 0).toFixed(2)}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="bg-white rounded-xl shadow-sm p-12 text-center">
              <Brain className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-800 mb-2">Select a Patient</h3>
              <p className="text-gray-600">Choose a patient from the list to view their detailed clinical analysis</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

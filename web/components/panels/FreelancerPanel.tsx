// components/panels/FreelancerPanel.tsx
'use client';

import React, { useState, useEffect } from 'react';
import {
  DollarSign, Clock, Star, TrendingUp, FileText,
  Search, Plus, Eye, MessageSquare, Calendar,
  CheckCircle, XCircle, AlertCircle, User, Settings,
  Filter, RefreshCw, Target, Award, Briefcase
} from 'lucide-react';

interface FreelancerStats {
  totalEarnings: number;
  activeProjects: number;
  completedProjects: number;
  averageRating: number;
  totalReviews: number;
  successRate: number;
  availableJobs: number;
  pendingProposals: number;
}

interface Project {
  id: number;
  title: string;
  description: string;
  budget: number;
  currency: string;
  category: string;
  skillsRequired: string[];
  customer: {
    id: number;
    name: string;
    rating: number;
    location: string;
  };
  deadline?: string;
  postedAt: string;
  proposalCount: number;
  maxProposals: number;
  isBookmarked?: boolean;
}

interface MyProposal {
  id: number;
  project: {
    id: number;
    title: string;
    customer: string;
  };
  proposedBudget: number;
  proposedTimeframe: string;
  status: 'pending' | 'accepted' | 'rejected';
  submittedAt: string;
  coverLetter: string;
}

interface ActiveContract {
  id: number;
  project: {
    id: number;
    title: string;
    customer: string;
  };
  budget: number;
  startDate: string;
  deadline?: string;
  status: 'active' | 'paused' | 'completed';
  progress: number;
  milestones: {
    id: number;
    title: string;
    amount: number;
    completed: boolean;
    dueDate?: string;
  }[];
}

const FreelancerPanel: React.FC = () => {
  const [stats, setStats] = useState<FreelancerStats | null>(null);
  const [availableJobs, setAvailableJobs] = useState<Project[]>([]);
  const [myProposals, setMyProposals] = useState<MyProposal[]>([]);
  const [activeContracts, setActiveContracts] = useState<ActiveContract[]>([]);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [budgetFilter, setBudgetFilter] = useState('all');
  const [showProposalModal, setShowProposalModal] = useState(false);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);

  useEffect(() => {
    fetchFreelancerStats();
    if (activeTab === 'jobs') {
      fetchAvailableJobs();
    } else if (activeTab === 'proposals') {
      fetchMyProposals();
    } else if (activeTab === 'contracts') {
      fetchActiveContracts();
    }
  }, [activeTab]);

  const fetchFreelancerStats = async () => {
    try {
      const response = await fetch('/api/freelancer/dashboard', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching freelancer stats:', error);
    }
  };

  const fetchAvailableJobs = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (searchTerm) params.append('search', searchTerm);
      if (categoryFilter !== 'all') params.append('category', categoryFilter);
      if (budgetFilter !== 'all') params.append('budget', budgetFilter);

      const response = await fetch(`/api/projects/available?${params}`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const data = await response.json();
      setAvailableJobs(data.data || []);
    } catch (error) {
      console.error('Error fetching available jobs:', error);
    }
    setLoading(false);
  };

  const fetchMyProposals = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/proposals', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const data = await response.json();
      setMyProposals(data.data || []);
    } catch (error) {
      console.error('Error fetching proposals:', error);
    }
    setLoading(false);
  };

  const fetchActiveContracts = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/freelancer/contracts', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const data = await response.json();
      setActiveContracts(data.data || []);
    } catch (error) {
      console.error('Error fetching contracts:', error);
    }
    setLoading(false);
  };

  const submitProposal = async (projectId: number, proposalData: any) => {
    try {
      await fetch('/api/proposals', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          project_id: projectId,
          ...proposalData
        })
      });
      setShowProposalModal(false);
      fetchMyProposals();
      fetchFreelancerStats();
    } catch (error) {
      console.error('Error submitting proposal:', error);
    }
  };

  const bookmarkProject = async (projectId: number) => {
    try {
      await fetch(`/api/projects/${projectId}/bookmark`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      fetchAvailableJobs();
    } catch (error) {
      console.error('Error bookmarking project:', error);
    }
  };

  const filteredJobs = availableJobs.filter(job => {
    if (searchTerm && !job.title.toLowerCase().includes(searchTerm.toLowerCase()) &&
      !job.description.toLowerCase().includes(searchTerm.toLowerCase())) {
      return false;
    }
    if (categoryFilter !== 'all' && job.category !== categoryFilter) {
      return false;
    }
    if (budgetFilter !== 'all') {
      if (budgetFilter === 'low' && job.budget > 1000) return false;
      if (budgetFilter === 'medium' && (job.budget <= 1000 || job.budget > 5000)) return false;
      if (budgetFilter === 'high' && job.budget <= 5000) return false;
    }
    return true;
  });

  const pendingProposals = myProposals.filter(p => p.status === 'pending');
  const acceptedProposals = myProposals.filter(p => p.status === 'accepted');

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: TrendingUp },
    { id: 'jobs', label: 'Browse Jobs', icon: Search },
    { id: 'proposals', label: 'My Proposals', icon: FileText },
    { id: 'contracts', label: 'Active Work', icon: Briefcase },
    { id: 'earnings', label: 'Earnings', icon: DollarSign },
    { id: 'profile', label: 'Profile', icon: User }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center space-x-3">
              <Briefcase className="h-8 w-8 text-green-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Freelancer Dashboard</h1>
                <p className="text-sm text-gray-500">Find work and manage your projects</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <div className="text-sm text-gray-500">
                <span className="font-medium">${stats?.totalEarnings?.toLocaleString()}</span> earned
              </div>
              <button
                onClick={() => window.location.reload()}
                className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm rounded-md text-gray-700 bg-white hover:bg-gray-50"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex space-x-8">
          {/* Sidebar Navigation */}
          <div className="w-64 flex-shrink-0">
            <nav className="space-y-1">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${activeTab === tab.id
                    ? 'bg-green-100 text-green-700 border-green-200'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                    }`}
                >
                  <tab.icon className="h-5 w-5 mr-3" />
                  {tab.label}
                  {tab.id === 'proposals' && pendingProposals.length > 0 && (
                    <span className="ml-auto bg-yellow-100 text-yellow-600 text-xs rounded-full px-2 py-1">
                      {pendingProposals.length}
                    </span>
                  )}
                  {tab.id === 'contracts' && activeContracts.length > 0 && (
                    <span className="ml-auto bg-blue-100 text-blue-600 text-xs rounded-full px-2 py-1">
                      {activeContracts.length}
                    </span>
                  )}
                </button>
              ))}
            </nav>

            {/* Quick Stats Sidebar */}
            {stats && (
              <div className="mt-8 bg-white p-4 rounded-lg shadow-sm border">
                <h3 className="text-sm font-medium text-gray-900 mb-3">Quick Stats</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">Rating</span>
                    <div className="flex items-center space-x-1">
                      <Star className="h-4 w-4 text-yellow-400 fill-current" />
                      <span className="text-sm font-semibold text-gray-900">{stats.averageRating}/5</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">Completed</span>
                    <span className="text-sm font-semibold text-green-600">{stats.completedProjects}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">Success Rate</span>
                    <span className="text-sm font-semibold text-blue-600">{stats.successRate}%</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">Available Jobs</span>
                    <span className="text-sm font-semibold text-purple-600">{stats.availableJobs}</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Main Content */}
          <div className="flex-1 min-w-0">
            {activeTab === 'dashboard' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-lg font-medium text-gray-900 mb-4">Performance Overview</h2>
                  {stats && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                      <div className="bg-white p-6 rounded-lg shadow-sm border">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <DollarSign className="h-6 w-6 text-green-600" />
                          </div>
                          <div className="ml-4">
                            <p className="text-sm font-medium text-gray-500">Total Earnings</p>
                            <p className="text-2xl font-semibold text-gray-900">${stats.totalEarnings?.toLocaleString()}</p>
                          </div>
                        </div>
                      </div>

                      <div className="bg-white p-6 rounded-lg shadow-sm border">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <Star className="h-6 w-6 text-yellow-600" />
                          </div>
                          <div className="ml-4">
                            <p className="text-sm font-medium text-gray-500">Average Rating</p>
                            <p className="text-2xl font-semibold text-gray-900">{stats.averageRating}/5</p>
                          </div>
                        </div>
                      </div>

                      <div className="bg-white p-6 rounded-lg shadow-sm border">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <CheckCircle className="h-6 w-6 text-blue-600" />
                          </div>
                          <div className="ml-4">
                            <p className="text-sm font-medium text-gray-500">Completed Projects</p>
                            <p className="text-2xl font-semibold text-gray-900">{stats.completedProjects}</p>
                          </div>
                        </div>
                      </div>

                      <div className="bg-white p-6 rounded-lg shadow-sm border">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <Target className="h-6 w-6 text-purple-600" />
                          </div>
                          <div className="ml-4">
                            <p className="text-sm font-medium text-gray-500">Success Rate</p>
                            <p className="text-2xl font-semibold text-gray-900">{stats.successRate}%</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Recent Opportunities */}
                  <div className="bg-white p-6 rounded-lg shadow-sm border">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-medium text-gray-900">New Opportunities</h3>
                      <button
                        onClick={() => setActiveTab('jobs')}
                        className="text-sm text-green-600 hover:text-green-700"
                      >
                        Browse All
                      </button>
                    </div>
                    <div className="space-y-3">
                      {availableJobs.slice(0, 5).map((job) => (
                        <div key={job.id} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-b-0">
                          <div>
                            <p className="text-sm font-medium text-gray-900">{job.title}</p>
                            <p className="text-xs text-gray-500">{job.category} • {job.proposalCount} proposals</p>
                          </div>
                          <div className="text-right">
                            <p className="text-sm font-medium text-gray-900">${job.budget}</p>
                            <p className="text-xs text-gray-500">{job.currency}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Active Work */}
                  <div className="bg-white p-6 rounded-lg shadow-sm border">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-medium text-gray-900">Active Work</h3>
                      <button
                        onClick={() => setActiveTab('contracts')}
                        className="text-sm text-green-600 hover:text-green-700"
                      >
                        View All
                      </button>
                    </div>
                    <div className="space-y-3">
                      {activeContracts.slice(0, 5).map((contract) => (
                        <div key={contract.id} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-b-0">
                          <div>
                            <p className="text-sm font-medium text-gray-900">{contract.project.title}</p>
                            <p className="text-xs text-gray-500">{contract.project.customer}</p>
                          </div>
                          <div className="text-right">
                            <p className="text-sm font-medium text-gray-900">{contract.progress}%</p>
                            <p className="text-xs text-gray-500">Complete</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'jobs' && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-medium text-gray-900">Browse Jobs</h2>
                  <div className="text-sm text-gray-500">
                    {filteredJobs.length} jobs available
                  </div>
                </div>

                {/* Filters */}
                <div className="bg-white p-4 rounded-lg shadow-sm border">
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Search</label>
                      <div className="relative">
                        <input
                          type="text"
                          placeholder="Search jobs..."
                          value={searchTerm}
                          onChange={(e) => setSearchTerm(e.target.value)}
                          className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                        />
                        <Search className="h-4 w-4 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
                      <select
                        value={categoryFilter}
                        onChange={(e) => setCategoryFilter(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                      >
                        <option value="all">All Categories</option>
                        <option value="web-development">Web Development</option>
                        <option value="mobile-development">Mobile Development</option>
                        <option value="design">Design</option>
                        <option value="writing">Writing</option>
                        <option value="marketing">Marketing</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Budget</label>
                      <select
                        value={budgetFilter}
                        onChange={(e) => setBudgetFilter(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                      >
                        <option value="all">All Budgets</option>
                        <option value="low">Under $1,000</option>
                        <option value="medium">$1,000 - $5,000</option>
                        <option value="high">Over $5,000</option>
                      </select>
                    </div>

                    <div className="flex items-end">
                      <button
                        onClick={fetchAvailableJobs}
                        className="w-full inline-flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700"
                      >
                        <Filter className="h-4 w-4 mr-2" />
                        Apply Filters
                      </button>
                    </div>
                  </div>
                </div>

                {/* Jobs List */}
                <div className="space-y-4">
                  {loading ? (
                    <div className="flex items-center justify-center py-12">
                      <RefreshCw className="h-6 w-6 animate-spin text-gray-400" />
                    </div>
                  ) : (
                    filteredJobs.map((job) => (
                      <div key={job.id} className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow">
                        <div className="p-6">
                          <div className="flex items-start justify-between mb-4">
                            <div className="flex-1">
                              <h3 className="text-lg font-medium text-gray-900 mb-2">{job.title}</h3>
                              <p className="text-sm text-gray-600 line-clamp-2 mb-3">{job.description}</p>

                              <div className="flex items-center space-x-4 text-sm text-gray-500 mb-3">
                                <span className="flex items-center">
                                  <DollarSign className="h-4 w-4 mr-1" />
                                  ${job.budget} {job.currency}
                                </span>
                                <span className="flex items-center">
                                  <FileText className="h-4 w-4 mr-1" />
                                  {job.proposalCount}/{job.maxProposals} proposals
                                </span>
                                <span className="flex items-center">
                                  <Calendar className="h-4 w-4 mr-1" />
                                  Posted {new Date(job.postedAt).toLocaleDateString()}
                                </span>
                              </div>

                              <div className="flex items-center space-x-3 mb-3">
                                <span className="inline-flex px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded">
                                  {job.category}
                                </span>
                                <div className="flex items-center space-x-1">
                                  <Star className="h-4 w-4 text-yellow-400 fill-current" />
                                  <span className="text-sm text-gray-600">{job.customer.rating}/5</span>
                                </div>
                                <span className="text-sm text-gray-500">{job.customer.location}</span>
                              </div>

                              {job.skillsRequired && job.skillsRequired.length > 0 && (
                                <div className="flex flex-wrap gap-1">
                                  {job.skillsRequired.slice(0, 5).map((skill, index) => (
                                    <span key={index} className="inline-flex px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">
                                      {skill}
                                    </span>
                                  ))}
                                  {job.skillsRequired.length > 5 && (
                                    <span className="inline-flex px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">
                                      +{job.skillsRequired.length - 5} more
                                    </span>
                                  )}
                                </div>
                              )}
                            </div>
                          </div>

                          <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                            <div className="flex items-center space-x-2">
                              <button
                                onClick={() => {
                                  setSelectedProject(job);
                                  setShowProposalModal(true);
                                }}
                                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700"
                                disabled={job.proposalCount >= job.maxProposals}
                              >
                                <Plus className="h-4 w-4 mr-2" />
                                {job.proposalCount >= job.maxProposals ? 'Proposals Full' : 'Submit Proposal'}
                              </button>
                              <button
                                onClick={() => console.log('View details', job.id)}
                                className="text-gray-600 hover:text-gray-700"
                                title="View Details"
                              >
                                <Eye className="h-4 w-4" />
                              </button>
                              <button
                                onClick={() => bookmarkProject(job.id)}
                                className="text-gray-600 hover:text-gray-700"
                                title="Save Job"
                              >
                                <Star className={`h-4 w-4 ${job.isBookmarked ? 'fill-current text-yellow-400' : ''}`} />
                              </button>
                            </div>
                            <div className="text-sm text-gray-500">
                              Client: {job.customer.name}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}

            {activeTab === 'proposals' && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-medium text-gray-900">My Proposals</h2>
                  <div className="text-sm text-gray-500">
                    {pendingProposals.length} pending • {acceptedProposals.length} accepted
                  </div>
                </div>

                <div className="bg-white shadow-sm border rounded-lg overflow-hidden">
                  {loading ? (
                    <div className="flex items-center justify-center py-12">
                      <RefreshCw className="h-6 w-6 animate-spin text-gray-400" />
                    </div>
                  ) : (
                    <div className="divide-y divide-gray-200">
                      {myProposals.map((proposal) => (
                        <div key={proposal.id} className="p-6 hover:bg-gray-50">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <h3 className="text-lg font-medium text-gray-900 mb-2">{proposal.project.title}</h3>
                              <p className="text-sm text-gray-600 mb-3">{proposal.coverLetter}</p>

                              <div className="grid grid-cols-2 gap-4 text-sm mb-3">
                                <div>
                                  <span className="text-gray-500">Proposed Budget:</span>
                                  <span className="ml-2 font-medium">${proposal.proposedBudget}</span>
                                </div>
                                <div>
                                  <span className="text-gray-500">Timeframe:</span>
                                  <span className="ml-2 font-medium">{proposal.proposedTimeframe}</span>
                                </div>
                              </div>

                              <p className="text-xs text-gray-500">
                                Client: {proposal.project.customer}
                              </p>
                            </div>

                            <div className="flex flex-col items-end space-y-2">
                              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${proposal.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                                proposal.status === 'accepted' ? 'bg-green-100 text-green-800' :
                                  'bg-red-100 text-red-800'
                                }`}>
                                {proposal.status}
                              </span>

                              <span className="text-xs text-gray-500">
                                {new Date(proposal.submittedAt).toLocaleDateString()}
                              </span>

                              <div className="flex space-x-2">
                                <button
                                  onClick={() => console.log('View proposal', proposal.id)}
                                  className="text-blue-600 hover:text-blue-700"
                                  title="View Details"
                                >
                                  <Eye className="h-4 w-4" />
                                </button>
                                <button
                                  onClick={() => console.log('Message client', proposal.project.id)}
                                  className="text-gray-600 hover:text-gray-700"
                                  title="Message Client"
                                >
                                  <MessageSquare className="h-4 w-4" />
                                </button>
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'contracts' && (
              <div className="space-y-6">
                <h2 className="text-lg font-medium text-gray-900">Active Work</h2>
                <div className="bg-white p-8 rounded-lg shadow-sm border text-center">
                  <Briefcase className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">Active contracts and project management will be implemented here</p>
                </div>
              </div>
            )}

            {activeTab === 'earnings' && (
              <div className="space-y-6">
                <h2 className="text-lg font-medium text-gray-900">Earnings</h2>
                <div className="bg-white p-8 rounded-lg shadow-sm border text-center">
                  <DollarSign className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">Earnings history and analytics will be implemented here</p>
                </div>
              </div>
            )}

            {activeTab === 'profile' && (
              <div className="space-y-6">
                <h2 className="text-lg font-medium text-gray-900">Profile Settings</h2>
                <div className="bg-white p-8 rounded-lg shadow-sm border text-center">
                  <User className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">Profile management and settings will be implemented here</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Proposal Modal */}
      {showProposalModal && selectedProject && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Submit Proposal</h3>
                <button
                  onClick={() => setShowProposalModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XCircle className="h-6 w-6" />
                </button>
              </div>

              <div className="mb-6">
                <h4 className="font-medium text-gray-900 mb-2">{selectedProject.title}</h4>
                <p className="text-sm text-gray-600 mb-3">{selectedProject.description}</p>
                <div className="flex items-center space-x-4 text-sm text-gray-500">
                  <span>Budget: ${selectedProject.budget} {selectedProject.currency}</span>
                  <span>Category: {selectedProject.category}</span>
                </div>
              </div>

              <form onSubmit={(e) => {
                e.preventDefault();
                const formData = new FormData(e.target as HTMLFormElement);
                const proposalData = {
                  proposed_budget: Number(formData.get('budget')),
                  proposed_timeframe: formData.get('timeframe'),
                  cover_letter: formData.get('coverLetter')
                };
                submitProposal(selectedProject.id, proposalData);
              }}>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Your Proposed Budget ($)
                    </label>
                    <input
                      type="number"
                      name="budget"
                      required
                      min="1"
                      max={selectedProject.budget}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                      placeholder="Enter your budget"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Estimated Timeframe
                    </label>
                    <select
                      name="timeframe"
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                    >
                      <option value="">Select timeframe</option>
                      <option value="1-3 days">1-3 days</option>
                      <option value="1 week">1 week</option>
                      <option value="2 weeks">2 weeks</option>
                      <option value="1 month">1 month</option>
                      <option value="2-3 months">2-3 months</option>
                      <option value="3+ months">3+ months</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Cover Letter
                    </label>
                    <textarea
                      name="coverLetter"
                      required
                      rows={6}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                      placeholder="Explain why you're the best fit for this project..."
                    />
                  </div>
                </div>

                <div className="mt-6 flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={() => setShowProposalModal(false)}
                    className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700"
                  >
                    Submit Proposal
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FreelancerPanel;
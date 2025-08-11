// components/panels/CustomerPanel.tsx
import React, { useState, useEffect } from 'react';
import {
  FileText, Users, DollarSign, Clock, Plus,
  Eye, Edit, Trash2, Star, MessageSquare, TrendingUp,
  Search, Filter, Calendar, CheckCircle, XCircle,
  AlertCircle, PlayCircle, PauseCircle, RefreshCw
} from 'lucide-react';

interface CustomerStats {
  activeProjects: number;
  totalProjects: number;
  totalSpent: number;
  avgProjectCost: number;
  pendingProposals: number;
  completedProjects: number;
}

interface Project {
  id: number;
  title: string;
  description: string;
  budget: number;
  currency: string;
  status: 'draft' | 'open' | 'in_progress' | 'completed' | 'cancelled';
  category: string;
  skillsRequired: string[];
  proposalCount: number;
  maxProposals: number;
  createdAt: string;
  deadline?: string;
  freelancer?: {
    id: number;
    name: string;
    avatar?: string;
    rating: number;
  };
}

interface Proposal {
  id: number;
  projectId: number;
  projectTitle: string;
  freelancer: {
    id: number;
    name: string;
    avatar?: string;
    rating: number;
    hourlyRate?: number;
  };
  proposedBudget: number;
  proposedTimeframe: string;
  coverLetter: string;
  status: 'pending' | 'accepted' | 'rejected';
  submittedAt: string;
}

const CustomerPanel: React.FC = () => {
  const [stats, setStats] = useState<CustomerStats | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showNewProjectModal, setShowNewProjectModal] = useState(false);

  useEffect(() => {
    fetchCustomerStats();
    if (activeTab === 'projects') {
      fetchProjects();
    } else if (activeTab === 'proposals') {
      fetchProposals();
    }
  }, [activeTab]);

  const fetchCustomerStats = async () => {
    try {
      const response = await fetch('/api/customer/dashboard', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching customer stats:', error);
    }
  };

  const fetchProjects = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (searchTerm) params.append('search', searchTerm);
      if (statusFilter !== 'all') params.append('status', statusFilter);

      const response = await fetch(`/api/projects?${params}`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const data = await response.json();
      setProjects(data.data || []);
    } catch (error) {
      console.error('Error fetching projects:', error);
    }
    setLoading(false);
  };

  const fetchProposals = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/proposals', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const data = await response.json();
      setProposals(data.data || []);
    } catch (error) {
      console.error('Error fetching proposals:', error);
    }
    setLoading(false);
  };

  const updateProjectStatus = async (projectId: number, status: string) => {
    try {
      await fetch(`/api/projects/${projectId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ status })
      });
      fetchProjects();
      fetchCustomerStats();
    } catch (error) {
      console.error('Error updating project status:', error);
    }
  };

  const deleteProject = async (projectId: number) => {
    if (!confirm('Are you sure you want to delete this project?')) return;

    try {
      await fetch(`/api/projects/${projectId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      fetchProjects();
      fetchCustomerStats();
    } catch (error) {
      console.error('Error deleting project:', error);
    }
  };

  const respondToProposal = async (proposalId: number, action: 'accept' | 'reject') => {
    try {
      await fetch(`/api/proposals/${proposalId}/${action}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      fetchProposals();
      fetchCustomerStats();
    } catch (error) {
      console.error('Error responding to proposal:', error);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'draft': return <Edit className="h-4 w-4" />;
      case 'open': return <PlayCircle className="h-4 w-4" />;
      case 'in_progress': return <Clock className="h-4 w-4" />;
      case 'completed': return <CheckCircle className="h-4 w-4" />;
      case 'cancelled': return <XCircle className="h-4 w-4" />;
      default: return <AlertCircle className="h-4 w-4" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft': return 'bg-gray-100 text-gray-800';
      case 'open': return 'bg-blue-100 text-blue-800';
      case 'in_progress': return 'bg-yellow-100 text-yellow-800';
      case 'completed': return 'bg-green-100 text-green-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredProjects = projects.filter(project => {
    if (searchTerm && !project.title.toLowerCase().includes(searchTerm.toLowerCase()) &&
      !project.description.toLowerCase().includes(searchTerm.toLowerCase())) {
      return false;
    }
    if (statusFilter !== 'all' && project.status !== statusFilter) {
      return false;
    }
    return true;
  });

  const pendingProposals = proposals.filter(p => p.status === 'pending');

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: TrendingUp },
    { id: 'projects', label: 'My Projects', icon: FileText },
    { id: 'proposals', label: 'Proposals', icon: Users },
    { id: 'contracts', label: 'Active Contracts', icon: FileText },
    { id: 'payments', label: 'Payments', icon: DollarSign },
    { id: 'messages', label: 'Messages', icon: MessageSquare }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center space-x-3">
              <FileText className="h-8 w-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Customer Dashboard</h1>
                <p className="text-sm text-gray-500">Manage your projects and freelancers</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setShowNewProjectModal(true)}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
              >
                <Plus className="h-4 w-4 mr-2" />
                New Project
              </button>
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
                    ? 'bg-blue-100 text-blue-700 border-blue-200'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                    }`}
                >
                  <tab.icon className="h-5 w-5 mr-3" />
                  {tab.label}
                  {tab.id === 'proposals' && pendingProposals.length > 0 && (
                    <span className="ml-auto bg-red-100 text-red-600 text-xs rounded-full px-2 py-1">
                      {pendingProposals.length}
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
                    <span className="text-sm text-gray-500">Active Projects</span>
                    <span className="text-sm font-semibold text-blue-600">{stats.activeProjects}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">Total Spent</span>
                    <span className="text-sm font-semibold text-green-600">${stats.totalSpent?.toLocaleString()}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">Pending Proposals</span>
                    <span className="text-sm font-semibold text-yellow-600">{stats.pendingProposals}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">Completed</span>
                    <span className="text-sm font-semibold text-gray-600">{stats.completedProjects}</span>
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
                  <h2 className="text-lg font-medium text-gray-900 mb-4">Project Overview</h2>
                  {stats && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                      <div className="bg-white p-6 rounded-lg shadow-sm border">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <FileText className="h-6 w-6 text-blue-600" />
                          </div>
                          <div className="ml-4">
                            <p className="text-sm font-medium text-gray-500">Active Projects</p>
                            <p className="text-2xl font-semibold text-gray-900">{stats.activeProjects}</p>
                          </div>
                        </div>
                      </div>

                      <div className="bg-white p-6 rounded-lg shadow-sm border">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <DollarSign className="h-6 w-6 text-green-600" />
                          </div>
                          <div className="ml-4">
                            <p className="text-sm font-medium text-gray-500">Total Spent</p>
                            <p className="text-2xl font-semibold text-gray-900">${stats.totalSpent?.toLocaleString()}</p>
                          </div>
                        </div>
                      </div>

                      <div className="bg-white p-6 rounded-lg shadow-sm border">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <Users className="h-6 w-6 text-yellow-600" />
                          </div>
                          <div className="ml-4">
                            <p className="text-sm font-medium text-gray-500">Pending Proposals</p>
                            <p className="text-2xl font-semibold text-gray-900">{stats.pendingProposals}</p>
                          </div>
                        </div>
                      </div>

                      <div className="bg-white p-6 rounded-lg shadow-sm border">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <CheckCircle className="h-6 w-6 text-green-600" />
                          </div>
                          <div className="ml-4">
                            <p className="text-sm font-medium text-gray-500">Completed</p>
                            <p className="text-2xl font-semibold text-gray-900">{stats.completedProjects}</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Recent Projects */}
                  <div className="bg-white p-6 rounded-lg shadow-sm border">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-medium text-gray-900">Recent Projects</h3>
                      <button
                        onClick={() => setActiveTab('projects')}
                        className="text-sm text-blue-600 hover:text-blue-700"
                      >
                        View All
                      </button>
                    </div>
                    <div className="space-y-3">
                      {projects.slice(0, 5).map((project) => (
                        <div key={project.id} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-b-0">
                          <div>
                            <p className="text-sm font-medium text-gray-900">{project.title}</p>
                            <p className="text-xs text-gray-500">{project.proposalCount} proposals</p>
                          </div>
                          <span className={`inline-flex items-center px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(project.status)}`}>
                            {getStatusIcon(project.status)}
                            <span className="ml-1">{project.status}</span>
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Pending Proposals */}
                  <div className="bg-white p-6 rounded-lg shadow-sm border">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-medium text-gray-900">Pending Proposals</h3>
                      <button
                        onClick={() => setActiveTab('proposals')}
                        className="text-sm text-blue-600 hover:text-blue-700"
                      >
                        View All
                      </button>
                    </div>
                    <div className="space-y-3">
                      {pendingProposals.slice(0, 5).map((proposal) => (
                        <div key={proposal.id} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-b-0">
                          <div>
                            <p className="text-sm font-medium text-gray-900">{proposal.freelancer.name}</p>
                            <p className="text-xs text-gray-500">{proposal.projectTitle}</p>
                          </div>
                          <div className="text-right">
                            <p className="text-sm font-medium text-gray-900">${proposal.proposedBudget}</p>
                            <p className="text-xs text-gray-500">{proposal.proposedTimeframe}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'projects' && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-medium text-gray-900">My Projects</h2>
                  <button
                    onClick={() => setShowNewProjectModal(true)}
                    className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    New Project
                  </button>
                </div>

                {/* Filters */}
                <div className="bg-white p-4 rounded-lg shadow-sm border">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Search</label>
                      <div className="relative">
                        <input
                          type="text"
                          placeholder="Search projects..."
                          value={searchTerm}
                          onChange={(e) => setSearchTerm(e.target.value)}
                          className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                        <Search className="h-4 w-4 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
                      <select
                        value={statusFilter}
                        onChange={(e) => setStatusFilter(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="all">All Status</option>
                        <option value="draft">Draft</option>
                        <option value="open">Open</option>
                        <option value="in_progress">In Progress</option>
                        <option value="completed">Completed</option>
                        <option value="cancelled">Cancelled</option>
                      </select>
                    </div>

                    <div className="flex items-end">
                      <button
                        onClick={fetchProjects}
                        className="w-full inline-flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
                      >
                        <Filter className="h-4 w-4 mr-2" />
                        Apply Filters
                      </button>
                    </div>
                  </div>
                </div>

                {/* Projects Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {loading ? (
                    <div className="col-span-2 flex items-center justify-center py-12">
                      <RefreshCw className="h-6 w-6 animate-spin text-gray-400" />
                    </div>
                  ) : (
                    filteredProjects.map((project) => (
                      <div key={project.id} className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow">
                        <div className="p-6">
                          <div className="flex items-start justify-between mb-4">
                            <div className="flex-1">
                              <h3 className="text-lg font-medium text-gray-900 mb-2">{project.title}</h3>
                              <p className="text-sm text-gray-600 line-clamp-2">{project.description}</p>
                            </div>
                            <span className={`inline-flex items-center px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(project.status)}`}>
                              {getStatusIcon(project.status)}
                              <span className="ml-1">{project.status}</span>
                            </span>
                          </div>

                          <div className="grid grid-cols-2 gap-4 mb-4">
                            <div>
                              <p className="text-xs text-gray-500">Budget</p>
                              <p className="text-sm font-medium text-gray-900">${project.budget} {project.currency}</p>
                            </div>
                            <div>
                              <p className="text-xs text-gray-500">Proposals</p>
                              <p className="text-sm font-medium text-gray-900">{project.proposalCount}/{project.maxProposals}</p>
                            </div>
                          </div>

                          {project.skillsRequired && project.skillsRequired.length > 0 && (
                            <div className="mb-4">
                              <p className="text-xs text-gray-500 mb-2">Skills Required</p>
                              <div className="flex flex-wrap gap-1">
                                {project.skillsRequired.slice(0, 3).map((skill, index) => (
                                  <span key={index} className="inline-flex px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">
                                    {skill}
                                  </span>
                                ))}
                                {project.skillsRequired.length > 3 && (
                                  <span className="inline-flex px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">
                                    +{project.skillsRequired.length - 3} more
                                  </span>
                                )}
                              </div>
                            </div>
                          )}

                          <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                            <div className="flex items-center space-x-2 text-xs text-gray-500">
                              <Calendar className="h-3 w-3" />
                              <span>Created {new Date(project.createdAt).toLocaleDateString()}</span>
                            </div>
                            <div className="flex items-center space-x-2">
                              <button
                                onClick={() => console.log('View project', project.id)}
                                className="text-blue-600 hover:text-blue-700"
                                title="View Details"
                              >
                                <Eye className="h-4 w-4" />
                              </button>
                              {project.status === 'draft' || project.status === 'open' ? (
                                <button
                                  onClick={() => console.log('Edit project', project.id)}
                                  className="text-gray-600 hover:text-gray-700"
                                  title="Edit Project"
                                >
                                  <Edit className="h-4 w-4" />
                                </button>
                              ) : null}
                              {project.status === 'open' && (
                                <button
                                  onClick={() => updateProjectStatus(project.id, 'paused')}
                                  className="text-yellow-600 hover:text-yellow-700"
                                  title="Pause Project"
                                >
                                  <PauseCircle className="h-4 w-4" />
                                </button>
                              )}
                              {project.status === 'draft' && (
                                <button
                                  onClick={() => deleteProject(project.id)}
                                  className="text-red-600 hover:text-red-700"
                                  title="Delete Project"
                                >
                                  <Trash2 className="h-4 w-4" />
                                </button>
                              )}
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
                  <h2 className="text-lg font-medium text-gray-900">Proposals</h2>
                  <div className="text-sm text-gray-500">
                    {pendingProposals.length} pending review
                  </div>
                </div>

                <div className="bg-white shadow-sm border rounded-lg overflow-hidden">
                  {loading ? (
                    <div className="flex items-center justify-center py-12">
                      <RefreshCw className="h-6 w-6 animate-spin text-gray-400" />
                    </div>
                  ) : (
                    <div className="divide-y divide-gray-200">
                      {proposals.map((proposal) => (
                        <div key={proposal.id} className="p-6 hover:bg-gray-50">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-3 mb-2">
                                <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                                  {proposal.freelancer.avatar ? (
                                    <img src={proposal.freelancer.avatar} alt="" className="w-10 h-10 rounded-full" />
                                  ) : (
                                    <Users className="h-5 w-5 text-gray-500" />
                                  )}
                                </div>
                                <div>
                                  <h3 className="text-lg font-medium text-gray-900">{proposal.freelancer.name}</h3>
                                  <div className="flex items-center space-x-2">
                                    <div className="flex items-center">
                                      {Array.from({ length: 5 }).map((_, i) => (
                                        <Star
                                          key={i}
                                          className={`h-4 w-4 ${i < proposal.freelancer.rating ? 'text-yellow-400 fill-current' : 'text-gray-300'
                                            }`}
                                        />
                                      ))}
                                    </div>
                                    <span className="text-sm text-gray-500">({proposal.freelancer.rating}/5)</span>
                                  </div>
                                </div>
                              </div>

                              <p className="text-sm text-gray-600 mb-3">{proposal.projectTitle}</p>
                              <p className="text-sm text-gray-800 mb-4">{proposal.coverLetter}</p>

                              <div className="grid grid-cols-2 gap-4 text-sm">
                                <div>
                                  <span className="text-gray-500">Proposed Budget:</span>
                                  <span className="ml-2 font-medium">${proposal.proposedBudget}</span>
                                </div>
                                <div>
                                  <span className="text-gray-500">Timeframe:</span>
                                  <span className="ml-2 font-medium">{proposal.proposedTimeframe}</span>
                                </div>
                              </div>
                            </div>

                            <div className="flex flex-col items-end space-y-2">
                              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${proposal.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                                proposal.status === 'accepted' ? 'bg-green-100 text-green-800' :
                                  'bg-red-100 text-red-800'
                                }`}>
                                {proposal.status}
                              </span>

                              {proposal.status === 'pending' && (
                                <div className="flex space-x-2">
                                  <button
                                    onClick={() => respondToProposal(proposal.id, 'accept')}
                                    className="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded text-white bg-green-600 hover:bg-green-700"
                                  >
                                    Accept
                                  </button>
                                  <button
                                    onClick={() => respondToProposal(proposal.id, 'reject')}
                                    className="inline-flex items-center px-3 py-1 border border-gray-300 text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50"
                                  >
                                    Decline
                                  </button>
                                </div>
                              )}

                              <span className="text-xs text-gray-500">
                                {new Date(proposal.submittedAt).toLocaleDateString()}
                              </span>
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
                <h2 className="text-lg font-medium text-gray-900">Active Contracts</h2>
                <div className="bg-white p-8 rounded-lg shadow-sm border text-center">
                  <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">Active contracts management will be implemented here</p>
                </div>
              </div>
            )}

            {activeTab === 'payments' && (
              <div className="space-y-6">
                <h2 className="text-lg font-medium text-gray-900">Payment History</h2>
                <div className="bg-white p-8 rounded-lg shadow-sm border text-center">
                  <DollarSign className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">Payment history and billing will be implemented here</p>
                </div>
              </div>
            )}

            {activeTab === 'messages' && (
              <div className="space-y-6">
                <h2 className="text-lg font-medium text-gray-900">Messages</h2>
                <div className="bg-white p-8 rounded-lg shadow-sm border text-center">
                  <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">Messaging system will be implemented here</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* New Project Modal Placeholder */}
      {showNewProjectModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Create New Project</h3>
                <button
                  onClick={() => setShowNewProjectModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XCircle className="h-6 w-6" />
                </button>
              </div>
              <p className="text-gray-500">New project creation form will be implemented here</p>
              <div className="mt-6 flex justify-end space-x-3">
                <button
                  onClick={() => setShowNewProjectModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={() => setShowNewProjectModal(false)}
                  className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
                >
                  Create Project
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CustomerPanel;
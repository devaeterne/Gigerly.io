// components/panels/ModeratorPanel.tsx
import React, { useState, useEffect } from 'react';
import {
  Users, AlertTriangle, Flag, MessageSquare, FileText,
  Eye, CheckCircle, XCircle, Clock, Search, Filter,
  Shield, UserCheck, Ban, RefreshCw, TrendingUp
} from 'lucide-react';

interface ModeratorStats {
  pendingReports: number;
  activeUsers: number;
  projectsUnderReview: number;
  resolvedToday: number;
}

interface Report {
  id: number;
  type: 'user' | 'project' | 'dispute';
  reportedItem: string;
  reportedBy: string;
  reason: string;
  status: 'pending' | 'investigating' | 'resolved';
  createdAt: string;
  severity: 'low' | 'medium' | 'high';
}

interface User {
  id: number;
  email: string;
  role: string;
  status: string;
  isVerified: boolean;
  createdAt: string;
  lastActivity: string;
  reportCount: number;
}

const ModeratorPanel: React.FC = () => {
  const [stats, setStats] = useState<ModeratorStats | null>(null);
  const [reports, setReports] = useState<Report[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [severityFilter, setSeverityFilter] = useState('all');

  useEffect(() => {
    fetchModeratorStats();
    if (activeTab === 'reports') {
      fetchReports();
    } else if (activeTab === 'users') {
      fetchUsers();
    }
  }, [activeTab]);

  const fetchModeratorStats = async () => {
    try {
      const response = await fetch('/api/moderator/dashboard', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching moderator stats:', error);
    }
  };

  const fetchReports = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (searchTerm) params.append('search', searchTerm);
      if (statusFilter !== 'all') params.append('status', statusFilter);
      if (severityFilter !== 'all') params.append('severity', severityFilter);

      const response = await fetch(`/api/moderator/reports?${params}`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const data = await response.json();
      setReports(data.data || []);
    } catch (error) {
      console.error('Error fetching reports:', error);
    }
    setLoading(false);
  };

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/moderator/users', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const data = await response.json();
      setUsers(data.data || []);
    } catch (error) {
      console.error('Error fetching users:', error);
    }
    setLoading(false);
  };

  const updateReportStatus = async (reportId: number, status: string) => {
    try {
      await fetch(`/api/moderator/reports/${reportId}/status`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ status })
      });
      fetchReports();
      fetchModeratorStats(); // Refresh stats
    } catch (error) {
      console.error('Error updating report status:', error);
    }
  };

  const moderateUser = async (userId: number, action: string) => {
    try {
      await fetch(`/api/moderator/users/${userId}/moderate`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ action })
      });
      fetchUsers();
    } catch (error) {
      console.error('Error moderating user:', error);
    }
  };

  const filteredReports = reports.filter(report => {
    if (searchTerm && !report.reportedItem.toLowerCase().includes(searchTerm.toLowerCase()) &&
      !report.reportedBy.toLowerCase().includes(searchTerm.toLowerCase())) {
      return false;
    }
    if (statusFilter !== 'all' && report.status !== statusFilter) {
      return false;
    }
    if (severityFilter !== 'all' && report.severity !== severityFilter) {
      return false;
    }
    return true;
  });

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: TrendingUp },
    { id: 'reports', label: 'Reports & Flags', icon: Flag },
    { id: 'users', label: 'User Moderation', icon: Users },
    { id: 'projects', label: 'Project Review', icon: FileText },
    { id: 'disputes', label: 'Dispute Resolution', icon: MessageSquare }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center space-x-3">
              <Shield className="h-8 w-8 text-orange-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Moderator Panel</h1>
                <p className="text-sm text-gray-500">Content & user moderation</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2 text-sm text-gray-500">
                <Clock className="h-4 w-4" />
                <span>Last updated: {new Date().toLocaleTimeString()}</span>
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
                    ? 'bg-orange-100 text-orange-700 border-orange-200'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                    }`}
                >
                  <tab.icon className="h-5 w-5 mr-3" />
                  {tab.label}
                </button>
              ))}
            </nav>

            {/* Quick Stats Sidebar */}
            {stats && (
              <div className="mt-8 bg-white p-4 rounded-lg shadow-sm border">
                <h3 className="text-sm font-medium text-gray-900 mb-3">Quick Stats</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">Pending Reports</span>
                    <span className="text-sm font-semibold text-red-600">{stats.pendingReports}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">Active Users</span>
                    <span className="text-sm font-semibold text-green-600">{stats.activeUsers}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">Under Review</span>
                    <span className="text-sm font-semibold text-yellow-600">{stats.projectsUnderReview}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">Resolved Today</span>
                    <span className="text-sm font-semibold text-blue-600">{stats.resolvedToday}</span>
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
                  <h2 className="text-lg font-medium text-gray-900 mb-4">Moderation Overview</h2>
                  {stats && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                      <div className="bg-white p-6 rounded-lg shadow-sm border">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <Flag className="h-6 w-6 text-red-600" />
                          </div>
                          <div className="ml-4">
                            <p className="text-sm font-medium text-gray-500">Pending Reports</p>
                            <p className="text-2xl font-semibold text-gray-900">{stats.pendingReports}</p>
                          </div>
                        </div>
                      </div>

                      <div className="bg-white p-6 rounded-lg shadow-sm border">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <Users className="h-6 w-6 text-blue-600" />
                          </div>
                          <div className="ml-4">
                            <p className="text-sm font-medium text-gray-500">Active Users</p>
                            <p className="text-2xl font-semibold text-gray-900">{stats.activeUsers}</p>
                          </div>
                        </div>
                      </div>

                      <div className="bg-white p-6 rounded-lg shadow-sm border">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <FileText className="h-6 w-6 text-yellow-600" />
                          </div>
                          <div className="ml-4">
                            <p className="text-sm font-medium text-gray-500">Under Review</p>
                            <p className="text-2xl font-semibold text-gray-900">{stats.projectsUnderReview}</p>
                          </div>
                        </div>
                      </div>

                      <div className="bg-white p-6 rounded-lg shadow-sm border">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <CheckCircle className="h-6 w-6 text-green-600" />
                          </div>
                          <div className="ml-4">
                            <p className="text-sm font-medium text-gray-500">Resolved Today</p>
                            <p className="text-2xl font-semibold text-gray-900">{stats.resolvedToday}</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                <div className="bg-white p-6 rounded-lg shadow-sm border">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between py-2 border-b border-gray-100">
                      <div className="flex items-center space-x-3">
                        <Flag className="h-4 w-4 text-red-500" />
                        <span className="text-sm text-gray-900">New report: Inappropriate project content</span>
                      </div>
                      <span className="text-xs text-gray-500">2 mins ago</span>
                    </div>
                    <div className="flex items-center justify-between py-2 border-b border-gray-100">
                      <div className="flex items-center space-x-3">
                        <UserCheck className="h-4 w-4 text-green-500" />
                        <span className="text-sm text-gray-900">User verification approved</span>
                      </div>
                      <span className="text-xs text-gray-500">15 mins ago</span>
                    </div>
                    <div className="flex items-center justify-between py-2 border-b border-gray-100">
                      <div className="flex items-center space-x-3">
                        <AlertTriangle className="h-4 w-4 text-yellow-500" />
                        <span className="text-sm text-gray-900">Dispute escalated to moderation</span>
                      </div>
                      <span className="text-xs text-gray-500">1 hour ago</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'reports' && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-medium text-gray-900">Reports & Flags</h2>
                </div>

                {/* Filters */}
                <div className="bg-white p-4 rounded-lg shadow-sm border">
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Search</label>
                      <div className="relative">
                        <input
                          type="text"
                          placeholder="Search reports..."
                          value={searchTerm}
                          onChange={(e) => setSearchTerm(e.target.value)}
                          className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
                        />
                        <Search className="h-4 w-4 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
                      <select
                        value={statusFilter}
                        onChange={(e) => setStatusFilter(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
                      >
                        <option value="all">All Status</option>
                        <option value="pending">Pending</option>
                        <option value="investigating">Investigating</option>
                        <option value="resolved">Resolved</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Severity</label>
                      <select
                        value={severityFilter}
                        onChange={(e) => setSeverityFilter(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
                      >
                        <option value="all">All Severity</option>
                        <option value="low">Low</option>
                        <option value="medium">Medium</option>
                        <option value="high">High</option>
                      </select>
                    </div>

                    <div className="flex items-end">
                      <button
                        onClick={fetchReports}
                        className="w-full inline-flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-orange-600 hover:bg-orange-700"
                      >
                        <Filter className="h-4 w-4 mr-2" />
                        Apply Filters
                      </button>
                    </div>
                  </div>
                </div>

                {/* Reports Table */}
                <div className="bg-white shadow-sm border rounded-lg overflow-hidden">
                  {loading ? (
                    <div className="flex items-center justify-center py-12">
                      <RefreshCw className="h-6 w-6 animate-spin text-gray-400" />
                    </div>
                  ) : (
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Report</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Severity</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {filteredReports.map((report) => (
                            <tr key={report.id} className="hover:bg-gray-50">
                              <td className="px-6 py-4">
                                <div>
                                  <div className="text-sm font-medium text-gray-900">{report.reportedItem}</div>
                                  <div className="text-sm text-gray-500">Reported by: {report.reportedBy}</div>
                                  <div className="text-xs text-gray-400 mt-1">{report.reason}</div>
                                </div>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${report.type === 'user' ? 'bg-blue-100 text-blue-800' :
                                  report.type === 'project' ? 'bg-green-100 text-green-800' :
                                    'bg-purple-100 text-purple-800'
                                  }`}>
                                  {report.type}
                                </span>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${report.severity === 'high' ? 'bg-red-100 text-red-800' :
                                  report.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                                    'bg-gray-100 text-gray-800'
                                  }`}>
                                  {report.severity}
                                </span>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${report.status === 'resolved' ? 'bg-green-100 text-green-800' :
                                  report.status === 'investigating' ? 'bg-yellow-100 text-yellow-800' :
                                    'bg-gray-100 text-gray-800'
                                  }`}>
                                  {report.status}
                                </span>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                {new Date(report.createdAt).toLocaleDateString()}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                <div className="flex items-center space-x-2">
                                  <button
                                    onClick={() => console.log('View report', report.id)}
                                    className="text-blue-600 hover:text-blue-900"
                                    title="View Details"
                                  >
                                    <Eye className="h-4 w-4" />
                                  </button>
                                  {report.status === 'pending' && (
                                    <button
                                      onClick={() => updateReportStatus(report.id, 'investigating')}
                                      className="text-yellow-600 hover:text-yellow-900"
                                      title="Start Investigation"
                                    >
                                      <Clock className="h-4 w-4" />
                                    </button>
                                  )}
                                  {report.status !== 'resolved' && (
                                    <button
                                      onClick={() => updateReportStatus(report.id, 'resolved')}
                                      className="text-green-600 hover:text-green-900"
                                      title="Mark Resolved"
                                    >
                                      <CheckCircle className="h-4 w-4" />
                                    </button>
                                  )}
                                </div>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'users' && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-medium text-gray-900">User Moderation</h2>
                </div>

                <div className="bg-white shadow-sm border rounded-lg overflow-hidden">
                  {loading ? (
                    <div className="flex items-center justify-center py-12">
                      <RefreshCw className="h-6 w-6 animate-spin text-gray-400" />
                    </div>
                  ) : (
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Reports</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Activity</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {users.map((user) => (
                            <tr key={user.id} className="hover:bg-gray-50">
                              <td className="px-6 py-4">
                                <div>
                                  <div className="text-sm font-medium text-gray-900">{user.email}</div>
                                  <div className="text-sm text-gray-500">ID: {user.id}</div>
                                </div>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${user.role === 'freelancer' ? 'bg-blue-100 text-blue-800' :
                                  'bg-green-100 text-green-800'
                                  }`}>
                                  {user.role}
                                </span>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${user.status === 'active' ? 'bg-green-100 text-green-800' :
                                  user.status === 'suspended' ? 'bg-yellow-100 text-yellow-800' :
                                    'bg-red-100 text-red-800'
                                  }`}>
                                  {user.status}
                                </span>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <span className={`text-sm font-medium ${user.reportCount > 0 ? 'text-red-600' : 'text-gray-500'
                                  }`}>
                                  {user.reportCount}
                                </span>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                {new Date(user.lastActivity).toLocaleDateString()}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                <div className="flex items-center space-x-2">
                                  <button
                                    onClick={() => console.log('View user', user.id)}
                                    className="text-blue-600 hover:text-blue-900"
                                    title="View Profile"
                                  >
                                    <Eye className="h-4 w-4" />
                                  </button>
                                  {user.status === 'active' && (
                                    <button
                                      onClick={() => moderateUser(user.id, 'suspend')}
                                      className="text-yellow-600 hover:text-yellow-900"
                                      title="Suspend User"
                                    >
                                      <AlertTriangle className="h-4 w-4" />
                                    </button>
                                  )}
                                  {user.status === 'suspended' && (
                                    <button
                                      onClick={() => moderateUser(user.id, 'activate')}
                                      className="text-green-600 hover:text-green-900"
                                      title="Reactivate User"
                                    >
                                      <UserCheck className="h-4 w-4" />
                                    </button>
                                  )}
                                  <button
                                    onClick={() => moderateUser(user.id, 'ban')}
                                    className="text-red-600 hover:text-red-900"
                                    title="Ban User"
                                  >
                                    <Ban className="h-4 w-4" />
                                  </button>
                                </div>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'projects' && (
              <div className="space-y-6">
                <h2 className="text-lg font-medium text-gray-900">Project Review</h2>
                <div className="bg-white p-8 rounded-lg shadow-sm border text-center">
                  <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">Project review interface for moderators will be implemented here</p>
                  <p className="text-sm text-gray-400 mt-2">Limited access compared to admin panel</p>
                </div>
              </div>
            )}

            {activeTab === 'disputes' && (
              <div className="space-y-6">
                <h2 className="text-lg font-medium text-gray-900">Dispute Resolution</h2>
                <div className="bg-white p-8 rounded-lg shadow-sm border text-center">
                  <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">Dispute resolution interface will be implemented here</p>
                  <p className="text-sm text-gray-400 mt-2">Mediate conflicts between users</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ModeratorPanel;
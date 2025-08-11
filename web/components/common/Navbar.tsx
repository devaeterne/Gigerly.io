// components/common/Navbar.tsx
'use client';

import React from 'react';
import { useAuth } from '@/app/contexts/AuthContext';
import { Briefcase, Search, Bell } from 'lucide-react';
import Link from 'next/link';
import UserMenu from './UserMenu';

const Navbar: React.FC = () => {
  const { user, isAuthenticated } = useAuth();

  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2">
            <Briefcase className="h-8 w-8 text-blue-600" />
            <span className="text-2xl font-bold text-gray-900">gigerly.io</span>
          </Link>

          {/* Navigation Links */}
          {isAuthenticated && user && (
            <div className="hidden md:flex items-center space-x-6">
              {user.role === 'freelancer' && (
                <>
                  <Link href="/freelancer" className="text-gray-700 hover:text-gray-900">
                    Dashboard
                  </Link>
                  <Link href="/freelancer/jobs" className="text-gray-700 hover:text-gray-900">
                    Find Work
                  </Link>
                  <Link href="/freelancer/proposals" className="text-gray-700 hover:text-gray-900">
                    My Proposals
                  </Link>
                </>
              )}

              {user.role === 'customer' && (
                <>
                  <Link href="/customer" className="text-gray-700 hover:text-gray-900">
                    Dashboard
                  </Link>
                  <Link href="/customer/projects" className="text-gray-700 hover:text-gray-900">
                    My Projects
                  </Link>
                  <Link href="/customer/hire" className="text-gray-700 hover:text-gray-900">
                    Hire Talent
                  </Link>
                </>
              )}

              {(user.role === 'admin' || user.role === 'moderator') && (
                <>
                  <Link href={`/${user.role}`} className="text-gray-700 hover:text-gray-900">
                    {user.role === 'admin' ? 'Admin Panel' : 'Moderation'}
                  </Link>
                  <Link href="/platform/users" className="text-gray-700 hover:text-gray-900">
                    Users
                  </Link>
                  <Link href="/platform/reports" className="text-gray-700 hover:text-gray-900">
                    Reports
                  </Link>
                </>
              )}
            </div>
          )}

          {/* Right side */}
          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                {/* Search */}
                <button className="p-2 text-gray-400 hover:text-gray-600">
                  <Search className="h-5 w-5" />
                </button>

                {/* Notifications */}
                <button className="p-2 text-gray-400 hover:text-gray-600 relative">
                  <Bell className="h-5 w-5" />
                  <span className="absolute top-1 right-1 h-2 w-2 bg-red-500 rounded-full"></span>
                </button>

                {/* User Menu */}
                <UserMenu />
              </>
            ) : (
              <>
                <Link
                  href="/login"
                  className="text-gray-700 hover:text-gray-900 px-3 py-2 text-sm font-medium"
                >
                  Sign In
                </Link>
                <Link
                  href="/register"
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium"
                >
                  Get Started
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;

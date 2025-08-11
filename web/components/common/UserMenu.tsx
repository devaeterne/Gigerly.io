// components/common/UserMenu.tsx
'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '@/app/contexts/AuthContext';
import { User, Settings, LogOut, ChevronDown, Shield, Users, FileText, Briefcase } from 'lucide-react';
import Link from 'next/link';

const UserMenu: React.FC = () => {
  const { user, logout } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  if (!user) return null;

  const getRoleIcon = () => {
    switch (user.role) {
      case 'admin':
        return <Shield className="h-4 w-4 text-red-600" />;
      case 'moderator':
        return <Shield className="h-4 w-4 text-orange-600" />;
      case 'customer':
        return <FileText className="h-4 w-4 text-blue-600" />;
      case 'freelancer':
        return <Briefcase className="h-4 w-4 text-green-600" />;
      default:
        return <User className="h-4 w-4" />;
    }
  };

  const getDashboardLink = () => {
    switch (user.role) {
      case 'admin':
        return '/admin';
      case 'moderator':
        return '/moderator';
      case 'customer':
        return '/customer';
      case 'freelancer':
        return '/freelancer';
      default:
        return '/';
    }
  };

  return (
    <div className="relative" ref={menuRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-100 transition-colors"
      >
        <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
          {user.profile?.avatar ? (
            <img
              src={user.profile.avatar}
              alt="Avatar"
              className="w-8 h-8 rounded-full object-cover"
            />
          ) : (
            <User className="h-4 w-4 text-gray-600" />
          )}
        </div>
        <div className="hidden md:block text-left">
          <p className="text-sm font-medium text-gray-900">
            {user.profile?.displayName || user.email}
          </p>
          <div className="flex items-center space-x-1">
            {getRoleIcon()}
            <span className="text-xs text-gray-500 capitalize">{user.role}</span>
          </div>
        </div>
        <ChevronDown className={`h-4 w-4 text-gray-500 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
          <div className="px-4 py-3 border-b border-gray-100">
            <p className="text-sm font-medium text-gray-900">
              {user.profile?.displayName || user.email}
            </p>
            <p className="text-xs text-gray-500">{user.email}</p>
            <div className="flex items-center space-x-1 mt-1">
              {getRoleIcon()}
              <span className="text-xs text-gray-500 capitalize">{user.role}</span>
            </div>
          </div>

          <Link
            href={getDashboardLink()}
            className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
            onClick={() => setIsOpen(false)}
          >
            <Users className="h-4 w-4 mr-3" />
            Dashboard
          </Link>

          <Link
            href="/profile"
            className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
            onClick={() => setIsOpen(false)}
          >
            <User className="h-4 w-4 mr-3" />
            Profile
          </Link>

          <Link
            href="/settings"
            className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
            onClick={() => setIsOpen(false)}
          >
            <Settings className="h-4 w-4 mr-3" />
            Settings
          </Link>

          <hr className="my-1" />

          <button
            onClick={() => {
              logout();
              setIsOpen(false);
            }}
            className="flex items-center w-full px-4 py-2 text-sm text-red-700 hover:bg-red-50"
          >
            <LogOut className="h-4 w-4 mr-3" />
            Sign Out
          </button>
        </div>
      )}
    </div>
  );
};

export default UserMenu;
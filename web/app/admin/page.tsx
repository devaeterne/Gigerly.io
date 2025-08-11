// app/admin/page.tsx

import React from 'react';
import { withAuth } from '@/app/contexts/AuthContext';
import AdminPanel from '@/components/panels/AdminPanel';

const AdminPage: React.FC = () => {
  return <AdminPanel />;
};

export default withAuth(AdminPage, {
  allowedRoles: ['admin']
});
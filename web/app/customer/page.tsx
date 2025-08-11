// app/customer/page.tsx
'use client';

import React from 'react';
import { withAuth } from '@/app/contexts/AuthContext';
import CustomerPanel from '@/components/panels/CustomerPanel';

const CustomerPage: React.FC = () => {
  return <CustomerPanel />;
};

export default withAuth(CustomerPage, {
  allowedRoles: ['customer']
});

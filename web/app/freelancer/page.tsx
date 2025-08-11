// app/freelancer/page.tsx
'use client';

import React from 'react';
import { withAuth } from '@/app/contexts/AuthContext';
import FreelancerPanel from '@/components/panels/FreelancerPanel';

const FreelancerPage: React.FC = () => {
  return <FreelancerPanel />;
};

export default withAuth(FreelancerPage, {
  allowedRoles: ['freelancer']
});
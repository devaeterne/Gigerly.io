// app/moderator/page.tsx
'use client';

import React from 'react';
import { withAuth } from '@/app/contexts/AuthContext';
import ModeratorPanel from '../../components/panels/ModeratorPanel';

const ModeratorPage: React.FC = () => {
  return <ModeratorPanel />;
};

export default withAuth(ModeratorPage, {
  allowedRoles: ['admin', 'moderator']
});
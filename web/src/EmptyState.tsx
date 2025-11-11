import React from 'react';

interface EmptyStateProps {
  message?: string;
  description?: string;
}

export function EmptyState({ 
  message = 'No properties found',
  description = 'Try adjusting your search filters or criteria'
}: EmptyStateProps) {
  return (
    <div className="empty-state">
      <div className="empty-state-icon">🏠</div>
      <div className="empty-state-title">{message}</div>
      <div className="empty-state-description">{description}</div>
    </div>
  );
}

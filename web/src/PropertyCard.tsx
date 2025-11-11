import React from 'react';
import type { Property } from './types/property';

interface PropertyCardProps {
  property: Property;
  isFavorite: boolean;
  onToggleFavorite: (propertyId: string) => void;
}

export function PropertyCard({ property, isFavorite, onToggleFavorite }: PropertyCardProps) {
  const handleViewDetails = () => {
    if (window.openai?.openExternal) {
      window.openai.openExternal({ href: property.detail_url });
    } else {
      window.open(property.detail_url, '_blank');
    }
  };

  const handleToggleFavorite = (e: React.MouseEvent) => {
    e.stopPropagation();
    onToggleFavorite(property.property_id);
  };

  return (
    <div className="property-card" onClick={handleViewDetails}>
      <img
        src={property.ld_image}
        alt={property.ld_name}
        className="property-image"
        loading="lazy"
        onError={(e) => {
          (e.target as HTMLImageElement).src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect fill="%23f3f4f6" width="400" height="300"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" fill="%239ca3af" font-family="sans-serif" font-size="18"%3ENo Image%3C/text%3E%3C/svg%3E';
        }}
      />
      
      <div className="property-content">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
          <div className="property-price">{property.price_text}</div>
          <button
            onClick={handleToggleFavorite}
            className="btn-secondary"
            style={{ padding: '0.25rem 0.5rem', fontSize: '1.25rem' }}
            title={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
          >
            {isFavorite ? '❤️' : '🤍'}
          </button>
        </div>
        
        <div className="property-name" title={property.ld_name}>
          {property.ld_name}
        </div>
        
        <div className="property-details">
          <span>🛏️ {property.bedrooms} bed{property.bedrooms !== 1 ? 's' : ''}</span>
          <span>🚿 {property.bathrooms} bath{property.bathrooms !== 1 ? 's' : ''}</span>
          <span>📍 {property.postcode}</span>
        </div>
        
        <div className="property-badges">
          <span className="badge">{property.property_type}</span>
          {property.garden && (
            <span className="badge badge-success">🌳 Garden</span>
          )}
          {property.parking && (
            <span className="badge badge-success">🚗 Parking</span>
          )}
          {property.status && (
            <span className="badge" style={{ fontSize: '0.7rem' }}>
              {property.status}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

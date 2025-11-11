import React, { useMemo } from 'react';
import { PropertyCard } from './PropertyCard';
import { EmptyState } from './EmptyState';
import { useToolOutput } from './hooks/useToolOutput';
import { useWidgetState } from './hooks/useWidgetState';
import { useTheme } from './hooks/useTheme';
import type { Property } from './types/property';

export function PropertyListWidget() {
  const toolOutput = useToolOutput();
  const theme = useTheme();
  const [widgetState, setWidgetState] = useWidgetState({
    favorites: [],
    hidden: [],
    sortBy: 'price_asc'
  });

  // Apply theme to root element
  React.useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  // Get properties and filter out hidden ones
  const properties = useMemo(() => {
    if (!toolOutput?.properties) return [];
    
    return toolOutput.properties.filter(
      (property) => !widgetState.hidden.includes(property.property_id)
    );
  }, [toolOutput, widgetState.hidden]);

  // Sort properties
  const sortedProperties = useMemo(() => {
    const sorted = [...properties];
    
    switch (widgetState.sortBy) {
      case 'price_asc':
        sorted.sort((a, b) => a.price_amount - b.price_amount);
        break;
      case 'price_desc':
        sorted.sort((a, b) => b.price_amount - a.price_amount);
        break;
      case 'bedrooms_desc':
        sorted.sort((a, b) => b.bedrooms - a.bedrooms);
        break;
    }
    
    return sorted;
  }, [properties, widgetState.sortBy]);

  const toggleFavorite = (propertyId: string) => {
    setWidgetState((prev) => ({
      ...prev,
      favorites: prev.favorites.includes(propertyId)
        ? prev.favorites.filter((id) => id !== propertyId)
        : [...prev.favorites, propertyId]
    }));
  };

  const handleSortChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setWidgetState((prev) => ({
      ...prev,
      sortBy: e.target.value as 'price_asc' | 'price_desc' | 'bedrooms_desc'
    }));
  };

  // Loading state
  if (!toolOutput) {
    return (
      <div className="widget-container">
        <div className="loading">
          <span>Loading properties...</span>
        </div>
      </div>
    );
  }

  // Empty state
  if (sortedProperties.length === 0) {
    return (
      <div className="widget-container">
        <EmptyState />
      </div>
    );
  }

  return (
    <div className="widget-container">
      {/* Header with filters info and sort */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: 'var(--spacing-md)',
        flexWrap: 'wrap',
        gap: 'var(--spacing-sm)'
      }}>
        <div>
          <h2 style={{ 
            fontSize: '1.5rem', 
            fontWeight: '700',
            marginBottom: 'var(--spacing-xs)'
          }}>
            {toolOutput.showing || sortedProperties.length} Properties
          </h2>
          {toolOutput.filters_applied && (
            <div style={{ 
              fontSize: '0.875rem', 
              color: 'var(--color-text-secondary)' 
            }}>
              {toolOutput.filters_applied.postcode && (
                <span>📍 {toolOutput.filters_applied.postcode} </span>
              )}
              {toolOutput.filters_applied.max_price && (
                <span>💰 Under £{toolOutput.filters_applied.max_price.toLocaleString()} </span>
              )}
              {toolOutput.filters_applied.min_bedrooms && (
                <span>🛏️ {toolOutput.filters_applied.min_bedrooms}+ beds </span>
              )}
            </div>
          )}
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
          <label htmlFor="sort-select" style={{ fontSize: '0.875rem' }}>
            Sort by:
          </label>
          <select
            id="sort-select"
            value={widgetState.sortBy}
            onChange={handleSortChange}
            className="btn-secondary"
            style={{ padding: '0.5rem' }}
          >
            <option value="price_asc">Price: Low to High</option>
            <option value="price_desc">Price: High to Low</option>
            <option value="bedrooms_desc">Bedrooms: Most First</option>
          </select>
        </div>
      </div>

      {/* Favorites count */}
      {widgetState.favorites.length > 0 && (
        <div style={{
          padding: 'var(--spacing-sm) var(--spacing-md)',
          backgroundColor: 'var(--color-bg-secondary)',
          borderRadius: 'var(--radius-md)',
          marginBottom: 'var(--spacing-md)',
          fontSize: '0.875rem'
        }}>
          ❤️ {widgetState.favorites.length} favorite{widgetState.favorites.length !== 1 ? 's' : ''}
        </div>
      )}

      {/* Property Grid */}
      <div className="property-grid">
        {sortedProperties.map((property) => (
          <PropertyCard
            key={property.property_id}
            property={property}
            isFavorite={widgetState.favorites.includes(property.property_id)}
            onToggleFavorite={toggleFavorite}
          />
        ))}
      </div>

      {/* Footer info */}
      {toolOutput.total_results && toolOutput.total_results > sortedProperties.length && (
        <div style={{
          marginTop: 'var(--spacing-lg)',
          textAlign: 'center',
          color: 'var(--color-text-secondary)',
          fontSize: '0.875rem'
        }}>
          Showing {sortedProperties.length} of {toolOutput.total_results} properties
        </div>
      )}
    </div>
  );
}

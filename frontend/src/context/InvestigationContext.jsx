/* oxlint-disable react/only-export-components */
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';

export const DEFAULT_FILTERS = { risk: 'All', state: 'All', category: 'All' };

const InvestigationContext = createContext(null);

export function InvestigationProvider({ children }) {
  const [filters, setFilters] = useState(DEFAULT_FILTERS);
  const [searchInput, setSearchInput] = useState('');
  const [search, setSearch] = useState('');
  const [searchMeta, setSearchMetaState] = useState({ loading: false, count: null, results: [] });

  useEffect(() => {
    const timer = window.setTimeout(() => setSearch(searchInput.trim()), 350);
    return () => window.clearTimeout(timer);
  }, [searchInput]);

  const setFilter = useCallback((key, value) => {
    setFilters((current) => ({ ...current, [key]: value }));
  }, []);

  const reset = useCallback(() => {
    setFilters(DEFAULT_FILTERS);
    setSearchInput('');
    setSearch('');
    setSearchMetaState({ loading: false, count: null, results: [] });
  }, []);

  const setSearchMeta = useCallback((meta) => setSearchMetaState(meta), []);

  const value = useMemo(
    () => ({
      filters,
      search,
      searchInput,
      searchMeta,
      isDebouncing: searchInput.trim() !== search,
      setFilter,
      setSearchInput,
      setSearchMeta,
      reset,
    }),
    [filters, search, searchInput, searchMeta, setFilter, setSearchMeta, reset],
  );

  return <InvestigationContext.Provider value={value}>{children}</InvestigationContext.Provider>;
}

export function useInvestigation() {
  const context = useContext(InvestigationContext);
  if (!context) throw new Error('useInvestigation must be used inside InvestigationProvider');
  return context;
}

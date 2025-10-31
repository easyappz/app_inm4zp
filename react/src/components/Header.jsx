import React, { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate, Link } from 'react-router-dom';
import listings from '../api/listings';
import authApi from '../api/auth';
import AuthModal from './AuthModal';

export default function Header() {
  const [search, setSearch] = useState('');
  const [authOpen, setAuthOpen] = useState(false);
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const meQuery = useQuery({
    queryKey: ['authMe'],
    queryFn: () => authApi.me(),
    retry: false,
  });

  const byUrlMutation = useMutation({
    mutationFn: (url) => listings.getByUrl(url),
    onSuccess: (data) => {
      if (data && data.id) {
        navigate(`/listing/${data.id}`);
        setSearch('');
      }
    },
  });

  const onSubmit = (e) => {
    e.preventDefault();
    const url = search.trim();
    if (!url) return;
    byUrlMutation.mutate(url);
  };

  const logout = () => {
    localStorage.removeItem('token');
    queryClient.invalidateQueries({ queryKey: ['authMe'] });
  };

  return (
    <header data-easytag="id1-react/src/components/Header.jsx" className="sticky top-0 z-20 border-b bg-white/95 backdrop-blur">
      <div data-easytag="id2-react/src/components/Header.jsx" className="mx-auto flex max-w-6xl items-center gap-4 px-4 py-3">
        <Link data-easytag="id3-react/src/components/Header.jsx" to="/" className="flex items-center gap-2">
          <div data-easytag="id4-react/src/components/Header.jsx" className="h-8 w-8 rounded-md bg-accent" aria-hidden="true" />
          <span data-easytag="id5-react/src/components/Header.jsx" className="text-lg font-semibold text-gray-900">Авитолог</span>
        </Link>
        <form data-easytag="id6-react/src/components/Header.jsx" onSubmit={onSubmit} className="flex w-full max-w-xl items-center gap-2">
          <input data-easytag="id7-react/src/components/Header.jsx" value={search} onChange={(e) => setSearch(e.target.value)} className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-accent focus:outline-none" placeholder="Вставьте ссылку на объявление Avito" />
          <button data-easytag="id8-react/src/components/Header.jsx" type="submit" className="rounded-md bg-accent px-4 py-2 text-sm font-medium text-white hover:opacity-90 disabled:opacity-60" disabled={byUrlMutation.isPending}>{byUrlMutation.isPending ? 'Ищем…' : 'Найти'}</button>
        </form>
        <div data-easytag="id9-react/src/components/Header.jsx" className="ml-auto flex items-center gap-3">
          {meQuery.isLoading ? (
            <div data-easytag="id10-react/src/components/Header.jsx" className="h-9 w-24 animate-pulse rounded-md bg-gray-200" />
          ) : meQuery.data ? (
            <div data-easytag="id11-react/src/components/Header.jsx" className="flex items-center gap-3">
              <span data-easytag="id12-react/src/components/Header.jsx" className="text-sm text-gray-700">{meQuery.data.username}</span>
              <button data-easytag="id13-react/src/components/Header.jsx" onClick={logout} className="rounded-md bg-gray-100 px-3 py-2 text-sm text-gray-700 hover:bg-gray-200">Выйти</button>
            </div>
          ) : (
            <button data-easytag="id14-react/src/components/Header.jsx" onClick={() => setAuthOpen(true)} className="rounded-md bg-accent px-4 py-2 text-sm font-semibold text-white hover:opacity-90">Войти</button>
          )}
        </div>
      </div>

      <AuthModal open={authOpen} onClose={() => setAuthOpen(false)} />
    </header>
  );
}

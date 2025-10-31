import React from 'react';
import { useQuery } from '@tanstack/react-query';
import listingsApi from '../api/listings';
import ListingCard from '../components/ListingCard';

export default function Home() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['popularListings'],
    queryFn: () => listingsApi.getPopular(12),
  });

  return (
    <div data-easytag="id1-react/src/pages/Home.jsx" className="mx-auto max-w-6xl px-4 py-6">
      <section data-easytag="id2-react/src/pages/Home.jsx" className="space-y-4">
        <h2 data-easytag="id3-react/src/pages/Home.jsx" className="text-xl font-semibold text-gray-900">Самые просматриваемые</h2>
        {isLoading ? (
          <div data-easytag="id4-react/src/pages/Home.jsx" className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
            {Array.from({ length: 8 }).map((_, i) => (
              <div data-easytag="id5-react/src/pages/Home.jsx" key={i} className="h-64 animate-pulse rounded-lg bg-gray-200" />
            ))}
          </div>
        ) : isError ? (
          <div data-easytag="id6-react/src/pages/Home.jsx" className="rounded-md bg-red-50 px-4 py-3 text-sm text-red-700">Не удалось загрузить список.</div>
        ) : (
          <div data-easytag="id7-react/src/pages/Home.jsx" className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
            {Array.isArray(data) && data.length > 0 ? (
              data.map((item) => <ListingCard key={item.id} item={item} />)
            ) : (
              <div data-easytag="id8-react/src/pages/Home.jsx" className="col-span-full rounded-lg border bg-white p-6 text-sm text-gray-600">Пока нет популярных объявлений.</div>
            )}
          </div>
        )}
      </section>
    </div>
  );
}

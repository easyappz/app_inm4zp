import React from 'react';
import { Link } from 'react-router-dom';

export default function ListingCard({ item }) {
  return (
    <Link data-easytag="id1-react/src/components/ListingCard.jsx" to={`/listing/${item.id}`} className="group block rounded-lg border bg-white shadow-sm hover:shadow-md">
      <div data-easytag="id2-react/src/components/ListingCard.jsx" className="h-40 w-full overflow-hidden rounded-t-lg bg-gray-100">
        {item.image_url ? (
          <img data-easytag="id3-react/src/components/ListingCard.jsx" src={item.image_url} alt={item.title} className="h-full w-full object-cover transition-transform group-hover:scale-105" />
        ) : (
          <div data-easytag="id4-react/src/components/ListingCard.jsx" className="h-full w-full" />
        )}
      </div>
      <div data-easytag="id5-react/src/components/ListingCard.jsx" className="space-y-1 px-4 py-3">
        <div data-easytag="id6-react/src/components/ListingCard.jsx" className="line-clamp-2 text-sm font-medium text-gray-900">{item.title}</div>
        <div data-easytag="id7-react/src/components/ListingCard.jsx" className="flex items-center justify-between">
          <div data-easytag="id8-react/src/components/ListingCard.jsx" className="text-base font-semibold text-gray-900">{item.price ? `${item.price} ₽` : '—'}</div>
          <div data-easytag="id9-react/src/components/ListingCard.jsx" className="text-xs text-gray-500">👁 {item.view_count ?? 0}</div>
        </div>
      </div>
    </Link>
  );
}

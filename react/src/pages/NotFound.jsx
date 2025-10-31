import React from 'react';
import { Link } from 'react-router-dom';

export default function NotFound() {
  return (
    <div data-easytag="id1-react/src/pages/NotFound.jsx" className="mx-auto max-w-6xl px-4 py-20 text-center">
      <div data-easytag="id2-react/src/pages/NotFound.jsx" className="mx-auto h-40 w-40 rounded-full bg-gray-100" />
      <h1 data-easytag="id3-react/src/pages/NotFound.jsx" className="mt-6 text-2xl font-semibold text-gray-900">Страница не найдена</h1>
      <p data-easytag="id4-react/src/pages/NotFound.jsx" className="mt-2 text-sm text-gray-600">Проверьте адрес или вернитесь на главную страницу.</p>
      <div data-easytag="id5-react/src/pages/NotFound.jsx" className="mt-6">
        <Link data-easytag="id6-react/src/pages/NotFound.jsx" to="/" className="inline-flex items-center rounded-md bg-accent px-5 py-2 text-sm font-semibold text-white hover:opacity-90">На главную</Link>
      </div>
    </div>
  );
}
